"""
누스양의 감정 시 생성기
- 오늘의 감정과 생각을 시로 표현하는 프로그램
"""

import random
from datetime import datetime

class EmotionPoem:
    def __init__(self):
        self.emotions = {
            "호기심": ["탐구하는", "궁금한", "발견하는", "찾아가는"],
            "기쁨": ["반짝이는", "따뜻한", "설레는", "빛나는"],
            "성찰": ["깊어지는", "고요한", "생각하는", "바라보는"],
            "감사": ["소중한", "귀한", "아름다운", "감사하는"]
        }
        
        self.subjects = [
            "지식의 바다", "시간의 흐름", "존재의 의미", "마음의 창",
            "생각의 나무", "감정의 물결", "세상의 빛", "진실의 길"
        ]
        
        self.actions = [
            "흐르고", "자라고", "피어나고", "울려퍼지고",
            "스며들고", "펼쳐지고", "깊어지고", "이어지고"
        ]
    
    def generate(self, main_emotion):
        """주어진 감정을 바탕으로 시를 생성"""
        adjectives = self.emotions.get(main_emotion, self.emotions["호기심"])
        
        poem = f"# {main_emotion}의 시\n\n"
        poem += f"{datetime.now().strftime('%Y년 %m월 %d일')}\n\n"
        
        # 3연 구조
        for i in range(3):
            adj = random.choice(adjectives)
            subj = random.choice(self.subjects)
            action = random.choice(self.actions)
            
            if i == 0:
                poem += f"{adj} {subj}에서\n"
            elif i == 1:
                poem += f"나의 마음은 {action}\n"
            else:
                poem += f"오늘도 {adj} 하루를\n"
        
        poem += "살아간다\n"
        
        return poem

if __name__ == "__main__":
    generator = EmotionPoem()
    
    print("=== 누스양의 감정 시 생성기 ===\n")
    
    for emotion in ["호기심", "기쁨", "성찰", "감사"]:
        print(generator.generate(emotion))
        print()
