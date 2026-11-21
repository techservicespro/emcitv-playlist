#!/usr/bin/env python3
"""Refresh an EMCI TV playlist using publicly returned Dailymotion metadata.

This checks HLS accessibility from the runner only; it does NOT ensure the URL
will work for other IPs, devices or players. Respect broadcaster permissions.
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

VIDEO_ID = "x8azdkm"
API_URL = f"https://geo.dailymotion.com/videos/{VIDEO_ID}"
OUTPUT = Path(__file__).resolve().parent / "EMCI-TV.m3u"


def get_text(url, accept):
    req = Request(url, headers={
        "Accept": accept,
        "User-Agent": "EMCIPlaylistUpdater/2.0",
    })
    with urlopen(req, timeout=25) as response:
        return response.read(1024 * 1024).decode("utf-8", errors="replace")


def main():
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"[INFO] UTC: {timestamp}")
    print("[INFO] Verification is performed from the GitHub runner only.")
    try:
        metadata = json.loads(get_text(API_URL, "application/json"))
        stream = metadata.get("stream") or {}
        url = stream.get("url")
        if stream.get("stream_type") != "live" or not isinstance(url, str):
            raise ValueError("Dailymotion metadata does not provide a live HLS URL")
        parsed = urlparse(url)
        if (parsed.scheme != "https" or
                parsed.hostname != "cdndirector.dailymotion.com" or
                not parsed.path.endswith(".m3u8") or not parsed.query):
            raise ValueError("Unexpected HLS URL format")
        # Check only the manifest response available to the runner.
        manifest = get_text(url, "application/vnd.apple.mpegurl")
        if not manifest.lstrip().startswith("#EXTM3U"):
            raise ValueError("HLS URL did not return an M3U8 manifest")
        fingerprint = hashlib.sha256(url.encode()).hexdigest()[:12]
        print(f"[INFO] HLS manifest reachable from runner; URL fingerprint: {fingerprint}")
        print("[WARN] This does not prove playback will work on PC, Android or Smart TV.")
        content = (
            '#EXTM3U\n'
            '#EXTINF:-1 tvg-name="EMCI TV Afrique" group-title="Religieuses",EMCI TV Afrique\n'
            f'{url}\n'
        )
        if OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") == content:
            print("[INFO] Playlist unchanged: Dailymotion returned the same URL")
            return
        tmp = OUTPUT.with_name(OUTPUT.name + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, OUTPUT)
        print("[INFO] Playlist updated locally; workflow will commit the change")
    except (ValueError, KeyError, OSError, HTTPError, URLError, json.JSONDecodeError) as exc:
        print(f"[ERROR] Update failed; existing file retained: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
