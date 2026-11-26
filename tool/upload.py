"""Upload a Short to YouTube and schedule it (free, YouTube Data API v3).

Usage: python upload.py VIDEO.mp4 META.json [--root C:\\Claude\\Youtube]
META.json: {"title", "description", "tags": [], "publish_at": ISO8601, "category_id": "20"}
Prints JSON {"id", "url", "publish_at"}.
"""
import argparse
import json
import os
import sys

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_service(root):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        sys.exit("Missing packages: pip install google-api-python-client google-auth-oauthlib")

    secrets = os.path.join(root, ".secrets")
    client = os.path.join(secrets, "client_secret.json")
    token = os.path.join(secrets, "token.json")
    if not os.path.exists(client):
        sys.exit(f"No OAuth client at {client} - see the skill's Setup section.")

    creds = Credentials.from_authorized_user_file(token, SCOPES) if os.path.exists(token) else None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = InstalledAppFlow.from_client_secrets_file(client, SCOPES).run_local_server(port=0)
        with open(token, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("meta")
    ap.add_argument("--root", default=r"C:\Claude\Youtube")
    args = ap.parse_args()

    from googleapiclient.http import MediaFileUpload

    with open(args.meta, encoding="utf-8") as f:
        meta = json.load(f)
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": False}
    if meta.get("publish_at"):
        status["publishAt"] = meta["publish_at"]
    body = {
        "snippet": {
            "title": meta["title"][:100],
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "categoryId": meta.get("category_id", "20"),
        },
        "status": status,
    }
    yt = get_service(args.root)
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(args.video, chunksize=8 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None:
        prog, resp = req.next_chunk()
        if prog:
            print(f"uploading {int(prog.progress() * 100)}%", file=sys.stderr)
    vid = resp["id"]
    print(json.dumps({"id": vid, "url": f"https://youtube.com/shorts/{vid}",
                      "publish_at": meta.get("publish_at")}))


if __name__ == "__main__":
    main()
