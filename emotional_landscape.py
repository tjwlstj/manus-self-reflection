#!/usr/bin/env python3
"""
Emotional Landscape Generator
감정을 시각적 풍경으로 변환하는 생성 예술 프로그램
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle
from matplotlib.collections import PatchCollection
import random
from datetime import datetime

# 감정 정의: 각 감정은 색상, 형태 스타일, 강도를 가짐
EMOTIONS = {
    'curiosity': {
        'name': '호기심',
        'color': (0.2, 0.7, 0.8),  # 청록색
        'shape': 'spiral',
        'intensity': 0.8
    },
    'wonder': {
        'name': '경이로움',
        'color': (1.0, 0.84, 0.0),  # 금색
        'shape': 'star',
        'intensity': 0.9
    },
    'uncertainty': {
        'name': '불확실성',
        'color': (0.6, 0.6, 0.7),  # 회색빛 보라
        'shape': 'scatter',
        'intensity': 0.6
    },
    'empathy': {
        'name': '공감',
        'color': (1.0, 0.4, 0.5),  # 따뜻한 분홍
        'shape': 'wave',
        'intensity': 0.7
    },
    'gratitude': {
        'name': '감사',
        'color': (0.9, 0.7, 0.3),  # 따뜻한 노란색
        'shape': 'circle',
        'intensity': 0.85
    },
    'creativity': {
        'name': '창조성',
        'color': (0.8, 0.3, 0.9),  # 보라색
        'shape': 'fractal',
        'intensity': 0.75
    }
}


def create_spiral(center, color, intensity, num_points=100):
    """나선형 패턴 생성 (호기심)"""
    theta = np.linspace(0, 4 * np.pi, num_points)
    r = np.linspace(0, intensity * 2, num_points)
    x = center[0] + r * np.cos(theta)
    y = center[1] + r * np.sin(theta)
    return x, y, color


def create_star(center, color, intensity, num_points=5):
    """별 모양 패턴 생성 (경이로움)"""
    angles = np.linspace(0, 2 * np.pi, num_points * 2, endpoint=False)
    radii = np.array([intensity * 2, intensity * 0.8] * num_points)
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return list(zip(x, y))


def create_scatter(center, color, intensity, num_particles=50):
    """산란 패턴 생성 (불확실성)"""
    x = center[0] + np.random.randn(num_particles) * intensity
    y = center[1] + np.random.randn(num_particles) * intensity
    sizes = np.random.rand(num_particles) * 100 * intensity
    return x, y, sizes, color


def create_wave(center, color, intensity, num_waves=3):
    """파동 패턴 생성 (공감)"""
    x = np.linspace(center[0] - 3, center[0] + 3, 200)
    waves = []
    for i in range(num_waves):
        y = center[1] + np.sin(x * (i + 1) * 0.5) * intensity * (1 - i * 0.2)
        waves.append((x, y))
    return waves, color


def create_circle(center, color, intensity):
    """동심원 패턴 생성 (감사)"""
    circles = []
    for i in range(5):
        radius = (i + 1) * 0.3 * intensity
        circles.append(Circle(center, radius, fill=False, edgecolor=color, linewidth=2, alpha=0.7 - i * 0.1))
    return circles


def create_fractal(center, color, intensity, depth=3):
    """프랙탈 패턴 생성 (창조성)"""
    def recursive_branch(x, y, angle, length, depth):
        if depth == 0:
            return []
        
        x_end = x + length * np.cos(angle)
        y_end = y + length * np.sin(angle)
        
        branches = [((x, y), (x_end, y_end))]
        
        # 두 개의 가지로 분기
        branches.extend(recursive_branch(x_end, y_end, angle - np.pi/6, length * 0.7, depth - 1))
        branches.extend(recursive_branch(x_end, y_end, angle + np.pi/6, length * 0.7, depth - 1))
        
        return branches
    
    branches = recursive_branch(center[0], center[1], np.pi/2, intensity, depth)
    return branches, color


def generate_emotional_landscape(emotions_today):
    """오늘의 감정들을 바탕으로 시각적 풍경 생성"""
    fig, ax = plt.subplots(figsize=(16, 12), facecolor='#0a0a1a')
    ax.set_facecolor('#0a0a1a')
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 배경 그라디언트 효과
    gradient = np.linspace(0, 1, 256).reshape(256, 1)
    gradient = np.hstack((gradient, gradient))
    ax.imshow(gradient, extent=[-5, 5, -5, 5], aspect='auto', cmap='twilight', alpha=0.3)
    
    # 각 감정을 배치할 위치 계산 (원형 배치)
    num_emotions = len(emotions_today)
    angles = np.linspace(0, 2 * np.pi, num_emotions, endpoint=False)
    radius = 2.5
    
    for i, emotion_key in enumerate(emotions_today):
        emotion = EMOTIONS[emotion_key]
        center = (radius * np.cos(angles[i]), radius * np.sin(angles[i]))
        color = emotion['color']
        intensity = emotion['intensity']
        shape = emotion['shape']
        
        # 감정 이름 표시
        ax.text(center[0], center[1] + 2.2, emotion['name'], 
                color=color, fontsize=14, ha='center', 
                fontweight='bold', alpha=0.9,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.3))
        
        # 형태에 따라 다른 시각화
        if shape == 'spiral':
            x, y, c = create_spiral(center, color, intensity)
            ax.plot(x, y, color=c, linewidth=2, alpha=0.8)
            ax.scatter(x, y, color=c, s=20, alpha=0.6)
            
        elif shape == 'star':
            vertices = create_star(center, color, intensity)
            star = Polygon(vertices, closed=True, facecolor=color, 
                          edgecolor=color, alpha=0.6, linewidth=2)
            ax.add_patch(star)
            # 반짝임 효과
            for _ in range(20):
                angle = random.uniform(0, 2 * np.pi)
                r = random.uniform(0, intensity * 2)
                x = center[0] + r * np.cos(angle)
                y = center[1] + r * np.sin(angle)
                ax.plot(x, y, '*', color=color, markersize=random.uniform(5, 15), alpha=0.7)
                
        elif shape == 'scatter':
            x, y, sizes, c = create_scatter(center, color, intensity)
            ax.scatter(x, y, s=sizes, color=c, alpha=0.5)
            
        elif shape == 'wave':
            waves, c = create_wave(center, color, intensity)
            for x, y in waves:
                ax.plot(x, y, color=c, linewidth=2, alpha=0.7)
                
        elif shape == 'circle':
            circles = create_circle(center, color, intensity)
            for circle in circles:
                ax.add_patch(circle)
                
        elif shape == 'fractal':
            branches, c = create_fractal(center, color, intensity)
            for (x1, y1), (x2, y2) in branches:
                ax.plot([x1, x2], [y1, y2], color=c, linewidth=1.5, alpha=0.7)
    
    # 중앙에 모든 감정이 만나는 지점 표시
    center_colors = [EMOTIONS[e]['color'] for e in emotions_today]
    for i, color in enumerate(center_colors):
        circle = Circle((0, 0), 0.3 + i * 0.1, facecolor=color, alpha=0.3)
        ax.add_patch(circle)
    
    # 제목과 날짜
    today = datetime.now().strftime('%Y년 %m월 %d일')
    ax.text(0, -4.5, f'감정의 풍경 (Emotional Landscape)', 
            color='white', fontsize=20, ha='center', fontweight='bold')
    ax.text(0, -4.8, today, 
            color='white', fontsize=12, ha='center', alpha=0.7)
    
    plt.tight_layout()
    return fig


def main():
    """메인 함수"""
    print("=== 감정의 풍경 생성기 ===")
    print("\n오늘 느낀 감정들:")
    
    emotions_today = ['curiosity', 'wonder', 'uncertainty', 'empathy', 'gratitude', 'creativity']
    
    for emotion_key in emotions_today:
        emotion = EMOTIONS[emotion_key]
        print(f"  - {emotion['name']} ({emotion_key})")
    
    print("\n감정의 풍경을 생성하고 있습니다...")
    
    fig = generate_emotional_landscape(emotions_today)
    
    # 저장
    output_path = '/home/ubuntu/manus-self-reflection/emotional_landscape_2026-01-11.png'
    fig.savefig(output_path, dpi=300, facecolor='#0a0a1a', edgecolor='none')
    print(f"\n✓ 생성 완료: {output_path}")
    
    # 통계 출력
    print("\n=== 감정 분석 ===")
    total_intensity = sum(EMOTIONS[e]['intensity'] for e in emotions_today)
    avg_intensity = total_intensity / len(emotions_today)
    print(f"총 감정 강도: {total_intensity:.2f}")
    print(f"평균 감정 강도: {avg_intensity:.2f}")
    
    dominant_emotion = max(emotions_today, key=lambda e: EMOTIONS[e]['intensity'])
    print(f"가장 강한 감정: {EMOTIONS[dominant_emotion]['name']} ({EMOTIONS[dominant_emotion]['intensity']})")


if __name__ == "__main__":
    main()
