import shutil
import subprocess
from pathlib import Path

def transcode_to_hls(source: str, output_dir: str) -> str:
    """Development worker. Run this in an isolated background worker in production."""
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is not installed on this server")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    playlist = out / "index.m3u8"
    cmd = [
        "ffmpeg", "-y", "-i", source,
        "-vf", "scale=w='min(1280,iw)':h=-2",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-hls_time", "6", "-hls_playlist_type", "vod",
        "-hls_segment_filename", str(out / "segment_%05d.ts"),
        str(playlist)
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=3600)
    return str(playlist)
