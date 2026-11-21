import re
from urllib.parse import quote, unquote, urljoin
from flask import Flask, Response, jsonify, request
import requests
import yt_dlp
from yt_dlp.networking.impersonate import ImpersonateTarget

app = Flask(__name__)

VIDEO_URL = "https://www.dailymotion.com/video/x8azdkm"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://www.dailymotion.com/",
    "Origin": "https://www.dailymotion.com",
}

def get_master_m3u8():
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "best",
        "impersonate": ImpersonateTarget("chrome"),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(VIDEO_URL, download=False)
        if "manifest_url" in info and info["manifest_url"]:
            return info["manifest_url"]
        if "url" in info and ".m3u8" in info["url"]:
            return info["url"]
        for f in reversed(info.get("formats", [])):
            if f.get("protocol") in ("m3u8", "m3u8_native") and f.get("url"):
                return f["url"]
    raise RuntimeError("Impossible d'extraire une URL m3u8 via yt-dlp.")
