#!/usr/bin/env python3
"""
使用 OpenAI 图像搜索 API 为33个选区搜集代表性图片
通过 requests 调用 Bing Image Search 或其他可用的图片源
"""
import os
import requests
import shutil
from pathlib import Path
import time
import urllib.parse

IMAGES_DIR = Path('/home/ubuntu/singapore_book/images')
IMAGES_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# 每个选区对应的搜索词和文件名
CONSTITUENCIES = [
    ("tanjong_pagar", "Tanjong Pagar Singapore skyline"),
    ("jalan_besar", "Jalan Besar Singapore"),
    ("bishan_toa_payoh", "Bishan Singapore town"),
    ("marymount", "Marymount Singapore"),
    ("potong_pasir", "Potong Pasir Singapore"),
    ("radin_mas", "Radin Mas Singapore"),
    ("kebun_baru", "Kebun Baru Singapore"),
    ("east_coast", "East Coast Park Singapore"),
    ("marine_parade", "Marine Parade Singapore"),
    ("aljunied", "Aljunied Singapore"),
    ("mountbatten", "Mountbatten Singapore"),
    ("pasir_ris_changi", "Pasir Ris Singapore"),
    ("tampines", "Tampines Singapore HDB"),
    ("tampines_changkat", "Tampines Singapore"),
    ("sembawang", "Sembawang Singapore"),
    ("sembawang_west", "Sembawang Singapore"),
    ("nee_soon", "Nee Soon Singapore"),
    ("marsiling_yew_tee", "Marsiling Singapore"),
    ("yio_chu_kang", "Yio Chu Kang Singapore"),
    ("jalan_kayu", "Jalan Kayu Singapore"),
    ("ang_mo_kio", "Ang Mo Kio Singapore"),
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

def try_download_image(url, dest_path):
    """尝试下载图片到指定路径"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, stream=True)
        if r.status_code == 200:
            content_type = r.headers.get("content-type", "")
            if any(x in content_type for x in ["image/jpeg", "image/png", "image/webp", "image/gif"]):
                with open(dest_path, 'wb') as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
                size = os.path.getsize(dest_path)
                if size > 10000:  # At least 10KB
                    return True
                else:
                    os.remove(dest_path)
                    return False
    except Exception as e:
        pass
    return False

def get_image_via_openverse(query, filename):
    """使用 Openverse API 搜索 CC 授权图片"""
    dest_jpg = IMAGES_DIR / f"{filename}.jpg"
    dest_png = IMAGES_DIR / f"{filename}.png"
    
    if (dest_jpg.exists() and dest_jpg.stat().st_size > 10000) or \
       (dest_png.exists() and dest_png.stat().st_size > 10000):
        print(f"  [SKIP] {filename} already exists")
        return True
    
    try:
        # Openverse API (formerly CC Search)
        api_url = "https://api.openverse.org/v1/images/"
        params = {
            "q": query,
            "license_type": "commercial,modification",
            "page_size": 5,
            "format": "json"
        }
        r = requests.get(api_url, params=params, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            for result in results:
                img_url = result.get("url", "")
                if img_url:
                    dest = dest_jpg if not img_url.lower().endswith(".png") else dest_png
                    if try_download_image(img_url, dest):
                        print(f"  [OK] {filename} from Openverse ({os.path.getsize(dest)//1024}KB)")
                        return True
    except Exception as e:
        print(f"  [ERR Openverse] {filename}: {e}")
    
    return False

def get_image_via_unsplash(query, filename):
    """使用 Unsplash Source API 获取图片"""
    dest = IMAGES_DIR / f"{filename}.jpg"
    if dest.exists() and dest.stat().st_size > 10000:
        return True
    
    try:
        # Unsplash Source (random image by keyword)
        encoded_query = urllib.parse.quote(query)
        url = f"https://source.unsplash.com/800x600/?{encoded_query}"
        r = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 10000:
            with open(dest, 'wb') as f:
                f.write(r.content)
            print(f"  [OK] {filename} from Unsplash ({os.path.getsize(dest)//1024}KB)")
            return True
    except Exception as e:
        print(f"  [ERR Unsplash] {filename}: {e}")
    
    return False

def get_image_via_wikimedia_commons(query, filename):
    """使用 Wikimedia Commons 搜索 API"""
    dest_jpg = IMAGES_DIR / f"{filename}.jpg"
    dest_png = IMAGES_DIR / f"{filename}.png"
    
    if (dest_jpg.exists() and dest_jpg.stat().st_size > 10000) or \
       (dest_png.exists() and dest_png.stat().st_size > 10000):
        return True
    
    try:
        # Search Wikimedia Commons
        search_url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": f"{query} filetype:jpg OR filetype:png",
            "srnamespace": "6",
            "srlimit": "10",
            "format": "json"
        }
        r = requests.get(search_url, params=params, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return False
        
        data = r.json()
        results = data.get("query", {}).get("search", [])
        
        for result in results[:5]:
            title = result["title"]
            # Get image info
            info_url = "https://commons.wikimedia.org/w/api.php"
            info_params = {
                "action": "query",
                "titles": title,
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "iiurlwidth": "800",
                "format": "json"
            }
            r2 = requests.get(info_url, params=info_params, headers=HEADERS, timeout=10)
            if r2.status_code != 200:
                continue
            
            data2 = r2.json()
            pages = data2.get("query", {}).get("pages", {})
            
            for page_id, page in pages.items():
                imageinfo = page.get("imageinfo", [])
                if not imageinfo:
                    continue
                
                info = imageinfo[0]
                mime = info.get("mime", "")
                if not any(x in mime for x in ["jpeg", "png", "jpg"]):
                    continue
                
                img_url = info.get("thumburl") or info.get("url")
                if not img_url:
                    continue
                
                is_png = "png" in mime or img_url.lower().endswith(".png")
                dest = dest_png if is_png else dest_jpg
                
                if try_download_image(img_url, dest):
                    print(f"  [OK] {filename} from Wikimedia ({os.path.getsize(dest)//1024}KB)")
                    return True
    except Exception as e:
        print(f"  [ERR Wikimedia] {filename}: {e}")
    
    return False

# Main loop
print(f"开始下载图片到 {IMAGES_DIR}")
print(f"已有图片: queenstown.jpg")
print()

success = 1  # queenstown already done
failed = []

for filename, query in CONSTITUENCIES:
    print(f"Fetching: {filename}")
    
    # Try multiple sources
    result = get_image_via_wikimedia_commons(query, filename)
    if not result:
        result = get_image_via_openverse(query, filename)
    if not result:
        result = get_image_via_unsplash(query, filename)
    
    if result:
        success += 1
    else:
        failed.append(filename)
        print(f"  [FAILED] {filename}")
    
    time.sleep(0.5)

print(f"\n成功: {success}/{len(CONSTITUENCIES)+1}")
if failed:
    print(f"失败 ({len(failed)}): {failed}")

print("\n已下载图片:")
for img in sorted(IMAGES_DIR.iterdir()):
    print(f"  {img.name} ({img.stat().st_size//1024}KB)")
