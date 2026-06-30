import json
import re

# 读取原始数据和修复后的数据
with open('/home/ubuntu/research_constituencies.json', 'r', encoding='utf-8') as f:
    orig_data = json.load(f)

with open('/home/ubuntu/fix_constituencies.json', 'r', encoding='utf-8') as f:
    fix_data = json.load(f)

orig_results = orig_data.get('results', [])
fix_results = fix_data.get('results', [])

# 按照分区整理选区
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

# 提取选区标准名称映射
# 18个集选区
grc_map = {
    "Aljunied": "阿裕尼集选区 (Aljunied GRC)",
    "Ang Mo Kio": "宏茂桥集选区 (Ang Mo Kio GRC)",
    "Bishan": "碧山-大巴窑集选区 (Bishan-Toa Payoh GRC)",
    "Chua Chu Kang": "蔡厝港集选区 (Chua Chu Kang GRC)",
    "East Coast": "东海岸集选区 (East Coast GRC)",
    "Holland": "荷兰-武吉知马集选区 (Holland-Bukit Timah GRC)",
    "Jalan Besar": "惹兰勿刹集选区 (Jalan Besar GRC)",
    "Jurong East": "裕廊东-武吉巴督集选区 (Jurong East-Bukit Batok GRC)",
    "Marine Parade": "马林百列-勿拉德高地集选区 (Marine Parade-Braddell Heights GRC)",
    "Marsiling": "马西岭-油池集选区 (Marsiling-Yew Tee GRC)",
    "Nee Soon": "义顺集选区 (Nee Soon GRC)",
    "Pasir Ris": "白沙-樟宜集选区 (Pasir Ris-Changi GRC)",
    "Punggol": "榜鹅集选区 (Punggol GRC)",
    "Sembawang GRC": "三巴旺集选区 (Sembawang GRC)",
    "Sengkang": "盛港集选区 (Sengkang GRC)",
    "Tampines GRC": "淡滨尼集选区 (Tampines GRC)",
    "Tanjong Pagar": "丹戎巴葛集选区 (Tanjong Pagar GRC)",
    "West Coast": "西海岸-裕廊西集选区 (West Coast-Jurong West GRC)"
}

# 15个单选区
smc_map = {
    "Bukit Gombak": "武吉甘柏单选区 (Bukit Gombak SMC)",
    "Bukit Panjang": "武吉班让单选区 (Bukit Panjang SMC)",
    "Hougang": "后港单选区 (Hougang SMC)",
    "Jalan Kayu": "惹兰加由单选区 (Jalan Kayu SMC)",
    "Jurong Central": "裕廊中单选区 (Jurong Central SMC)",
    "Kebun Baru": "锦茂单选区 (Kebun Baru SMC)",
    "Marymount": "玛丽蒙单选区 (Marymount SMC)",
    "Mountbatten": "蒙巴登单选区 (Mountbatten SMC)",
    "Pioneer": "先驱单选区 (Pioneer SMC)",
    "Potong Pasir": "波东巴西单选区 (Potong Pasir SMC)",
    "Queenstown": "女皇镇单选区 (Queenstown SMC)",
    "Radin Mas": "拉丁马士单选区 (Radin Mas SMC)",
    "Sembawang West": "三巴旺西单选区 (Sembawang West SMC)",
    "Tampines Changkat": "淡滨尼尚育单选区 (Tampines Changkat SMC)",
    "Yio Chu Kang": "杨厝港单选区 (Yio Chu Kang SMC)"
}

# 合并所有标准名称
std_names = {**grc_map, **smc_map}

def find_data(eng_name):
    # 优先从修复后的数据中找
    eng_name_clean = eng_name.lower().split('grc')[0].split('smc')[0].strip()
    
    for item in fix_results:
        output = item.get('output', {})
        if not output: continue
        if eng_name_clean in output.get('constituency_name', '').lower() or eng_name_clean in item.get('input', '').lower():
            return output
            
    # 如果没找到，从原始数据中找
    for item in orig_results:
        output = item.get('output', {})
        if not output: continue
        if eng_name_clean in output.get('constituency_name', '').lower() or eng_name_clean in item.get('input', '').lower():
            return output
            
    return None

def clean_markdown_and_format(text):
    if not text:
        return ""
    
    # 清理各种Markdown语法
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # 粗体
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # 斜体
    text = re.sub(r'^#{1,6}\s+(.*)$', r'\1', text, flags=re.MULTILINE)  # 标题
    text = re.sub(r'^\s*[-*+]\s+(.*)$', r'\1', text, flags=re.MULTILINE)  # 无序列表
    text = re.sub(r'^\s*\d+\.\s+(.*)$', r'\1', text, flags=re.MULTILINE)  # 有序列表
    
    # 修复LaTeX特殊字符
    replacements = {
        '\\': '\\textbackslash{}',
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '~': '\\textasciitilde{}',
        '^': '\\textasciicircum{}',
    }
    
    for k, v in replacements.items():
        text = text.replace(k, v)
        
    # 处理段落（将连续换行替换为LaTeX的段落分隔）
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    return '\n\n'.join(paragraphs)

# LaTeX 模板头部，添加了 xurl 宏包以处理 URL 折行
latex_content = r"""\documentclass[11pt,a4paper,twoside]{book}

% 引入宏包
\usepackage{xeCJK}
\usepackage{geometry}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{tocloft}
\usepackage{hyperref}
\usepackage{xurl}  % 自动处理URL折行
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{caption}
\usepackage{xcolor}

% 页面设置
\geometry{left=2.5cm,right=2.5cm,top=3cm,bottom=3cm,headheight=14pt}

% 字体设置
\setCJKmainfont[BoldFont=Noto Serif CJK SC]{Noto Serif CJK SC}
\setCJKsansfont{Noto Sans CJK SC}
\setmainfont{TeX Gyre Termes}

% 颜色设置
\definecolor{primary}{RGB}{128,0,0}
\definecolor{darkgray}{RGB}{64,64,64}

% 链接设置
\hypersetup{
    colorlinks=true,
    linkcolor=primary,
    filecolor=primary,      
    urlcolor=primary,
    pdftitle={狮城脉络：从选区看新加坡街区历史与变迁},
    pdfauthor={Manus AI},
}

% 标题格式
\titleformat{\part}[display]
  {\normalfont\huge\bfseries\centering\color{primary}}
  {\partname}{20pt}{\Huge}
\titleformat{\chapter}[display]
  {\normalfont\Large\bfseries\color{darkgray}}
  {\chaptertitlename\ \thechapter}{16pt}{\LARGE}
\titleformat{\section}
  {\normalfont\large\bfseries}{\thesection}{1em}{}

% 页眉页脚设置
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE,RO]{\thepage}
\fancyhead[RE]{\leftmark}
\fancyhead[LO]{\rightmark}
\renewcommand{\headrulewidth}{0.4pt}

\begin{document}

% 封面
\begin{titlepage}
    \centering
    \vspace*{4cm}
    {\Huge \bfseries \textcolor{primary}{狮城脉络} \par}
    \vspace{1cm}
    {\LARGE \bfseries 从选区看新加坡街区历史与变迁 \par}
    \vspace{2cm}
    {\Large 基于2025年最新选区划分 \par}
    \vspace{4cm}
    {\Large \bfseries Manus AI 编著 \par}
    \vfill
    {\large 2026年6月 \par}
\end{titlepage}

\frontmatter

\chapter*{前言}
\addcontentsline{toc}{chapter}{前言}

本书旨在通过2025年新加坡选区范围检讨委员会（EBRC）发布的最新选区划分，系统梳理新加坡33个选区（18个集选区和15个单选区）的历史与城市发展脉络。

从早期甘榜的烟火气，到新加坡改良信托局（SIT）和建屋发展局（HDB）主导的现代卫星镇建设，再到近年来的生态城市更新，每一个选区不仅是政治地理的划分，更是新加坡社会变迁、族群融合与城市规划的实体缩影。

本书综合了英文、中文、马来文等多语种历史档案，采用城市社会学与历史地理学的专业视角，试图为读者呈现一幅高密度、多维度的狮城街区变迁全景图。

\tableofcontents

\mainmatter
"""

# 生成正文
for part_name, constituencies in sections.items():
    latex_content += f"\n\\part{{{part_name}}}\n\n"
    
    for eng_name in constituencies:
        data = find_data(eng_name)
        if not data:
            print(f"Warning: Data not found for {eng_name}")
            continue
            
        # 使用标准映射的名称，确保SMC/GRC格式一致且中英文对应
        std_name = std_names.get(eng_name, data.get('constituency_name', eng_name))
        name = clean_markdown_and_format(std_name)
        
        early_history = clean_markdown_and_format(data.get('early_history', ''))
        urbanization = clean_markdown_and_format(data.get('urbanization', ''))
        landmarks = clean_markdown_and_format(data.get('landmarks', ''))
        demographics = clean_markdown_and_format(data.get('demographics', ''))
        political_history = clean_markdown_and_format(data.get('political_history', ''))
        recent_development = clean_markdown_and_format(data.get('recent_development', ''))
        community_memory = clean_markdown_and_format(data.get('community_memory', ''))
        references = data.get('references', '')
        
        latex_content += f"\\chapter{{{name}}}\n\n"
        
        latex_content += "\\section{选区划界与政治地理背景}\n"
        latex_content += f"{political_history}\n\n"
        
        latex_content += "\\section{早期地貌与前城市化时期}\n"
        latex_content += f"{early_history}\n\n"
        
        latex_content += "\\section{城市规划与建设进程}\n"
        latex_content += f"{urbanization}\n\n"
        
        latex_content += "\\section{重要地标与建筑}\n"
        latex_content += f"{landmarks}\n\n"
        
        latex_content += "\\section{人口变迁与族群结构}\n"
        latex_content += f"{demographics}\n\n"
        
        latex_content += "\\section{近年发展与城市更新}\n"
        latex_content += f"{recent_development}\n\n"
        
        latex_content += "\\section{社区记忆与空间认同}\n"
        latex_content += f"{community_memory}\n\n"
        
        latex_content += "\\section*{参考资料}\n"
        latex_content += "\\addcontentsline{toc}{section}{参考资料}\n"
        latex_content += "\\begin{itemize}\n"
        for ref in references.split('\n'):
            ref = ref.strip()
            if not ref:
                continue
            # 先提取原始URL（转义前），再分别处理文字和URL
            url_match = re.search(r'(https?://[^\s\)\]]+)', ref)
            if url_match:
                raw_url = url_match.group(1)
                # 对URL之前的文字部分进行LaTeX转义
                before_url = ref[:url_match.start()]
                before_url_clean = clean_markdown_and_format(before_url)
                # URL本身不进行LaTeX转义，直接用\url{}包裹
                ref_clean = before_url_clean + f"\\url{{{raw_url}}}"
            else:
                ref_clean = clean_markdown_and_format(ref)
            latex_content += f"\\item {ref_clean}\n"
        latex_content += "\\end{itemize}\n\n"

# 结尾
latex_content += "\\end{document}\n"

with open('/home/ubuntu/singapore_book/book_fixed.tex', 'w', encoding='utf-8') as f:
    f.write(latex_content)

print("book_fixed.tex 生成完成")
