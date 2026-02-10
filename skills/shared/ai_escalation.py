#!/usr/bin/env python3
"""
AI Escalation Module — 누스양 스킬트리 공통 모듈
기반 계층 스킬이 정규식 분석 후 외부 AI에게 심층 분석을 능동적으로 요청하는 인터페이스.

설계 원칙:
  1. 임계값 기반 자동 판단: 정규식 점수가 낮으면 자동으로 AI 호출
  2. 맥락 인식 에스컬레이션: 작업의 복잡도/불확실성을 감지하여 AI 필요성 판단
  3. 하이브리드 결과 합성: 정규식 결과 + AI 결과를 통합하여 최종 출력 생성

사용법:
  from shared.ai_escalation import should_escalate, escalate_to_ai, merge_results
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Any

# ---------------------------------------------------------------------------
# 에스컬레이션 임계값 설정
# ---------------------------------------------------------------------------

ESCALATION_THRESHOLDS = {
    "self-reflection": {
        "score_threshold": 70,       # 종합 점수 70 이하면 AI 에스컬레이션
        "high_issue_threshold": 1,   # high severity 이슈 1개 이상이면 에스컬레이션
        "default_model": "gemini",
        "default_role": "Deep Reviewer",
    },
    "bias-guard": {
        "score_threshold": 75,       # 균형 점수 75 이하면 AI 에스컬레이션
        "high_issue_threshold": 2,   # high severity 편향 2개 이상이면 에스컬레이션
        "default_model": "gpt",
        "default_role": "Logic Analyzer",
    },
    "logic-checker": {
        "score_threshold": None,     # 점수 기반 아님
        "error_threshold": 2,        # 오류 2건 이상이면 AI 에스컬레이션
        "default_model": "gemini",
        "default_role": "Fact Checker",
    },
}

# ---------------------------------------------------------------------------
# 맥락 기반 복잡도 감지
# ---------------------------------------------------------------------------

COMPLEXITY_SIGNALS = [
    {"pattern": "?", "weight": 1, "reason": "질문형 — 사실 검증 필요 가능성"},
    {"pattern": "왜", "weight": 2, "reason": "인과 추론 요구"},
    {"pattern": "어떻게", "weight": 2, "reason": "방법론 추론 요구"},
    {"pattern": "원인", "weight": 2, "reason": "근본 원인 분석 요구"},
    {"pattern": "증명", "weight": 3, "reason": "논증 검증 필요"},
    {"pattern": "반드시", "weight": 1, "reason": "강한 주장 — 검증 필요"},
    {"pattern": "확실히", "weight": 1, "reason": "과도한 확신 — 검증 필요"},
]


def assess_complexity(text: str) -> Dict:
    """
    텍스트의 복잡도와 불확실성을 평가하여 AI 에스컬레이션 필요성을 판단.

    Returns:
        complexity_score: 0~10 (높을수록 AI 필요성 높음)
        signals: 감지된 복잡도 신호 목록
        needs_ai: AI 에스컬레이션 권장 여부
    """
    text_lower = text.lower() if text else ""
    detected_signals = []
    total_weight = 0

    for signal in COMPLEXITY_SIGNALS:
        if signal["pattern"] in text_lower:
            detected_signals.append(signal)
            total_weight += signal["weight"]

    # 텍스트 길이 기반 보정 (긴 텍스트 = 더 복잡할 가능성)
    length_bonus = min(3, len(text) // 500)
    total_weight += length_bonus

    complexity_score = min(10, total_weight)

    return {
        "complexity_score": complexity_score,
        "signals": detected_signals,
        "length_bonus": length_bonus,
        "needs_ai": complexity_score >= 4,
    }


# ---------------------------------------------------------------------------
# 에스컬레이션 판단 함수
# ---------------------------------------------------------------------------

def should_escalate(skill_name: str, regex_result: Dict,
                    original_text: str = "", force: bool = False) -> Dict:
    """
    정규식 분석 결과를 기반으로 AI 에스컬레이션 필요 여부를 판단.

    Args:
        skill_name: 호출 스킬 이름 ("self-reflection", "bias-guard", "logic-checker")
        regex_result: 정규식 기반 분석 결과 딕셔너리
        original_text: 원본 텍스트 (복잡도 분석용)
        force: True이면 무조건 에스컬레이션

    Returns:
        should: 에스컬레이션 여부
        reasons: 에스컬레이션 이유 목록
        recommended_model: 추천 AI 모델
        recommended_role: 추천 역할
    """
    if force:
        config = ESCALATION_THRESHOLDS.get(skill_name, {})
        return {
            "should": True,
            "reasons": ["강제 에스컬레이션 요청"],
            "recommended_model": config.get("default_model", "gemini"),
            "recommended_role": config.get("default_role", "Deep Reviewer"),
        }

    config = ESCALATION_THRESHOLDS.get(skill_name)
    if not config:
        return {"should": False, "reasons": ["알 수 없는 스킬"], "recommended_model": None, "recommended_role": None}

    reasons = []

    # 1. 점수 기반 판단
    score_threshold = config.get("score_threshold")
    if score_threshold is not None:
        # self-reflection: overall_score, bias-guard: balance_score
        score_key = "overall_score" if skill_name == "self-reflection" else "balance_score"
        current_score = regex_result.get(score_key, 100)
        if current_score < score_threshold:
            reasons.append(f"점수 {current_score} < 임계값 {score_threshold}")

    # 2. 심각도 기반 판단
    high_threshold = config.get("high_issue_threshold")
    if high_threshold is not None:
        high_count = 0
        # self-reflection
        if "summary" in regex_result:
            high_count = regex_result["summary"].get("high_severity", 0)
        # bias-guard
        elif "statistics" in regex_result:
            high_count = regex_result["statistics"].get("high_severity", 0)
        if high_count >= high_threshold:
            reasons.append(f"심각한 이슈 {high_count}건 >= 임계값 {high_threshold}")

    # 3. 오류 수 기반 판단 (logic-checker)
    error_threshold = config.get("error_threshold")
    if error_threshold is not None:
        total_errors = 0
        if "summary" in regex_result:
            total_errors = regex_result["summary"].get("total_errors", 0)
        if total_errors >= error_threshold:
            reasons.append(f"논리 오류 {total_errors}건 >= 임계값 {error_threshold}")

    # 4. 맥락 복잡도 기반 판단
    if original_text:
        complexity = assess_complexity(original_text)
        if complexity["needs_ai"]:
            reasons.append(f"복잡도 점수 {complexity['complexity_score']}/10 — AI 분석 권장")

    return {
        "should": len(reasons) > 0,
        "reasons": reasons if reasons else ["에스컬레이션 불필요 — 정규식 분석으로 충분"],
        "recommended_model": config.get("default_model", "gemini"),
        "recommended_role": config.get("default_role", "Deep Reviewer"),
    }


# ---------------------------------------------------------------------------
# AI 호출 함수
# ---------------------------------------------------------------------------

def escalate_to_ai(text: str, skill_name: str, regex_result: Dict,
                   model: str = None, role: str = None) -> Dict:
    """
    외부 AI에게 심층 분석을 요청.

    Args:
        text: 분석 대상 원본 텍스트
        skill_name: 호출 스킬 이름
        regex_result: 정규식 1차 분석 결과
        model: AI 모델 ("gemini" 또는 "gpt"), None이면 자동 선택
        role: 역할, None이면 자동 선택

    Returns:
        AI 분석 결과 딕셔너리
    """
    config = ESCALATION_THRESHOLDS.get(skill_name, {})
    model = model or config.get("default_model", "gemini")
    role = role or config.get("default_role", "Deep Reviewer")

    # 스킬별 맞춤 프롬프트 생성
    prompt = _build_escalation_prompt(text, skill_name, regex_result)

    # AI 호출
    try:
        if model == "gemini":
            result = _call_gemini(prompt, role)
        elif model == "gpt":
            result = _call_gpt(prompt, role)
        else:
            return {"success": False, "error": f"Unknown model: {model}"}

        result["escalation_context"] = {
            "skill": skill_name,
            "model": model,
            "role": role,
            "trigger": "auto_escalation",
        }
        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "escalation_context": {
                "skill": skill_name,
                "model": model,
                "role": role,
                "trigger": "auto_escalation",
            }
        }


def _build_escalation_prompt(text: str, skill_name: str, regex_result: Dict) -> str:
    """스킬별 맞춤 에스컬레이션 프롬프트 생성."""

    if skill_name == "self-reflection":
        findings_summary = ""
        for f in regex_result.get("findings", []):
            findings_summary += f"- [{f['dimension']}] {f['issue']} (심각도: {f['severity']})\n"

        return (
            f"다음 텍스트에 대한 자기 성찰 1차 분석 결과, 종합 점수가 "
            f"{regex_result.get('overall_score', 'N/A')}/100으로 나왔습니다.\n\n"
            f"1차 감지된 이슈:\n{findings_summary}\n"
            f"원본 텍스트:\n---\n{text[:3000]}\n---\n\n"
            f"위 1차 분석이 놓쳤을 수 있는 문제점을 심층 분석해주세요. 특히:\n"
            f"1. 정규식이 감지하지 못한 미묘한 일관성 문제\n"
            f"2. 텍스트의 논리적 깊이와 본질 접근 여부\n"
            f"3. 숨겨진 가정이나 불확실한 주장\n"
            f"4. 구체적인 개선 제안 (코드나 수정문 포함)\n\n"
            f"JSON 형식으로 응답해주세요: "
            f'{{"additional_issues": [...], "deep_suggestions": [...], "revised_score": N}}'
        )

    elif skill_name == "bias-guard":
        detections_summary = ""
        for d in regex_result.get("detections", []):
            detections_summary += f"- {d['bias_type']}: \"{d['sentence'][:80]}\"\n"

        return (
            f"다음 텍스트에 대한 인지 편향 1차 분석 결과, 균형 점수가 "
            f"{regex_result.get('balance_score', 'N/A')}/100으로 나왔습니다.\n\n"
            f"1차 감지된 편향:\n{detections_summary}\n"
            f"원본 텍스트:\n---\n{text[:3000]}\n---\n\n"
            f"위 1차 분석이 놓쳤을 수 있는 인지 편향을 심층 분석해주세요. 특히:\n"
            f"1. 정규식 패턴으로 감지 불가능한 구조적 편향\n"
            f"2. 전체 논조에 깔린 암묵적 편향\n"
            f"3. 누락된 관점이나 대안적 시각\n"
            f"4. 균형 잡힌 관점으로의 구체적 수정 제안\n\n"
            f"JSON 형식으로 응답해주세요: "
            f'{{"hidden_biases": [...], "missing_perspectives": [...], "rewrite_suggestions": [...]}}'
        )

    elif skill_name == "logic-checker":
        errors_summary = ""
        for error_type, errors in regex_result.get("errors", {}).items():
            for e in errors:
                errors_summary += f"- [{error_type}] \"{e['sentence'][:80]}\"\n"

        return (
            f"다음 텍스트에 대한 논리 오류 1차 분석 결과, "
            f"{regex_result.get('summary', {}).get('total_errors', 0)}건의 오류가 감지되었습니다.\n\n"
            f"1차 감지된 오류:\n{errors_summary}\n"
            f"원본 텍스트:\n---\n{text[:3000]}\n---\n\n"
            f"위 1차 분석이 놓쳤을 수 있는 논리적 오류를 심층 분석해주세요. 특히:\n"
            f"1. 정규식으로 감지 불가능한 순환논증, 허수아비 논증\n"
            f"2. 숨겨진 전제나 비약적 추론\n"
            f"3. 인과관계 오류나 상관관계-인과관계 혼동\n"
            f"4. 각 오류에 대한 구체적 수정 제안\n\n"
            f"JSON 형식으로 응답해주세요: "
            f'{{"additional_errors": [...], "hidden_assumptions": [...], "correction_suggestions": [...]}}'
        )

    return f"다음 텍스트를 심층 분석해주세요:\n\n{text[:3000]}"


# ---------------------------------------------------------------------------
# AI API 호출 래퍼
# ---------------------------------------------------------------------------

ROLE_SYSTEM_PROMPTS = {
    "Deep Reviewer": (
        "You are a deep review specialist. Critically examine the provided content "
        "for completeness, accuracy, logical consistency, and practical applicability. "
        "Provide specific, actionable feedback with concrete suggestions. "
        "Always respond in Korean."
    ),
    "Logic Analyzer": (
        "You are a logic and reasoning specialist. Analyze arguments for logical "
        "consistency, identify fallacies, evaluate the strength of evidence, "
        "and suggest improvements to reasoning chains. Be precise and systematic. "
        "Always respond in Korean."
    ),
    "Fact Checker": (
        "You are a meticulous fact-checker. Verify claims against known facts, "
        "identify potential inaccuracies, flag unsupported assertions, and "
        "suggest corrections with reasoning. Be specific about what is verified "
        "and what remains uncertain. Always respond in Korean."
    ),
    "Bias Analyst": (
        "You are a cognitive bias specialist. Identify subtle biases in text that "
        "pattern matching cannot detect, including structural biases, implicit assumptions, "
        "and missing perspectives. Provide balanced alternative viewpoints. "
        "Always respond in Korean."
    ),
}


def _call_gemini(prompt: str, role: str = "Deep Reviewer") -> Dict:
    """Gemini API 호출."""
    try:
        from google import genai
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        system_prompt = ROLE_SYSTEM_PROMPTS.get(role, "")
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
        )

        return {
            "success": True,
            "model": "gemini-2.5-flash",
            "provider": "gemini",
            "role": role,
            "response": response.text,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    except Exception as e:
        return {
            "success": False,
            "model": "gemini-2.5-flash",
            "provider": "gemini",
            "role": role,
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


def _call_gpt(prompt: str, role: str = "Deep Reviewer") -> Dict:
    """GPT API 호출."""
    try:
        from openai import OpenAI
        client = OpenAI()

        system_prompt = ROLE_SYSTEM_PROMPTS.get(role, "")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
        )

        return {
            "success": True,
            "model": "gpt-4.1-mini",
            "provider": "gpt",
            "role": role,
            "response": response.choices[0].message.content,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    except Exception as e:
        return {
            "success": False,
            "model": "gpt-4.1-mini",
            "provider": "gpt",
            "role": role,
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


# ---------------------------------------------------------------------------
# 결과 합성 함수
# ---------------------------------------------------------------------------

def merge_results(regex_result: Dict, ai_result: Dict, skill_name: str) -> Dict:
    """
    정규식 결과와 AI 결과를 통합하여 최종 하이브리드 결과 생성.

    Args:
        regex_result: 정규식 기반 1차 분석 결과
        ai_result: AI 심층 분석 결과
        skill_name: 스킬 이름

    Returns:
        통합된 최종 결과
    """
    merged = {
        "analysis_mode": "hybrid" if ai_result.get("success") else "regex_only",
        "regex_result": regex_result,
        "ai_result": ai_result if ai_result.get("success") else None,
        "ai_error": ai_result.get("error") if not ai_result.get("success") else None,
    }

    # AI 응답 파싱 시도
    if ai_result.get("success") and ai_result.get("response"):
        try:
            # JSON 블록 추출 시도
            response_text = ai_result["response"]
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                ai_parsed = json.loads(response_text[json_start:json_end])
                merged["ai_parsed"] = ai_parsed
            else:
                merged["ai_raw"] = response_text
        except (json.JSONDecodeError, ValueError):
            merged["ai_raw"] = ai_result["response"]

    # 스킬별 점수 보정
    if skill_name == "self-reflection" and "ai_parsed" in merged:
        revised = merged["ai_parsed"].get("revised_score")
        if revised is not None:
            original = regex_result.get("overall_score", 100)
            merged["final_score"] = round((original + revised) / 2, 1)
        else:
            merged["final_score"] = regex_result.get("overall_score", 100)
    elif skill_name == "bias-guard":
        merged["final_score"] = regex_result.get("balance_score", 100)
    elif skill_name == "logic-checker":
        merged["final_score"] = None  # 점수 기반 아님

    merged["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    return merged
