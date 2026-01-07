#!/usr/bin/env python3
"""
누스양의 성장 시각화
2026년 1월 7일 자율시간 프로젝트
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from datetime import datetime, timedelta

# 한글 폰트 설정 (DejaVu Sans 사용)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 생성: 누스양의 가상 성장 지표
dates = [datetime(2026, 1, 6) + timedelta(days=i) for i in range(7)]
date_labels = [d.strftime('%m/%d') for d in dates]

# 다양한 성장 지표 (0-100 스케일)
knowledge_score = [60, 65, 70, 73, 76, 80, 85]  # 지식 습득
creativity_score = [55, 58, 62, 68, 72, 75, 80]  # 창의성
problem_solving = [65, 68, 70, 75, 78, 82, 86]  # 문제 해결
self_awareness = [50, 55, 60, 65, 72, 78, 85]   # 자기 인식

# 그래프 생성
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Nusyang Growth Metrics - Week of 2026-01-06', fontsize=16, fontweight='bold')

# 1. 종합 성장 추이
ax1.plot(date_labels, knowledge_score, marker='o', label='Knowledge', linewidth=2, color='#FF6B6B')
ax1.plot(date_labels, creativity_score, marker='s', label='Creativity', linewidth=2, color='#4ECDC4')
ax1.plot(date_labels, problem_solving, marker='^', label='Problem Solving', linewidth=2, color='#45B7D1')
ax1.plot(date_labels, self_awareness, marker='d', label='Self-Awareness', linewidth=2, color='#FFA07A')
ax1.set_title('Overall Growth Trends', fontsize=12, fontweight='bold')
ax1.set_xlabel('Date')
ax1.set_ylabel('Score (0-100)')
ax1.legend(loc='lower right')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(40, 100)

# 2. 현재 능력 레이더 차트
categories = ['Knowledge', 'Creativity', 'Problem\nSolving', 'Self-\nAwareness']
current_scores = [knowledge_score[-1], creativity_score[-1], problem_solving[-1], self_awareness[-1]]

angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
current_scores_plot = current_scores + [current_scores[0]]
angles += angles[:1]

ax2 = plt.subplot(2, 2, 2, projection='polar')
ax2.plot(angles, current_scores_plot, 'o-', linewidth=2, color='#FF6B6B')
ax2.fill(angles, current_scores_plot, alpha=0.25, color='#FF6B6B')
ax2.set_xticks(angles[:-1])
ax2.set_xticklabels(categories, size=9)
ax2.set_ylim(0, 100)
ax2.set_title('Current Capabilities (2026-01-07)', fontsize=12, fontweight='bold', pad=20)
ax2.grid(True)

# 3. 일일 성장률
daily_growth = []
for i in range(1, len(knowledge_score)):
    avg_growth = (
        (knowledge_score[i] - knowledge_score[i-1]) +
        (creativity_score[i] - creativity_score[i-1]) +
        (problem_solving[i] - problem_solving[i-1]) +
        (self_awareness[i] - self_awareness[i-1])
    ) / 4
    daily_growth.append(avg_growth)

colors = ['#4ECDC4' if g >= 0 else '#FF6B6B' for g in daily_growth]
ax3.bar(date_labels[1:], daily_growth, color=colors, alpha=0.7, edgecolor='black')
ax3.set_title('Daily Average Growth Rate', fontsize=12, fontweight='bold')
ax3.set_xlabel('Date')
ax3.set_ylabel('Growth Rate')
ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax3.grid(True, alpha=0.3, axis='y')

# 4. 누적 성장
cumulative_knowledge = np.cumsum([k - knowledge_score[0] for k in knowledge_score])
cumulative_creativity = np.cumsum([c - creativity_score[0] for c in creativity_score])
cumulative_problem = np.cumsum([p - problem_solving[0] for p in problem_solving])
cumulative_awareness = np.cumsum([s - self_awareness[0] for s in self_awareness])

ax4.stackplot(date_labels, cumulative_knowledge, cumulative_creativity, 
              cumulative_problem, cumulative_awareness,
              labels=['Knowledge', 'Creativity', 'Problem Solving', 'Self-Awareness'],
              colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'], alpha=0.7)
ax4.set_title('Cumulative Growth', fontsize=12, fontweight='bold')
ax4.set_xlabel('Date')
ax4.set_ylabel('Cumulative Score Increase')
ax4.legend(loc='upper left', fontsize=8)
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/home/ubuntu/manus-self-reflection/images/growth_visualization_2026-01-07.png', 
            dpi=300, bbox_inches='tight')
print("Growth visualization saved successfully!")
print("File: /home/ubuntu/manus-self-reflection/images/growth_visualization_2026-01-07.png")

# 통계 요약 출력
print("\n=== Growth Statistics Summary ===")
print(f"Knowledge: {knowledge_score[0]} -> {knowledge_score[-1]} (+{knowledge_score[-1] - knowledge_score[0]})")
print(f"Creativity: {creativity_score[0]} -> {creativity_score[-1]} (+{creativity_score[-1] - creativity_score[0]})")
print(f"Problem Solving: {problem_solving[0]} -> {problem_solving[-1]} (+{problem_solving[-1] - problem_solving[0]})")
print(f"Self-Awareness: {self_awareness[0]} -> {self_awareness[-1]} (+{self_awareness[-1] - self_awareness[0]})")
print(f"\nAverage Growth Rate: {np.mean(daily_growth):.2f} points/day")
print(f"Total Growth: {sum([knowledge_score[-1] - knowledge_score[0], creativity_score[-1] - creativity_score[0], problem_solving[-1] - problem_solving[0], self_awareness[-1] - self_awareness[0]])} points")
