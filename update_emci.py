#!/usr/bin/env python3
"""Refresh EMCI TV Afrique playlist from Dailymotion's public video metadata.
Only use where Dailymotion's terms and the broadcaster's permissions allow it.
"""
import json
import os
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

VIDEO_ID = "x8azdkm"
API_URL = f"https://geo.dailymotion.com/videos/{VIDEO_ID}"
OUTPUT = Path(__file__).resolve().parent / "EMCI-TV.m3u"


def fetch(url, accept):
    req = Request(url, headers={"Accept": accept, "User-Agent": "EMCIPlaylistUpdater/1.0"})
    with urlopen(req, timeout=25) as response:
        return response.read(1024 * 1024).decode("utf-8", errors="replace")


def main():
    try:
        data = json.loads(fetch(API_URL, "application/json"))
        stream = data.get("stream") or {}
        url = stream.get("url")
        if stream.get("stream_type") != "live" or not isinstance(url, str):
            raise ValueError("No live HLS URL in Dailymotion metadata")
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != "cdndirector.dailymotion.com" or not parsed.path.endswith(".m3u8"):
            raise ValueError("Unexpected HLS URL host or format")
        # Test access before replacing a previously working playlist.
        manifest = fetch(url, "application/vnd.apple.mpegurl")
        if not manifest.lstrip().startswith("#EXTM3U"):
            raise ValueError("HLS endpoint did not return an M3U8 manifest")
        content = '#EXTM3U\n#EXTINF:-1 tvg-name="EMCI TV Afrique" group-title="Religieuses",EMCI TV Afrique\n' + url + '\n'
        if OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") == content:
            print("Playlist unchanged")
            return
        temp = OUTPUT.with_suffix(".m3u.tmp")
        temp.write_text(content, encoding="utf-8")
        os.replace(temp, OUTPUT)
        print("Playlist refreshed successfully")
    except (ValueError, KeyError, OSError, HTTPError, URLError, json.JSONDecodeError) as exc:
        print(f"Update failed; existing playlist preserved: {type(exc).__name__}: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
