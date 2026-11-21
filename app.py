import re
from urllib.parse import quote, unquote, urljoin
from flask import Flask, Response, jsonify, request
import requests
import yt_dlp

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
        "http_headers": HEADERS,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(VIDEO_URL, download=False)
        # Récupérer le manifeste m3u8 global ou la meilleure qualité HLS
        if "manifest_url" in info and info["manifest_url"]:
            return info["manifest_url"]
        if "url" in info and ".m3u8" in info["url"]:
            return info["url"]
        for f in reversed(info.get("formats", [])):
            if f.get("protocol") in ("m3u8", "m3u8_native") and f.get("url"):
                return f["url"]
    raise RuntimeError("Impossible d'extraire une URL m3u8 via yt-dlp.")

@app.route("/")
def index():
    return "EMCI TV Proxy actif. Routes disponibles : /playlist.m3u, /live.m3u8, /debug"

@app.route("/debug")
def debug():
    try:
        master_url = get_master_m3u8()
        r = requests.get(master_url, headers=HEADERS, timeout=10)
        return jsonify({
            "status": "ok",
            "master_url_prefix": master_url[:65] + "...",
            "m3u8_http_status": r.status_code,
            "m3u8_preview": r.text[:400]
        })
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

@app.route("/playlist.m3u")
def playlist():
    base_url = request.host_url.rstrip("/")
    content = (
        "#EXTM3U\n"
        '#EXTINF:-1 tvg-id="EMCITV" tvg-name="EMCI TV Afrique",EMCI TV Afrique\n'
        f"{base_url}/live.m3u8\n"
    )
    return Response(content, mimetype="audio/x-mpegurl")

@app.route("/live.m3u8")
def live_m3u8():
    try:
        master_url = get_master_m3u8()
        return proxy_m3u8(master_url)
    except Exception as e:
        return Response(f"Erreur flux: {e}", status=502)

@app.route("/proxy")
def proxy():
    target_url = unquote(request.args.get("url", ""))
    if not target_url.startswith("http"):
        return Response("URL invalide", status=400)

    if ".m3u8" in target_url:
        return proxy_m3u8(target_url)

    r = requests.get(target_url, headers=HEADERS, stream=True, timeout=15)
    return Response(
        r.iter_content(chunk_size=32768),
        status=r.status_code,
        content_type=r.headers.get("Content-Type", "video/MP2T")
    )

def proxy_m3u8(m3u8_url):
    r = requests.get(m3u8_url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    base_proxy = f"{request.host_url.rstrip('/')}/proxy?url="

    rewritten_lines = []
    for line in r.text.splitlines():
        stripped = line.strip()
        if not stripped:
            rewritten_lines.append(line)
        elif stripped.startswith("#"):
            def replace_uri(match):
                abs_url = urljoin(m3u8_url, match.group(1))
                return f'URI="{base_proxy}{quote(abs_url, safe="")}"'
            rewritten_lines.append(re.sub(r'URI="([^"]+)"', replace_uri, line))
        else:
            abs_url = urljoin(m3u8_url, stripped)
            rewritten_lines.append(f"{base_proxy}{quote(abs_url, safe='')}")

    return Response("\n".join(rewritten_lines), mimetype="application/vnd.apple.mpegurl")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
