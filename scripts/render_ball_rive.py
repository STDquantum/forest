import argparse, base64, json, os, re, shutil, subprocess, tempfile, threading, zipfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from PIL import Image
import io

ROOT = Path(__file__).resolve().parent.parent
PREFIX = 'assets/composeResources/com.seekrtech.stforestkit.resources/files/'
NAMES = [f'ground{i:02d}_plant_ball' for i in range(100)]

def main():
 p=argparse.ArgumentParser(description='Render transparent ball WebP images from a Forest APK.')
 p.add_argument('apk',type=Path); p.add_argument('--themes',nargs='+',type=int,default=None);p.add_argument('--output',type=Path,default=ROOT/'docs/assets/ball');p.add_argument('--replace',action='store_true',help='Overwrite selected existing images (requires --themes)');args=p.parse_args()
 if args.replace and args.themes is None: p.error('--replace requires explicit --themes')
 with zipfile.ZipFile(args.apk) as apk:
  available = sorted(int(m.group(1)) for name in apk.namelist() if (m := re.fullmatch(re.escape(PREFIX) + r'plant/theme_(\d+)\.webp', name)))
 requested = sorted(set(args.themes if args.themes is not None else available))
 if any(n<0 or n>=len(NAMES) for n in requested): p.error('theme IDs must be between 0 and 99')
 args.themes = [n for n in requested if args.replace or not (args.output/(NAMES[n]+'.webp')).exists()]
 if not args.themes:
  print('No new ball images to render.'); return
 with tempfile.TemporaryDirectory(prefix='forest-ball-') as tmp:
  d=Path(tmp)
  with zipfile.ZipFile(args.apk) as z:
   (d/'focus_screen.riv').write_bytes(z.read(PREFIX+'rive/focus_screen.riv'))
   for n in args.themes:
    (d/f'theme_{n}.webp').write_bytes(z.read(PREFIX+f'plant/theme_{n}.webp'))
  (d/'params.json').write_text(json.dumps(args.themes),encoding='utf8'); shutil.copy(ROOT/'scripts/ball_render.html',d/'index.html')
  # Dependencies are installed into a temporary directory and never added to the website.
  npm='npm.cmd' if os.name=='nt' else 'npm'
  subprocess.run([npm,'install','--prefix',str(d),'--cache',str(d/'cache'),'--no-audit','--no-fund','--offline=false','--registry=https://registry.npmjs.org','@rive-app/canvas@2.49.4','playwright-core@1.56.1'],check=True)
  for name in ['rive.js','rive.wasm']: shutil.copy(d/'node_modules/@rive-app/canvas'/name,d/name)
  result={}
  class Handler(SimpleHTTPRequestHandler):
   def __init__(self,*a,**kw): super().__init__(*a,directory=str(d),**kw)
   def do_POST(self):
    result.update(json.loads(self.rfile.read(int(self.headers['Content-Length']))));self.send_response(200);self.end_headers()
  server=ThreadingHTTPServer(('127.0.0.1',0),Handler); thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   runner=ROOT/'scripts/ball_render_runner.cjs';env=os.environ.copy();env['NODE_PATH']=str(d/'node_modules');env['BALL_URL']=f'http://127.0.0.1:{server.server_port}/'
   subprocess.run(['node',str(runner)],env=env,check=True,timeout=120)
  finally: server.shutdown();server.server_close()
  if set(result)!=set(map(str,args.themes)): raise RuntimeError('Rendering did not return all requested themes')
  args.output.mkdir(parents=True,exist_ok=True)
  for n in args.themes:
   im=Image.open(io.BytesIO(base64.b64decode(result[str(n)].split(',',1)[1]))).convert('RGBA')
   # Match the 936 px globe frame used by existing homepage images.
   scale=1.04514; sx,sy=466.696,443.867;tx,ty=467.,467.5
   im=im.convert('RGBa').transform((936,936),Image.Transform.AFFINE,(1/scale,0,sx-tx/scale,0,1/scale,sy-ty/scale),Image.Resampling.BICUBIC).convert('RGBA')
   path=args.output/(NAMES[n]+'.webp')
   if not args.replace and path.exists():
    print('Skipped existing',path); continue
   im.save(path,'WEBP',lossless=True,method=6);print('Saved',path)
if __name__=='__main__': main()

