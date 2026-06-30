"""修正所有JSON数据中的地名错误"""
import json

REPLACEMENTS = [
    # 勿地申 → 勿洛
    ('勿地申', '勿洛'),
    # 实美 → 四美（但保留「樟宜-实美」→「樟宜-四美」的同时，避免误改其他含「实」字的词）
    ('樟宜-实美', '樟宜-四美'),
    ('樟宜－实美', '樟宜-四美'),
    ('Changi–实美', '樟宜-四美'),
    ('Changi-实美', '樟宜-四美'),
    # 甘榜蔡厝 → 甘榜菜市
    ('甘榜蔡厝', '甘榜菜市'),
    # 如吉 → 如切
    ('如吉', '如切'),
    # 顺带修正：「实美」单独出现时也改为「四美」（已在clean_text中处理Simei→四美，但原始数据中可能有「实美」）
    # 注意：不能全局替换「实」，只替换「实美」
    ('实美', '四美'),
]

files = [
    '/home/ubuntu/research_constituencies.json',
    '/home/ubuntu/fix_constituencies.json',
    '/home/ubuntu/fix_empty_sections.json',
]

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        original = content
        for old, new in REPLACEMENTS:
            content = content.replace(old, new)
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            # 统计替换次数
            count = sum(original.count(old) for old, _ in REPLACEMENTS)
            print(f'[OK] {filepath}: 已替换 {count} 处')
        else:
            print(f'[--] {filepath}: 无需修改')
    except FileNotFoundError:
        print(f'[SKIP] {filepath}: 文件不存在')

print('地名修正完成。')
