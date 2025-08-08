#!/usr/bin/env python3
"""
Delete all PDFs (and related questions) from the backend via REST API.
This calls DELETE /pdfs/{id} for each existing PDF. The backend endpoint
also removes the physical file from UPLOAD_DIR when present.

Usage:
  python3 scripts/delete_all_pdfs_via_api.py --base-url https://your-backend --yes

Notes:
  - Supports pagination (limit=100) until all PDFs are collected
  - Prints progress and a summary report
  - Requires no extra dependencies beyond Python stdlib
"""

import argparse
import json
import sys
import time
from urllib.request import Request, urlopen
from urllib.parse import urlencode, urljoin
from urllib.error import HTTPError, URLError


def http_get_json(url: str):
    req = Request(url, headers={
        "User-Agent": "curl/8.0 Python-urllib/3",
        "Accept": "application/json",
    })
    with urlopen(req, timeout=30) as resp:
        data = resp.read()
        return json.loads(data.decode("utf-8"))


def http_delete(url: str):
    req = Request(url, method="DELETE", headers={
        "User-Agent": "curl/8.0 Python-urllib/3",
        "Accept": "application/json",
        "Content-Type": "application/json",
    })
    with urlopen(req, timeout=60) as resp:
        code = resp.getcode()
        data = resp.read()
        try:
            body = json.loads(data.decode("utf-8")) if data else {}
        except Exception:
            body = {"raw": data.decode("utf-8", errors="replace")}
        return code, body


def list_all_pdfs(base_url: str, page_size: int = 100):
    pdfs = []
    skip = 0
    while True:
        params = urlencode({"skip": skip, "limit": page_size})
        url = urljoin(base_url, f"/pdfs/?{params}")
        batch = http_get_json(url)
        if not batch:
            break
        pdfs.extend(batch)
        if len(batch) < page_size:
            break
        skip += page_size
    return pdfs


def main():
    parser = argparse.ArgumentParser(description="Delete all PDFs via API")
    parser.add_argument("--base-url", required=True, help="Backend base URL, e.g. https://example.com")
    parser.add_argument("--yes", action="store_true", help="Do not ask for confirmation")
    parser.add_argument("--sleep", type=float, default=0.1, help="Sleep seconds between delete calls")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    print(f"Base URL: {base_url}")

    if not args.yes:
        print("This will delete ALL PDFs via the backend API. Re-run with --yes to proceed.")
        sys.exit(1)

    try:
        pdfs = list_all_pdfs(base_url)
    except (HTTPError, URLError) as e:
        print(f"Failed to list PDFs: {e}")
        sys.exit(2)

    print(f"Found {len(pdfs)} PDFs to delete")
    if not pdfs:
        print("Nothing to delete.")
        return

    successes = 0
    failures = 0
    for i, pdf in enumerate(pdfs, 1):
        pdf_id = pdf.get("id")
        filename = pdf.get("filename")
        url = urljoin(base_url + "/", f"pdfs/{pdf_id}")
        try:
            code, body = http_delete(url)
            ok = 200 <= code < 300 and (body.get("success") is True or True)
            if ok:
                successes += 1
                print(f"[{i}/{len(pdfs)}] Deleted id={pdf_id} filename={filename}")
            else:
                failures += 1
                print(f"[{i}/{len(pdfs)}] FAILED to delete id={pdf_id} filename={filename}: code={code} body={body}")
        except HTTPError as e:
            failures += 1
            try:
                detail = e.read().decode("utf-8")
            except Exception:
                detail = str(e)
            print(f"[{i}/{len(pdfs)}] ERROR deleting id={pdf_id} filename={filename}: {e.code} {detail}")
        except URLError as e:
            failures += 1
            print(f"[{i}/{len(pdfs)}] URL ERROR deleting id={pdf_id} filename={filename}: {e}")

        time.sleep(args.sleep)

    print("\nSummary:")
    print(f"  Total:     {len(pdfs)}")
    print(f"  Deleted:   {successes}")
    print(f"  Failed:    {failures}")


if __name__ == "__main__":
    main()


