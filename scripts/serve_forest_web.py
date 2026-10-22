"""Serve the planting demo with live workspace tree metadata and images."""
import argparse
import base64
import hashlib
import json
import re
import webbrowser
from urllib.request import urlopen
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'docs'
TREE_FILE = re.compile(r'tree_type_(\d+)_phase_(\d+|dead|product)(_christmas)?\.(png|webp)')


def catalog():
    metadata = json.loads((WEB / 'treeType.json').read_text(encoding='utf-8-sig'))
    paths, phases, frames = {}, {}, {}
    selected = {}
    # All tree images live in the single workspace resource directory.
    for directory in (WEB / 'assets' / 'trees',):
        for file in sorted(directory.iterdir()):
            match = TREE_FILE.fullmatch(file.name)
            if not match:
                continue
            tid, phase, suffix, extension = match.groups()
            key = f'{tid}_{phase}{suffix or ""}'
            if key in selected and extension != 'webp':
                continue
            selected[key] = file
    for key, file in selected.items():
        tid, phase, suffix, _ = TREE_FILE.fullmatch(file.name).groups()
        stat = file.stat()
        paths[key] = f'assets/trees/{file.name}?v={stat.st_mtime_ns}-{stat.st_size}'
        if not suffix and phase.isdigit():
            phases.setdefault(tid, set()).add(int(phase))
    for file in sorted((WEB / 'assets' / 'frames').iterdir()):
        match = re.fullmatch(r'frame_(\w+)_tree_type_(\d+)_phase_(\d+)_(\d+)\.(webp|png)', file.name)
        if match:
            state, tid, phase, frame, _ = match.groups()
            frames.setdefault(f'{state}_{tid}_{phase}', []).append((int(frame), 'assets/frames/' + file.name))
    frames = {key: [url for _, url in sorted(value)] for key, value in frames.items()}
    rows = []
    animated = {key.split('_')[1] for key in frames}
    for tid in sorted(phases, key=int):
        tree = metadata.get(tid, {})
        growth = sorted(phases[tid])
        xmas = [int(key.split('_')[1]) for key in paths if key.startswith(tid + '_') and key.endswith('_christmas')]
        rows.append([int(tid), tree.get('nameZH') or tree.get('nameEN') or f'树 #{tid}', tree.get('nameEN', ''),
                     int(tid in animated), max(growth), int(bool(xmas)), max(xmas or growth)])
    result = dict(trees=rows, metadata=metadata, phases={key: sorted(value) for key, value in phases.items()},
                  frames=frames, imagePaths=paths)
    result['revision'] = hashlib.sha256(json.dumps(result, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return result


def refresh_snapshots():
    """Keep offline pages current at startup without a separate build pipeline."""
    data = catalog()
    themes = json.loads((WEB / 'land-themes.json').read_text(encoding='utf-8-sig'))
    def encoded(value):
        return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    (WEB / 'forest-bootstrap.js').write_text('window.FOREST_BOOTSTRAP=' + encoded({'catalog': data, 'themes': themes}) + ';', encoding='utf-8')
    # Local-file canvases need embedded textures for pixel picking and PNG export.
    offline = {}
    for folder in ('trees', 'ground'):
        for image in sorted((WEB / 'assets' / folder).iterdir()):
            if image.suffix.lower() not in ('.png', '.webp'):
                continue
            mime = 'image/webp' if image.suffix.lower() == '.webp' else 'image/png'
            offline[image.relative_to(WEB).as_posix()] = 'data:' + mime + ';base64,' + base64.b64encode(image.read_bytes()).decode('ascii')
    offline_file = WEB / 'forest-local-textures.js'
    offline_source = 'window.FOREST_LOCAL_IMAGES=' + encoded(offline) + ';'
    if not offline_file.exists() or offline_file.read_text(encoding='utf-8') != offline_source:
        offline_file.write_text(offline_source, encoding='utf-8')
    page = WEB / 'index.html'
    html = page.read_text(encoding='utf-8-sig')
    plant_themes = {theme['id']: theme['plant'] for theme in themes if theme.get('plant')}
    if plant_themes:
        html = re.sub(r'(?:const|let) THEMES=[\s\S]*?;\s*\n',
                      lambda match: 'const THEMES=' + encoded(plant_themes) + ';\n', html, count=1)
    for variable, value in {'TREES': data['trees'], 'TREE_METADATA': data['metadata'], 'TREE_PHASES': data['phases'],
                            'FRAME_PATHS': data['frames'], 'TREE_IMAGE_PATHS': data['imagePaths']}.items():
        html = re.sub(r'(?:const|let) ' + variable + r'=.*?;\s*\n',
                      lambda match: 'let ' + variable + '=' + encoded(value) + ';\n', html, count=1)
    page.write_text(html, encoding='utf-8')


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_GET(self):
        if urlsplit(self.path).path == '/api/tree-data':
            try:
                payload = json.dumps(catalog(), ensure_ascii=False).encode('utf-8')
            except (OSError, ValueError) as error:
                # A partially saved JSON must not replace the last valid browser state.
                self.send_error(503, 'Tree data temporarily unavailable')
                print(f'Data refresh deferred: {error}')
                return
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        super().do_GET()

    def translate_path(self, path):
        clean = unquote(urlsplit(path).path)
        if clean.startswith('/assets/trees/'):
            name = clean.removeprefix('/assets/trees/')
            if TREE_FILE.fullmatch(name):
                current = WEB / 'assets' / 'trees' / name
                if current.is_file():
                    return str(current)
        return super().translate_path(path)

    def log_message(self, format, *args):
        if len(args) < 2 or str(args[1]) != '200':
            super().log_message(format, *args)


class ForestHTTPServer(ThreadingHTTPServer):
    # Windows otherwise permits multiple old servers to bind the same port.
    allow_reuse_address = False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8766)
    parser.add_argument('--open', action='store_true')
    parser.add_argument('--page', choices=('forest-editor.html', 'index.html'), default='index.html')
    args = parser.parse_args()
    refresh_snapshots()
    url = f'http://127.0.0.1:{args.port}/'
    try:
        server = ForestHTTPServer(('127.0.0.1', args.port), Handler)
    except OSError:
        # Reuse an already running copy when the user double-clicks again.
        if args.open:
            with urlopen(url + 'api/tree-data', timeout=3) as response:
                existing = json.load(response)
            if all(key in existing for key in ('trees', 'metadata', 'revision')):
                webbrowser.open(url + 'index.html')
                return
        raise
    print(f'Forest live web: {url}', flush=True)
    if args.open:
        webbrowser.open(url + 'index.html')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
