#!/usr/bin/env python3
"""
新加坡分区历史 - LaTeX 生成脚本 v3
修复：
1. 首段首行缩进2字符（中文排版规范）
2. 参考资料改为 [1][2] 编号格式，无缩进，小段间距
3. 书名改为「新加坡分区历史」
4. 参考资料链接保持黑色
5. 有图片的选区插入图片
6. 补写空白节（urbanization）
7. 修正汉字错误（后港、四美）
"""
import json
import re
import os
from pathlib import Path

# ── 读取数据 ──────────────────────────────────────────────────────────────────
with open('/home/ubuntu/research_constituencies.json', 'r', encoding='utf-8') as f:
    orig_data = json.load(f)
with open('/home/ubuntu/fix_constituencies.json', 'r', encoding='utf-8') as f:
    fix_data = json.load(f)
with open('/home/ubuntu/fix_empty_sections.json', 'r', encoding='utf-8') as f:
    empty_fix_data = json.load(f)

orig_results = orig_data.get('results', [])
fix_results  = fix_data.get('results', [])
empty_fix_results = empty_fix_data.get('results', [])

# ── 已有图片映射 ──────────────────────────────────────────────────────────────
IMAGES_DIR = Path('/home/ubuntu/singapore_book/images')
AVAILABLE_IMAGES = {p.stem: str(p) for p in IMAGES_DIR.glob('*') if p.suffix in ('.jpg','.png','.jpeg')}

# 选区英文关键词 → 图片文件名（stem）
IMAGE_MAP = {
    "Queenstown":     "queenstown",
    "Tanjong Pagar":  "tanjong_pagar",
    "Jalan Besar":    "jalan_besar",
    "Bishan":         "bishan_toa_payoh",
    "Marymount":      "marymount",
    "Potong Pasir":   "potong_pasir",
    "Radin Mas":      "radin_mas",
    "Kebun Baru":     "kebun_baru",
    "East Coast":     "east_coast",
    "Marine Parade":  "marine_parade",
    "Aljunied":       "aljunied",
    "Mountbatten":    "mountbatten",
    "Pasir Ris":      "pasir_ris_changi",
    "Tampines GRC":   "tampines",
    "Tampines Changkat": "tampines_changkat",
    "Sembawang GRC":  "sembawang",
    "Sembawang West": "sembawang_west",
    "Nee Soon":       "nee_soon",
}

# 图片说明文字（中文）
IMAGE_CAPTIONS = {
    "queenstown":        "女皇镇组屋区全景，新加坡首个卫星新镇",
    "tanjong_pagar":     "丹戎巴葛一带的历史街区与现代天际线",
    "jalan_besar":       "惹兰勿刹一带的传统店屋建筑群",
    "bishan_toa_payoh":  "碧山-大巴窑新镇的组屋景观",
    "marymount":         "玛丽蒙一带的绿化住宅环境",
    "potong_pasir":      "波东巴西组屋区街景",
    "radin_mas":         "拉丁马士一带的住宅区景观",
    "kebun_baru":        "哥本峇鲁一带的绿化社区环境",
    "east_coast":        "东海岸公园海滨景观",
    "marine_parade":     "马林百列一带的海滨住宅区",
    "aljunied":          "阿裕尼一带的组屋与商业区",
    "mountbatten":       "蒙巴登一带的历史建筑与现代发展",
    "pasir_ris_changi":  "白沙海滩与樟宜一带的自然景观",
    "tampines":          "淡滨尼新镇的组屋区全景",
    "tampines_changkat": "淡滨尼尚育一带的住宅区景观",
    "sembawang":         "三巴旺一带的海滨与住宅区",
    "sembawang_west":    "三巴旺西一带的组屋社区",
    "nee_soon":          "义顺新镇的组屋与绿化环境",
}

# ── 选区分区结构 ──────────────────────────────────────────────────────────────
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

grc_map = {
    "Aljunied":       "阿裕尼集选区 (Aljunied GRC)",
    "Ang Mo Kio":     "宏茂桥集选区 (Ang Mo Kio GRC)",
    "Bishan":         "碧山-大巴窑集选区 (Bishan-Toa Payoh GRC)",
    "Chua Chu Kang":  "蔡厝港集选区 (Chua Chu Kang GRC)",
    "East Coast":     "东海岸集选区 (East Coast GRC)",
    "Holland":        "荷兰-武吉知马集选区 (Holland-Bukit Timah GRC)",
    "Jalan Besar":    "惹兰勿刹集选区 (Jalan Besar GRC)",
    "Jurong East":    "裕廊东-武吉巴督集选区 (Jurong East-Bukit Batok GRC)",
    "Marine Parade":  "马林百列-勿拉德高地集选区 (Marine Parade-Braddell Heights GRC)",
    "Marsiling":      "马西岭-油池集选区 (Marsiling-Yew Tee GRC)",
    "Nee Soon":       "义顺集选区 (Nee Soon GRC)",
    "Pasir Ris":      "白沙-樟宜集选区 (Pasir Ris-Changi GRC)",
    "Punggol":        "榜鹅集选区 (Punggol GRC)",
    "Sembawang GRC":  "三巴旺集选区 (Sembawang GRC)",
    "Sengkang":       "盛港集选区 (Sengkang GRC)",
    "Tampines GRC":   "淡滨尼集选区 (Tampines GRC)",
    "Tanjong Pagar":  "丹戎巴葛集选区 (Tanjong Pagar GRC)",
    "West Coast":     "西海岸-裕廊西集选区 (West Coast-Jurong West GRC)"
}

smc_map = {
    "Bukit Gombak":       "武吉甘柏单选区 (Bukit Gombak SMC)",
    "Bukit Panjang":      "武吉班让单选区 (Bukit Panjang SMC)",
    "Hougang":            "后港单选区 (Hougang SMC)",
    "Jalan Kayu":         "惹兰加由单选区 (Jalan Kayu SMC)",
    "Jurong Central":     "裕廊中单选区 (Jurong Central SMC)",
    "Kebun Baru":         "哥本峇鲁单选区 (Kebun Baru SMC)",
    "Marymount":          "玛丽蒙单选区 (Marymount SMC)",
    "Mountbatten":        "蒙巴登单选区 (Mountbatten SMC)",
    "Pioneer":            "先驱单选区 (Pioneer SMC)",
    "Potong Pasir":       "波东巴西单选区 (Potong Pasir SMC)",
    "Queenstown":         "女皇镇单选区 (Queenstown SMC)",
    "Radin Mas":          "拉丁马士单选区 (Radin Mas SMC)",
    "Sembawang West":     "三巴旺西单选区 (Sembawang West SMC)",
    "Tampines Changkat":  "淡滨尼尚育单选区 (Tampines Changkat SMC)",
    "Yio Chu Kang":       "杨厝港单选区 (Yio Chu Kang SMC)"
}

std_names = {**grc_map, **smc_map}

# ── 数据查找 ──────────────────────────────────────────────────────────────────
def find_data(eng_name):
    key = eng_name.lower().split('grc')[0].split('smc')[0].strip()
    for item in fix_results:
        out = item.get('output', {})
        if not out: continue
        if key in out.get('constituency_name','').lower() or key in item.get('input','').lower():
            return out
    for item in orig_results:
        out = item.get('output', {})
        if not out: continue
        if key in out.get('constituency_name','').lower() or key in item.get('input','').lower():
            return out
    return None

def find_empty_fix(eng_name):
    key = eng_name.lower().split('grc')[0].split('smc')[0].strip()
    for item in empty_fix_results:
        out = item.get('output', {})
        if not out: continue
        if key in out.get('constituency_name','').lower() or key in item.get('input','').lower():
            return out.get('urbanization','')
    return ''

# ── 文本清理 ──────────────────────────────────────────────────────────────────
def clean_text(text):
    """清理Markdown残留并转义LaTeX特殊字符"""
    if not text:
        return ""
    # 去除Markdown格式
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*',     r'\1', text)
    text = re.sub(r'^#{1,6}\s+(.*)$', r'\1', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # 修正已知汉字错误
    text = text.replace('欧港', '后港')
    text = text.replace('Simei', '四美').replace('西美', '四美')
    # LaTeX 转义（先处理反斜杠）
    text = text.replace('\\', '\\textbackslash{}')
    text = text.replace('&',  '\\&')
    text = text.replace('%',  '\\%')
    text = text.replace('$',  '\\$')
    text = text.replace('#',  '\\#')
    text = text.replace('_',  '\\_')
    text = text.replace('{',  '\\{')
    text = text.replace('}',  '\\}')
    text = text.replace('~',  '\\textasciitilde{}')
    text = text.replace('^',  '\\textasciicircum{}')
    return text

def format_paragraphs(text):
    """将文本格式化为LaTeX段落，首段有首行缩进"""
    if not text:
        return ""
    paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    return '\n\n'.join(paras)

def format_references(refs_text):
    """将参考资料格式化为带编号的列表，URL直接用url命令（颜色由hypersetup统一设为black）"""
    if not refs_text:
        return ""
    lines = [l.strip() for l in refs_text.split('\n') if l.strip()]
    # 去除开头的 - 或 * 或数字编号
    cleaned = []
    for line in lines:
        line = re.sub(r'^[-*•]\s*', '', line)
        line = re.sub(r'^\d+\.\s*', '', line)
        if line:
            cleaned.append(line)
    
    if not cleaned:
        return ""
    
    result = "\\begin{enumerate}[label={[\\arabic*]},leftmargin=*,topsep=2pt,itemsep=1pt,parsep=0pt]\n"
    for ref in cleaned:
        # 提取URL并用\url{}包裹（不加\textcolor，颜色由hypersetup统一控制）
        url_match = re.search(r'(https?://[^\s\)\]，。]+)', ref)
        if url_match:
            raw_url = url_match.group(1).rstrip('.,;)')
            before = ref[:url_match.start()]
            after  = ref[url_match.start()+len(raw_url):]
            before_clean = clean_text(before)
            after_clean  = clean_text(after)
            ref_line = f"{before_clean}\\url{{{raw_url}}}{after_clean}"
        else:
            ref_line = clean_text(ref)
        result += f"  \\item {ref_line}\n"
    result += "\\end{enumerate}\n"
    return result

# ── LaTeX 文档头 ──────────────────────────────────────────────────────────────
latex_header = r"""\documentclass[11pt,a4paper,oneside,openany]{book}

% ── 宏包 ──────────────────────────────────────────────────────────────────────
\usepackage{xeCJK}
\usepackage{geometry}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{tocloft}
\usepackage{xurl}
\usepackage{hyperref}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{caption}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{indentfirst}   % 首段首行缩进

% ── 页面设置 ──────────────────────────────────────────────────────────────────
\geometry{left=2.5cm,right=2.5cm,top=3cm,bottom=3cm,headheight=14pt}

% ── 字体设置 ──────────────────────────────────────────────────────────────────
\setCJKmainfont[BoldFont=Noto Serif CJK SC]{Noto Serif CJK SC}
\setCJKsansfont{Noto Sans CJK SC}
\setmainfont{TeX Gyre Termes}

% ── 中文首行缩进2字符 ─────────────────────────────────────────────────────────
\setlength{\parindent}{2em}
\setlength{\parskip}{0.3em}

% ── 颜色 ──────────────────────────────────────────────────────────────────────
\definecolor{primary}{RGB}{90,90,90}
\definecolor{darkgray}{RGB}{40,40,40}

% ── 超链接设置（所有链接黑色，参考资料URL不着色） ──────────────────────────
\hypersetup{
    colorlinks=true,
    linkcolor=darkgray,
    filecolor=darkgray,
    urlcolor=black,
    pdftitle={新加坡分区历史},
    pdfauthor={Manus AI},
    pdfsubject={新加坡33个选区的历史与城市发展},
}

% ── 标题格式 ──────────────────────────────────────────────────────────────────
\titleformat{\part}[display]
  {\normalfont\huge\bfseries\centering\color{darkgray}}
  {}{0pt}{\Huge}
\titleformat{\chapter}[display]
  {\normalfont\Large\bfseries\color{darkgray}}
  {}{0pt}{\LARGE}
\titleformat{\section}
  {\normalfont\large\bfseries}{\thesection}{1em}{}
% 去掉章之间的空白页
\renewcommand{\cleardoublepage}{\clearpage}

% ── 图片设置 ──────────────────────────────────────────────────────────────────
\graphicspath{{/home/ubuntu/singapore_book/images/}}
\captionsetup{font=small,labelfont=bf,skip=4pt}

% ── 页眉页脚（仅显示页码，不显示章节标题） ────────────────────────────────────
\pagestyle{fancy}
\fancyhf{}
\fancyhead[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\fancypagestyle{plain}{\fancyhf{}\fancyhead[C]{\thepage}\renewcommand{\headrulewidth}{0.4pt}}

\begin{document}

% ── 封面 ──────────────────────────────────────────────────────────────────────
\begin{titlepage}
    \centering
    \vspace*{4cm}
    {\Huge \bfseries \textcolor{darkgray}{新加坡分区历史} \par}
    \vspace{1.5cm}
    {\LARGE \bfseries 基于2025年最新选区划分 \par}
    \vspace{2cm}
    \vspace{4cm}
    {\Large \bfseries Manus AI 编著 \par}
    \vfill
    {\large 2026年6月 \par}
\end{titlepage}

\frontmatter

\chapter*{前言}
\addcontentsline{toc}{chapter}{前言}

本书以2025年新加坡选区范围检讨委员会（Electoral Boundaries Review Committee，EBRC）发布的最新选区划分为框架，系统梳理新加坡33个选区（18个集选区与15个单选区）的历史沿革与城市发展脉络。

选区作为新加坡政治地理的基本单元，其边界的历次调整折射出城市扩张、人口迁移与政策导向的深层逻辑。从早期甘榜（Kampong）的农业聚落，到新加坡改良信托局（Singapore Improvement Trust，SIT）时期的初步城市化，再到建屋发展局（Housing and Development Board，HDB）主导的大规模新镇建设，每一个选区都是新加坡社会变迁、族群融合与规划理念演进的实体缩影。

本书综合运用英文、中文、马来文等多语种历史档案与学术文献，采用城市社会学与历史地理学的专业视角，力求以高密度的史料与多维度的分析，为读者呈现一幅完整的狮城街区变迁全景图。各章末尾附有参考资料，以便读者深入查阅原始文献。

\clearpage

\renewcommand{\contentsname}{目录}
\tableofcontents

\mainmatter
"""

# ── 生成正文 ──────────────────────────────────────────────────────────────────
body = ""
chapter_count = 0

for part_name, constituencies in sections.items():
    body += f"\n\\part{{{part_name}}}\n\n"

    for eng_name in constituencies:
        data = find_data(eng_name)
        if not data:
            print(f"[WARN] Data not found for {eng_name}")
            continue

        chapter_count += 1
        std_name = std_names.get(eng_name, data.get('constituency_name', eng_name))

        # 获取各节内容
        political_history  = format_paragraphs(clean_text(data.get('political_history', '')))

        early_history = format_paragraphs(clean_text(data.get('early_history', '')))
        urbanization_raw   = data.get('urbanization', '')
        # 若空，使用补写数据
        if not urbanization_raw or len(urbanization_raw.strip()) < 30:
            urbanization_raw = find_empty_fix(eng_name)
        urbanization       = format_paragraphs(clean_text(urbanization_raw))
        landmarks          = format_paragraphs(clean_text(data.get('landmarks', '')))
        demographics       = format_paragraphs(clean_text(data.get('demographics', '')))
        recent_development = format_paragraphs(clean_text(data.get('recent_development', '')))
        community_memory   = format_paragraphs(clean_text(data.get('community_memory', '')))
        references_raw     = data.get('references', '')

        # 图片处理
        img_stem = IMAGE_MAP.get(eng_name)
        img_block = ""
        if img_stem and img_stem in AVAILABLE_IMAGES:
            img_path = AVAILABLE_IMAGES[img_stem]
            caption  = IMAGE_CAPTIONS.get(img_stem, std_name)
            # 使用相对路径（已设置graphicspath）
            img_filename = Path(img_path).name
            img_block = f"""
\\begin{{figure}}[h]
  \\centering
  \\includegraphics[width=0.85\\textwidth,height=0.35\\textheight,keepaspectratio]{{{img_filename}}}
  \\caption{{{caption}}}
\\end{{figure}}

"""

        # 章节内容
        body += f"\\chapter{{{std_name}}}\n\n"
        body += img_block

        body += "\\section{选区划界与政治地理背景}\n"
        body += f"{political_history}\n\n" if political_history else "相关资料待补充。\n\n"

        body += "\\section{早期地貌与前城市化时期}\n"
        body += f"{early_history}\n\n" if early_history else "相关资料待补充。\n\n"

        body += "\\section{城市规划与建设进程}\n"
        body += f"{urbanization}\n\n" if urbanization else "相关资料待补充。\n\n"

        body += "\\section{重要地标与建筑}\n"
        body += f"{landmarks}\n\n" if landmarks else "相关资料待补充。\n\n"

        body += "\\section{人口变迁与族群结构}\n"
        body += f"{demographics}\n\n" if demographics else "相关资料待补充。\n\n"

        body += "\\section{近年发展与城市更新}\n"
        body += f"{recent_development}\n\n" if recent_development else "相关资料待补充。\n\n"

        body += "\\section{社区记忆与空间认同}\n"
        body += f"{community_memory}\n\n" if community_memory else "相关资料待补充。\n\n"

        # 参考资料
        refs_formatted = format_references(references_raw)
        if refs_formatted:
            body += "\\section*{参考资料}\n"
            body += "\\addcontentsline{toc}{section}{参考资料}\n"
            body += refs_formatted + "\n"

latex_footer = "\n\\end{document}\n"

# ── 写入文件 ──────────────────────────────────────────────────────────────────
output_path = '/home/ubuntu/singapore_book/book_v3.tex'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(latex_header)
    f.write(body)
    f.write(latex_footer)

print(f"book_v3.tex 生成完成，共 {chapter_count} 章")
print(f"文件大小: {os.path.getsize(output_path)//1024} KB")
