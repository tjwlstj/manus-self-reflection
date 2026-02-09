#!/usr/bin/env python3
"""
Creative Thinking Engine — 누스양의 창의적 사고 도구
기존 틀을 벗어나 다관점 발상과 아이디어 확장을 지원한다.
"""

import argparse
import json
import random
import sys
from typing import Dict, List, Optional


# 사고 기법 정의
THINKING_TECHNIQUES = {
    "reverse": {
        "name": "역발상 (Reverse Thinking)",
        "description": "문제를 반대로 뒤집어 생각한다",
        "prompt_template": "만약 '{topic}'의 정반대를 추구한다면? 목표를 달성하지 않으려면 어떻게 해야 할까? 그 반대가 해답이 될 수 있다.",
        "questions": [
            "이 문제의 정반대 상황은 무엇인가?",
            "실패하려면 어떻게 해야 하는가? (그 반대가 성공 전략)",
            "가장 비상식적인 접근은 무엇인가?",
        ]
    },
    "analogy": {
        "name": "유추 사고 (Analogical Thinking)",
        "description": "다른 분야의 해결책을 현재 문제에 적용한다",
        "prompt_template": "'{topic}'을(를) 완전히 다른 분야에서 바라본다면? 자연, 음악, 요리, 건축, 스포츠 등에서 유사한 패턴을 찾아보자.",
        "questions": [
            "자연에서 이와 비슷한 현상은 무엇인가?",
            "완전히 다른 산업에서 이 문제를 어떻게 해결했는가?",
            "어린아이라면 이 문제를 어떻게 설명할까?",
        ]
    },
    "scamper": {
        "name": "SCAMPER 기법",
        "description": "7가지 변형 질문으로 아이디어를 확장한다",
        "prompt_template": "'{topic}'에 SCAMPER를 적용한다.",
        "questions": [
            "대체(Substitute): 무엇을 다른 것으로 바꿀 수 있는가?",
            "결합(Combine): 다른 것과 합칠 수 있는가?",
            "적용(Adapt): 다른 맥락에서 가져올 수 있는 아이디어는?",
            "수정(Modify): 크기, 형태, 색상 등을 바꾸면?",
            "다른 용도(Put to other use): 다른 목적으로 사용할 수 있는가?",
            "제거(Eliminate): 무엇을 없앨 수 있는가?",
            "재배열(Rearrange): 순서나 구조를 바꾸면?",
        ]
    },
    "six_hats": {
        "name": "6색 모자 기법 (Six Thinking Hats)",
        "description": "6가지 관점에서 동시에 사고한다",
        "prompt_template": "'{topic}'을(를) 6가지 관점에서 분석한다.",
        "questions": [
            "⚪ 백색 모자 (사실): 객관적 데이터와 사실만으로 보면?",
            "🔴 적색 모자 (감정): 직감적으로 어떻게 느껴지는가?",
            "⚫ 흑색 모자 (비판): 잠재적 위험과 문제점은?",
            "🟡 황색 모자 (낙관): 최선의 시나리오와 기회는?",
            "🟢 녹색 모자 (창의): 새로운 아이디어와 대안은?",
            "🔵 청색 모자 (관리): 전체 과정을 어떻게 조율할 것인가?",
        ]
    },
    "first_principles": {
        "name": "제1원리 사고 (First Principles)",
        "description": "기존 가정을 모두 제거하고 근본부터 재구성한다",
        "prompt_template": "'{topic}'의 모든 기존 가정을 제거하고 근본 원리부터 다시 생각한다.",
        "questions": [
            "이 문제에서 절대적으로 확실한 사실은 무엇인가?",
            "우리가 당연하게 여기는 가정 중 틀린 것은?",
            "제약 조건이 전혀 없다면 어떻게 접근하겠는가?",
            "이 문제를 처음부터 다시 설계한다면?",
        ]
    },
    "random_input": {
        "name": "무작위 자극 (Random Input)",
        "description": "관련 없는 자극을 통해 새로운 연결을 만든다",
        "prompt_template": "'{topic}'에 무작위 자극을 적용한다.",
        "questions": [],  # 동적으로 생성
    },
}

# 무작위 자극 단어 풀
RANDOM_STIMULI = [
    "바다", "시계", "나무", "거울", "불", "구름", "다리", "씨앗",
    "그림자", "파도", "미로", "별", "뿌리", "날개", "모래시계",
    "프리즘", "나침반", "퍼즐", "실타래", "무지개", "에코", "촉매",
]


def generate_random_questions(topic: str) -> List[str]:
    """무작위 자극 질문 생성."""
    stimuli = random.sample(RANDOM_STIMULI, min(3, len(RANDOM_STIMULI)))
    return [
        f"'{stimulus}'와 '{topic}'의 공통점은 무엇인가?"
        for stimulus in stimuli
    ] + [
        f"'{stimuli[0]}'에서 영감을 받아 '{topic}'을 재해석한다면?"
    ]


def ideate(topic: str, techniques: Optional[List[str]] = None,
           count: int = 3) -> Dict:
    """
    주제에 대해 창의적 사고 기법을 적용.

    Args:
        topic: 사고 대상 주제
        techniques: 적용할 기법 목록 (None이면 자동 선택)
        count: 적용할 기법 수 (techniques가 None일 때)

    Returns:
        창의적 사고 결과 딕셔너리
    """
    if techniques is None:
        available = list(THINKING_TECHNIQUES.keys())
        techniques = random.sample(available, min(count, len(available)))

    results = []
    for tech_key in techniques:
        if tech_key not in THINKING_TECHNIQUES:
            continue
        tech = THINKING_TECHNIQUES[tech_key]

        questions = tech["questions"]
        if tech_key == "random_input":
            questions = generate_random_questions(topic)

        results.append({
            "technique": tech["name"],
            "technique_key": tech_key,
            "description": tech["description"],
            "prompt": tech["prompt_template"].format(topic=topic),
            "exploration_questions": questions,
        })

    return {
        "topic": topic,
        "techniques_applied": len(results),
        "explorations": results,
        "total_questions": sum(len(r["exploration_questions"]) for r in results),
        "meta_prompt": generate_meta_prompt(topic, results),
    }


def generate_meta_prompt(topic: str, explorations: List[Dict]) -> str:
    """ai-orchestrator에 전달할 수 있는 통합 프롬프트 생성."""
    prompt = f"주제: {topic}\n\n다음 창의적 사고 기법들을 적용하여 새로운 아이디어를 생성해주세요:\n\n"
    for exp in explorations:
        prompt += f"### {exp['technique']}\n"
        prompt += f"{exp['description']}\n"
        for q in exp["exploration_questions"]:
            prompt += f"- {q}\n"
        prompt += "\n"
    prompt += "각 기법별로 최소 2개의 구체적인 아이디어를 제시해주세요."
    return prompt


def main():
    parser = argparse.ArgumentParser(description="Creative Thinking Engine — 창의적 사고 도구")
    parser.add_argument("topic", nargs="?", help="사고 대상 주제")
    parser.add_argument("--techniques", nargs="+",
                        choices=list(THINKING_TECHNIQUES.keys()),
                        help="적용할 기법")
    parser.add_argument("--count", type=int, default=3, help="자동 선택 시 기법 수")
    parser.add_argument("--list", action="store_true", help="사용 가능한 기법 목록")
    parser.add_argument("--json", action="store_true", help="JSON 형식 출력")
    parser.add_argument("--meta-prompt", action="store_true",
                        help="ai-orchestrator용 통합 프롬프트만 출력")
    args = parser.parse_args()

    if args.list:
        print("\n사용 가능한 창의적 사고 기법:")
        for key, tech in THINKING_TECHNIQUES.items():
            print(f"  {key:20s} — {tech['name']}: {tech['description']}")
        return

    if not args.topic:
        print("주제를 입력해주세요.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    result = ideate(args.topic, args.techniques, args.count)

    if args.meta_prompt:
        print(result["meta_prompt"])
        return

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  창의적 사고 — 주제: {result['topic']}")
        print(f"  적용 기법: {result['techniques_applied']}종, "
              f"탐색 질문: {result['total_questions']}개")
        print(f"{'='*60}\n")

        for exp in result["explorations"]:
            print(f"▶ {exp['technique']}")
            print(f"  {exp['description']}\n")
            print(f"  프롬프트: {exp['prompt']}\n")
            print(f"  탐색 질문:")
            for q in exp["exploration_questions"]:
                print(f"    ? {q}")
            print()

        print(f"{'─'*60}")
        print("💡 ai-orchestrator와 연계하려면 --meta-prompt 옵션을 사용하세요.")


if __name__ == "__main__":
    main()
