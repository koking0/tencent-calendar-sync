#!/usr/bin/env python3
"""
sync_caldav.py - 并发拉取腾讯会议 CalDAV 日程，跳过 404 race condition
用法: python3 sync_caldav.py
"""
import requests
import re
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

CALDAV_URL = os.environ.get(
    "CALDAV_URL",
    "https://cal.meeting.tencent.com/caldav/{user}/calendar/".format(
        user=os.environ.get("CALDAV_USER", "").split("@")[0]
    )
)
AUTH = (
    os.environ.get("CALDAV_USER", ""),
    os.environ.get("CALDAV_PASS", "")
)
OUT_DIR = os.path.expanduser("~/.vdirsyncer/calendars/tencent/events/")
MAX_WORKERS = 20

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # PROPFIND 列出所有 .ics href
    print("Fetching calendar index...", flush=True)
    r = requests.request(
        "PROPFIND", CALDAV_URL, auth=AUTH,
        headers={"Depth": "1", "Content-Type": "application/xml"},
        data='<?xml version="1.0"?><propfind xmlns="DAV:"><prop><getetag/></prop></propfind>',
        timeout=30
    )
    print(f"PROPFIND status: {r.status_code}", flush=True)
    if r.status_code != 207:
        print(f"PROPFIND failed: {r.text[:300]}", file=sys.stderr)
        sys.exit(1)

    hrefs = re.findall(r'<[Dd]:?href>([^<]+\.ics)</[Dd]:?href>', r.text)
    print(f"Found {len(hrefs)} items, downloading with {MAX_WORKERS} workers...", flush=True)

    def fetch_one(href):
        fname = href.split("/")[-1]
        out_path = os.path.join(OUT_DIR, fname)
        base = "https://cal.meeting.tencent.com"
        try:
            res = requests.get(f"{base}{href}", auth=AUTH, timeout=15)
            if res.status_code == 404:
                return "skip"
            if res.status_code != 200:
                return f"err:{res.status_code}"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(res.text)
            return "ok"
        except Exception as e:
            return f"err:{e}"

    ok = skip = err = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(fetch_one, h): h for h in hrefs}
        for i, fut in enumerate(as_completed(futures), 1):
            result = fut.result()
            if result == "ok":
                ok += 1
            elif result == "skip":
                skip += 1
            else:
                err += 1
            if i % 100 == 0:
                print(f"  Progress: {i}/{len(hrefs)} (saved={ok}, skip={skip}, err={err})", flush=True)

    print(f"Done: saved={ok}, skipped(404)={skip}, errors={err}", flush=True)
    if ok == 0:
        print("ERROR: No files downloaded, aborting.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
