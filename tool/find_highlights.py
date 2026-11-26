"""Find the loudest non-overlapping moments in a gameplay recording.

Usage: python find_highlights.py VIDEO [--count 4] [--seconds 45]
Prints JSON list of {start, end, score} sorted by start time.
"""
import argparse
import json
import re
import subprocess
import sys


def loudness_series(path):
    """Momentary loudness (LUFS) sampled every 0.1 s via ffmpeg ebur128."""
    cmd = [
        "ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn",
        "-af", "ebur128=metadata=1,ametadata=print:key=lavfi.r128.M:file=-",
        "-f", "null", "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    times, values = [], []
    t = None
    for line in proc.stdout.splitlines():
        m = re.search(r"pts_time:([\d.]+)", line)
        if m:
            t = float(m.group(1))
            continue
        m = re.search(r"lavfi\.r128\.M=(-?[\d.]+|-inf)", line)
        if m and t is not None:
            v = m.group(1)
            values.append(-70.0 if v == "-inf" else max(float(v), -70.0))
            times.append(t)
    if not values:
        sys.exit("No audio found (or ffmpeg failed):\n" + proc.stderr[-2000:])
    return times, values


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--count", type=int, default=4)
    ap.add_argument("--seconds", type=float, default=45)
    args = ap.parse_args()

    times, vals = loudness_series(args.video)
    step = (times[-1] - times[0]) / max(len(times) - 1, 1) or 0.1
    win = max(1, int(args.seconds / step))
    duration = times[-1]
    if duration <= args.seconds:
        print(json.dumps([{"start": 0.0, "end": round(duration, 1), "score": 0}]))
        return

    # Score each window: mean loudness + bonus for sharp peaks (reactions/kills).
    prefix = [0.0]
    for v in vals:
        prefix.append(prefix[-1] + v)
    scores = []
    for i in range(0, len(vals) - win, max(1, int(1 / step))):
        seg = vals[i:i + win]
        mean = (prefix[i + win] - prefix[i]) / win
        peak = sorted(seg)[-max(1, win // 20):]
        scores.append((mean + 0.5 * (sum(peak) / len(peak) - mean), times[i]))

    scores.sort(reverse=True)
    picked = []
    for score, start in scores:
        if all(abs(start - p["start"]) >= args.seconds for p in picked):
            # Start a few seconds earlier so the hook has context.
            s = max(0.0, start - 3)
            picked.append({"start": round(s, 1), "end": round(min(s + args.seconds, duration), 1),
                           "score": round(score, 2)})
        if len(picked) >= args.count:
            break
    print(json.dumps(sorted(picked, key=lambda p: p["start"]), indent=2))


if __name__ == "__main__":
    main()
