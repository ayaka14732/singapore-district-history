#!/usr/bin/env python3
"""
使用 Wikipedia REST API 为33个选区搜集代表性图片
"""
import os
import requests
import shutil
from pathlib import Path
import time

IMAGES_DIR = Path('/home/ubuntu/singapore_book/images')
IMAGES_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "SingaporeBookProject/1.0 (educational; contact@example.com)",
    "Accept": "application/json"
}

# 每个选区对应的 Wikipedia 页面标题和文件名
CONSTITUENCIES = [
    ("tanjong_pagar", "Tanjong Pagar"),
    ("jalan_besar", "Jalan Besar"),
    ("bishan_toa_payoh", "Bishan, Singapore"),
    ("marymount", "Marymount, Singapore"),
    ("potong_pasir", "Potong Pasir"),
    ("radin_mas", "Radin Mas"),
    ("kebun_baru", "Kebun Baru"),
    ("east_coast", "East Coast, Singapore"),
    ("marine_parade", "Marine Parade"),
    ("aljunied", "Aljunied"),
    ("mountbatten", "Mountbatten, Singapore"),
    ("pasir_ris_changi", "Pasir Ris"),
    ("tampines", "Tampines"),
    ("tampines_changkat", "Tampines"),
    ("sembawang", "Sembawang"),
    ("sembawang_west", "Sembawang"),
    ("nee_soon", "Nee Soon"),
    ("marsiling_yew_tee", "Marsiling"),
    ("yio_chu_kang", "Yio Chu Kang"),
    ("jalan_kayu", "Jalan Kayu"),
    ("ang_mo_kio", "Ang Mo Kio"),
    ("sengkang", "Sengkang"),
    ("punggol", "Punggol"),
    ("hougang", "Hougang"),
    ("holland_bukit_timah", "Holland Village, Singapore"),
    ("jurong_east_bukit_batok", "Jurong East"),
    ("west_coast_jurong_west", "Jurong West"),
    ("chua_chu_kang", "Chua Chu Kang"),
    ("bukit_gombak", "Bukit Gombak"),
    ("bukit_panjang", "Bukit Panjang"),
    ("jurong_central", "Jurong Central"),
    ("pioneer", "Pioneer, Singapore"),
]

def get_wikipedia_image(wiki_title, filename):
    dest = IMAGES_DIR / f"{filename}.jpg"
    if dest.exists() and dest.stat().st_size > 5000:
        print(f"  [SKIP] {filename} already exists")
        return str(dest)
    
    try:
        # Use Wikipedia REST API to get page summary (includes thumbnail)
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(wiki_title)}"
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print(f"  [WARN] Wikipedia API returned {r.status_code} for {wiki_title}")
            return None
        
        data = r.json()
        thumbnail = data.get("thumbnail") or data.get("originalimage")
        if not thumbnail:
            print(f"  [WARN] No thumbnail for {wiki_title}")
            return None
        
        img_url = thumbnail.get("source", "")
        if not img_url:
            return None
        
        # Download image
        img_r = requests.get(img_url, headers=HEADERS, timeout=20)
        if img_r.status_code == 200:
            # Determine extension
            content_type = img_r.headers.get("content-type", "")
            if "png" in content_type or img_url.lower().endswith(".png"):
                dest = IMAGES_DIR / f"{filename}.png"
            else:
                dest = IMAGES_DIR / f"{filename}.jpg"
            
            with open(dest, 'wb') as f:
                f.write(img_r.content)
            print(f"  [OK] {filename} saved ({dest.stat().st_size//1024}KB) from {img_url[:60]}")
            return str(dest)
        else:
            print(f"  [ERR] Image download failed: {img_r.status_code}")
            return None
            
    except Exception as e:
        print(f"  [ERR] {filename}: {e}")
        return None

success = 0
failed = []

# queenstown already done
print("[SKIP] queenstown already exists")
success += 1

for filename, wiki_title in CONSTITUENCIES:
    print(f"Fetching: {filename} (Wikipedia: {wiki_title})")
    result = get_wikipedia_image(wiki_title, filename)
    if result:
        success += 1
    else:
        failed.append((filename, wiki_title))
    time.sleep(0.3)  # Be polite to Wikipedia API

print(f"\n成功: {success}/{len(CONSTITUENCIES)+1}")
if failed:
    print(f"失败 ({len(failed)}):")
    for f, w in failed:
        print(f"  {f}: {w}")

# List all images
print("\n已下载图片:")
for img in sorted(IMAGES_DIR.iterdir()):
    print(f"  {img.name} ({img.stat().st_size//1024}KB)")
