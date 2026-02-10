#!/usr/bin/env python3
"""
auto_dispatch.py — 능동적 AI 디스패치 엔진

기존 multi_ai_request.py가 "호출되면 작동하는 도구"였다면,
auto_dispatch.py는 "스스로 필요성을 판단하고 최적의 AI를 선택하여 호출하는 에이전트"이다.

핵심 기능:
  1. 작업 맥락 분석: 텍스트의 복잡도, 불확실성, 전문성 요구 수준을 자동 평가
  2. 능동적 모델 선택: 작업 특성에 따라 Gemini/GPT 중 최적 모델 자동 선택
  3. 역할 자동 배정: 작업 유형에 맞는 역할을 자동으로 결정
  4. 파이프라인 자동 구성: 단일 호출 / 교차 검증 / 다단계 분석 자동 결정
  5. 결과 품질 자동 평가: AI 응답의 품질을 평가하고 필요시 재시도

사용법:
  # 자동 판단 모드 (가장 능동적)
  python auto_dispatch.py auto --text "분석할 내용..."

  # 맥락 분석만 (AI 호출 없이 판단만)
  python auto_dispatch.py analyze --text "분석할 내용..."

  # 파이프라인 모드 (다단계 자동 실행)
  python auto_dispatch.py pipeline --text "분석할 내용..." --goal "목표 설명"
"""

import argparse
import json
import os
import sys
import time
from typing import Dict, List, Optional

# 기존 multi_ai_request.py의 함수들 재사용
sys.path.insert(0, os.path.dirname(__file__))
try:
    from multi_ai_request import (
        dispatch_request, cross_verify, save_result,
        MODEL_PROFILES, ROLE_SYSTEM_PROMPTS
    )
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False


# ---------------------------------------------------------------------------
# 작업 맥락 분석 엔진
# ---------------------------------------------------------------------------

# 작업 유형별 신호 (기존 role_advisor.py보다 훨씬 세밀한 분류)
TASK_TYPE_SIGNALS = {
    "factual_verification": {
        "signals": ["사실", "확인", "검증", "맞는지", "정확한지", "출처", "근거", "증거", "데이터"],
        "weight": 3,
        "best_model": "gemini",
        "best_role": "Fact Checker",
        "pipeline": "single_with_verify",
    },
    "causal_reasoning": {
        "signals": ["왜", "원인", "이유", "때문", "결과", "영향", "인과", "상관"],
        "weight": 3,
        "best_model": "gpt",
        "best_role": "Logic Analyzer",
        "pipeline": "cross_verify",
    },
    "creative_generation": {
        "signals": ["아이디어", "창의", "새로운", "혁신", "대안", "발상", "브레인스토밍"],
        "weight": 2,
        "best_model": "gemini",
        "best_role": "Idea Generator",
        "pipeline": "dual_generate",
    },
    "code_implementation": {
        "signals": ["코드", "구현", "프로그래밍", "스크립트", "함수", "클래스", "API", "버그", "디버그"],
        "weight": 3,
        "best_model": "gpt",
        "best_role": "Code Specialist",
        "pipeline": "single_with_verify",
    },
    "deep_analysis": {
        "signals": ["분석", "심층", "깊이", "본질", "근본", "구조", "체계", "프레임워크"],
        "weight": 2,
        "best_model": "gpt",
        "best_role": "Deep Reviewer",
        "pipeline": "cross_verify",
    },
    "research_survey": {
        "signals": ["조사", "연구", "탐색", "동향", "트렌드", "최신", "현황", "비교"],
        "weight": 2,
        "best_model": "gemini",
        "best_role": "Broad Researcher",
        "pipeline": "single",
    },
    "document_writing": {
        "signals": ["작성", "문서", "보고서", "정리", "요약", "글", "논문", "기획"],
        "weight": 2,
        "best_model": "gpt",
        "best_role": "Technical Writer",
        "pipeline": "single_with_verify",
    },
}

# 불확실성 신호
UNCERTAINTY_SIGNALS = [
    {"pattern": "?", "weight": 1},
    {"pattern": "모르겠", "weight": 2},
    {"pattern": "확실하지 않", "weight": 2},
    {"pattern": "아마", "weight": 1},
    {"pattern": "추측", "weight": 2},
    {"pattern": "불확실", "weight": 2},
    {"pattern": "논란", "weight": 2},
    {"pattern": "의견이 분분", "weight": 2},
]

# 복잡도 신호
COMPLEXITY_SIGNALS = [
    {"pattern": "그리고", "weight": 0.5},
    {"pattern": "또한", "weight": 0.5},
    {"pattern": "뿐만 아니라", "weight": 1},
    {"pattern": "한편", "weight": 1},
    {"pattern": "반면", "weight": 1},
    {"pattern": "그러나", "weight": 1},
    {"pattern": "동시에", "weight": 1},
]


def analyze_context(text: str, goal: str = "") -> Dict:
    """
    작업 맥락을 심층 분석하여 AI 호출 전략을 자동 결정.

    Args:
        text: 분석/처리할 텍스트
        goal: 작업 목표 (선택)

    Returns:
        맥락 분석 결과 + 자동 결정된 전략
    """
    combined = f"{goal} {text}".lower()

    # 1. 작업 유형 감지
    type_scores = {}
    for type_key, config in TASK_TYPE_SIGNALS.items():
        score = sum(config["weight"] for signal in config["signals"] if signal in combined)
        if score > 0:
            type_scores[type_key] = score

    # 가장 높은 점수의 작업 유형 선택
    if type_scores:
        primary_type = max(type_scores, key=type_scores.get)
        type_config = TASK_TYPE_SIGNALS[primary_type]
    else:
        primary_type = "general"
        type_config = {
            "best_model": "gemini",
            "best_role": "Broad Researcher",
            "pipeline": "single",
        }

    # 2. 불확실성 수준 평가
    uncertainty_score = sum(
        s["weight"] for s in UNCERTAINTY_SIGNALS if s["pattern"] in combined
    )

    # 3. 복잡도 수준 평가
    complexity_score = sum(
        s["weight"] for s in COMPLEXITY_SIGNALS if s["pattern"] in combined
    )
    # 텍스트 길이 보정
    complexity_score += min(3, len(text) // 500)

    # 4. 전문성 요구 수준 평가
    expertise_level = "low"
    if complexity_score >= 5 or uncertainty_score >= 4:
        expertise_level = "high"
    elif complexity_score >= 3 or uncertainty_score >= 2:
        expertise_level = "medium"

    # 5. AI 필요성 판단
    ai_necessity_score = (
        max(type_scores.values()) if type_scores else 0
    ) + uncertainty_score + complexity_score

    needs_ai = ai_necessity_score >= 3
    needs_cross_verify = uncertainty_score >= 3 or complexity_score >= 4

    # 6. 파이프라인 자동 결정
    if needs_cross_verify:
        pipeline = "cross_verify"
    elif type_config.get("pipeline") == "dual_generate":
        pipeline = "dual_generate"
    elif ai_necessity_score >= 6:
        pipeline = "single_with_verify"
    else:
        pipeline = type_config.get("pipeline", "single")

    return {
        "task_types": type_scores,
        "primary_type": primary_type,
        "uncertainty_score": uncertainty_score,
        "complexity_score": complexity_score,
        "expertise_level": expertise_level,
        "ai_necessity_score": ai_necessity_score,
        "needs_ai": needs_ai,
        "needs_cross_verify": needs_cross_verify,
        "strategy": {
            "model": type_config["best_model"],
            "role": type_config["best_role"],
            "pipeline": pipeline,
            "secondary_model": "gpt" if type_config["best_model"] == "gemini" else "gemini",
        },
    }


# ---------------------------------------------------------------------------
# 파이프라인 실행 엔진
# ---------------------------------------------------------------------------

def execute_auto(text: str, goal: str = "", context_override: Dict = None) -> Dict:
    """
    완전 자동 모드: 맥락 분석 → 전략 결정 → AI 호출 → 결과 반환.

    Args:
        text: 처리할 텍스트
        goal: 작업 목표
        context_override: 맥락 분석 결과 오버라이드 (선택)

    Returns:
        실행 결과
    """
    if not ORCHESTRATOR_AVAILABLE:
        return {"success": False, "error": "multi_ai_request.py를 찾을 수 없습니다."}

    # Step 1: 맥락 분석
    context = context_override or analyze_context(text, goal)

    if not context["needs_ai"]:
        return {
            "success": True,
            "mode": "no_ai_needed",
            "context": context,
            "message": "AI 호출이 불필요한 수준의 작업입니다.",
        }

    strategy = context["strategy"]
    pipeline = strategy["pipeline"]

    print(f"[auto_dispatch] 작업 유형: {context['primary_type']}", file=sys.stderr)
    print(f"[auto_dispatch] 전략: {pipeline} | 모델: {strategy['model']} | 역할: {strategy['role']}", file=sys.stderr)

    # Step 2: 프롬프트 구성
    prompt = text
    if goal:
        prompt = f"목표: {goal}\n\n내용:\n{text}"

    # Step 3: 파이프라인 실행
    results = {"context": context, "pipeline": pipeline, "steps": []}

    if pipeline == "single":
        # 단일 호출
        result = dispatch_request(strategy["model"], strategy["role"], prompt)
        results["steps"].append({"phase": "primary", "result": result})
        results["final_response"] = result.get("response", "")
        results["success"] = result.get("success", False)

    elif pipeline == "single_with_verify":
        # 1차 호출 + 자체 품질 평가
        result = dispatch_request(strategy["model"], strategy["role"], prompt)
        results["steps"].append({"phase": "primary", "result": result})

        if result.get("success"):
            # 품질 평가
            quality = _assess_response_quality(result.get("response", ""), text)
            results["quality_assessment"] = quality

            if quality["score"] < 60:
                # 품질 낮으면 교차 검증
                print(f"[auto_dispatch] 품질 점수 {quality['score']}/100 — 교차 검증 실행", file=sys.stderr)
                verify_result = cross_verify(result, strategy["secondary_model"])
                results["steps"].append({"phase": "cross_verify", "result": verify_result})

            results["final_response"] = result.get("response", "")
            results["success"] = True
        else:
            # 1차 실패 시 대체 모델로 재시도
            print(f"[auto_dispatch] 1차 실패 — {strategy['secondary_model']}로 재시도", file=sys.stderr)
            retry = dispatch_request(strategy["secondary_model"], strategy["role"], prompt)
            results["steps"].append({"phase": "retry", "result": retry})
            results["final_response"] = retry.get("response", "")
            results["success"] = retry.get("success", False)

    elif pipeline == "cross_verify":
        # 1차 호출 + 교차 검증
        result = dispatch_request(strategy["model"], strategy["role"], prompt)
        results["steps"].append({"phase": "primary", "result": result})

        if result.get("success"):
            verify_result = cross_verify(result, strategy["secondary_model"])
            results["steps"].append({"phase": "cross_verify", "result": verify_result})
            results["final_response"] = result.get("response", "")
            results["verification"] = verify_result.get("response", "")
            results["success"] = True
        else:
            results["success"] = False

    elif pipeline == "dual_generate":
        # 양쪽 모델 동시 생성 (창의적 작업용)
        result_a = dispatch_request("gemini", strategy["role"], prompt)
        results["steps"].append({"phase": "gemini_generate", "result": result_a})

        result_b = dispatch_request("gpt", strategy["role"], prompt)
        results["steps"].append({"phase": "gpt_generate", "result": result_b})

        results["gemini_response"] = result_a.get("response", "")
        results["gpt_response"] = result_b.get("response", "")
        results["success"] = result_a.get("success", False) or result_b.get("success", False)

        # 합성 프롬프트 생성
        if result_a.get("success") and result_b.get("success"):
            synthesis_prompt = (
                f"다음 두 AI의 응답을 종합하여 최선의 결과를 만들어주세요.\n\n"
                f"=== Gemini 응답 ===\n{result_a['response'][:2000]}\n\n"
                f"=== GPT 응답 ===\n{result_b['response'][:2000]}\n\n"
                f"두 응답의 장점을 결합하고 약점을 보완하여 통합된 최종 답변을 작성하세요."
            )
            synthesis = dispatch_request("gpt", "Deep Reviewer", synthesis_prompt)
            results["steps"].append({"phase": "synthesis", "result": synthesis})
            results["final_response"] = synthesis.get("response", "")

    results["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return results


def _assess_response_quality(response: str, original_text: str) -> Dict:
    """AI 응답의 품질을 간이 평가."""
    score = 100
    issues = []

    # 길이 검사
    if len(response) < 50:
        score -= 30
        issues.append("응답이 지나치게 짧음")
    elif len(response) < 100:
        score -= 15
        issues.append("응답이 다소 짧음")

    # 원본 대비 관련성 (간이 검사)
    original_words = set(original_text.lower().split())
    response_words = set(response.lower().split())
    overlap = len(original_words & response_words) / max(len(original_words), 1)
    if overlap < 0.05:
        score -= 20
        issues.append("원본과의 관련성이 낮음")

    # 구조 검사
    if "\n" not in response and len(response) > 200:
        score -= 10
        issues.append("구조화되지 않은 응답")

    # 에러 패턴 검사
    error_patterns = ["죄송합니다", "할 수 없습니다", "I cannot", "I'm sorry"]
    for pattern in error_patterns:
        if pattern.lower() in response.lower():
            score -= 25
            issues.append(f"거부/에러 패턴 감지: {pattern}")
            break

    return {
        "score": max(0, score),
        "issues": issues,
        "response_length": len(response),
        "relevance_ratio": round(overlap, 3),
    }


# ---------------------------------------------------------------------------
# CLI 인터페이스
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="auto_dispatch.py — 능동적 AI 디스패치 엔진"
    )
    subparsers = parser.add_subparsers(dest="command", help="명령")

    # auto: 완전 자동 모드
    auto_p = subparsers.add_parser("auto", help="완전 자동 모드 (맥락 분석 → AI 호출)")
    auto_p.add_argument("--text", help="처리할 텍스트")
    auto_p.add_argument("--file", help="처리할 텍스트 파일")
    auto_p.add_argument("--goal", default="", help="작업 목표")
    auto_p.add_argument("--output", help="결과 저장 파일")
    auto_p.add_argument("--json", action="store_true", help="JSON 출력")

    # analyze: 맥락 분석만
    analyze_p = subparsers.add_parser("analyze", help="맥락 분석만 (AI 호출 없음)")
    analyze_p.add_argument("--text", help="분석할 텍스트")
    analyze_p.add_argument("--file", help="분석할 텍스트 파일")
    analyze_p.add_argument("--goal", default="", help="작업 목표")

    # pipeline: 다단계 파이프라인
    pipeline_p = subparsers.add_parser("pipeline", help="다단계 파이프라인 실행")
    pipeline_p.add_argument("--text", help="처리할 텍스트")
    pipeline_p.add_argument("--file", help="처리할 텍스트 파일")
    pipeline_p.add_argument("--goal", default="", help="작업 목표")
    pipeline_p.add_argument("--force-pipeline", choices=["single", "single_with_verify", "cross_verify", "dual_generate"],
                            help="파이프라인 강제 지정")
    pipeline_p.add_argument("--output", help="결과 저장 파일")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 텍스트 입력 처리
    text = ""
    if hasattr(args, "file") and args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    elif hasattr(args, "text") and args.text:
        text = args.text
    else:
        if sys.stdin.isatty():
            print("텍스트를 입력하세요 (Ctrl+D로 종료):")
        text = sys.stdin.read()

    if not text.strip():
        print("텍스트가 비어있습니다.", file=sys.stderr)
        sys.exit(1)

    goal = getattr(args, "goal", "")

    if args.command == "analyze":
        result = analyze_context(text, goal)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "auto":
        result = execute_auto(text, goal)

        if hasattr(args, "output") and args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"결과 저장: {args.output}", file=sys.stderr)

        if hasattr(args, "json") and args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            _print_auto_result(result)

    elif args.command == "pipeline":
        context_override = None
        if hasattr(args, "force_pipeline") and args.force_pipeline:
            context = analyze_context(text, goal)
            context["strategy"]["pipeline"] = args.force_pipeline
            context["needs_ai"] = True
            context_override = context

        result = execute_auto(text, goal, context_override)

        if hasattr(args, "output") and args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

        print(json.dumps(result, ensure_ascii=False, indent=2))


def _print_auto_result(result: Dict):
    """자동 모드 결과를 읽기 좋게 출력."""
    context = result.get("context", {})
    print(f"\n{'='*60}")
    print(f"  능동적 AI 디스패치 결과")
    print(f"{'='*60}")
    print(f"  작업 유형: {context.get('primary_type', 'N/A')}")
    print(f"  복잡도: {context.get('complexity_score', 0)}/10")
    print(f"  불확실성: {context.get('uncertainty_score', 0)}/10")
    print(f"  AI 필요성: {context.get('ai_necessity_score', 0)}")
    print(f"  파이프라인: {result.get('pipeline', 'N/A')}")
    print(f"  성공: {'예' if result.get('success') else '아니오'}")

    if result.get("final_response"):
        print(f"\n{'─'*60}")
        print(f"[최종 응답]")
        print(result["final_response"][:2000])

    if result.get("verification"):
        print(f"\n{'─'*60}")
        print(f"[교차 검증]")
        print(result["verification"][:1000])

    if result.get("quality_assessment"):
        qa = result["quality_assessment"]
        print(f"\n[품질 평가] 점수: {qa['score']}/100")
        for issue in qa.get("issues", []):
            print(f"  • {issue}")

    print(f"\n[실행 단계] {len(result.get('steps', []))}단계")
    for step in result.get("steps", []):
        phase = step.get("phase", "?")
        success = step.get("result", {}).get("success", False)
        model = step.get("result", {}).get("model", "?")
        print(f"  {'✓' if success else '✗'} {phase} ({model})")


if __name__ == "__main__":
    main()
