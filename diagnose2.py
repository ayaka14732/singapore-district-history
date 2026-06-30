import json
import re

# 读取原始数据和修复后的数据
with open('/home/ubuntu/research_constituencies.json', 'r', encoding='utf-8') as f:
    orig_data = json.load(f)

with open('/home/ubuntu/fix_constituencies.json', 'r', encoding='utf-8') as f:
    fix_data = json.load(f)

orig_results = orig_data.get('results', [])
fix_results = fix_data.get('results', [])

# 标准选区列表（与生成脚本一致）
sections = {
    "第一篇：中部与中南部": [
        "Queenstown", "Tanjong Pagar", "Jalan Besar", 
        "Bishan", "Marymount", "Potong Pasir", 
        "Radin Mas", "Kebun Baru"
    ],
    "第二篇：东部": [
        "East Coast", "Marine Parade", "Aljunied", 
        "Mountbatten", "Pasir Ris", "Tampines GRC", "Tampines Changkat"
    ],
    "第三篇：北部": [
        "Sembawang GRC", "Sembawang West", "Nee Soon", 
        "Marsiling", "Yio Chu Kang", "Jalan Kayu"
    ],
    "第四篇：东北部": [
        "Ang Mo Kio", "Sengkang", "Punggol", "Hougang"
    ],
    "第五篇：西部": [
        "Holland", "Jurong East", "West Coast", 
        "Chua Chu Kang", "Bukit Gombak", "Bukit Panjang", 
        "Jurong Central", "Pioneer"
    ]
}

FIELDS = ['early_history', 'urbanization', 'landmarks', 'demographics',
          'political_history', 'recent_development', 'community_memory']

def is_mostly_english(text):
    if not text or len(text) < 30:
        return True
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(re.sub(r'\s', '', text))
    if total_chars == 0:
        return True
    return chinese_chars / total_chars < 0.15

def has_markdown(text):
    if not text:
        return False
    patterns = [r'\*\*', r'^\s*[-*+]\s', r'^\s*\d+\.\s']
    for p in patterns:
        if re.search(p, text, re.MULTILINE):
            return True
    return False

def is_empty(text):
    return not text or len(text.strip()) < 30

def find_data(eng_name):
    eng_name_clean = eng_name.lower().split('grc')[0].split('smc')[0].strip()
    for item in fix_results:
        output = item.get('output', {})
        if not output: continue
        if eng_name_clean in output.get('constituency_name', '').lower() or eng_name_clean in item.get('input', '').lower():
            return output
    for item in orig_results:
        output = item.get('output', {})
        if not output: continue
        if eng_name_clean in output.get('constituency_name', '').lower() or eng_name_clean in item.get('input', '').lower():
            return output
    return None

print("=== 空章节诊断报告 ===\n")
all_constituencies = []
for part, names in sections.items():
    for name in names:
        all_constituencies.append((part, name))

empty_chapters = []
for part, eng_name in all_constituencies:
    data = find_data(eng_name)
    if not data:
        print(f"[NOT FOUND] {eng_name}")
        empty_chapters.append(eng_name)
        continue
    
    issues = []
    for field in FIELDS:
        val = data.get(field, '')
        if is_empty(val):
            issues.append(f'EMPTY: {field}')
        elif is_mostly_english(val):
            issues.append(f'ENGLISH: {field}')
        elif has_markdown(val):
            issues.append(f'MARKDOWN: {field}')
    
    if issues:
        print(f"[{eng_name}]")
        for i in issues:
            print(f"  - {i}")
        print()

print(f"\n总选区数: {len(all_constituencies)}")
print(f"有问题的选区: {len([x for x in all_constituencies if find_data(x[1]) is None])}")
