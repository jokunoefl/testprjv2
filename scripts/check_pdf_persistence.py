#!/usr/bin/env python3
"""
Check PDF file persistence and provide recommendations for Render environment.
This script helps diagnose file system issues in cloud environments.

Usage:
  python3 scripts/check_pdf_persistence.py --base-url https://your-backend
"""

import argparse
import json
import sys
import time
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from urllib.error import HTTPError, URLError


def http_get_json(url: str):
    req = Request(url, headers={
        "User-Agent": "PDF-Persistence-Check/1.0",
        "Accept": "application/json",
    })
    with urlopen(req, timeout=30) as resp:
        data = resp.read()
        return json.loads(data.decode("utf-8"))


def check_pdf_status(base_url: str):
    """Check all PDFs and their file status"""
    print(f"Checking PDF persistence at: {base_url}")
    print("=" * 60)
    
    try:
        # Get all PDFs
        pdfs = http_get_json(urljoin(base_url, "/pdfs/"))
        print(f"Found {len(pdfs)} PDFs in database")
        
        if not pdfs:
            print("No PDFs found in database.")
            return
        
        # Check each PDF
        missing_files = []
        working_files = []
        no_url_files = []
        
        for i, pdf in enumerate(pdfs, 1):
            pdf_id = pdf.get("id")
            filename = pdf.get("filename", "unknown")
            url = pdf.get("url", "")
            
            print(f"\n[{i}/{len(pdfs)}] Checking PDF ID {pdf_id}: {filename}")
            
            # Check if file exists via view endpoint
            try:
                view_url = urljoin(base_url, f"/pdfs/{pdf_id}/view")
                req = Request(view_url, method="HEAD")
                with urlopen(req, timeout=10) as resp:
                    if resp.getcode() == 200:
                        working_files.append(pdf)
                        print(f"  ✅ File exists and accessible")
                    else:
                        missing_files.append(pdf)
                        print(f"  ❌ File missing (HTTP {resp.getcode()})")
            except HTTPError as e:
                if e.code == 404:
                    missing_files.append(pdf)
                    print(f"  ❌ File missing (404)")
                else:
                    print(f"  ⚠️  HTTP Error: {e.code}")
            except URLError as e:
                print(f"  ⚠️  Network Error: {e}")
            
            # Check URL status
            if not url:
                no_url_files.append(pdf)
                print(f"  ⚠️  No URL set")
            else:
                print(f"  📎 URL: {url[:50]}...")
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY:")
        print(f"  Total PDFs: {len(pdfs)}")
        print(f"  Working files: {len(working_files)}")
        print(f"  Missing files: {len(missing_files)}")
        print(f"  No URL set: {len(no_url_files)}")
        
        if missing_files:
            print(f"\n⚠️  ISSUES DETECTED:")
            print(f"  {len(missing_files)} PDF files are missing from the file system")
            print(f"  This is normal in Render's ephemeral file system")
            print(f"  Files will be lost on deploy/sleep")
            
            print(f"\n🔧 RECOMMENDATIONS:")
            print(f"  1. Use external storage (S3, Google Cloud Storage)")
            print(f"  2. Implement file backup/restore system")
            print(f"  3. Store files in persistent database (BLOB)")
            print(f"  4. Use CDN for file serving")
            
            print(f"\n📋 MISSING FILES:")
            for pdf in missing_files[:5]:  # Show first 5
                print(f"  - ID {pdf.get('id')}: {pdf.get('filename')}")
            if len(missing_files) > 5:
                print(f"  ... and {len(missing_files) - 5} more")
        
        if no_url_files:
            print(f"\n⚠️  PDFs WITHOUT URL:")
            print(f"  {len(no_url_files)} PDFs have no URL set")
            print(f"  These cannot be re-downloaded automatically")
            
            print(f"\n📋 PDFs WITHOUT URL:")
            for pdf in no_url_files[:5]:  # Show first 5
                print(f"  - ID {pdf.get('id')}: {pdf.get('filename')}")
            if len(no_url_files) > 5:
                print(f"  ... and {len(no_url_files) - 5} more")
        
        if not missing_files and not no_url_files:
            print(f"\n✅ ALL GOOD:")
            print(f"  All PDF files are accessible and have URLs set")
        
    except Exception as e:
        print(f"Error checking PDFs: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Check PDF file persistence")
    parser.add_argument("--base-url", required=True, help="Backend base URL")
    args = parser.parse_args()
    
    base_url = args.base_url.rstrip("/")
    check_pdf_status(base_url)


if __name__ == "__main__":
    main()
