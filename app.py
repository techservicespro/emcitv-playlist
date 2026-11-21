import re
from urllib.parse import quote, unquote, urljoin
from flask import Flask, Response, request
import requests

app = Flask(__name__)

VIDEO_ID = "x8azdkm"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.dailymotion.com/",
    "Origin": "https://www.dailymotion.com"
}

def get_master_m3u8():
    meta_url = f"https://www.dailymotion.com/player/metadata/video/{VIDEO_ID}"
    r = requests.get(meta_url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    data = r.json()
    qualities = data.get("qualities", {})
    auto = qualities.get("auto", [])
    if not auto:
        raise RuntimeError("Aucun flux HLS trouvé dans les métadonnées Dailymotion.")
    return auto[0]["url"]

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
        return Response(f"Erreur récupération flux: {e}", status=502)

@app.route("/proxy")
def proxy():
    target_url = unquote(request.args.get("url", ""))
    if not target_url.startswith("http"):
        return Response("URL invalide", status=400)

    if ".m3u8" in target_url:
        return proxy_m3u8(target_url)

    # Relais des segments vidéo (.ts / .aac) en streaming
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
            # Réécrire les URI intégrées dans les balises (ex: #EXT-X-KEY ou #EXT-X-MEDIA)
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
