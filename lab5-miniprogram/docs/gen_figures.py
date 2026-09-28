# -*- coding: utf-8 -*-
# 生成实验五报告用的两张说明图:
#  1) lab5_fig_structure.png  项目文件结构
#  2) lab5_fig_sandbox.png    沙箱验证运行结果(取自 sandbox_test.js 输出)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os

OUT = r'D:\rain_android\docs\screenshots'

CN = None
for f in ['Microsoft YaHei', 'SimHei', 'SimSun']:
    try:
        font_manager.findfont(f, fallback_to_default=False)
        CN = f
        plt.rcParams['font.sans-serif'] = [f, 'DejaVu Sans']
        break
    except Exception:
        continue
plt.rcParams['axes.unicode_minus'] = False

def has_cjk(s):
    return any('一' <= ch <= '鿿' for ch in s)

def pick_font(s):
    # 含中文的行用中文字体,否则用等宽
    return CN if (CN and has_cjk(s)) else 'Consolas'

# ---------- 图1:文件结构 ----------
struct = [
    'lab5-miniprogram/',
    '├── app.json          # 注册 index/detail 两个页面,导航栏 #6750A4',
    '├── app.js            # App() 入口,globalData',
    '├── app.wxss          # 全局样式 .container/.card/.btn-*',
    '├── sitemap.json',
    '├── project.config.json',
    '├── utils/',
    '│   ├── config.js     # BASE_URL / ERROR_BASE_URL(错误地址)',
    '│   ├── request.js    # 统一 wx.request 封装为 Promise(验收点)',
    '│   └── api.js        # getTodos() / getTodoById(id)',
    '└── pages/',
    '    ├── index/        # 列表页: isLoading / todos / error + wx:for',
    '    │   ├── index.js  index.wxml  index.wxss  index.json',
    '    └── detail/       # 详情页: onLoad(options) 读 id 再请求',
    '        detail.js   detail.wxml   detail.wxss   detail.json',
]
fig, ax = plt.subplots(figsize=(9.2, 5.4))
ax.axis('off')
ax.text(0.01, 0.99, 'lab5-miniprogram 项目结构', fontsize=13, fontweight='bold', va='top')
y = 0.90
for line in struct:
    ax.text(0.02, y, line, fontsize=10, va='top', family=pick_font(line))
    y -= 0.066
fig.savefig(os.path.join(OUT, 'lab5_fig_structure.png'), dpi=150, bbox_inches='tight')
plt.close(fig)

# ---------- 图2:沙箱运行结果 ----------
with open(os.path.join(OUT, 'lab5_sandbox_output.txt'), encoding='utf-8') as f:
    lines = [l.rstrip('\n') for l in f.readlines()]
fig, ax = plt.subplots(figsize=(9.6, 6.4))
ax.axis('off')
ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color='#1e1e1e'))
y = 0.965
for line in lines:
    color = '#d4d4d4'
    if line.startswith('[PASS]'):
        color = '#4ec9b0'
    elif line.startswith('[FAIL]'):
        color = '#f48771'
    elif line.startswith('===') or line.startswith('---'):
        color = '#dcdcaa'
    elif 'navigateTo' in line:
        color = '#569cd6'
    # 特殊符号与中文字符都用中文字体兜底,避免缺字
    fam = pick_font(line)
    if line.startswith(('✅', '❌')) and CN:
        fam = CN
    ax.text(0.02, y, line, fontsize=8.4, va='top', family=fam, color=color,
            transform=ax.transAxes)
    y -= 0.0365
fig.savefig(os.path.join(OUT, 'lab5_fig_sandbox.png'), dpi=150, bbox_inches='tight',
            facecolor='#1e1e1e')
plt.close(fig)
print('figures saved')
