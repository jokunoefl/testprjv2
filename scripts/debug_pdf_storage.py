#!/usr/bin/env python3
"""
Debug PDF storage issues in Render environment.
This script provides comprehensive diagnostics for file persistence problems.

Usage:
  python3 scripts/debug_pdf_storage.py --base-url https://your-backend
"""

import argparse
import json
import sys
import os
import time
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from urllib.error import HTTPError, URLError


def http_get_json(url: str):
    req = Request(url, headers={
        "User-Agent": "PDF-Debug/1.0",
        "Accept": "application/json",
    })
    with urlopen(req, timeout=30) as resp:
        data = resp.read()
        return json.loads(data.decode("utf-8"))


def check_server_health(base_url: str):
    """Check server health and basic info"""
    print("🔍 SERVER HEALTH CHECK")
    print("=" * 50)
    
    try:
        # Health check
        health_url = urljoin(base_url, "/health")
        health_data = http_get_json(health_url)
        print(f"✅ Health: {health_data}")
        
        # Root endpoint
        root_url = urljoin(base_url, "/")
        root_data = http_get_json(root_url)
        print(f"✅ Root: {root_data}")
        
    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        return False
    
    return True


def check_pdf_database(base_url: str):
    """Check PDF database status"""
    print("\n📊 PDF DATABASE STATUS")
    print("=" * 50)
    
    try:
        pdfs = http_get_json(urljoin(base_url, "/pdfs/"))
        print(f"📋 Total PDFs in database: {len(pdfs)}")
        
        if not pdfs:
            print("⚠️  No PDFs found in database")
            return []
        
        # Analyze PDFs
        with_url = [p for p in pdfs if p.get('url')]
        without_url = [p for p in pdfs if not p.get('url')]
        
        print(f"🔗 PDFs with URL: {len(with_url)}")
        print(f"❌ PDFs without URL: {len(without_url)}")
        
        if without_url:
            print("\n📋 PDFs WITHOUT URL:")
            for pdf in without_url[:5]:
                print(f"  - ID {pdf.get('id')}: {pdf.get('filename')}")
            if len(without_url) > 5:
                print(f"  ... and {len(without_url) - 5} more")
        
        return pdfs
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return []


def check_pdf_files(base_url: str, pdfs: list):
    """Check individual PDF file accessibility"""
    print("\n📁 PDF FILE ACCESSIBILITY")
    print("=" * 50)
    
    if not pdfs:
        print("No PDFs to check")
        return
    
    working = []
    missing = []
    errors = []
    
    for i, pdf in enumerate(pdfs, 1):
        pdf_id = pdf.get('id')
        filename = pdf.get('filename', 'unknown')
        url = pdf.get('url', '')
        
        print(f"\n[{i}/{len(pdfs)}] Checking PDF ID {pdf_id}: {filename}")
        
        # Check file accessibility
        try:
            view_url = urljoin(base_url, f"/pdfs/{pdf_id}/view")
            req = Request(view_url, method="HEAD")
            with urlopen(req, timeout=10) as resp:
                if resp.getcode() == 200:
                    working.append(pdf)
                    print(f"  ✅ File accessible (HTTP 200)")
                else:
                    missing.append(pdf)
                    print(f"  ❌ File missing (HTTP {resp.getcode()})")
        except HTTPError as e:
            if e.code == 404:
                missing.append(pdf)
                print(f"  ❌ File missing (404)")
            else:
                errors.append((pdf, f"HTTP {e.code}"))
                print(f"  ⚠️  HTTP Error: {e.code}")
        except URLError as e:
            errors.append((pdf, str(e)))
            print(f"  ⚠️  Network Error: {e}")
        
        # Check URL status
        if url:
            print(f"  🔗 URL: {url[:60]}...")
        else:
            print(f"  ❌ No URL set")
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"  Total PDFs: {len(pdfs)}")
    print(f"  Working files: {len(working)}")
    print(f"  Missing files: {len(missing)}")
    print(f"  Errors: {len(errors)}")
    
    return working, missing, errors


def check_upload_directory(base_url: str):
    """Check upload directory status via API"""
    print("\n📂 UPLOAD DIRECTORY STATUS")
    print("=" * 50)
    
    try:
        # Try to get a sample PDF to check directory
        pdfs = http_get_json(urljoin(base_url, "/pdfs/"))
        if pdfs:
            sample_pdf = pdfs[0]
            pdf_id = sample_pdf.get('id')
            
            # Try to access the file
            view_url = urljoin(base_url, f"/pdfs/{pdf_id}/view")
            req = Request(view_url)
            with urlopen(req, timeout=10) as resp:
                if resp.getcode() == 200:
                    content_length = resp.headers.get('content-length', 'unknown')
                    content_type = resp.headers.get('content-type', 'unknown')
                    print(f"✅ Sample file accessible")
                    print(f"  Content-Length: {content_length}")
                    print(f"  Content-Type: {content_type}")
                else:
                    print(f"❌ Sample file not accessible (HTTP {resp.getcode()})")
        else:
            print("⚠️  No PDFs available to test directory")
            
    except Exception as e:
        print(f"❌ Directory check failed: {e}")


def provide_recommendations(working: list, missing: list, errors: list):
    """Provide recommendations based on findings"""
    print("\n💡 RECOMMENDATIONS")
    print("=" * 50)
    
    if missing:
        print(f"⚠️  {len(missing)} PDF files are missing from storage")
        print("\n🔧 IMMEDIATE ACTIONS:")
        print("  1. Check if files were actually uploaded")
        print("  2. Verify upload directory permissions")
        print("  3. Check server logs for file system errors")
        print("  4. Re-upload missing PDFs")
        
        print("\n🔧 LONG-TERM SOLUTIONS:")
        print("  1. Implement file backup system")
        print("  2. Use external storage (S3, GCS)")
        print("  3. Store files in database as BLOB")
        print("  4. Implement file integrity checks")
        
        print("\n📋 MISSING FILES:")
        for pdf in missing[:10]:
            print(f"  - ID {pdf.get('id')}: {pdf.get('filename')}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")
    
    if errors:
        print(f"\n⚠️  {len(errors)} PDFs have access errors")
        print("🔧 TROUBLESHOOTING:")
        print("  1. Check network connectivity")
        print("  2. Verify server is running")
        print("  3. Check firewall settings")
        print("  4. Review server logs")
    
    if not missing and not errors:
        print("✅ All PDF files are accessible!")
        print("🎉 No immediate action required")
    
    print(f"\n📊 STATISTICS:")
    print(f"  Working: {len(working)}")
    print(f"  Missing: {len(missing)}")
    print(f"  Errors: {len(errors)}")
    print(f"  Success Rate: {len(working)/(len(working)+len(missing)+len(errors))*100:.1f}%" if (working or missing or errors) else "N/A")


def main():
    parser = argparse.ArgumentParser(description="Debug PDF storage issues")
    parser.add_argument("--base-url", required=True, help="Backend base URL")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    base_url = args.base_url.rstrip("/")
    print(f"🔍 PDF Storage Debug Tool")
    print(f"Target: {base_url}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Run diagnostics
    if not check_server_health(base_url):
        print("❌ Server is not responding properly")
        sys.exit(1)
    
    pdfs = check_pdf_database(base_url)
    working, missing, errors = check_pdf_files(base_url, pdfs)
    check_upload_directory(base_url)
    provide_recommendations(working, missing, errors)
    
    print(f"\n✅ Debug completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
