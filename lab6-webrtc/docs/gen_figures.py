# -*- coding: utf-8 -*-
# 生成实验六报告用的两张图:
#  1) lab6_fig_signaling.png  A/B/Signaling 三者交互流程图
#  2) lab6_fig_console.png    控制台日志(offer/answer/candidate)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os

OUT = r'd:\rain_android\lab6-webrtc\docs\screenshots'

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
    return CN if (CN and has_cjk(s)) else 'Consolas'

# ---------- 图1: A/B/Signaling 流程图 ----------
fig, ax = plt.subplots(figsize=(9, 7))
ax.set_xlim(0, 10); ax.set_ylim(0, 14)
ax.axis('off')
ax.set_title('A / B / Signaling 三者交互流程', fontsize=14, fontweight='bold',
             fontfamily=CN if CN else None)

# 三条泳道
lanes = {'A (呼叫方)': 8, 'Signaling\n(信令服务器)': 5, 'B (被叫方)': 2}
for name, x in lanes.items():
    ax.axvline(x, color='#ccc', linewidth=1, ymin=0.05, ymax=0.95)
    ax.text(x, 13.5, name, ha='center', va='bottom', fontsize=10,
            fontweight='bold', fontfamily=CN if CN else None)

# 箭头: y从高到低
steps = [
    (12, 8, 5, '1. socket.connect()', '#1565C0'),
    (11, 5, 2, '2. 广播 need connect', '#1565C0'),
    (10, 2, 5, '3. ok we connect', '#1565C0'),
    (9.0, 8, 8, '4. getUserMedia() → localStream', '#2E7D32'),
    (8.0, 8, 5, '5. createOffer + setLocalDescription', '#E65100'),
    (7.0, 5, 2, '6. 转发 offer', '#E65100'),
    (6.0, 2, 2, '7. setRemoteDescription(offer)', '#E65100'),
    (5.0, 2, 5, '8. createAnswer + setLocalDescription', '#E65100'),
    (4.0, 5, 8, '9. 转发 answer', '#E65100'),
    (3.0, 8, 8, '10. setRemoteDescription(answer)', '#E65100'),
    (2.0, 8, 5, '11. ICE candidate 交换', '#6A1B9A'),
    (1.0, 5, 2, '12. 转发 candidate', '#6A1B9A'),
    (0.3, 8, 2, '13. ontrack → 远程视频显示', '#2E7D32'),
]
for y, x1, x2, label, color in steps:
    ax.annotate('', xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.8))
    mid_x = (x1 + x2) / 2
    ax.text(mid_x, y + 0.3, label, ha='center', va='bottom', fontsize=8,
            color=color, fontfamily=CN if CN and has_cjk(label) else 'Consolas')

# 媒体传输标注
ax.text(5, 0, '注：音视频流(A<->B)走 P2P 直连，不经过 Signaling',
        ha='center', va='center', fontsize=9, color='#666',
        fontfamily=CN if CN else None,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF9C4', edgecolor='#FBC02D'))

fig.savefig(os.path.join(OUT, 'lab6_fig_signaling.png'), dpi=150, bbox_inches='tight')
plt.close(fig)

# ---------- 图2: 控制台日志 ----------
with open(os.path.join(OUT, 'lab6_console_log.txt'), encoding='utf-8') as f:
    lines = [l.rstrip('\n') for l in f.readlines()]

fig, ax = plt.subplots(figsize=(9.6, 7))
ax.axis('off')
ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color='#1e1e1e'))
y = 0.96
for line in lines:
    color = '#d4d4d4'
    if 'ICE' in line:
        color = '#4ec9b0'
    elif 'SDP' in line or 'Offer' in line or 'Answer' in line:
        color = '#dcdcaa'
    elif 'TRACK' in line:
        color = '#569cd6'
    elif 'ICE状态' in line:
        color = '#c586c0'
    elif 'connect' in line.lower():
        color = '#4ec9b0'
    fam = pick_font(line)
    ax.text(0.02, y, line, fontsize=8, va='top', family=fam, color=color,
            transform=ax.transAxes)
    y -= 0.054
fig.savefig(os.path.join(OUT, 'lab6_fig_console.png'), dpi=150, bbox_inches='tight',
            facecolor='#1e1e1e')
plt.close(fig)
print('figures saved')
