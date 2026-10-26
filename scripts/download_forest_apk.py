"""Resolve the Forest Android download used by the official Chinese website."""
import argparse
import json
import re
import shutil
import time
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit
from urllib.request import Request, urlopen

HOME = "https://www.upwardsware.com/zh_CN/"
USER_AGENT = "Mozilla/5.0 (compatible; ForestResourceUpdater/1.0)"


def open_url(url, headers=None):
    return urlopen(Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})}), timeout=120)


def read_text(url):
    for attempt in range(3):
        try:
            with open_url(url) as response:
                return response.read().decode("utf-8")
        except OSError:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("src"):
            self.scripts.append(attrs["src"])


def discover_apk_url(home=HOME):
    # The Android button is populated by client JavaScript, absent from HTML links.
    parser = PageLinks()
    parser.feed(read_text(home))
    endpoints = set()
    for source in parser.scripts:
        if "/_next/static/chunks/pages/" not in source or "/_app-" in source:
            continue
        script = read_text(urljoin(home, source))
        endpoints.update(re.findall(
            r'https://cn-android-apk\.seekrtech\.com/[^\s"\x27`<>]*\.json', script
        ))
    if len(endpoints) != 1:
        raise RuntimeError(f"Expected one official Forest APK version endpoint, found {len(endpoints)}")
    endpoint = endpoints.pop()
    # Bypass CDN caches in the same way as the website's download button.
    data = json.loads(read_text(endpoint + f"?ts={time.time_ns() // 1_000_000}"))
    title = data.get("apk_title", "")
    if not isinstance(title, str) or not re.fullmatch(r"Forest[^/\\]*\.apk", title, re.IGNORECASE):
        raise ValueError("Official version metadata did not contain a Forest APK filename")
    url = urljoin(endpoint, quote(title))
    if urlsplit(url).netloc != "cn-android-apk.seekrtech.com":
        raise ValueError("Unexpected APK download host")
    return url


def _download_chunks(url, partial):
    # Small ranges avoid losing the entire large APK when a CDN connection ends early.
    chunk_size = 8 * 1024 * 1024
    offset, total = 0, None
    with partial.open("wb") as output:
        while total is None or offset < total:
            for attempt in range(3):
                try:
                    with open_url(url, {"Range": f"bytes={offset}-{offset + chunk_size - 1}"}) as response:
                        if response.status == 200 and offset == 0:
                            shutil.copyfileobj(response, output, length=1024 * 1024)
                            expected = response.headers.get("Content-Length")
                            if expected and output.tell() != int(expected):
                                raise OSError("Incomplete APK response")
                            return
                        match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", response.headers.get("Content-Range", ""))
                        if response.status != 206 or not match:
                            raise OSError("CDN did not return the requested APK range")
                        start, end, size = map(int, match.groups())
                        if start != offset or end < start or end >= size or end - start >= chunk_size or (total is not None and total != size):
                            raise OSError("Inconsistent APK range metadata")
                        chunk = response.read(chunk_size + 1)
                        if len(chunk) != end - start + 1:
                            raise OSError("Incomplete APK range response")
                    output.write(chunk)
                    offset += len(chunk)
                    total = size
                    break
                except OSError:
                    output.seek(offset)
                    output.truncate()
                    if attempt == 2:
                        raise
                    time.sleep(2 ** attempt)


def download_apk(url, destination):
    destination = Path(destination)
    partial = destination.with_suffix(".apk.part")
    try:
        for attempt in range(3):
            try:
                _download_chunks(url, partial)
                with zipfile.ZipFile(partial) as apk:
                    if not {"AndroidManifest.xml", "resources.arsc"}.issubset(apk.namelist()):
                        raise ValueError("Download is missing required Android APK resources")
                    bad_file = apk.testzip()
                    if bad_file:
                        raise ValueError(f"Corrupt APK member: {bad_file}")
                partial.replace(destination)
                return
            except (OSError, zipfile.BadZipFile):
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
    finally:
        partial.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resolve-only", action="store_true", help="Print the current URL without downloading")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "Forest 专注森林.apk")
    args = parser.parse_args()
    url = discover_apk_url()
    print(f"Official Forest APK: {url}", flush=True)
    if not args.resolve_only:
        download_apk(url, args.output)
        print(f"Downloaded: {args.output}")


if __name__ == "__main__":
    main()
