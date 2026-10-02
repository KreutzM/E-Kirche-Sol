#!/usr/bin/env python3
"""Fetch the curated free reference set from Wikimedia Commons.

Standard library only. Licence metadata is checked live at download time.
"""
from pathlib import Path
import argparse, csv, hashlib, html, json, re, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "manifest.json"
META = ROOT / "sources" / "commons_download_metadata.jsonl"
REPORT = ROOT / "sources" / "download_report.csv"
API = "https://commons.wikimedia.org/w/api.php"
UA = "E-Kirche-Sol/1.0 (https://github.com/KreutzM/E-Kirche-Sol)"

def clean(value):
    if not value:
        return ""
    value = html.unescape(value)
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", value).strip()

def info(title, width):
    params = {
        "action":"query","format":"json","formatversion":"2",
        "prop":"imageinfo","titles":"File:"+title,
        "iiprop":"url|size|mime|sha1|extmetadata|commonmetadata",
    }
    if width:
        params["iiurlwidth"] = str(width)
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent":UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    page = data["query"]["pages"][0]
    if page.get("missing"):
        raise RuntimeError("Commons file not found")
    ii = page["imageinfo"][0]
    ext = ii.get("extmetadata", {})
    def em(k):
        v = ext.get(k, {})
        return clean(v.get("value","")) if isinstance(v, dict) else ""
    return {
        "original_url": ii.get("url",""),
        "thumb_url": ii.get("thumburl",""),
        "width": ii.get("width"),
        "height": ii.get("height"),
        "mime": ii.get("mime"),
        "sha1": ii.get("sha1"),
        "license_short_name": em("LicenseShortName"),
        "license_url": em("LicenseUrl"),
        "artist": em("Artist"),
        "credit": em("Credit"),
        "source": em("Source"),
        "date_time_original": em("DateTimeOriginal"),
        "commonmetadata": ii.get("commonmetadata", {}),
    }

def allowed(name):
    # Full match: CC BY-NC / BY-ND must never pass as CC BY.
    normalized = re.sub(r"[-\s]+", " ", (name or "").lower()).strip()
    return bool(re.fullmatch(
        r"(?:cc by(?: sa)?(?: \d+(?:\.\d+)?)?|cc0(?: 1\.0)?|public domain|pdm(?: 1\.0)?|gfdl(?: \d+(?:\.\d+)?)?)",
        normalized,
    ))

def destination(rec):
    if rec["group"] == "modern":
        base = ROOT / "references" / "images" / "modern"
    elif rec["group"] == "historic_pd":
        base = ROOT / "references" / "images" / "historic"
    else:
        base = ROOT / "references" / "plans" / "downloaded"
    return base / f'{rec["id"]}_{Path(rec["title"]).name}'

def download(url, dest):
    if dest.exists():
        raise FileExistsError(f"Preserving existing reference: {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent":UA})
    with urllib.request.urlopen(req, timeout=120) as r, tmp.open("wb") as f:
        while True:
            chunk = r.read(1024*1024)
            if not chunk:
                break
            f.write(chunk)
    tmp.replace(dest)

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--priority", type=int, choices=(1,2,3))
    ap.add_argument("--max-width", type=int, default=2500)
    ap.add_argument("--originals", action="store_true")
    args = ap.parse_args(argv)
    if args.max_width <= 0:
        ap.error("--max-width must be positive")

    rows = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if args.priority:
        rows = [r for r in rows if int(r["priority"]) <= args.priority]

    # Keep all previous provenance, including records outside this priority subset.
    META.parent.mkdir(parents=True, exist_ok=True)
    report = []
    ok = 0
    failed = 0
    for i, rec in enumerate(rows, 1):
        print(f'[{i}/{len(rows)}] {rec["id"]} {rec["title"]}')
        try:
            dest = destination(rec)
            if dest.exists():
                report.append([rec["id"], "existing", "", str(dest.relative_to(ROOT)), ""])
                print("  existing (preserved; licence/provenance not rechecked)")
                continue
            meta = info(rec["title"], None if args.originals else args.max_width)
            if not allowed(meta["license_short_name"]):
                raise RuntimeError(f'licence not accepted: {meta["license_short_name"]!r}')
            url = meta["original_url"] if args.originals else (meta["thumb_url"] or meta["original_url"])
            download(url, dest)
            meta.update({"dataset_id":rec["id"],"title":rec["title"],"commons_page":rec["commons_page"],
                         "downloaded_to":str(dest.relative_to(ROOT)),
                         "download_url":url,
                         "downloaded_at_utc":datetime.now(timezone.utc).isoformat(),
                         "local_sha256":hashlib.sha256(dest.read_bytes()).hexdigest()})
            with META.open("a", encoding="utf-8") as f:
                f.write(json.dumps(meta, ensure_ascii=False)+"\n")
            report.append([rec["id"], "downloaded", meta["license_short_name"], str(dest.relative_to(ROOT)), ""])
            ok += 1
        except Exception as exc:
            failed += 1
            report.append([rec["id"], "ERROR", "", "", str(exc)])
            print("  ERROR:", exc)
        time.sleep(0.2)
    with REPORT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "status", "license", "file", "error"])
        writer.writerows(report)
    print(f"Downloaded {ok}/{len(rows)} assets; {failed} errors. Existing files preserved.")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
