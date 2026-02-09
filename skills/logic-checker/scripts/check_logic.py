#!/usr/bin/env python3
"""
Manus 스킬 시스템용 논리 오류 감지기 (Logic Checker)
- 5가지 논리적 오류 패턴 감지: 순환논증, 허수아비 논증, 거짓 이분법, 성급한 일반화, 권위에의 호소
- CLI 및 함수 호출 모두 지원
"""

import argparse
import json
import re
import sys
from typing import List, Dict, Optional


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
    논리 오류 감지 메인 함수.

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


def main() -> None:
    """CLI 진입점."""
    parser = argparse.ArgumentParser(description="논리 오류 감지기 (Logic Checker)")
    parser.add_argument("-f", "--file", type=str, help="분석할 텍스트 파일 경로")
    parser.add_argument("-t", "--text", type=str, help="직접 입력할 텍스트")
    parser.add_argument("--json", action="store_true", help="JSON 형식으로 출력")
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

    result = check_logic(input_text)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n분석 완료: {result['summary']['sentences_analyzed']}개 문장, "
              f"{result['summary']['total_errors']}건 오류 감지\n")
        for error_type, errors in result["errors"].items():
            if errors:
                print(f"[{error_type}] {len(errors)}건:")
                for i, err in enumerate(errors, 1):
                    print(f"  {i}. 문장: {err['sentence']}")
                    print(f"     심각도: {err['severity']}")
                    print(f"     제안: {err['suggestion']}")
                print()
        if result["summary"]["total_errors"] == 0:
            print("논리 오류가 감지되지 않았습니다.")


if __name__ == "__main__":
    main()
