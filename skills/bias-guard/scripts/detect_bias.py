#!/usr/bin/env python3
"""
Bias Guard — 누스양의 인지 편향 감지 및 보정 도구
12가지 인지 편향을 감지하고 균형 잡힌 관점을 제안한다.

v2.0: AI 에스컬레이션 로직 내장
  - 정규식 1차 분석 후 균형 점수가 임계값 이하이면 자동으로 외부 AI에게 심층 분석 요청
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


# 12가지 인지 편향 패턴
BIAS_PATTERNS = {
    "confirmation_bias": {
        "name": "확증 편향",
        "description": "기존 믿음에 부합하는 정보만 선택적으로 수용",
        "patterns": [
            r"(역시|예상대로|당연히|아니나 다를까)",
            r"(이것은? 증명|이것은? 확인)(한다|된다|했다)",
        ],
        "counter": "반대 증거나 대안적 설명도 적극적으로 탐색하세요.",
        "severity": "high",
    },
    "anchoring_bias": {
        "name": "앵커링 편향",
        "description": "처음 접한 정보에 과도하게 의존",
        "patterns": [
            r"(처음|최초|원래|기본적으로).{0,20}(기준|표준|근거)",
            r"(앞서 언급한|이전에 말한).{0,20}(따라|기반)",
        ],
        "counter": "초기 정보 외에 다양한 기준점을 설정하여 비교하세요.",
        "severity": "medium",
    },
    "availability_bias": {
        "name": "가용성 편향",
        "description": "쉽게 떠오르는 사례에 과도한 비중 부여",
        "patterns": [
            r"(최근에?|요즘|얼마 전).{0,30}(많이|자주|흔히)",
            r"(유명한|잘 알려진|대표적인) 사례",
        ],
        "counter": "쉽게 떠오르는 사례 외에 통계적 데이터나 체계적 조사를 참고하세요.",
        "severity": "medium",
    },
    "dunning_kruger": {
        "name": "더닝-크루거 효과",
        "description": "능력이 부족한 영역에서 과도한 자신감",
        "patterns": [
            r"(간단히|쉽게|단순히).{0,20}(해결|처리|구현)(할 수|가능)",
            r"(어렵지 않|복잡하지 않|문제없)",
        ],
        "counter": "해당 분야의 복잡성과 자신의 전문성 수준을 객관적으로 평가하세요.",
        "severity": "medium",
    },
    "sunk_cost": {
        "name": "매몰 비용 오류",
        "description": "이미 투자한 것 때문에 비합리적 결정 지속",
        "patterns": [
            r"(이미|지금까지|여태).{0,20}(투자|노력|시간).{0,20}(때문|아까|아깝)",
            r"(여기서 포기|여기서 멈추).{0,10}(아깝|낭비)",
        ],
        "counter": "과거 투자와 무관하게, 현재 시점에서의 최선의 선택을 판단하세요.",
        "severity": "high",
    },
    "bandwagon": {
        "name": "편승 효과",
        "description": "다수가 하니까 따라가는 경향",
        "patterns": [
            r"(모두|다들|대부분|많은 사람).{0,20}(하고 있|사용하|선택하)",
            r"(트렌드|유행|대세)(이다|이니|이므로)",
        ],
        "counter": "다수의 선택이 반드시 최선은 아닙니다. 독립적으로 장단점을 평가하세요.",
        "severity": "low",
    },
    "framing_effect": {
        "name": "프레이밍 효과",
        "description": "같은 정보를 어떻게 제시하느냐에 따라 판단이 달라짐",
        "patterns": [
            r"(~만|불과|겨우|단지)\s?\d",
            r"(무려|자그마치|놀랍게도)\s?\d",
        ],
        "counter": "같은 정보를 긍정적/부정적 양쪽 프레임으로 모두 제시하세요.",
        "severity": "medium",
    },
    "status_quo_bias": {
        "name": "현상 유지 편향",
        "description": "변화보다 현재 상태를 선호하는 경향",
        "patterns": [
            r"(기존|현재|지금).{0,15}(유지|그대로|바꿀 필요 없)",
            r"(굳이|새삼|일부러).{0,15}(바꿀|변경할|전환할)",
        ],
        "counter": "현재 방식의 문제점과 변화의 잠재적 이점을 객관적으로 비교하세요.",
        "severity": "low",
    },
    "survivorship_bias": {
        "name": "생존자 편향",
        "description": "성공 사례만 보고 실패 사례를 무시",
        "patterns": [
            r"(성공한|성공적인|잘 된) (사례|기업|사람)",
            r"(~처럼|~와 같이).{0,20}(성공|성장|발전)",
        ],
        "counter": "성공 사례와 함께 실패 사례도 분석하여 균형 잡힌 시각을 유지하세요.",
        "severity": "medium",
    },
    "hindsight_bias": {
        "name": "사후 확신 편향",
        "description": "결과를 알고 나서 예측 가능했다고 착각",
        "patterns": [
            r"(예상할 수 있었|예측 가능했|당연한 결과)",
            r"(돌이켜 보면|결과적으로 보면).{0,20}(당연|필연|불가피)",
        ],
        "counter": "결과를 모르는 시점에서의 불확실성을 인정하세요.",
        "severity": "low",
    },
    "negativity_bias": {
        "name": "부정성 편향",
        "description": "부정적 정보에 과도한 가중치 부여",
        "patterns": [
            r"(위험|위협|문제|결함|단점|약점).{0,10}(크다|심각|중대|치명)",
            r"(실패|손실|피해).{0,10}(막대|엄청|심각)",
        ],
        "counter": "부정적 측면과 함께 긍정적 측면, 기회, 해결 가능성도 함께 제시하세요.",
        "severity": "medium",
    },
    "optimism_bias": {
        "name": "낙관주의 편향",
        "description": "긍정적 결과를 과대평가하고 위험을 과소평가",
        "patterns": [
            r"(분명|반드시|틀림없이).{0,20}(성공|잘 될|해결될)",
            r"(문제없|걱정 없|위험.{0,5}없)",
        ],
        "counter": "잠재적 위험과 최악의 시나리오도 함께 고려하세요.",
        "severity": "medium",
    },
}


def detect_bias(text: str, bias_types: Optional[List[str]] = None) -> Dict:
    """
    텍스트에서 인지 편향을 감지 (정규식 기반 1차 분석).

    Args:
        text: 분석 대상 텍스트
        bias_types: 검사할 편향 유형 (None이면 전체 12종)

    Returns:
        감지 결과 딕셔너리
    """
    if bias_types is None:
        bias_types = list(BIAS_PATTERNS.keys())

    sentences = [s.strip() for s in re.split(r'[.!?。]\s*', text) if s.strip()]
    detections = []

    for bias_key in bias_types:
        if bias_key not in BIAS_PATTERNS:
            continue
        bias = BIAS_PATTERNS[bias_key]

        for sentence in sentences:
            for pattern in bias["patterns"]:
                if re.search(pattern, sentence, re.IGNORECASE):
                    detections.append({
                        "bias_type": bias["name"],
                        "bias_key": bias_key,
                        "description": bias["description"],
                        "severity": bias["severity"],
                        "sentence": sentence[:120],
                        "counter_suggestion": bias["counter"],
                    })
                    break  # 같은 문장에서 같은 편향 중복 방지

    # 편향 유형별 집계
    bias_summary = {}
    for d in detections:
        key = d["bias_type"]
        if key not in bias_summary:
            bias_summary[key] = 0
        bias_summary[key] += 1

    # 균형 점수 (100점 기준)
    penalty = sum(
        {"high": 15, "medium": 8, "low": 4}.get(d["severity"], 4)
        for d in detections
    )
    balance_score = max(0, 100 - penalty)

    return {
        "balance_score": balance_score,
        "detections": detections,
        "bias_summary": bias_summary,
        "statistics": {
            "total_biases": len(detections),
            "unique_types": len(bias_summary),
            "sentences_analyzed": len(sentences),
            "high_severity": sum(1 for d in detections if d["severity"] == "high"),
            "medium_severity": sum(1 for d in detections if d["severity"] == "medium"),
            "low_severity": sum(1 for d in detections if d["severity"] == "low"),
        },
        "top_counters": list(set(d["counter_suggestion"] for d in detections))[:5],
    }


def generate_balanced_view(text: str, detections: List[Dict]) -> str:
    """감지된 편향을 기반으로 균형 잡힌 관점 프롬프트 생성."""
    if not detections:
        return "편향이 감지되지 않았습니다. 현재 텍스트는 균형 잡혀 있습니다."

    unique_biases = set(d["bias_type"] for d in detections)
    counters = set(d["counter_suggestion"] for d in detections)

    prompt = f"다음 텍스트에서 {', '.join(unique_biases)} 편향이 감지되었습니다.\n\n"
    prompt += "균형 잡힌 관점을 위한 제안:\n"
    for i, c in enumerate(counters, 1):
        prompt += f"{i}. {c}\n"

    return prompt


def detect_bias_hybrid(text: str, bias_types: Optional[List[str]] = None,
                       suggest: bool = False, force_escalate: bool = False,
                       no_escalate: bool = False) -> Dict:
    """
    하이브리드 편향 감지: 정규식 1차 → 자동 판단 → AI 심층 분석.

    v2.0의 핵심 함수.

    Args:
        text: 분석 대상 텍스트
        bias_types: 검사할 편향 유형
        suggest: 균형 잡힌 관점 제안 포함 여부
        force_escalate: 강제 AI 에스컬레이션
        no_escalate: AI 에스컬레이션 비활성화

    Returns:
        하이브리드 분석 결과
    """
    # Step 1: 정규식 기반 1차 분석
    regex_result = detect_bias(text, bias_types)

    if suggest:
        regex_result["balanced_view"] = generate_balanced_view(text, regex_result["detections"])

    # AI 에스컬레이션 비활성화 또는 모듈 미설치
    if no_escalate or not AI_ESCALATION_AVAILABLE:
        regex_result["analysis_mode"] = "regex_only"
        if not AI_ESCALATION_AVAILABLE and not no_escalate:
            regex_result["escalation_note"] = "AI 에스컬레이션 모듈을 찾을 수 없습니다."
        return regex_result

    # Step 2: 에스컬레이션 필요 여부 자동 판단
    escalation_decision = should_escalate(
        skill_name="bias-guard",
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
        skill_name="bias-guard",
        regex_result=regex_result,
        model=escalation_decision["recommended_model"],
        role=escalation_decision["recommended_role"],
    )

    # Step 4: 결과 합성
    hybrid_result = merge_results(regex_result, ai_result, "bias-guard")

    # 기존 필드 유지 (하위 호환)
    hybrid_result["balance_score"] = regex_result.get("balance_score", 100)
    hybrid_result["detections"] = regex_result.get("detections", [])
    hybrid_result["bias_summary"] = regex_result.get("bias_summary", {})
    hybrid_result["statistics"] = regex_result.get("statistics", {})
    hybrid_result["top_counters"] = regex_result.get("top_counters", [])

    if suggest and "balanced_view" in regex_result:
        hybrid_result["balanced_view"] = regex_result["balanced_view"]

    return hybrid_result


def main():
    parser = argparse.ArgumentParser(description="Bias Guard v2.0 — 인지 편향 감지 도구 (AI 에스컬레이션 내장)")
    parser.add_argument("-f", "--file", type=str, help="분석할 텍스트 파일")
    parser.add_argument("-t", "--text", type=str, help="분석할 텍스트 직접 입력")
    parser.add_argument("--types", nargs="+", help="검사할 편향 유형 키")
    parser.add_argument("--json", action="store_true", help="JSON 형식 출력")
    parser.add_argument("--suggest", action="store_true", help="균형 잡힌 관점 제안 포함")
    parser.add_argument("--escalate", action="store_true", help="강제 AI 에스컬레이션")
    parser.add_argument("--no-escalate", action="store_true", help="AI 에스컬레이션 비활성화")
    args = parser.parse_args()

    input_text = None
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            input_text = f.read()
    elif args.text:
        input_text = args.text
    else:
        if sys.stdin.isatty():
            print("분석할 텍스트를 입력하세요 (Ctrl+D로 종료):")
        input_text = sys.stdin.read()

    if not input_text or not input_text.strip():
        print("분석할 텍스트가 없습니다.", file=sys.stderr)
        sys.exit(1)

    # v2.0: 하이브리드 분석 실행
    result = detect_bias_hybrid(
        text=input_text,
        bias_types=args.types,
        suggest=args.suggest,
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
        print(f"  편향 감지 결과 — 균형 점수: {result['balance_score']}/100")
        print(f"  분석 모드: {mode_label}")
        print(f"{'='*50}\n")

        if result["detections"]:
            print(f"[정규식 감지 편향] {result['statistics']['total_biases']}건 "
                  f"({result['statistics']['unique_types']}종)")
            for d in result["detections"]:
                icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(d["severity"], "⚪")
                print(f"\n  {icon} {d['bias_type']} ({d['severity']})")
                print(f"     설명: {d['description']}")
                print(f"     문장: \"{d['sentence']}\"")
                print(f"     보정: {d['counter_suggestion']}")
        else:
            print("정규식 기반 편향이 감지되지 않았습니다.")

        # AI 심층 분석 결과 표시
        if result.get("analysis_mode") == "hybrid":
            print(f"\n{'─'*50}")
            print(f"[AI 심층 분석 결과]")
            if result.get("ai_parsed"):
                ai_data = result["ai_parsed"]
                if "hidden_biases" in ai_data:
                    print(f"  숨겨진 편향:")
                    for bias in ai_data["hidden_biases"]:
                        print(f"    • {bias if isinstance(bias, str) else bias.get('description', bias)}")
                if "missing_perspectives" in ai_data:
                    print(f"  누락된 관점:")
                    for persp in ai_data["missing_perspectives"]:
                        print(f"    • {persp if isinstance(persp, str) else persp.get('perspective', persp)}")
                if "rewrite_suggestions" in ai_data:
                    print(f"  수정 제안:")
                    for sug in ai_data["rewrite_suggestions"]:
                        print(f"    → {sug if isinstance(sug, str) else sug.get('suggestion', sug)}")
            elif result.get("ai_raw"):
                print(f"  {result['ai_raw'][:500]}")
            elif result.get("ai_error"):
                print(f"  ⚠ AI 호출 실패: {result['ai_error']}")

        # 에스컬레이션 판단 근거
        if result.get("escalation_decision"):
            decision = result["escalation_decision"]
            status = "실행됨" if decision["should"] else "불필요"
            print(f"\n[에스컬레이션 판단] {status}")
            for reason in decision["reasons"]:
                print(f"  • {reason}")

        if args.suggest and "balanced_view" in result:
            print(f"\n{'─'*50}")
            print(result["balanced_view"])


if __name__ == "__main__":
    main()
