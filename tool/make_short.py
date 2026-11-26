"""Cut a clip and render it as a 1080x1920 YouTube Short.

Usage: python make_short.py VIDEO START SECONDS OUT.mp4
Landscape footage is centered over a blurred, zoomed copy of itself.
"""
import os
import subprocess
import sys


def main():
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    src, start, seconds, out = sys.argv[1], float(sys.argv[2]), min(float(sys.argv[3]), 59), sys.argv[4]
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    vf = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "boxblur=20:5,eq=brightness=-0.08[bg];"
        "[0:v]scale=1080:-2[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,fps=60,format=yuv420p[v]"
    )
    cmd = [
        "ffmpeg", "-hide_banner", "-y", "-ss", str(start), "-t", str(seconds), "-i", src,
        "-filter_complex", vf, "-map", "[v]", "-map", "0:a?",
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-profile:v", "high",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", out,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        sys.exit(r.stderr[-3000:])
    print(out)


if __name__ == "__main__":
    main()
