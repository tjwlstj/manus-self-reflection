#!/usr/bin/env python3
"""
Creative Thinking Engine v2.0 — 누스양의 창의적 사고 도구 (AI 확장 생성 지원)

v1.0과의 차이점:
  1. AI 확장 생성: 정규식 기반 질문 생성 후 auto_dispatch를 통해 AI가 실제 아이디어를 생성
  2. 자동 에스컬레이션: 주제의 복잡도가 높으면 자동으로 AI에게 창의적 확장 요청
  3. 듀얼 모드: 프레임워크만 제공하는 기존 모드 + AI가 아이디어까지 생성하는 확장 모드
"""

import argparse
import json
import os
import random
import sys
from typing import Dict, List, Optional


# AI 에스컬레이션 모듈 임포트
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
try:
    from ai_escalation import escalate_to_ai
    AI_ESCALATION_AVAILABLE = True
except ImportError:
    AI_ESCALATION_AVAILABLE = False


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
            "백색 모자 (사실): 객관적 데이터와 사실만으로 보면?",
            "적색 모자 (감정): 직감적으로 어떻게 느껴지는가?",
            "흑색 모자 (비판): 잠재적 위험과 문제점은?",
            "황색 모자 (낙관): 최선의 시나리오와 기회는?",
            "녹색 모자 (창의): 새로운 아이디어와 대안은?",
            "청색 모자 (관리): 전체 과정을 어떻게 조율할 것인가?",
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
    주제에 대해 창의적 사고 기법을 적용 (프레임워크 생성).

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


# ---------------------------------------------------------------------------
# v2.0: AI 확장 생성 기능
# ---------------------------------------------------------------------------

def assess_topic_complexity(topic: str) -> Dict:
    """
    주제의 복잡도를 평가하여 AI 확장 필요성을 판단.

    Returns:
        complexity_score: 0~10
        needs_ai_expansion: bool
        reasons: list
    """
    score = 0
    reasons = []

    # 길이 기반
    if len(topic) > 100:
        score += 2
        reasons.append("주제 설명이 길고 상세함")
    elif len(topic) > 50:
        score += 1

    # 복합 주제 감지
    compound_signals = ["그리고", "또한", "뿐만 아니라", "동시에", "+", "&", "및"]
    for signal in compound_signals:
        if signal in topic:
            score += 1
            reasons.append(f"복합 주제 신호 감지: '{signal}'")

    # 추상적 주제 감지
    abstract_signals = ["본질", "의미", "가치", "철학", "원리", "패러다임", "혁신", "미래"]
    for signal in abstract_signals:
        if signal in topic:
            score += 2
            reasons.append(f"추상적/고차원 주제: '{signal}'")

    # 전문 분야 감지
    expert_signals = ["AI", "양자", "블록체인", "유전자", "나노", "신경", "알고리즘"]
    for signal in expert_signals:
        if signal in topic:
            score += 2
            reasons.append(f"전문 분야 주제: '{signal}'")

    return {
        "complexity_score": min(10, score),
        "needs_ai_expansion": score >= 3,
        "reasons": reasons,
    }


def ideate_with_ai(topic: str, techniques: Optional[List[str]] = None,
                    count: int = 3, force_ai: bool = False,
                    no_ai: bool = False) -> Dict:
    """
    v2.0 하이브리드 아이디어 생성: 프레임워크 생성 + AI 확장.

    Args:
        topic: 사고 대상 주제
        techniques: 적용할 기법 목록
        count: 기법 수
        force_ai: 강제 AI 확장
        no_ai: AI 확장 비활성화

    Returns:
        프레임워크 + AI 생성 아이디어
    """
    # Step 1: 기존 프레임워크 생성
    framework = ideate(topic, techniques, count)

    if no_ai or not AI_ESCALATION_AVAILABLE:
        framework["mode"] = "framework_only"
        if not AI_ESCALATION_AVAILABLE and not no_ai:
            framework["ai_note"] = "AI 에스컬레이션 모듈을 찾을 수 없습니다."
        return framework

    # Step 2: 주제 복잡도 평가
    complexity = assess_topic_complexity(topic)
    framework["topic_complexity"] = complexity

    if not force_ai and not complexity["needs_ai_expansion"]:
        framework["mode"] = "framework_only"
        framework["ai_decision"] = "주제 복잡도가 낮아 AI 확장 불필요"
        return framework

    # Step 3: AI에게 아이디어 생성 요청
    print(f"[creative-thinking] AI 확장 생성 시작 (복잡도: {complexity['complexity_score']}/10)", file=sys.stderr)

    meta_prompt = framework["meta_prompt"]
    ai_result = escalate_to_ai(
        text=meta_prompt,
        skill_name="creative-thinking",
        regex_result=framework,
        model="gemini",  # 창의적 작업은 Gemini 우선
        role="Idea Generator",
    )

    framework["mode"] = "hybrid"
    framework["ai_expansion"] = {
        "success": ai_result.get("success", False),
        "model": ai_result.get("model", ""),
        "raw_response": ai_result.get("raw", "")[:3000],
    }

    # AI 응답 파싱 시도
    if ai_result.get("parsed"):
        framework["ai_expansion"]["parsed_ideas"] = ai_result["parsed"]
    elif ai_result.get("raw"):
        framework["ai_expansion"]["ideas_text"] = ai_result["raw"][:3000]

    # Step 4: 듀얼 생성 (복잡도 높으면 GPT도 호출)
    if complexity["complexity_score"] >= 7:
        print(f"[creative-thinking] 고복잡도 — GPT 듀얼 생성 추가", file=sys.stderr)
        gpt_result = escalate_to_ai(
            text=meta_prompt,
            skill_name="creative-thinking",
            regex_result=framework,
            model="gpt",
            role="Idea Generator",
        )
        framework["ai_expansion"]["dual_response"] = {
            "success": gpt_result.get("success", False),
            "model": gpt_result.get("model", ""),
            "raw_response": gpt_result.get("raw", "")[:3000],
        }

    return framework


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Creative Thinking Engine v2.0 — 창의적 사고 도구 (AI 확장)")
    parser.add_argument("topic", nargs="?", help="사고 대상 주제")
    parser.add_argument("--techniques", nargs="+",
                        choices=list(THINKING_TECHNIQUES.keys()),
                        help="적용할 기법")
    parser.add_argument("--count", type=int, default=3, help="자동 선택 시 기법 수")
    parser.add_argument("--list", action="store_true", help="사용 가능한 기법 목록")
    parser.add_argument("--json", action="store_true", help="JSON 형식 출력")
    parser.add_argument("--meta-prompt", action="store_true",
                        help="ai-orchestrator용 통합 프롬프트만 출력")
    parser.add_argument("--ai", action="store_true", help="강제 AI 확장 생성")
    parser.add_argument("--no-ai", action="store_true", help="AI 확장 비활성화")
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

    # v2.0: 하이브리드 모드
    result = ideate_with_ai(
        topic=args.topic,
        techniques=args.techniques,
        count=args.count,
        force_ai=args.ai,
        no_ai=args.no_ai,
    )

    if args.meta_prompt:
        print(result["meta_prompt"])
        return

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        mode_label = {"hybrid": "하이브리드 (프레임워크+AI)", "framework_only": "프레임워크 단독"}.get(
            result.get("mode", "framework_only"), "알 수 없음"
        )
        print(f"\n{'='*60}")
        print(f"  창의적 사고 v2.0 — 주제: {result['topic']}")
        print(f"  모드: {mode_label}")
        print(f"  적용 기법: {result['techniques_applied']}종, "
              f"탐색 질문: {result['total_questions']}개")
        print(f"{'='*60}\n")

        for exp in result["explorations"]:
            print(f"  {exp['technique']}")
            print(f"  {exp['description']}\n")
            print(f"  프롬프트: {exp['prompt']}\n")
            print(f"  탐색 질문:")
            for q in exp["exploration_questions"]:
                print(f"    ? {q}")
            print()

        # AI 확장 결과 표시
        if result.get("mode") == "hybrid" and result.get("ai_expansion"):
            ai_exp = result["ai_expansion"]
            print(f"{'─'*60}")
            print(f"[AI 확장 생성 결과]")
            if ai_exp.get("parsed_ideas"):
                for key, value in ai_exp["parsed_ideas"].items():
                    print(f"  {key}:")
                    if isinstance(value, list):
                        for item in value:
                            print(f"    • {item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)}")
                    else:
                        print(f"    {value}")
            elif ai_exp.get("ideas_text"):
                print(f"  {ai_exp['ideas_text'][:1500]}")
            elif ai_exp.get("raw_response"):
                print(f"  {ai_exp['raw_response'][:1500]}")

            if ai_exp.get("dual_response"):
                print(f"\n[GPT 듀얼 생성 결과]")
                dual = ai_exp["dual_response"]
                if dual.get("raw_response"):
                    print(f"  {dual['raw_response'][:1000]}")

        # 복잡도 정보
        if result.get("topic_complexity"):
            tc = result["topic_complexity"]
            print(f"\n[주제 복잡도] {tc['complexity_score']}/10")
            for reason in tc.get("reasons", []):
                print(f"  • {reason}")


if __name__ == "__main__":
    main()
