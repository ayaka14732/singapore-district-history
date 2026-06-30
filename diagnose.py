import json
import re

with open('/home/ubuntu/research_constituencies.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

results = data.get('results', [])

FIELDS = ['early_history', 'urbanization', 'landmarks', 'demographics',
          'political_history', 'recent_development', 'community_memory']

def is_mostly_english(text):
    if not text or len(text) < 50:
        return True  # 太短也算问题
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(re.sub(r'\s', '', text))
    if total_chars == 0:
        return True
    return chinese_chars / total_chars < 0.15  # 中文字符少于15%视为英文

def has_markdown(text):
    if not text:
        return False
    patterns = [r'\*\*', r'\*[^*]', r'^#{1,6}\s', r'^\s*[-*+]\s', r'^\s*\d+\.\s']
    for p in patterns:
        if re.search(p, text, re.MULTILINE):
            return True
    return False

def is_empty(text):
    return not text or len(text.strip()) < 30

issues = {}

for item in results:
    output = item.get('output', {})
    if not output:
        continue
    name = output.get('constituency_name', item.get('input', 'Unknown'))
    item_issues = []
    
    for field in FIELDS:
        val = output.get(field, '')
        if is_empty(val):
            item_issues.append(f'EMPTY: {field}')
        elif is_mostly_english(val):
            item_issues.append(f'ENGLISH: {field}')
        elif has_markdown(val):
            item_issues.append(f'MARKDOWN: {field}')
    
    if item_issues:
        issues[name] = item_issues

print(f"=== 问题诊断报告 ===")
print(f"总选区数: {len(results)}")
print(f"有问题的选区数: {len(issues)}")
print()
for name, probs in issues.items():
    print(f"[{name}]")
    for p in probs:
        print(f"  - {p}")
    print()
