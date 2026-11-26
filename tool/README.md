# Jagstar Auto Pilot – upload tool

Complete working scripts used by the Jagstar (@jagstargaming) channel owner.

- `upload.py` – uploads a Short via YouTube Data API v3 (`videos.insert`, scope `youtube.upload`) as private with an optional `publishAt` schedule. OAuth 2.0 installed-app flow; token stored only on the owner's PC.
- `find_highlights.py` – finds loud highlight moments in the owner's own gameplay recordings (ffmpeg).
- `make_short.py` – renders a 1080x1920 Short from a highlight (ffmpeg).

No credentials are included in this repository.

Usage:
```
python upload.py short.mp4 meta.json
```
meta.json: `{"title": "...", "description": "...", "tags": [], "publish_at": "2026-11-27T12:00:00+00:00", "category_id": "20"}`
