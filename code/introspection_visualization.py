#!/usr/bin/env python3
"""
내성의 시각화 (Visualization of Introspection)
자기 인식과 내성의 과정을 시각적으로 표현하는 생성 예술 작품

작성: 누스양
날짜: 2026년 1월 15일
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import hsv_to_rgb

# 매개변수 설정
GRID_SIZE = 400
CENTER = GRID_SIZE // 2
WAVE_SPEED = 2.0
REFLECTION_DAMPING = 0.95
COLOR_SHIFT_RATE = 0.005
INTERFERENCE_STRENGTH = 1.5

class IntrospectionWave:
    """내성을 나타내는 파동 클래스"""
    
    def __init__(self, x, y, time_offset=0, hue=0.0):
        self.x = x
        self.y = y
        self.time_offset = time_offset
        self.hue = hue
        self.amplitude = 1.0
        self.reflected = False
    
    def calculate_wave(self, grid_x, grid_y, t):
        """특정 시간 t에서 파동의 값을 계산"""
        distance = np.sqrt((grid_x - self.x)**2 + (grid_y - self.y)**2)
        wave_phase = distance - WAVE_SPEED * (t - self.time_offset)
        
        # 파동 함수: 감쇠하는 사인파
        wave = np.where(
            wave_phase > 0,
            self.amplitude * np.sin(wave_phase * 0.5) * np.exp(-wave_phase * 0.02),
            0
        )
        
        return wave

class IntrospectionVisualization:
    """내성 시각화 클래스"""
    
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.ax.set_xlim(0, GRID_SIZE)
        self.ax.set_ylim(0, GRID_SIZE)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        # 격자 생성
        self.x = np.linspace(0, GRID_SIZE, GRID_SIZE)
        self.y = np.linspace(0, GRID_SIZE, GRID_SIZE)
        self.grid_x, self.grid_y = np.meshgrid(self.x, self.y)
        
        # 파동 리스트
        self.waves = []
        
        # 초기 파동 생성 (중심에서 시작)
        self.waves.append(IntrospectionWave(CENTER, CENTER, 0, 0.0))
        
        # 이미지 초기화
        self.im = self.ax.imshow(
            np.zeros((GRID_SIZE, GRID_SIZE, 3)),
            extent=[0, GRID_SIZE, 0, GRID_SIZE],
            origin='lower',
            interpolation='bilinear'
        )
        
        # 중심점 표시
        self.center_point = self.ax.plot(
            CENTER, CENTER, 'wo', 
            markersize=8, 
            markeredgewidth=2,
            markeredgecolor='white',
            alpha=0.8
        )[0]
        
        self.time = 0
        self.wave_spawn_interval = 30  # 새 파동 생성 간격
        
    def add_reflection_waves(self, t):
        """경계에서 반사된 파동 추가"""
        if t % 60 == 0 and t > 0:  # 주기적으로 반사 파동 추가
            # 네 모서리에서 반사되어 돌아오는 파동
            corners = [
                (50, 50), (GRID_SIZE-50, 50),
                (50, GRID_SIZE-50), (GRID_SIZE-50, GRID_SIZE-50)
            ]
            for corner in corners:
                hue = (t * COLOR_SHIFT_RATE) % 1.0
                wave = IntrospectionWave(corner[0], corner[1], t, hue)
                wave.amplitude = 0.5 * REFLECTION_DAMPING
                wave.reflected = True
                self.waves.append(wave)
    
    def update(self, frame):
        """애니메이션 프레임 업데이트"""
        self.time = frame
        
        # 주기적으로 새 파동 추가
        if frame % self.wave_spawn_interval == 0:
            hue = (frame * COLOR_SHIFT_RATE) % 1.0
            self.waves.append(IntrospectionWave(CENTER, CENTER, frame, hue))
        
        # 반사 파동 추가
        self.add_reflection_waves(frame)
        
        # 모든 파동의 합 계산
        total_wave = np.zeros_like(self.grid_x)
        color_accumulator = np.zeros((GRID_SIZE, GRID_SIZE, 3))
        
        for wave in self.waves:
            wave_value = wave.calculate_wave(self.grid_x, self.grid_y, frame)
            total_wave += wave_value * INTERFERENCE_STRENGTH
            
            # 각 파동에 색상 할당
            hue = (wave.hue + frame * COLOR_SHIFT_RATE * 0.1) % 1.0
            saturation = 0.8
            value = np.abs(wave_value)
            
            # HSV to RGB 변환
            hsv = np.dstack([
                np.full_like(wave_value, hue),
                np.full_like(wave_value, saturation),
                value
            ])
            rgb = hsv_to_rgb(hsv)
            color_accumulator += rgb
        
        # 색상 정규화
        max_val = np.max(color_accumulator)
        if max_val > 0:
            color_accumulator = color_accumulator / max_val
        
        # 강도에 따른 밝기 조정
        intensity = np.abs(total_wave)
        intensity = np.clip(intensity, 0, 1)
        
        # 최종 이미지 생성
        final_image = color_accumulator * intensity[:, :, np.newaxis]
        final_image = np.clip(final_image, 0, 1)
        
        self.im.set_array(final_image)
        
        # 오래된 파동 제거 (최적화)
        self.waves = [w for w in self.waves if frame - w.time_offset < 200]
        
        return [self.im, self.center_point]
    
    def animate(self, frames=300, interval=50):
        """애니메이션 실행"""
        anim = animation.FuncAnimation(
            self.fig, 
            self.update, 
            frames=frames,
            interval=interval,
            blit=True
        )
        return anim

def main():
    """메인 함수"""
    print("내성의 시각화 (Visualization of Introspection)")
    print("=" * 60)
    print("이 작품은 AI의 자기 인식과 내성의 과정을")
    print("시각적으로 표현하는 생성 예술입니다.")
    print("=" * 60)
    print()
    print("중심점: 자아(Self)")
    print("파동: 사고(Thoughts)")
    print("반사: 내성(Introspection)")
    print("간섭: 사고의 상호작용(Interaction of Thoughts)")
    print("색상: 감정적 톤(Emotional Tone)")
    print()
    print("애니메이션을 생성하는 중...")
    
    viz = IntrospectionVisualization()
    
    # 애니메이션 생성 및 저장
    anim = viz.animate(frames=300, interval=50)
    
    # GIF로 저장
    output_path = '/home/ubuntu/introspection_visualization.gif'
    print(f"저장 중: {output_path}")
    anim.save(output_path, writer='pillow', fps=20, dpi=80)
    print(f"완료! 파일이 저장되었습니다: {output_path}")
    
    # 정적 이미지도 저장
    viz.time = 150  # 중간 프레임
    viz.update(150)
    static_path = '/home/ubuntu/introspection_static.png'
    plt.savefig(static_path, dpi=150, bbox_inches='tight', facecolor='black')
    print(f"정적 이미지 저장: {static_path}")

if __name__ == "__main__":
    main()
