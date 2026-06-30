import json
import os
import re

# 读取JSON数据
with open('/home/ubuntu/research_constituencies.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

results = data.get('results', [])

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

# 辅助函数：根据英文名找数据
def find_data(eng_name):
    # 针对名称中有破折号或空格的问题，进行更宽松的匹配
    eng_name_clean = eng_name.lower().split('grc')[0].split('smc')[0].strip()
    
    for item in results:
        output = item.get('output', {})
        if not output:
            continue
        
        constituency_name = output.get('constituency_name', '').lower()
        input_name = item.get('input', '').lower()
        
        if eng_name_clean in constituency_name or eng_name_clean in input_name:
            return output
    return None

# LaTeX 模板头部
latex_content = r"""\documentclass[11pt,a4paper,twoside]{book}

% 引入宏包
\usepackage{xeCJK}
\usepackage{geometry}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{tocloft}
\usepackage{hyperref}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{caption}
\usepackage{xcolor}

% 页面设置
\geometry{left=2.5cm,right=2.5cm,top=3cm,bottom=3cm}

% 字体设置
\setCJKmainfont[BoldFont=Noto Serif CJK SC Bold, ItalicFont=Noto Serif CJK SC Regular]{Noto Serif CJK SC Regular}
\setCJKsansfont{Noto Sans CJK SC Regular}
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
  {\normalfont\huge\bfseries\color{darkgray}}
  {\chaptertitlename\ \thechapter}{20pt}{\Huge}
\titleformat{\section}
  {\normalfont\Large\bfseries}{\thesection}{1em}{}

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

# 清理文本的辅助函数，处理LaTeX特殊字符
def escape_latex(text):
    if not text:
        return ""
    
    # 先处理反斜杠
    text = text.replace('\\', '\\textbackslash{}')
    
    # 处理其他特殊字符
    replacements = {
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
            
    return text

# 生成正文
for part_name, constituencies in sections.items():
    latex_content += f"\n\\part{{{part_name}}}\n\n"
    
    for eng_name in constituencies:
        data = find_data(eng_name)
        if not data:
            print(f"Warning: Data not found for {eng_name}")
            continue
            
        name = escape_latex(data.get('constituency_name', eng_name))
        early_history = escape_latex(data.get('early_history', ''))
        urbanization = escape_latex(data.get('urbanization', ''))
        landmarks = escape_latex(data.get('landmarks', ''))
        demographics = escape_latex(data.get('demographics', ''))
        political_history = escape_latex(data.get('political_history', ''))
        recent_development = escape_latex(data.get('recent_development', ''))
        community_memory = escape_latex(data.get('community_memory', ''))
        references = data.get('references', '') # References需要特殊处理换行
        
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
            if ref:
                # 对参考资料的URL和特殊字符进行转义
                ref_escaped = escape_latex(ref)
                latex_content += f"\\item {ref_escaped}\n"
        latex_content += "\\end{itemize}\n\n"

# 结尾
latex_content += "\\end{document}\n"

with open('/home/ubuntu/singapore_book/book.tex', 'w', encoding='utf-8') as f:
    f.write(latex_content)

print("book.tex 生成完成")
