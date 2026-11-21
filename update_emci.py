# Test access before replacing a previously working playlist.
manifest = fetch(url, "application/vnd.apple.mpegurl")
if not manifest.lstrip().startswith("#EXTM3U"):
    raise ValueError("HLS endpoint did not return an M3U8 manifest")
