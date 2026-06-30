#!/usr/bin/env python3
"""
批量为33个选区搜集代表性图片
使用 requests 从 Wikimedia Commons 或其他公开图片源下载
"""
import os
import json
import requests
import shutil
from pathlib import Path

IMAGES_DIR = Path('/home/ubuntu/singapore_book/images')
IMAGES_DIR.mkdir(exist_ok=True)

# 每个选区对应的搜索词和文件名
CONSTITUENCIES = [
    ("queenstown", "Queenstown Singapore HDB"),
    ("tanjong_pagar", "Tanjong Pagar Singapore"),
    ("jalan_besar", "Jalan Besar Singapore"),
    ("bishan_toa_payoh", "Bishan Singapore HDB"),
    ("marymount", "Marymount Singapore"),
    ("potong_pasir", "Potong Pasir Singapore"),
    ("radin_mas", "Radin Mas Singapore"),
    ("kebun_baru", "Kebun Baru Singapore"),
    ("east_coast", "East Coast Park Singapore"),
    ("marine_parade", "Marine Parade Singapore"),
    ("aljunied", "Aljunied Singapore"),
    ("mountbatten", "Mountbatten Singapore"),
    ("pasir_ris_changi", "Pasir Ris Singapore beach"),
    ("tampines", "Tampines Singapore HDB"),
    ("tampines_changkat", "Tampines Changkat Singapore"),
    ("sembawang", "Sembawang Singapore"),
    ("sembawang_west", "Sembawang West Singapore"),
    ("nee_soon", "Nee Soon Singapore"),
    ("marsiling_yew_tee", "Marsiling Singapore"),
    ("yio_chu_kang", "Yio Chu Kang Singapore"),
    ("jalan_kayu", "Jalan Kayu Singapore"),
    ("ang_mo_kio", "Ang Mo Kio Singapore HDB"),
    ("sengkang", "Sengkang Singapore"),
    ("punggol", "Punggol Singapore waterway"),
    ("hougang", "Hougang Singapore"),
    ("holland_bukit_timah", "Holland Village Singapore"),
    ("jurong_east_bukit_batok", "Jurong East Singapore"),
    ("west_coast_jurong_west", "Jurong West Singapore"),
    ("chua_chu_kang", "Chua Chu Kang Singapore"),
    ("bukit_gombak", "Bukit Gombak Singapore"),
    ("bukit_panjang", "Bukit Panjang Singapore"),
    ("jurong_central", "Jurong Central Singapore"),
    ("pioneer", "Pioneer Singapore"),
]

# Wikimedia Commons API 搜索图片
def search_wikimedia(query, filename):
    dest = IMAGES_DIR / f"{filename}.jpg"
    if dest.exists():
        print(f"  [SKIP] {filename} already exists")
        return str(dest)
    
    try:
        # 搜索 Wikimedia Commons
        search_url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srnamespace": "6",  # File namespace
            "srlimit": "5",
            "format": "json"
        }
        r = requests.get(search_url, params=params, timeout=10)
        data = r.json()
        results = data.get("query", {}).get("search", [])
        
        if not results:
            print(f"  [WARN] No results for {query}")
            return None
        
        # 获取第一个结果的图片URL
        title = results[0]["title"]
        info_url = "https://commons.wikimedia.org/w/api.php"
        info_params = {
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url|size",
            "iiurlwidth": "800",
            "format": "json"
        }
        r2 = requests.get(info_url, params=info_params, timeout=10)
        data2 = r2.json()
        pages = data2.get("query", {}).get("pages", {})
        
        for page_id, page in pages.items():
            imageinfo = page.get("imageinfo", [])
            if imageinfo:
                img_url = imageinfo[0].get("thumburl") or imageinfo[0].get("url")
                if img_url:
                    img_r = requests.get(img_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
                    if img_r.status_code == 200:
                        with open(dest, 'wb') as f:
                            f.write(img_r.content)
                        print(f"  [OK] {filename} saved ({len(img_r.content)//1024}KB)")
                        return str(dest)
    except Exception as e:
        print(f"  [ERR] {filename}: {e}")
    
    return None

# 检查已有图片
existing = list(IMAGES_DIR.glob("*.jpg")) + list(IMAGES_DIR.glob("*.png"))
print(f"已有图片: {len(existing)} 张")

# 批量下载
success = 0
failed = []
for filename, query in CONSTITUENCIES:
    dest = IMAGES_DIR / f"{filename}.jpg"
    if dest.exists() and dest.stat().st_size > 5000:
        print(f"  [SKIP] {filename} already exists ({dest.stat().st_size//1024}KB)")
        success += 1
        continue
    
    print(f"Fetching: {filename} ({query})")
    result = search_wikimedia(query, filename)
    if result:
        success += 1
    else:
        failed.append(filename)

print(f"\n成功: {success}/{len(CONSTITUENCIES)}")
if failed:
    print(f"失败: {failed}")
