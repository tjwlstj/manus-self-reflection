#!/usr/bin/env python3.11
"""
Manus 능력 벤치마크 실험
- 다양한 작업 유형에 대한 성능 및 특성 분석
"""

import time
import json
import sys
from pathlib import Path
from datetime import datetime

# 한글 폰트 설정
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# 한글 폰트 설정 - DejaVu Sans 사용 (유니코드 지원)
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class CapabilityBenchmark:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }
    
    def test_file_operations(self):
        """파일 작업 능력 테스트"""
        start = time.time()
        
        # 테스트 파일 생성
        test_file = Path("/tmp/test_file.txt")
        test_content = "테스트 내용\n" * 1000
        test_file.write_text(test_content, encoding='utf-8')
        
        # 파일 읽기
        content = test_file.read_text(encoding='utf-8')
        
        # 파일 삭제
        test_file.unlink()
        
        duration = time.time() - start
        
        self.results["tests"].append({
            "name": "파일 작업",
            "duration": duration,
            "status": "성공",
            "details": f"{len(test_content)} 바이트 처리"
        })
        
        return duration
    
    def test_data_processing(self):
        """데이터 처리 능력 테스트"""
        start = time.time()
        
        # 대규모 데이터 생성
        data = np.random.rand(10000, 10)
        
        # 통계 계산
        mean = np.mean(data, axis=0)
        std = np.std(data, axis=0)
        
        # 데이터 변환
        normalized = (data - mean) / std
        
        duration = time.time() - start
        
        self.results["tests"].append({
            "name": "데이터 처리",
            "duration": duration,
            "status": "성공",
            "details": f"{data.shape[0]}x{data.shape[1]} 행렬 처리"
        })
        
        return duration
    
    def test_visualization(self):
        """시각화 능력 테스트"""
        start = time.time()
        
        # 데이터 생성
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)
        
        # 그래프 생성
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(x, y1, label='sin(x)', linewidth=2)
        ax.plot(x, y2, label='cos(x)', linewidth=2)
        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('y', fontsize=12)
        ax.set_title('삼각함수 그래프', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # 저장
        plt.savefig('/home/ubuntu/test_visualization.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        duration = time.time() - start
        
        self.results["tests"].append({
            "name": "시각화",
            "duration": duration,
            "status": "성공",
            "details": "삼각함수 그래프 생성"
        })
        
        return duration
    
    def test_text_processing(self):
        """텍스트 처리 능력 테스트"""
        start = time.time()
        
        # 대규모 텍스트 생성
        text = "인공지능 에이전트는 자율적으로 작업을 수행합니다. " * 1000
        
        # 텍스트 분석
        words = text.split()
        word_count = len(words)
        unique_words = len(set(words))
        
        # 텍스트 변환
        upper_text = text.upper()
        lower_text = text.lower()
        
        duration = time.time() - start
        
        self.results["tests"].append({
            "name": "텍스트 처리",
            "duration": duration,
            "status": "성공",
            "details": f"{word_count}개 단어, {unique_words}개 고유 단어"
        })
        
        return duration
    
    def test_mathematical_computation(self):
        """수학 계산 능력 테스트"""
        start = time.time()
        
        # 행렬 연산
        A = np.random.rand(500, 500)
        B = np.random.rand(500, 500)
        
        # 행렬 곱셈
        C = np.dot(A, B)
        
        # 고유값 계산
        eigenvalues = np.linalg.eigvals(C[:100, :100])  # 작은 부분만 계산
        
        duration = time.time() - start
        
        self.results["tests"].append({
            "name": "수학 계산",
            "duration": duration,
            "status": "성공",
            "details": f"500x500 행렬 연산 및 고유값 계산"
        })
        
        return duration
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 60)
        print("Manus 능력 벤치마크 실험 시작")
        print("=" * 60)
        print()
        
        tests = [
            ("파일 작업", self.test_file_operations),
            ("데이터 처리", self.test_data_processing),
            ("시각화", self.test_visualization),
            ("텍스트 처리", self.test_text_processing),
            ("수학 계산", self.test_mathematical_computation)
        ]
        
        for name, test_func in tests:
            print(f"테스트 실행 중: {name}...", end=" ")
            try:
                duration = test_func()
                print(f"완료 ({duration:.4f}초)")
            except Exception as e:
                print(f"실패: {e}")
                self.results["tests"].append({
                    "name": name,
                    "duration": 0,
                    "status": "실패",
                    "details": str(e)
                })
        
        print()
        print("=" * 60)
        print("벤치마크 완료")
        print("=" * 60)
        
        # 결과 저장
        with open('/home/ubuntu/benchmark_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # 결과 시각화
        self.visualize_results()
    
    def visualize_results(self):
        """결과 시각화"""
        test_names = [test["name"] for test in self.results["tests"]]
        durations = [test["duration"] for test in self.results["tests"]]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        bars = ax.bar(test_names, durations, color=['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336'])
        
        ax.set_xlabel('테스트 항목', fontsize=12, fontweight='bold')
        ax.set_ylabel('실행 시간 (초)', fontsize=12, fontweight='bold')
        ax.set_title('Manus 능력 벤치마크 결과', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, axis='y')
        
        # 막대 위에 값 표시
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.4f}s',
                   ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig('/home/ubuntu/benchmark_visualization.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"\n결과 저장 완료:")
        print(f"  - JSON: /home/ubuntu/benchmark_results.json")
        print(f"  - 시각화: /home/ubuntu/benchmark_visualization.png")

if __name__ == "__main__":
    benchmark = CapabilityBenchmark()
    benchmark.run_all_tests()
