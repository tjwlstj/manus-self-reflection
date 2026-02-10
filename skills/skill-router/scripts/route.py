#!/usr/bin/env python3
"""
Skill Router v2.0 — 누스양의 자율 라우팅 엔진 (능동적 AI 연계 강화)

v1.0과의 차이점:
  1. 맥락 기반 능동 라우팅: 키워드 매칭을 넘어 작업의 복잡도/불확실성을 감지
  2. AI 에스컬레이션 자동 삽입: 기반 스킬 결과가 임계값 이하이면 ai-orchestrator를 파이프라인에 자동 삽입
  3. auto_dispatch 연계: ai-orchestrator의 새 auto_dispatch.py와 직접 연동
  4. 적응형 파이프라인: 실행 중 결과에 따라 파이프라인을 동적으로 조정
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional


# 스킬 트리 레지스트리 (v2.0: AI 에스컬레이션 정보 추가)
SKILL_REGISTRY = {
    "ai-orchestrator": {
        "name": "AI Orchestrator",
        "description": "다중 AI(Gemini, GPT) 역할 분배 및 교차 검증",
        "triggers": ["조사", "연구", "코드", "구현", "검증", "API", "AI", "분석", "비교"],
        "capabilities": ["research", "code_generation", "cross_verify", "deep_analysis"],
        "layer": "core",
        "depends_on": [],
        "ai_escalation": True,  # v2.0: 이 스킬 자체가 AI 에스컬레이션 대상
        "scripts": {
            "main": "/home/ubuntu/skills/ai-orchestrator/scripts/multi_ai_request.py",
            "advisor": "/home/ubuntu/skills/ai-orchestrator/scripts/role_advisor.py",
            "auto": "/home/ubuntu/skills/ai-orchestrator/scripts/auto_dispatch.py",  # v2.0
        }
    },
    "logic-checker": {
        "name": "Logic Checker",
        "description": "논리적 오류 5종 감지 (v2.0: AI 에스컬레이션 내장)",
        "triggers": ["논리", "오류", "추론", "논증", "모순", "타당"],
        "capabilities": ["fallacy_detection", "argument_analysis"],
        "layer": "base",
        "depends_on": [],
        "ai_escalation": True,  # v2.0: 임계값 초과 시 자동 AI 호출
        "escalation_threshold": {"error_count": 2},
        "scripts": {
            "main": "/home/ubuntu/skills/logic-checker/scripts/check_logic.py",
        }
    },
    "self-reflection": {
        "name": "Self-Reflection",
        "description": "5차원 자기 성찰 (v2.0: AI 에스컬레이션 내장)",
        "triggers": ["검토", "성찰", "리뷰", "품질", "개선", "자기", "돌아보"],
        "capabilities": ["self_review", "quality_check", "improvement_suggestion"],
        "layer": "base",
        "depends_on": [],
        "ai_escalation": True,  # v2.0: 점수 70 이하 시 자동 AI 호출
        "escalation_threshold": {"score": 70},
        "scripts": {
            "main": "/home/ubuntu/skills/self-reflection/scripts/reflect.py",
        }
    },
    "bias-guard": {
        "name": "Bias Guard",
        "description": "12종 인지 편향 감지 (v2.0: AI 에스컬레이션 내장)",
        "triggers": ["편향", "균형", "객관", "공정", "편견", "치우", "한쪽"],
        "capabilities": ["bias_detection", "balanced_perspective", "debiasing"],
        "layer": "base",
        "depends_on": [],
        "ai_escalation": True,  # v2.0: 점수 75 이하 시 자동 AI 호출
        "escalation_threshold": {"score": 75},
        "scripts": {
            "main": "/home/ubuntu/skills/bias-guard/scripts/detect_bias.py",
        }
    },
    "creative-thinking": {
        "name": "Creative Thinking",
        "description": "6가지 창의적 사고 기법 (v2.0: AI 확장 생성 지원)",
        "triggers": ["창의", "아이디어", "브레인스토밍", "새로운", "혁신", "발상", "관점"],
        "capabilities": ["ideation", "perspective_shift", "creative_exploration"],
        "layer": "extension",
        "depends_on": [],
        "ai_escalation": True,  # v2.0: meta_prompt를 auto_dispatch로 전달 가능
        "scripts": {
            "main": "/home/ubuntu/skills/creative-thinking/scripts/ideate.py",
        }
    },
    "memory-manager": {
        "name": "Memory Manager",
        "description": "경험 축적, 검색, 학습 기록 (v2.0: AI 기반 유사 경험 검색)",
        "triggers": ["기억", "경험", "학습", "기록", "저장", "이전에", "과거"],
        "capabilities": ["memory_store", "memory_search", "experience_recall"],
        "layer": "extension",
        "depends_on": [],
        "ai_escalation": False,
        "scripts": {
            "main": "/home/ubuntu/skills/memory-manager/scripts/memory.py",
        }
    },
}

# 파이프라인 패턴 (v2.0: AI 에스컬레이션 옵션 추가)
PIPELINE_PATTERNS = {
    "deep_analysis": {
        "name": "심층 분석 체인",
        "description": "조사 → 논리 검증 → 편향 보정 → 자기 성찰",
        "triggers": ["심층", "철저", "깊이", "종합"],
        "pipeline": ["ai-orchestrator", "logic-checker", "bias-guard", "self-reflection"],
        "ai_mode": "always",  # v2.0: 항상 AI 사용
    },
    "creative_solve": {
        "name": "창의적 문제 해결",
        "description": "창의적 발상 → AI 검증 → 경험 저장",
        "triggers": ["창의적 해결", "새로운 방법", "혁신적"],
        "pipeline": ["creative-thinking", "ai-orchestrator", "memory-manager"],
        "ai_mode": "always",
    },
    "self_improve": {
        "name": "자기 개선 루프",
        "description": "자기 성찰 → 편향 감지 → 논리 검증 → 학습 기록",
        "triggers": ["개선", "발전", "성장", "반성"],
        "pipeline": ["self-reflection", "bias-guard", "logic-checker", "memory-manager"],
        "ai_mode": "adaptive",  # v2.0: 결과에 따라 AI 삽입
    },
    "quality_gate": {
        "name": "품질 관문",
        "description": "논리 검증 + 편향 감지 + 자기 성찰 (병렬)",
        "triggers": ["품질", "검수", "확인", "최종"],
        "pipeline": ["logic-checker", "bias-guard", "self-reflection"],
        "ai_mode": "adaptive",
    },
    "research_create": {
        "name": "조사 → 창작",
        "description": "AI 조사 → 창의적 확장 → 품질 검증",
        "triggers": ["조사 후", "연구 기반", "근거 있는"],
        "pipeline": ["ai-orchestrator", "creative-thinking", "self-reflection"],
        "ai_mode": "always",
    },
}


# ---------------------------------------------------------------------------
# v2.0: 맥락 기반 능동 라우팅 엔진
# ---------------------------------------------------------------------------

# 복잡도/불확실성 신호 (키워드 매칭을 넘어선 맥락 분석)
CONTEXT_SIGNALS = {
    "high_complexity": {
        "patterns": [
            r"(그리고|또한|뿐만 아니라|한편|반면|동시에|더불어)",
            r"(복잡|다층적|다면적|종합적|체계적)",
            r"(여러|다양한|다수의|복수의)\s*(관점|요소|측면|변수)",
        ],
        "weight": 2,
    },
    "high_uncertainty": {
        "patterns": [
            r"(모르겠|확실하지 않|불확실|논란|의견이 분분)",
            r"(아마|추측|가능성|~일 수도|~일지도)",
            r"\?",  # 질문형
        ],
        "weight": 2,
    },
    "causal_reasoning": {
        "patterns": [
            r"(왜|원인|이유|때문|결과|영향|인과)",
            r"(어떻게|방법|과정|메커니즘|원리)",
        ],
        "weight": 3,
    },
    "factual_claim": {
        "patterns": [
            r"(사실|실제로|확실히|분명히|틀림없이)",
            r"(항상|모두|절대|전부|언제나)",
            r"\d+%|\d+명|\d+건",  # 수치 포함
        ],
        "weight": 2,
    },
    "emotional_content": {
        "patterns": [
            r"(걱정|불안|두려|화남|슬프|기쁘|행복)",
            r"(힘들|어렵|고민|갈등|딜레마)",
        ],
        "weight": 1,
    },
}


def analyze_context(text: str) -> Dict:
    """
    텍스트의 맥락을 분석하여 복잡도, 불확실성, AI 필요성을 평가.

    Returns:
        context_score: 0~20 (높을수록 AI 필요성 높음)
        detected_signals: 감지된 맥락 신호
        needs_ai_boost: AI 에스컬레이션 권장 여부
    """
    text_lower = text.lower()
    detected = {}
    total_score = 0

    for signal_key, config in CONTEXT_SIGNALS.items():
        matches = []
        for pattern in config["patterns"]:
            found = re.findall(pattern, text_lower)
            if found:
                matches.extend(found if isinstance(found[0], str) else [m[0] for m in found])
        if matches:
            detected[signal_key] = {
                "matches": matches[:5],
                "count": len(matches),
                "weight": config["weight"],
            }
            total_score += config["weight"] * min(3, len(matches))

    # 텍스트 길이 보정
    length_bonus = min(3, len(text) // 500)
    total_score += length_bonus

    return {
        "context_score": min(20, total_score),
        "detected_signals": detected,
        "length_bonus": length_bonus,
        "needs_ai_boost": total_score >= 6,
        "ai_urgency": "high" if total_score >= 10 else "medium" if total_score >= 6 else "low",
    }


def analyze_task_v2(task_description: str, context_text: str = "") -> Dict:
    """
    v2.0 작업 분석: 키워드 매칭 + 맥락 기반 능동 라우팅.

    Args:
        task_description: 작업 설명
        context_text: 추가 맥락 텍스트 (분석 대상 원본 등)

    Returns:
        라우팅 결과 (v2.0 확장)
    """
    task_lower = task_description.lower()

    # 1. 기존 키워드 매칭 (v1.0 호환)
    skill_scores = {}
    for skill_key, skill in SKILL_REGISTRY.items():
        score = 0
        matched_triggers = []
        for trigger in skill["triggers"]:
            if trigger in task_lower:
                score += 1
                matched_triggers.append(trigger)
        if score > 0:
            skill_scores[skill_key] = {
                "score": score,
                "matched_triggers": matched_triggers,
                "skill": skill,
            }

    # 2. 파이프라인 패턴 매칭
    pipeline_scores = {}
    for pattern_key, pattern in PIPELINE_PATTERNS.items():
        score = 0
        for trigger in pattern["triggers"]:
            if trigger in task_lower:
                score += 1
        if score > 0:
            pipeline_scores[pattern_key] = {
                "score": score,
                "pattern": pattern,
            }

    # 3. v2.0: 맥락 기반 분석
    combined_text = f"{task_description}\n{context_text}" if context_text else task_description
    context_analysis = analyze_context(combined_text)

    # 4. v2.0: 맥락 분석 결과에 따라 AI 에스컬레이션 강제 삽입
    ai_boost_applied = False
    if context_analysis["needs_ai_boost"]:
        # ai-orchestrator가 매칭되지 않았어도 강제 삽입
        if "ai-orchestrator" not in skill_scores:
            skill_scores["ai-orchestrator"] = {
                "score": 0,
                "matched_triggers": [],
                "skill": SKILL_REGISTRY["ai-orchestrator"],
                "auto_injected": True,  # v2.0: 자동 삽입 표시
                "injection_reason": f"맥락 복잡도 {context_analysis['context_score']}/20 — AI 보강 필요",
            }
        ai_boost_applied = True

    # 5. 최적 파이프라인 결정
    recommended_pipeline = None
    if pipeline_scores:
        best_pattern_key = max(pipeline_scores, key=lambda k: pipeline_scores[k]["score"])
        recommended_pipeline = pipeline_scores[best_pattern_key]["pattern"].copy()
    else:
        sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        if sorted_skills:
            recommended_pipeline = {
                "name": "자동 구성 파이프라인",
                "description": "매칭된 스킬 기반 자동 구성",
                "pipeline": [s[0] for s in sorted_skills[:4]],
                "ai_mode": "adaptive",
            }

    # 6. v2.0: AI 부스트 적용 — 파이프라인에 ai-orchestrator 삽입
    if ai_boost_applied and recommended_pipeline:
        pipeline_list = recommended_pipeline.get("pipeline", [])
        if "ai-orchestrator" not in pipeline_list:
            # 기반 스킬 뒤에 ai-orchestrator 삽입 (검증 역할)
            insert_idx = 0
            for i, skill_key in enumerate(pipeline_list):
                if SKILL_REGISTRY.get(skill_key, {}).get("layer") == "base":
                    insert_idx = i + 1
            pipeline_list.insert(insert_idx, "ai-orchestrator")
            recommended_pipeline["pipeline"] = pipeline_list
            recommended_pipeline["ai_boosted"] = True

    # 7. 실행 계획 생성
    execution_plan = generate_execution_plan_v2(
        recommended_pipeline, skill_scores, task_description, context_analysis
    )

    return {
        "task": task_description,
        "version": "2.0",
        "matched_skills": {k: {
            "score": v["score"],
            "triggers": v["matched_triggers"],
            "auto_injected": v.get("auto_injected", False),
            "injection_reason": v.get("injection_reason", ""),
        } for k, v in skill_scores.items()},
        "matched_pipelines": {k: {"score": v["score"], "name": v["pattern"]["name"]}
                             for k, v in pipeline_scores.items()},
        "context_analysis": context_analysis,
        "ai_boost_applied": ai_boost_applied,
        "recommended_pipeline": recommended_pipeline,
        "execution_plan": execution_plan,
    }


def generate_execution_plan_v2(pipeline: Optional[Dict], skill_scores: Dict,
                                task: str, context: Dict) -> List[Dict]:
    """v2.0 실행 계획 생성 (AI 에스컬레이션 옵션 포함)."""
    if not pipeline:
        return [{"step": 1, "action": "직접 처리", "note": "매칭된 스킬 없음 — 마누스가 직접 처리"}]

    plan = []
    ai_mode = pipeline.get("ai_mode", "adaptive")

    for i, skill_key in enumerate(pipeline.get("pipeline", []), 1):
        skill = SKILL_REGISTRY.get(skill_key, {})
        step = {
            "step": i,
            "skill": skill_key,
            "skill_name": skill.get("name", skill_key),
            "action": skill.get("description", ""),
            "script": skill.get("scripts", {}).get("main", ""),
            "layer": skill.get("layer", "unknown"),
        }

        # v2.0: AI 에스컬레이션 옵션 추가
        if skill.get("ai_escalation"):
            if ai_mode == "always":
                step["ai_escalation"] = "enabled"
                step["escalation_flag"] = "--escalate"
            elif ai_mode == "adaptive":
                step["ai_escalation"] = "auto"
                step["escalation_flag"] = ""  # 스킬 내부에서 자동 판단
            else:
                step["ai_escalation"] = "disabled"
                step["escalation_flag"] = "--no-escalate"

        # v2.0: auto_dispatch 사용 여부
        if skill_key == "ai-orchestrator" and context.get("needs_ai_boost"):
            step["use_auto_dispatch"] = True
            step["auto_dispatch_script"] = skill.get("scripts", {}).get("auto", "")

        plan.append(step)

    # 마지막에 memory-manager로 학습 기록 추가
    if "memory-manager" not in pipeline.get("pipeline", []):
        plan.append({
            "step": len(plan) + 1,
            "skill": "memory-manager",
            "skill_name": "Memory Manager",
            "action": "작업 결과 및 학습 내용 기록",
            "script": SKILL_REGISTRY["memory-manager"]["scripts"]["main"],
            "layer": "extension",
        })

    return plan


# ---------------------------------------------------------------------------
# v1.0 호환 함수
# ---------------------------------------------------------------------------

def analyze_task(task_description: str) -> Dict:
    """v1.0 호환: 기존 키워드 기반 분석 (내부적으로 v2.0 호출)."""
    return analyze_task_v2(task_description)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Skill Router v2.0 — 자율 라우팅 엔진 (능동적 AI 연계)")
    parser.add_argument("task", nargs="?", help="작업 설명")
    parser.add_argument("--context", help="추가 맥락 텍스트 (파일 경로)")
    parser.add_argument("--context-text", help="추가 맥락 텍스트 (직접 입력)")
    parser.add_argument("--list-skills", action="store_true", help="등록된 스킬 목록")
    parser.add_argument("--list-pipelines", action="store_true", help="파이프라인 패턴 목록")
    parser.add_argument("--json", action="store_true", help="JSON 출력")
    parser.add_argument("--v1", action="store_true", help="v1.0 호환 모드 (맥락 분석 비활성화)")
    args = parser.parse_args()

    if args.list_skills:
        print("\n등록된 스킬 (v2.0):")
        for key, skill in SKILL_REGISTRY.items():
            ai_tag = " [AI 에스컬레이션]" if skill.get("ai_escalation") else ""
            print(f"  [{skill['layer']:9s}] {key:20s} — {skill['description']}{ai_tag}")
        return

    if args.list_pipelines:
        print("\n파이프라인 패턴 (v2.0):")
        for key, pattern in PIPELINE_PATTERNS.items():
            ai_mode = pattern.get("ai_mode", "N/A")
            print(f"  {key:20s} — {pattern['name']} [AI: {ai_mode}]")
            print(f"    {pattern['description']}")
            print(f"    체인: {' → '.join(pattern['pipeline'])}")
        return

    if not args.task:
        print("작업 설명을 입력해주세요.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    # 맥락 텍스트 로드
    context_text = ""
    if args.context:
        with open(args.context, "r", encoding="utf-8") as f:
            context_text = f.read()
    elif args.context_text:
        context_text = args.context_text

    # 분석 실행
    result = analyze_task_v2(args.task, context_text)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  Skill Router v2.0 — 자율 라우팅 결과")
        print(f"{'='*60}")
        print(f"\n작업: {result['task']}\n")

        # 맥락 분석 결과
        ctx = result.get("context_analysis", {})
        print(f"[맥락 분석]")
        print(f"  복잡도 점수: {ctx.get('context_score', 0)}/20")
        print(f"  AI 긴급도: {ctx.get('ai_urgency', 'N/A')}")
        print(f"  AI 부스트: {'적용됨' if result.get('ai_boost_applied') else '불필요'}")
        if ctx.get("detected_signals"):
            print(f"  감지된 신호:")
            for sig_key, sig_data in ctx["detected_signals"].items():
                print(f"    • {sig_key}: {sig_data['count']}건 (가중치 {sig_data['weight']})")
        print()

        if result["matched_skills"]:
            print("[매칭된 스킬]")
            for skill, info in sorted(result["matched_skills"].items(),
                                       key=lambda x: x[1]["score"], reverse=True):
                auto_tag = " [자동 삽입]" if info.get("auto_injected") else ""
                reason = f" — {info['injection_reason']}" if info.get("injection_reason") else ""
                triggers = f"(트리거: {', '.join(info['triggers'])})" if info['triggers'] else ""
                print(f"  {'★' * max(1, info['score'])} {skill} {triggers}{auto_tag}{reason}")
            print()

        if result["recommended_pipeline"]:
            pipe = result["recommended_pipeline"]
            ai_tag = " [AI 부스트 적용]" if pipe.get("ai_boosted") else ""
            print(f"[추천 파이프라인] {pipe['name']}{ai_tag}")
            print(f"  {pipe.get('description', '')}\n")

        if result["execution_plan"]:
            print("[실행 계획]")
            for step in result["execution_plan"]:
                ai_flag = ""
                if step.get("ai_escalation"):
                    ai_flag = f" [AI: {step['ai_escalation']}]"
                if step.get("use_auto_dispatch"):
                    ai_flag += " [auto_dispatch]"
                print(f"  Step {step['step']}: {step.get('skill_name', '')} — {step['action']}{ai_flag}")
                if step.get("script"):
                    print(f"         → {step['script']}")
            print()


if __name__ == "__main__":
    main()
