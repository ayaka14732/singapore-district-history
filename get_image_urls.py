#!/usr/bin/env python3
"""获取缺失图片的直接下载URL"""
import requests
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
}

MISSING = [
    ("marsiling_yew_tee", "Marsiling Singapore"),
    ("yio_chu_kang", "Yio Chu Kang Singapore"),
    ("jalan_kayu", "Jalan Kayu Singapore"),
    ("ang_mo_kio", "Ang Mo Kio Singapore"),
    ("sengkang", "Sengkang Singapore"),
    ("punggol", "Punggol Singapore"),
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

print("缺失图片的下载URL：\n")

for filename, query in MISSING:
    try:
        api_url = "https://api.openverse.org/v1/images/"
        params = {
            "q": query,
            "license_type": "commercial,modification",
            "page_size": 3,
            "format": "json"
        }
        r = requests.get(api_url, params=params, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            if results:
                img_url = results[0].get("url", "")
                title = results[0].get("title", "")
                creator = results[0].get("creator", "")
                print(f"### {filename}.jpg")
                print(f"URL: {img_url}")
                print(f"标题: {title}")
                print(f"作者: {creator}")
                print()
            else:
                print(f"### {filename}.jpg")
                print(f"URL: (无结果)")
                print()
        else:
            print(f"### {filename}.jpg")
            print(f"URL: (API错误 {r.status_code})")
            print()
    except Exception as e:
        print(f"### {filename}.jpg")
        print(f"URL: (异常: {e})")
        print()
    time.sleep(1)
