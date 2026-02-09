#!/usr/bin/env python3
"""
Self-Reflection Engine — 누스양의 자기 성찰 도구
자신의 출력을 다차원으로 검토하고 개선점을 도출한다.
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Optional


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
    텍스트에 대해 다차원 자기 성찰을 수행.

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


def main():
    parser = argparse.ArgumentParser(description="Self-Reflection Engine — 자기 성찰 도구")
    parser.add_argument("-f", "--file", type=str, help="성찰할 텍스트 파일 경로")
    parser.add_argument("-t", "--text", type=str, help="성찰할 텍스트 직접 입력")
    parser.add_argument("--dimensions", nargs="+", help="검사할 차원 (completeness consistency depth honesty empathy)")
    parser.add_argument("--deep", action="store_true", help="소크라테스식 심층 성찰 모드")
    parser.add_argument("--json", action="store_true", help="JSON 형식 출력")
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

    if args.deep:
        result = reflect_with_questions(input_text)
    else:
        result = reflect_on_text(input_text, args.dimensions)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*50}")
        print(f"  자기 성찰 결과 — 종합 점수: {result['overall_score']}/100")
        print(f"{'='*50}\n")

        print("[차원별 점수]")
        for dim, score in result["dimension_scores"].items():
            bar = "█" * (score // 10) + "░" * (10 - score // 10)
            print(f"  {dim:8s} {bar} {score}")
        print()

        if result["findings"]:
            print(f"[발견된 이슈] {result['summary']['total_issues']}건")
            for f in result["findings"]:
                icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(f["severity"], "⚪")
                print(f"  {icon} [{f['dimension']}] {f['issue']}")
                print(f"     → \"{f['sentence']}\"")
            print()

        print("[개선 제안]")
        for i, s in enumerate(result["suggestions"], 1):
            print(f"  {i}. {s}")

        if args.deep and "self_questions" in result:
            print(f"\n[소크라테스식 자기 질문]")
            for q in result["self_questions"]:
                print(f"  ? {q['q']}")


if __name__ == "__main__":
    main()
