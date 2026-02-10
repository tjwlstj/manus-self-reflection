#!/usr/bin/env python3
"""
Self-Reflection Engine — 누스양의 자기 성찰 도구
자신의 출력을 다차원으로 검토하고 개선점을 도출한다.

v2.0: AI 에스컬레이션 로직 내장
  - 정규식 1차 분석 후 점수가 임계값 이하이면 자동으로 외부 AI에게 심층 분석 요청
  - --escalate 옵션으로 강제 AI 분석 가능
  - --no-escalate 옵션으로 정규식만 사용 가능
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional

# AI 에스컬레이션 모듈 임포트
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
try:
    from ai_escalation import should_escalate, escalate_to_ai, merge_results
    AI_ESCALATION_AVAILABLE = True
except ImportError:
    AI_ESCALATION_AVAILABLE = False


# 성찰 차원 정의
REFLECTION_DIMENSIONS = {
    "completeness": {
        "name": "완전성",
        "description": "요청된 모든 요소를 빠짐없이 다루었는가",
        "checks": [
            {"pattern": r"(TODO|FIXME|미완성|추후|나중에)", "issue": "미완성 항목 존재", "severity": "high"},
            {"pattern": r"(생략|skip|제외)", "issue": "의도적 생략 감지", "severity": "medium"},
        ]
    },
    "consistency": {
        "name": "일관성",
        "description": "내부적으로 모순되는 주장이 없는가",
        "checks": [
            {"pattern": r"(하지만 앞서|그러나 위에서|반면에 이전)", "issue": "자기 모순 가능성", "severity": "high"},
            {"pattern": r"(항상.*때때로|모두.*일부|절대.*가끔)", "issue": "양립 불가 한정사 충돌", "severity": "medium"},
        ]
    },
    "depth": {
        "name": "깊이",
        "description": "표면적 답변을 넘어 본질에 접근했는가",
        "checks": [
            {"pattern": r"^.{0,50}$", "issue": "지나치게 짧은 응답", "severity": "medium"},
            {"pattern": r"(일반적으로|보통|대체로)\s", "issue": "구체성 부족 — 일반론에 머무름", "severity": "low"},
        ]
    },
    "honesty": {
        "name": "정직성",
        "description": "불확실한 것을 확실하다고 표현하지 않았는가",
        "checks": [
            {"pattern": r"(확실히|분명히|틀림없이|반드시)\s.*(?!것 같|수 있|추정)", "issue": "과도한 확신 표현", "severity": "medium"},
            {"pattern": r"(사실|실제로|명백히)\s", "issue": "단정적 표현 — 근거 확인 필요", "severity": "low"},
        ]
    },
    "empathy": {
        "name": "공감성",
        "description": "사용자의 맥락과 감정을 고려했는가",
        "checks": [
            {"pattern": r"(당연히|말할 것도 없이|누구나 알듯)", "issue": "사용자 관점 무시 가능성", "severity": "low"},
        ]
    },
}


def reflect_on_text(text: str, dimensions: Optional[List[str]] = None) -> Dict:
    """
    텍스트에 대해 다차원 자기 성찰을 수행 (정규식 기반 1차 분석).

    Args:
        text: 성찰 대상 텍스트 (자신의 출력)
        dimensions: 검사할 차원 목록 (None이면 전체)

    Returns:
        성찰 결과 딕셔너리
    """
    if dimensions is None:
        dimensions = list(REFLECTION_DIMENSIONS.keys())

    sentences = [s.strip() for s in re.split(r'[.!?。]\s*', text) if s.strip()]
    findings = []
    dimension_scores = {}

    for dim_key in dimensions:
        if dim_key not in REFLECTION_DIMENSIONS:
            continue
        dim = REFLECTION_DIMENSIONS[dim_key]
        dim_findings = []

        for check in dim["checks"]:
            for sentence in sentences:
                if re.search(check["pattern"], sentence, re.IGNORECASE):
                    dim_findings.append({
                        "dimension": dim["name"],
                        "issue": check["issue"],
                        "severity": check["severity"],
                        "sentence": sentence[:100],
                    })

        # 점수 계산 (100점 기준, 발견된 이슈마다 감점)
        penalty = sum(
            {"high": 20, "medium": 10, "low": 5}.get(f["severity"], 5)
            for f in dim_findings
        )
        score = max(0, 100 - penalty)
        dimension_scores[dim["name"]] = score
        findings.extend(dim_findings)

    # 종합 점수
    avg_score = sum(dimension_scores.values()) / len(dimension_scores) if dimension_scores else 100

    # 개선 제안 생성
    suggestions = generate_suggestions(findings)

    return {
        "overall_score": round(avg_score, 1),
        "dimension_scores": dimension_scores,
        "findings": findings,
        "suggestions": suggestions,
        "summary": {
            "total_issues": len(findings),
            "high_severity": sum(1 for f in findings if f["severity"] == "high"),
            "medium_severity": sum(1 for f in findings if f["severity"] == "medium"),
            "low_severity": sum(1 for f in findings if f["severity"] == "low"),
            "sentences_analyzed": len(sentences),
        }
    }


def generate_suggestions(findings: List[Dict]) -> List[str]:
    """발견된 이슈를 기반으로 개선 제안 생성."""
    suggestions = []
    issue_types = set(f["issue"] for f in findings)

    suggestion_map = {
        "미완성 항목 존재": "미완성 항목을 완료하거나, 의도적 제외라면 그 이유를 명시하세요.",
        "의도적 생략 감지": "생략된 부분이 사용자 요청에 포함되었는지 확인하세요.",
        "자기 모순 가능성": "앞뒤 문맥을 재검토하여 논리적 일관성을 확보하세요.",
        "양립 불가 한정사 충돌": "한정사(항상/모두/절대 등)의 사용이 정확한지 재검토하세요.",
        "지나치게 짧은 응답": "더 구체적인 설명이나 예시를 추가하여 깊이를 높이세요.",
        "구체성 부족 — 일반론에 머무름": "구체적인 데이터, 사례, 수치를 포함하세요.",
        "과도한 확신 표현": "'~일 수 있다', '~로 추정된다' 등 불확실성을 반영하는 표현을 고려하세요.",
        "단정적 표현 — 근거 확인 필요": "출처나 근거를 함께 제시하세요.",
        "사용자 관점 무시 가능성": "사용자의 배경지식 수준을 고려하여 설명 수준을 조정하세요.",
    }

    for issue in issue_types:
        if issue in suggestion_map:
            suggestions.append(suggestion_map[issue])

    if not suggestions:
        suggestions.append("현재 출력은 전반적으로 양호합니다. 지속적인 자기 성찰을 유지하세요.")

    return suggestions


def reflect_with_questions(text: str) -> Dict:
    """
    소크라테스식 자기 질문을 통한 심층 성찰.
    """
    questions = [
        {"q": "이 답변이 사용자의 진짜 의도를 파악했는가?", "dimension": "empathy"},
        {"q": "내가 확실히 아는 것과 추측하는 것을 구분했는가?", "dimension": "honesty"},
        {"q": "다른 관점에서 보면 이 답변이 어떻게 보일까?", "dimension": "consistency"},
        {"q": "빠뜨린 중요한 정보가 있는가?", "dimension": "completeness"},
        {"q": "이 답변은 표면적인가, 본질적인가?", "dimension": "depth"},
    ]

    result = reflect_on_text(text)
    result["self_questions"] = questions
    return result


def reflect_hybrid(text: str, dimensions: Optional[List[str]] = None,
                   deep: bool = False, force_escalate: bool = False,
                   no_escalate: bool = False) -> Dict:
    """
    하이브리드 성찰: 정규식 1차 → 자동 판단 → AI 심층 분석.

    이것이 v2.0의 핵심 함수입니다.

    Args:
        text: 성찰 대상 텍스트
        dimensions: 검사할 차원 목록
        deep: 소크라테스식 심층 모드
        force_escalate: 강제 AI 에스컬레이션
        no_escalate: AI 에스컬레이션 비활성화

    Returns:
        하이브리드 성찰 결과
    """
    # Step 1: 정규식 기반 1차 분석
    if deep:
        regex_result = reflect_with_questions(text)
    else:
        regex_result = reflect_on_text(text, dimensions)

    # AI 에스컬레이션 비활성화 또는 모듈 미설치
    if no_escalate or not AI_ESCALATION_AVAILABLE:
        regex_result["analysis_mode"] = "regex_only"
        if not AI_ESCALATION_AVAILABLE and not no_escalate:
            regex_result["escalation_note"] = "AI 에스컬레이션 모듈을 찾을 수 없습니다."
        return regex_result

    # Step 2: 에스컬레이션 필요 여부 자동 판단
    escalation_decision = should_escalate(
        skill_name="self-reflection",
        regex_result=regex_result,
        original_text=text,
        force=force_escalate,
    )

    regex_result["escalation_decision"] = escalation_decision

    if not escalation_decision["should"]:
        regex_result["analysis_mode"] = "regex_only"
        return regex_result

    # Step 3: AI 심층 분석 요청
    print(f"[AI 에스컬레이션] {', '.join(escalation_decision['reasons'])}", file=sys.stderr)
    print(f"[AI 에스컬레이션] {escalation_decision['recommended_model']}/{escalation_decision['recommended_role']}에게 심층 분석 요청 중...", file=sys.stderr)

    ai_result = escalate_to_ai(
        text=text,
        skill_name="self-reflection",
        regex_result=regex_result,
        model=escalation_decision["recommended_model"],
        role=escalation_decision["recommended_role"],
    )

    # Step 4: 결과 합성
    hybrid_result = merge_results(regex_result, ai_result, "self-reflection")

    # 기존 정규식 결과의 주요 필드를 최상위에 유지 (하위 호환)
    hybrid_result["overall_score"] = hybrid_result.get("final_score", regex_result.get("overall_score", 100))
    hybrid_result["dimension_scores"] = regex_result.get("dimension_scores", {})
    hybrid_result["findings"] = regex_result.get("findings", [])
    hybrid_result["suggestions"] = regex_result.get("suggestions", [])
    hybrid_result["summary"] = regex_result.get("summary", {})

    if deep and "self_questions" in regex_result:
        hybrid_result["self_questions"] = regex_result["self_questions"]

    return hybrid_result


def main():
    parser = argparse.ArgumentParser(description="Self-Reflection Engine v2.0 — 자기 성찰 도구 (AI 에스컬레이션 내장)")
    parser.add_argument("-f", "--file", type=str, help="성찰할 텍스트 파일 경로")
    parser.add_argument("-t", "--text", type=str, help="성찰할 텍스트 직접 입력")
    parser.add_argument("--dimensions", nargs="+", help="검사할 차원 (completeness consistency depth honesty empathy)")
    parser.add_argument("--deep", action="store_true", help="소크라테스식 심층 성찰 모드")
    parser.add_argument("--json", action="store_true", help="JSON 형식 출력")
    parser.add_argument("--escalate", action="store_true", help="강제 AI 에스컬레이션 (항상 외부 AI 호출)")
    parser.add_argument("--no-escalate", action="store_true", help="AI 에스컬레이션 비활성화 (정규식만 사용)")
    args = parser.parse_args()

    input_text = None
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            input_text = f.read()
    elif args.text:
        input_text = args.text
    else:
        if sys.stdin.isatty():
            print("성찰할 텍스트를 입력하세요 (Ctrl+D로 종료):")
        input_text = sys.stdin.read()

    if not input_text or not input_text.strip():
        print("성찰할 텍스트가 없습니다.", file=sys.stderr)
        sys.exit(1)

    # v2.0: 하이브리드 성찰 실행
    result = reflect_hybrid(
        text=input_text,
        dimensions=args.dimensions,
        deep=args.deep,
        force_escalate=args.escalate,
        no_escalate=args.no_escalate,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        mode_label = {"hybrid": "하이브리드 (정규식+AI)", "regex_only": "정규식 단독"}.get(
            result.get("analysis_mode", "regex_only"), "알 수 없음"
        )
        print(f"\n{'='*50}")
        print(f"  자기 성찰 결과 — 종합 점수: {result.get('overall_score', 'N/A')}/100")
        print(f"  분석 모드: {mode_label}")
        print(f"{'='*50}\n")

        print("[차원별 점수]")
        for dim, score in result.get("dimension_scores", {}).items():
            bar = "█" * (score // 10) + "░" * (10 - score // 10)
            print(f"  {dim:8s} {bar} {score}")
        print()

        if result.get("findings"):
            print(f"[정규식 감지 이슈] {result['summary']['total_issues']}건")
            for f in result["findings"]:
                icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(f["severity"], "⚪")
                print(f"  {icon} [{f['dimension']}] {f['issue']}")
                print(f"     → \"{f['sentence']}\"")
            print()

        # AI 심층 분석 결과 표시
        if result.get("analysis_mode") == "hybrid":
            print(f"[AI 심층 분석 결과]")
            if result.get("ai_parsed"):
                ai_data = result["ai_parsed"]
                if "additional_issues" in ai_data:
                    print(f"  추가 발견 이슈:")
                    for issue in ai_data["additional_issues"]:
                        if isinstance(issue, dict):
                            print(f"    • {issue.get('issue', issue)}")
                        else:
                            print(f"    • {issue}")
                if "deep_suggestions" in ai_data:
                    print(f"  심층 개선 제안:")
                    for sug in ai_data["deep_suggestions"]:
                        if isinstance(sug, dict):
                            print(f"    → {sug.get('suggestion', sug)}")
                        else:
                            print(f"    → {sug}")
            elif result.get("ai_raw"):
                print(f"  {result['ai_raw'][:500]}")
            elif result.get("ai_error"):
                print(f"  ⚠ AI 호출 실패: {result['ai_error']}")
            print()

        # 에스컬레이션 판단 근거 표시
        if result.get("escalation_decision"):
            decision = result["escalation_decision"]
            status = "실행됨" if decision["should"] else "불필요"
            print(f"[에스컬레이션 판단] {status}")
            for reason in decision["reasons"]:
                print(f"  • {reason}")
            print()

        print("[개선 제안]")
        for i, s in enumerate(result.get("suggestions", []), 1):
            print(f"  {i}. {s}")

        if result.get("self_questions"):
            print(f"\n[소크라테스식 자기 질문]")
            for q in result["self_questions"]:
                print(f"  ? {q['q']}")


if __name__ == "__main__":
    main()
