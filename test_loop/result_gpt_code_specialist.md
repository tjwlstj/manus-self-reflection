# Code Specialist (gpt)

**Model**: gpt-4.1-mini  
**Timestamp**: 2026-02-09T15:14:58Z  

---

```python
#!/usr/bin/env python3
# check_logic.py

import argparse
import re
import sys
from typing import List, Dict, Optional


def check_circular_reasoning(sentences: List[str]) -> List[Dict[str, str]]:
    """
    Detect circular reasoning patterns.
    Circular reasoning often repeats the claim as evidence or uses synonyms in a circle.

    Pattern examples:
    - "X is true because X is true."
    - "A because B, B because A."
    """
    results = []
    # Simple heuristic: sentence containing a phrase like "because [same phrase]"
    # or repeated phrase in a single sentence.
    for sentence in sentences:
        lowered = sentence.lower()
        # Check simple pattern: X because X
        match = re.search(r'([a-z\s]{3,30}) because \1', lowered)
        if match:
            results.append({
                "error_type": "순환논증 (Circular Reasoning)",
                "sentence": sentence.strip(),
                "severity": "high",
                "suggestion": "논증의 근거가 주장의 반복인지 확인하고, 독립적인 증거를 제시하세요."
            })
            continue

        # Check if sentence contains "A because B" and B sentence contains "because A"
        # (cross sentence detection)
        # Skipped due to complexity for heuristic, but can be expanded.
    return results


def check_strawman(sentences: List[str]) -> List[Dict[str, str]]:
    """
    Detect straw man fallacy patterns.
    Typically involves misrepresenting someone's argument and attacking the distorted version.

    Patterns:
    - Phrases that indicate distortion such as "people say X, but...", "some claim X, however..."
    - Followed by an exaggerated/oversimplified argument counter.

    We'll look heuristically for phrases like "그들은 ~라고 하지만", "사람들은 ~라 주장하지만" + presence of words like "거짓", "왜곡"
    """
    results = []
    strawman_indicators = [
        r'그들은.*라고 하지만',
        r'사람들은.*라고 주장하지만',
        r'일부는.*라고 하지만',
        r'그 주장은.*과도하다',
        r'그 논점은.*왜곡',
        r'그것은.*틀리다',
    ]
    for sentence in sentences:
        for pattern in strawman_indicators:
            if re.search(pattern, sentence):
                results.append({
                    "error_type": "허수아비 논증 (Straw Man)",
                    "sentence": sentence.strip(),
                    "severity": "medium",
                    "suggestion": "상대 주장을 정확히 이해하고 정직하게 반박하세요."
                })
                break

    return results


def check_false_dichotomy(sentences: List[str]) -> List[Dict[str, str]]:
    """
    Detect false dichotomy (거짓 이분법) patterns.
    Often expressed as "either ... or ...", ignoring other options.

    Look for sequences like 'either ... or ...' or 'A or B, no other option'.

    Korean equivalents:
    - '둘 중 하나다', 'A 아니면 B 뿐이다', '반드시 A 아니면 B', 'A 아니면 B'
    """
    results = []
    false_dichotomy_patterns = [
        r'둘 중 하나(이다|다)',
        r'반드시 .* 아니면 .*',
        r'(?:A|B) 아니면 (?:B|A) 뿐이다',
        r'.* 아니면 .* 뿐이다',
        r'무조건 .* 아니면 .*',
        r'오로지 .* 아니면 .*',
    ]
    for sentence in sentences:
        for pattern in false_dichotomy_patterns:
            if re.search(pattern, sentence):
                results.append({
                    "error_type": "거짓 이분법 (False Dichotomy)",
                    "sentence": sentence.strip(),
                    "severity": "medium",
                    "suggestion": "더 다양한 가능성을 고려하고, 양자택일이 아니도록 논리를 확장하세요."
                })
                break

    return results


def check_hasty_generalization(sentences: List[str]) -> List[Dict[str, str]]:
    """
    Detect hasty generalization (성급한 일반화).
    Often presented with words like '항상', '전부', '모두', '절대', '늘' implying an unwarranted universal statement.

    Example:
    - "모든 X는 Y다" but with insufficient evidence.

    We'll look for universal quantifiers combined with absolutes.
    """
    results = []
    universal_quantifiers = [
        r'항상',
        r'전부',
        r'모두',
        r'절대',
        r'늘',
        r'언제나',
        r'전적으로',
        r'완전히',
    ]
    # If statement contains universal quantifiers with sweeping predicates, flag.
    for sentence in sentences:
        for quantifier in universal_quantifiers:
            # Look for quantifier combined with a strong claim (verb/adjective)
            pattern = rf'{quantifier} .* (이다|하다|한다|있다|없다|좋다|나쁘다)'
            if re.search(pattern, sentence):
                results.append({
                    "error_type": "성급한 일반화 (Hasty Generalization)",
                    "sentence": sentence.strip(),
                    "severity": "high",
                    "suggestion": "충분한 근거 없이 일반화하지 말고 구체적 사례를 제시하세요."
                })
                break
    return results


def check_appeal_to_authority(sentences: List[str]) -> List[Dict[str, str]]:
    """
    Detect appeal to authority (권위에의 호소).
    Often involves citing authority figures as sole evidence.

    Look for patterns:
    - "전문가가 말하기를", "권위자는", "교수가", "과학자가", "연구 결과에 따르면"
    - Especially when followed by no additional evidence.
    """
    results = []
    authority_indicators = [
        r'(전문가|권위자|교수|과학자|박사|연구원|논문|연구 결과|보고서|통계)가 말하기를',
        r'(전문가|권위자|교수|과학자|박사|연구원|논문|연구 결과|보고서|통계)에 따르면',
        r'~했다고 한다',
    ]
    for sentence in sentences:
        for pattern in authority_indicators:
            if re.search(pattern, sentence):
                results.append({
                    "error_type": "권위에의 호소 (Appeal to Authority)",
                    "sentence": sentence.strip(),
                    "severity": "low",
                    "suggestion": "권위자의 의견 외에도 구체적이고 객관적인 근거를 제시하세요."
                })
                break
    return results


def split_sentences(text: str) -> List[str]:
    """
    간단한 문장 분리 함수.
    마침표, 물음표, 느낌표 기준으로 분리하되, 과도한 분리 막음.

    Args:
        text (str): 분석할 텍스트

    Returns:
        List[str]: 문장 리스트
    """
    # 한국어 문장 끝에 흔히 사용되는 종료 문자 기준 분리
    # 단 축약어 등 예외는 간단한 heuristic으로 무시
    sentences = re.split(r'(?<=[.?!])\s+', text.strip())
    # 만약 문장 끝에 마침표 없으면 그대로
    if len(sentences) == 1:
        # 문장 끝에 마침표 붙여서 다시 시도
        sentences = re.split(r'(?<=[.?!])\s+', text.strip() + ".")
    return [s.strip() for s in sentences if s.strip()]


def check_logic(text: str) -> Dict[str, List[Dict[str, str]]]:
    """
    논리 오류 감지기 메인 함수.
    입력 텍스트 내 문장별로 5가지 논리 오류 종류를 검사하여 감지 결과를 반환.

    Args:
        text (str): 분석 대상 텍스트

    Returns:
        dict: 검출된 오류 유형별 리스트 포함 딕셔너리
        {
            "순환논증": [...],
            "허수아비 논증": [...],
            "거짓 이분법": [...],
            "성급한 일반화": [...],
            "권위에의 호소": [...],
        }
        각 리스트 아이템은 dict 형태:
        {
            "error_type": str,
            "sentence": str,
            "severity": "low"|"medium"|"high",
            "suggestion": str
        }
    """
    sentences = split_sentences(text)
    result: Dict[str, List[Dict[str, str]]] = {
        "순환논증": [],
        "허수아비 논증": [],
        "거짓 이분법": [],
        "성급한 일반화": [],
        "권위에의 호소": [],
    }

    circular = check_circular_reasoning(sentences)
    strawman = check_strawman(sentences)
    false_dichotomy = check_false_dichotomy(sentences)
    hasty_gen = check_hasty_generalization(sentences)
    appeal_authority = check_appeal_to_authority(sentences)

    # 분류별로 결과 넣기
    for item in circular:
        result["순환논증"].append(item)
    for item in strawman:
        result["허수아비 논증"].append(item)
    for item in false_dichotomy:
        result["거짓 이분법"].append(item)
    for item in hasty_gen:
        result["성급한 일반화"].append(item)
    for item in appeal_authority:
        result["권위에의 호소"].append(item)

    return result


def main() -> None:
    """
    Command-line interface entry point.

    Parses arguments, reads input text from file or stdin, performs logic check,
    and prints the results formatted.
    """
    parser = argparse.ArgumentParser(
        description="Manus 스킬 시스템용 논리 오류 감지기 (Logic Checker)"
    )
    parser.add_argument(
        "-f", "--file", type=str, help="분석할 텍스트 파일 경로"
    )
    parser.add_argument(
        "-t", "--text", type=str, help="직접 입력할 텍스트 (따옴표로 감싸기)"
    )
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
        # stdin에서 읽기 (pipe 또는 직접 입력)
        if sys.stdin.isatty():
            print("분석할 텍스트를 입력하세요 (Ctrl+D로 종료):")
        try:
            input_text = sys.stdin.read()
        except Exception as e:
            print(f"입력 읽기 오류: {e}", file=sys.stderr)
            sys.exit(1)
    if not input_text or input_text.strip() == "":
        print("분석할 텍스트가 제공되지 않았습니다.", file=sys.stderr)
        sys.exit(1)

    results = check_logic(input_text)

    has_error = False
    for error_type, errors in results.items():
        if len(errors) > 0:
            has_error = True
            print(f"\n[{error_type}] 발견된 오류 {len(errors)}건:")
            for i, err in enumerate(errors, start=1):
                print(f"{i}. 문장: {err['sentence']}")
                print(f"   심각도: {err['severity']}")
                print(f"   제안: {err['suggestion']}")
    if not has_error:
        print("논리 오류가 감지되지 않았습니다.")


if __name__ == "__main__":
    main()
```

---

### 설명

- **`check_logic(text: str) -> dict`**: 텍스트를 문장 단위로 나누고, 각 논리 오류 탐지 함수들을 호출하여 결과를 모은 뒤 오류 유형별로 딕셔너리에 담아 반환합니다.
- 문장 분리는 한국어 텍스트의 특성을 고려해 간단히 마침표, 물음표, 느낌표 뒤로 분리합니다.
- 5가지 오류 탐지 함수 모두 문장 리스트를 받아 정규식 기반 휴리스틱으로 탐지합니다.
- 각 함수는 발견된 오류별로 오류 종류, 문장, 심각도, 수정 제안을 반환하도록 설계했습니다.
- CLI 파서는 `-f` (파일 입력), `-t` (직접 텍스트 입력), 또는 파이프를 통한 표준 입력을 지원합니다.
- UTF-8 인코딩을 기본으로 하며, 에러 처리도 포함했습니다.
- 타입 힌트와 docstring을 모두 포함해 가독성과 유지보수를 고려했습니다.

필요 시 탐지 로직과 정규식은 더욱 정교하게 개선할 수 있습니다.
