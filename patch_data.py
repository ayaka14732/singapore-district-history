"""直接修改原始JSON数据中的错误内容"""
import json

# ── 修复 research_constituencies.json（原始数据）──────────────────────────────
with open('/home/ubuntu/research_constituencies.json', 'r', encoding='utf-8') as f:
    orig = json.load(f)

for item in orig.get('results', []):
    out = item.get('output', {})
    name = out.get('constituency_name', '')
    if 'yio' in name.lower():
        eh = out.get('early_history', '')
        # 修正：「厝港」意为「背水港／内港聚落」，与地名「后港」（Hougang）无关
        eh = eh.replace(
            '"厝港"（chu kang），这是一个潮州词，意为"后港"',
            '"厝港"（chu kang），潮州词，指河流偏远支流处用于转运农产品的内港聚落，与地名"后港"（Hougang）并无关联'
        )
        # 修正「杨厝港，又称杨厝港」的重复表述
        eh = eh.replace('杨厝港，又称杨厝港，', '杨厝港（Yio Chu Kang），')
        out['early_history'] = eh
        print(f"[OK] 已修正 research_constituencies.json 中的杨厝港 early_history")
        break

with open('/home/ubuntu/research_constituencies.json', 'w', encoding='utf-8') as f:
    json.dump(orig, f, ensure_ascii=False, indent=2)

# ── 修复 fix_constituencies.json（覆盖错误的fix数据）─────────────────────────
with open('/home/ubuntu/fix_constituencies.json', 'r', encoding='utf-8') as f:
    fix = json.load(f)

for item in fix.get('results', []):
    out = item.get('output', {})
    name = out.get('constituency_name', '')
    if 'yio' in name.lower():
        # 直接替换为正确内容
        out['early_history'] = (
            '杨厝港（Yio Chu Kang），位于新加坡东北部，其名称由两部分构成：'
            '"杨"（Yio）为姓氏，指该地区早期的土地拥有者或宗族；'
            '"厝港"（Chu Kang，潮州话：cu3 gang2）则指河流偏远支流处用于转运农产品的内港聚落，'
            '与地名"后港"（Hougang）并无关联。'
            '类似的命名方式亦见于蔡厝港（Chua Chu Kang）和林厝港（Lim Chu Kang），'
            '均以宗族姓氏冠于"厝港"之前。这些"厝港"聚落在19世纪新加坡的康头（Kangchu）经济体系下兴起，'
            '作为附近种植园所产甘蜜（gambier）与胡椒的集散港口。'
            '历史记录显示，至1855年5月，杨厝港已是一个拥有161名苦力的定居点。'
            '殖民时期，该地区以种植园与甘榜（kampong）为主要地貌，'
            '甘蜜种植者中超过90%为潮州籍华人，采用“刀耕火种”与游耕方式，导致大面积森林牀伐。'
            '19世纪90年代甘蜜产业衰退后，橡胶种植逐渐取而代之。'
        )
        print(f"[OK] 已修正 fix_constituencies.json 中的杨厝港 early_history")
        break

with open('/home/ubuntu/fix_constituencies.json', 'w', encoding='utf-8') as f:
    json.dump(fix, f, ensure_ascii=False, indent=2)

print("数据修复完成。")
