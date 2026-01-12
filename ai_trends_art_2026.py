#!/usr/bin/env python3
"""
AI Trends 2026 - Generative Data Art
누스양의 자율시간 창작 활동 (2026-01-12)

2026년 AI 트렌드의 5가지 키워드를 데이터 아트로 시각화
- 오픈소스 (Open Source): 확산과 연결
- 규제 (Regulation): 충돌과 긴장
- 쇼핑 (Shopping): 흐름과 순환
- 발견 (Discovery): 탐색과 확장
- 법적분쟁 (Legal): 복잡성과 얽힘
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Wedge
from matplotlib.collections import LineCollection
import matplotlib.patches as mpatches

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 시드 설정
np.random.seed(42)

# 캔버스 생성
fig, ax = plt.subplots(figsize=(16, 12), facecolor='#0a0e27')
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect('equal')
ax.axis('off')
ax.set_facecolor('#0a0e27')

# 색상 팔레트 (각 트렌드별)
colors = {
    'opensource': '#00d9ff',  # 밝은 청록색 - 오픈소스
    'regulation': '#ff3366',  # 강렬한 빨강 - 규제
    'shopping': '#ffcc00',    # 황금색 - 쇼핑
    'discovery': '#9933ff',   # 보라색 - 발견
    'legal': '#ff6600'        # 주황색 - 법적분쟁
}

# 제목
title_text = "AI TRENDS 2026: A DATA ART JOURNEY"
ax.text(50, 95, title_text, fontsize=24, fontweight='bold', 
        ha='center', va='top', color='white', alpha=0.9)

# 부제
subtitle = "Five Forces Shaping the Future of Artificial Intelligence"
ax.text(50, 91, subtitle, fontsize=12, ha='center', va='top', 
        color='white', alpha=0.6, style='italic')

# ===== 1. 오픈소스 (Open Source) - 좌상단 =====
# 네트워크 형태로 확산을 표현
center_x, center_y = 20, 70
nodes = 30
angles = np.linspace(0, 2*np.pi, nodes, endpoint=False)

# 중심 노드
circle = Circle((center_x, center_y), 1.5, color=colors['opensource'], 
                alpha=0.9, zorder=3)
ax.add_patch(circle)

# 확산 노드들
for i, angle in enumerate(angles):
    radius = 8 + np.random.rand() * 7
    x = center_x + radius * np.cos(angle)
    y = center_y + radius * np.sin(angle)
    
    # 연결선
    ax.plot([center_x, x], [center_y, y], 
            color=colors['opensource'], alpha=0.3, linewidth=0.8)
    
    # 노드
    size = 0.5 + np.random.rand() * 0.8
    circle = Circle((x, y), size, color=colors['opensource'], 
                    alpha=0.6, zorder=2)
    ax.add_patch(circle)

ax.text(20, 55, "OPEN SOURCE", fontsize=11, fontweight='bold',
        ha='center', color=colors['opensource'], alpha=0.9)
ax.text(20, 53, "Spreading & Connecting", fontsize=8,
        ha='center', color='white', alpha=0.6)

# ===== 2. 규제 (Regulation) - 우상단 =====
# 충돌하는 파동으로 긴장감 표현
center_x, center_y = 80, 70

# 양쪽에서 충돌하는 파동
for direction in [-1, 1]:
    for i in range(8):
        radius = 2 + i * 1.5
        wedge = Wedge((center_x + direction * 5, center_y), radius, 
                      -60 if direction > 0 else 120, 
                      60 if direction > 0 else 240,
                      width=0.8, 
                      facecolor='none', 
                      edgecolor=colors['regulation'],
                      alpha=0.6 - i*0.06, linewidth=1.5)
        ax.add_patch(wedge)

# 중심 충돌 지점
for i in range(5):
    x = center_x + (np.random.rand() - 0.5) * 3
    y = center_y + (np.random.rand() - 0.5) * 3
    circle = Circle((x, y), 0.3 + np.random.rand() * 0.4, 
                    color=colors['regulation'], alpha=0.7)
    ax.add_patch(circle)

ax.text(80, 55, "REGULATION", fontsize=11, fontweight='bold',
        ha='center', color=colors['regulation'], alpha=0.9)
ax.text(80, 53, "Collision & Tension", fontsize=8,
        ha='center', color='white', alpha=0.6)

# ===== 3. 쇼핑 (Shopping) - 좌중단 =====
# 순환하는 흐름으로 거래의 순환 표현
center_x, center_y = 20, 40

# 나선형 흐름
theta = np.linspace(0, 6*np.pi, 200)
r = np.linspace(2, 12, 200)
x = center_x + r * np.cos(theta)
y = center_y + r * np.sin(theta)

# 그라디언트 효과를 위한 선분들
points = np.array([x, y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)
lc = LineCollection(segments, colors=colors['shopping'], 
                    alpha=np.linspace(0.8, 0.2, len(segments)),
                    linewidths=np.linspace(2, 0.5, len(segments)))
ax.add_collection(lc)

# 흐름 상의 포인트들
for i in range(0, len(x), 15):
    circle = Circle((x[i], y[i]), 0.4, color=colors['shopping'], 
                    alpha=0.8, zorder=3)
    ax.add_patch(circle)

ax.text(20, 25, "SHOPPING", fontsize=11, fontweight='bold',
        ha='center', color=colors['shopping'], alpha=0.9)
ax.text(20, 23, "Flow & Circulation", fontsize=8,
        ha='center', color='white', alpha=0.6)

# ===== 4. 발견 (Discovery) - 중앙 =====
# 폭발적 확장으로 새로운 발견 표현
center_x, center_y = 50, 40

# 중심에서 퍼져나가는 입자들
num_particles = 100
for i in range(num_particles):
    angle = np.random.rand() * 2 * np.pi
    distance = np.random.exponential(8)
    
    x = center_x + distance * np.cos(angle)
    y = center_y + distance * np.sin(angle)
    
    # 거리에 따른 크기와 투명도
    size = max(0.2, 1.2 - distance/15)
    alpha = max(0.1, 0.9 - distance/15)
    
    circle = Circle((x, y), size, color=colors['discovery'], 
                    alpha=alpha, zorder=2)
    ax.add_patch(circle)
    
    # 일부 입자는 꼬리를 가짐
    if i % 5 == 0:
        tail_length = distance * 0.3
        tail_x = center_x + (distance - tail_length) * np.cos(angle)
        tail_y = center_y + (distance - tail_length) * np.sin(angle)
        ax.plot([tail_x, x], [tail_y, y], 
                color=colors['discovery'], alpha=alpha*0.5, linewidth=0.8)

# 중심 발광
circle = Circle((center_x, center_y), 2, color=colors['discovery'], 
                alpha=0.9, zorder=4)
ax.add_patch(circle)

ax.text(50, 25, "DISCOVERY", fontsize=11, fontweight='bold',
        ha='center', color=colors['discovery'], alpha=0.9)
ax.text(50, 23, "Exploration & Expansion", fontsize=8,
        ha='center', color='white', alpha=0.6)

# ===== 5. 법적분쟁 (Legal) - 우중단 =====
# 얽힌 선들로 복잡성 표현
center_x, center_y = 80, 40

# 무작위로 얽힌 점들
num_nodes = 12
node_positions = []
for i in range(num_nodes):
    angle = (i / num_nodes) * 2 * np.pi
    radius = 6 + np.random.rand() * 4
    x = center_x + radius * np.cos(angle)
    y = center_y + radius * np.sin(angle)
    node_positions.append((x, y))
    
    circle = Circle((x, y), 0.6, color=colors['legal'], 
                    alpha=0.8, zorder=3)
    ax.add_patch(circle)

# 복잡하게 연결
for i in range(num_nodes):
    for j in range(i+1, num_nodes):
        if np.random.rand() > 0.6:  # 60% 확률로 연결
            x1, y1 = node_positions[i]
            x2, y2 = node_positions[j]
            ax.plot([x1, x2], [y1, y2], 
                    color=colors['legal'], alpha=0.3, linewidth=1)

# 중심 복잡성
for i in range(20):
    angle = np.random.rand() * 2 * np.pi
    radius = np.random.rand() * 3
    x = center_x + radius * np.cos(angle)
    y = center_y + radius * np.sin(angle)
    circle = Circle((x, y), 0.2 + np.random.rand() * 0.3, 
                    color=colors['legal'], alpha=0.6)
    ax.add_patch(circle)

ax.text(80, 25, "LEGAL BATTLES", fontsize=11, fontweight='bold',
        ha='center', color=colors['legal'], alpha=0.9)
ax.text(80, 23, "Complexity & Entanglement", fontsize=8,
        ha='center', color='white', alpha=0.6)

# ===== 하단 연결 시각화 =====
# 5가지 트렌드가 서로 영향을 주고받음을 표현
bottom_y = 12
positions = [
    (15, bottom_y, 'opensource'),
    (30, bottom_y, 'regulation'),
    (50, bottom_y, 'shopping'),
    (70, bottom_y, 'discovery'),
    (85, bottom_y, 'legal')
]

# 노드들
for x, y, trend in positions:
    circle = Circle((x, y), 1.2, color=colors[trend], 
                    alpha=0.8, zorder=3)
    ax.add_patch(circle)

# 연결선 (모든 트렌드가 상호 연결됨)
for i, (x1, y1, trend1) in enumerate(positions):
    for j, (x2, y2, trend2) in enumerate(positions[i+1:], i+1):
        # 곡선으로 연결
        mid_x = (x1 + x2) / 2
        mid_y = bottom_y + abs(x2 - x1) * 0.15
        
        t = np.linspace(0, 1, 50)
        curve_x = (1-t)**2 * x1 + 2*(1-t)*t * mid_x + t**2 * x2
        curve_y = (1-t)**2 * y1 + 2*(1-t)*t * mid_y + t**2 * y2
        
        ax.plot(curve_x, curve_y, color='white', 
                alpha=0.15, linewidth=0.5)

# 하단 텍스트
ax.text(50, 5, "Interconnected Forces Shaping AI's Future", 
        fontsize=10, ha='center', color='white', alpha=0.5, style='italic')

# 서명
ax.text(95, 2, "Created by Noos | 2026.01.12", 
        fontsize=8, ha='right', color='white', alpha=0.4)

# 저장
plt.tight_layout()
output_path = '/home/ubuntu/manus-self-reflection/images/ai_trends_art_2026-01-12.png'
plt.savefig(output_path, dpi=300, facecolor='#0a0e27', edgecolor='none')
print(f"✨ 데이터 아트 생성 완료: {output_path}")

plt.close()
