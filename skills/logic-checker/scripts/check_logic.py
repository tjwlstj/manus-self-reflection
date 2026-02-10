#!/usr/bin/env python3
"""
Manus 스킬 시스템용 논리 오류 감지기 (Logic Checker)
- 5가지 논리적 오류 패턴 감지: 순환논증, 허수아비 논증, 거짓 이분법, 성급한 일반화, 권위에의 호소
- CLI 및 함수 호출 모두 지원

v2.0: AI 에스컬레이션 로직 내장
  - 정규식 1차 분석 후 오류가 임계값 이상이면 자동으로 외부 AI에게 심층 분석 요청
  - --escalate 옵션으로 강제 AI 분석 가능
  - --no-escalate 옵션으로 정규식만 사용 가능
"""

import argparse
import json
import os
import re
import sys
from typing import List, Dict, Optional

# AI 에스컬레이션 모듈 임포트
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
try:
    from ai_escalation import should_escalate, escalate_to_ai, merge_results
    AI_ESCALATION_AVAILABLE = True
except ImportError:
    AI_ESCALATION_AVAILABLE = False


def split_sentences(text: str) -> List[str]:
    """텍스트를 문장 단위로 분리."""
    sentences = re.split(r'(?<=[.?!。])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def check_circular_reasoning(sentences: List[str]) -> List[Dict[str, str]]:
    """순환논증 감지: 결론이 전제를 반복하는 패턴."""
    results = []
    patterns_kr = [
        r'(.{4,20})(이기 때문에|이므로|이라서).*\1',
        r'(.{4,20})(는|은) (.{4,20})(이다|다)\. .*\3.*(이기 때문에|이므로)',
    ]
    for sentence in sentences:
        for pattern in patterns_kr:
            if re.search(pattern, sentence):
                results.append({
                    "error_type": "순환논증 (Circular Reasoning)",
                    "sentence": sentence.strip(),
                    "severity": "high",
                    "suggestion": "논증의 근거가 주장의 반복인지 확인하고, 독립적인 증거를 제시하세요."
                })
                break
    return results


def check_strawman(sentences: List[str]) -> List[Dict[str, str]]:
    """허수아비 논증 감지: 상대 주장을 왜곡하여 공격하는 패턴."""
    results = []
    strawman_indicators = [
        r'그들은.*라고 하지만',
        r'사람들은.*라고 주장하지만',
        r'일부는.*라고 하지만',
        r'.*의 주장은.*과도하',
        r'.*의 논점.*왜곡',
    ]
    for sentence in sentences:
        for pattern in strawman_indicators:
            if re.search(pattern, sentence):
                results.append({
                    "error_type": "허수아비 논증 (Straw Man)",
                    "sentence": sentence.strip(),
                    "severity": "medium",
                    "suggestion": "상대 주장을 정확히 이해하고 원래 논점에 대해 반박하세요."
                })
                break
    return results


def check_false_dichotomy(sentences: List[str]) -> List[Dict[str, str]]:
    """거짓 이분법 감지: 양자택일만 제시하는 패턴."""
    results = []
    patterns = [
        r'둘 중 하나(이다|다)',
        r'반드시 .+ 아니면',
        r'.+ 아니면 .+ 뿐이다',
        r'무조건 .+ 아니면',
        r'오로지 .+ 아니면',
        r'.+(이거나|하거나) .+(뿐이다|밖에 없다)',
    ]
    for sentence in sentences:
        for pattern in patterns:
            if re.search(pattern, sentence):
                results.append({
                    "error_type": "거짓 이분법 (False Dichotomy)",
                    "sentence": sentence.strip(),
                    "severity": "medium",
                    "suggestion": "더 다양한 가능성을 고려하고, 양자택일이 아닌 대안을 탐색하세요."
                })
                break
    return results


def check_hasty_generalization(sentences: List[str]) -> List[Dict[str, str]]:
    """성급한 일반화 감지: 불충분한 근거로 보편적 주장을 하는 패턴."""
    results = []
    quantifiers = [r'항상', r'전부', r'모두', r'절대', r'늘', r'언제나', r'전적으로']
    for sentence in sentences:
        for q in quantifiers:
            pattern = rf'{q}\s*.*(이다|하다|한다|있다|없다|좋다|나쁘다|된다|않다)'
            if re.search(pattern, sentence):
                results.append({
                    "error_type": "성급한 일반화 (Hasty Generalization)",
                    "sentence": sentence.strip(),
                    "severity": "high",
                    "suggestion": "충분한 근거 없이 일반화하지 말고 구체적 사례와 예외를 함께 제시하세요."
                })
                break
    return results


def check_appeal_to_authority(sentences: List[str]) -> List[Dict[str, str]]:
    """권위에의 호소 감지: 권위자 언급만으로 주장을 정당화하는 패턴."""
    results = []
    patterns = [
        r'(전문가|권위자|교수|과학자|박사|연구원)가 말하',
        r'(전문가|권위자|교수|과학자|박사|연구원)에 따르면',
        r'(논문|연구 결과|보고서|통계)에 따르면',
    ]
    for sentence in sentences:
        for pattern in patterns:
            if re.search(pattern, sentence):
                results.append({
                    "error_type": "권위에의 호소 (Appeal to Authority)",
                    "sentence": sentence.strip(),
                    "severity": "low",
                    "suggestion": "권위자의 전문성과 근거의 적절성을 확인하고, 독립적 증거도 함께 제시하세요."
                })
                break
    return results


def check_logic(text: str) -> Dict[str, object]:
    """
    논리 오류 감지 메인 함수 (정규식 기반 1차 분석).

    Args:
        text: 분석 대상 텍스트

    Returns:
        dict with keys: errors (유형별 오류 리스트), summary (통계), input_text
    """
    sentences = split_sentences(text)

    checkers = {
        "순환논증": check_circular_reasoning,
        "허수아비 논증": check_strawman,
        "거짓 이분법": check_false_dichotomy,
        "성급한 일반화": check_hasty_generalization,
        "권위에의 호소": check_appeal_to_authority,
    }

    errors = {}
    total_count = 0
    for name, func in checkers.items():
        found = func(sentences)
        errors[name] = found
        total_count += len(found)

    return {
        "errors": errors,
        "summary": {
            "total_errors": total_count,
            "sentences_analyzed": len(sentences),
            "error_types_found": [k for k, v in errors.items() if v],
        },
        "input_text": text[:200] + "..." if len(text) > 200 else text,
    }


def check_logic_hybrid(text: str, force_escalate: bool = False,
                        no_escalate: bool = False) -> Dict:
    """
    하이브리드 논리 검사: 정규식 1차 → 자동 판단 → AI 심층 분석.

    v2.0의 핵심 함수.

    Args:
        text: 분석 대상 텍스트
        force_escalate: 강제 AI 에스컬레이션
        no_escalate: AI 에스컬레이션 비활성화

    Returns:
        하이브리드 분석 결과
    """
    # Step 1: 정규식 기반 1차 분석
    regex_result = check_logic(text)

    # AI 에스컬레이션 비활성화 또는 모듈 미설치
    if no_escalate or not AI_ESCALATION_AVAILABLE:
        regex_result["analysis_mode"] = "regex_only"
        if not AI_ESCALATION_AVAILABLE and not no_escalate:
            regex_result["escalation_note"] = "AI 에스컬레이션 모듈을 찾을 수 없습니다."
        return regex_result

    # Step 2: 에스컬레이션 필요 여부 자동 판단
    escalation_decision = should_escalate(
        skill_name="logic-checker",
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
        skill_name="logic-checker",
        regex_result=regex_result,
        model=escalation_decision["recommended_model"],
        role=escalation_decision["recommended_role"],
    )

    # Step 4: 결과 합성
    hybrid_result = merge_results(regex_result, ai_result, "logic-checker")

    # 기존 필드 유지 (하위 호환)
    hybrid_result["errors"] = regex_result.get("errors", {})
    hybrid_result["summary"] = regex_result.get("summary", {})
    hybrid_result["input_text"] = regex_result.get("input_text", "")

    return hybrid_result


def main() -> None:
    """CLI 진입점."""
    parser = argparse.ArgumentParser(description="논리 오류 감지기 v2.0 (Logic Checker, AI 에스컬레이션 내장)")
    parser.add_argument("-f", "--file", type=str, help="분석할 텍스트 파일 경로")
    parser.add_argument("-t", "--text", type=str, help="직접 입력할 텍스트")
    parser.add_argument("--json", action="store_true", help="JSON 형식으로 출력")
    parser.add_argument("--escalate", action="store_true", help="강제 AI 에스컬레이션")
    parser.add_argument("--no-escalate", action="store_true", help="AI 에스컬레이션 비활성화")
    args = parser.parse_args()

    input_text: Optional[str] = None

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                input_text = f.read()
        except Exception as e:
            print(f"파일 읽기 오류: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        input_text = args.text
    else:
        if sys.stdin.isatty():
            print("분석할 텍스트를 입력하세요 (Ctrl+D로 종료):")
        input_text = sys.stdin.read()

    if not input_text or not input_text.strip():
        print("분석할 텍스트가 제공되지 않았습니다.", file=sys.stderr)
        sys.exit(1)

    # v2.0: 하이브리드 분석 실행
    result = check_logic_hybrid(
        text=input_text,
        force_escalate=args.escalate,
        no_escalate=args.no_escalate,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        mode_label = {"hybrid": "하이브리드 (정규식+AI)", "regex_only": "정규식 단독"}.get(
            result.get("analysis_mode", "regex_only"), "알 수 없음"
        )
        print(f"\n분석 완료: {result['summary']['sentences_analyzed']}개 문장, "
              f"{result['summary']['total_errors']}건 오류 감지")
        print(f"분석 모드: {mode_label}\n")

        for error_type, errors in result["errors"].items():
            if errors:
                print(f"[{error_type}] {len(errors)}건:")
                for i, err in enumerate(errors, 1):
                    print(f"  {i}. 문장: {err['sentence']}")
                    print(f"     심각도: {err['severity']}")
                    print(f"     제안: {err['suggestion']}")
                print()
        if result["summary"]["total_errors"] == 0:
            print("정규식 기반 논리 오류가 감지되지 않았습니다.")

        # AI 심층 분석 결과 표시
        if result.get("analysis_mode") == "hybrid":
            print(f"\n{'─'*50}")
            print(f"[AI 심층 분석 결과]")
            if result.get("ai_parsed"):
                ai_data = result["ai_parsed"]
                if "additional_errors" in ai_data:
                    print(f"  추가 발견 오류:")
                    for err in ai_data["additional_errors"]:
                        print(f"    • {err if isinstance(err, str) else err.get('error', err)}")
                if "hidden_assumptions" in ai_data:
                    print(f"  숨겨진 전제:")
                    for assumption in ai_data["hidden_assumptions"]:
                        print(f"    • {assumption if isinstance(assumption, str) else assumption.get('assumption', assumption)}")
                if "correction_suggestions" in ai_data:
                    print(f"  수정 제안:")
                    for sug in ai_data["correction_suggestions"]:
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


if __name__ == "__main__":
    main()
