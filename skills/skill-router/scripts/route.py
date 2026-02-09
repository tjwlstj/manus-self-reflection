#!/usr/bin/env python3
"""
Skill Router — 누스양의 자율 라우팅 엔진
작업을 분석하여 어떤 스킬 조합을 사용할지 자동으로 결정하고,
실행 파이프라인을 생성한다.
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional


# 스킬 트리 레지스트리
SKILL_REGISTRY = {
    "ai-orchestrator": {
        "name": "AI Orchestrator",
        "description": "다중 AI(Gemini, GPT) 역할 분배 및 교차 검증",
        "triggers": ["조사", "연구", "코드", "구현", "검증", "API", "AI", "분석", "비교"],
        "capabilities": ["research", "code_generation", "cross_verify", "deep_analysis"],
        "layer": "core",
        "depends_on": [],
        "scripts": {
            "main": "/home/ubuntu/skills/ai-orchestrator/scripts/multi_ai_request.py",
            "advisor": "/home/ubuntu/skills/ai-orchestrator/scripts/role_advisor.py",
        }
    },
    "logic-checker": {
        "name": "Logic Checker",
        "description": "논리적 오류 5종 감지 (정규식 기반)",
        "triggers": ["논리", "오류", "추론", "논증", "모순", "타당"],
        "capabilities": ["fallacy_detection", "argument_analysis"],
        "layer": "base",
        "depends_on": [],
        "scripts": {
            "main": "/home/ubuntu/skills/logic-checker/scripts/check_logic.py",
        }
    },
    "self-reflection": {
        "name": "Self-Reflection",
        "description": "5차원 자기 성찰 (완전성, 일관성, 깊이, 정직성, 공감성)",
        "triggers": ["검토", "성찰", "리뷰", "품질", "개선", "자기", "돌아보"],
        "capabilities": ["self_review", "quality_check", "improvement_suggestion"],
        "layer": "base",
        "depends_on": [],
        "scripts": {
            "main": "/home/ubuntu/skills/self-reflection/scripts/reflect.py",
        }
    },
    "bias-guard": {
        "name": "Bias Guard",
        "description": "12종 인지 편향 감지 및 균형 관점 제안",
        "triggers": ["편향", "균형", "객관", "공정", "편견", "치우", "한쪽"],
        "capabilities": ["bias_detection", "balanced_perspective", "debiasing"],
        "layer": "base",
        "depends_on": [],
        "scripts": {
            "main": "/home/ubuntu/skills/bias-guard/scripts/detect_bias.py",
        }
    },
    "creative-thinking": {
        "name": "Creative Thinking",
        "description": "6가지 창의적 사고 기법 (역발상, 유추, SCAMPER 등)",
        "triggers": ["창의", "아이디어", "브레인스토밍", "새로운", "혁신", "발상", "관점"],
        "capabilities": ["ideation", "perspective_shift", "creative_exploration"],
        "layer": "extension",
        "depends_on": [],
        "scripts": {
            "main": "/home/ubuntu/skills/creative-thinking/scripts/ideate.py",
        }
    },
    "memory-manager": {
        "name": "Memory Manager",
        "description": "경험 축적, 검색, 학습 기록",
        "triggers": ["기억", "경험", "학습", "기록", "저장", "이전에", "과거"],
        "capabilities": ["memory_store", "memory_search", "experience_recall"],
        "layer": "extension",
        "depends_on": [],
        "scripts": {
            "main": "/home/ubuntu/skills/memory-manager/scripts/memory.py",
        }
    },
}

# 파이프라인 패턴
PIPELINE_PATTERNS = {
    "deep_analysis": {
        "name": "심층 분석 체인",
        "description": "조사 → 논리 검증 → 편향 보정 → 자기 성찰",
        "triggers": ["심층", "철저", "깊이", "종합"],
        "pipeline": ["ai-orchestrator", "logic-checker", "bias-guard", "self-reflection"],
    },
    "creative_solve": {
        "name": "창의적 문제 해결",
        "description": "창의적 발상 → AI 검증 → 경험 저장",
        "triggers": ["창의적 해결", "새로운 방법", "혁신적"],
        "pipeline": ["creative-thinking", "ai-orchestrator", "memory-manager"],
    },
    "self_improve": {
        "name": "자기 개선 루프",
        "description": "자기 성찰 → 편향 감지 → 논리 검증 → 학습 기록",
        "triggers": ["개선", "발전", "성장", "반성"],
        "pipeline": ["self-reflection", "bias-guard", "logic-checker", "memory-manager"],
    },
    "quality_gate": {
        "name": "품질 관문",
        "description": "논리 검증 + 편향 감지 + 자기 성찰 (병렬)",
        "triggers": ["품질", "검수", "확인", "최종"],
        "pipeline": ["logic-checker", "bias-guard", "self-reflection"],
    },
    "research_create": {
        "name": "조사 → 창작",
        "description": "AI 조사 → 창의적 확장 → 품질 검증",
        "triggers": ["조사 후", "연구 기반", "근거 있는"],
        "pipeline": ["ai-orchestrator", "creative-thinking", "self-reflection"],
    },
}


def analyze_task(task_description: str) -> Dict:
    """
    작업을 분석하여 필요한 스킬과 파이프라인을 추천.

    Args:
        task_description: 작업 설명

    Returns:
        라우팅 결과
    """
    task_lower = task_description.lower()

    # 1. 개별 스킬 매칭
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

    # 3. 최적 파이프라인 결정
    recommended_pipeline = None
    if pipeline_scores:
        best_pattern_key = max(pipeline_scores, key=lambda k: pipeline_scores[k]["score"])
        recommended_pipeline = pipeline_scores[best_pattern_key]["pattern"]
    else:
        # 파이프라인 매칭 없으면 개별 스킬로 구성
        sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        if sorted_skills:
            recommended_pipeline = {
                "name": "자동 구성 파이프라인",
                "description": "매칭된 스킬 기반 자동 구성",
                "pipeline": [s[0] for s in sorted_skills[:4]],
            }

    # 4. 실행 계획 생성
    execution_plan = generate_execution_plan(
        recommended_pipeline, skill_scores, task_description
    )

    return {
        "task": task_description,
        "matched_skills": {k: {"score": v["score"], "triggers": v["matched_triggers"]}
                          for k, v in skill_scores.items()},
        "matched_pipelines": {k: {"score": v["score"], "name": v["pattern"]["name"]}
                             for k, v in pipeline_scores.items()},
        "recommended_pipeline": recommended_pipeline,
        "execution_plan": execution_plan,
    }


def generate_execution_plan(pipeline: Optional[Dict], skill_scores: Dict,
                           task: str) -> List[Dict]:
    """실행 계획 생성."""
    if not pipeline:
        return [{"step": 1, "action": "직접 처리", "note": "매칭된 스킬 없음 — 마누스가 직접 처리"}]

    plan = []
    for i, skill_key in enumerate(pipeline["pipeline"], 1):
        skill = SKILL_REGISTRY.get(skill_key, {})
        step = {
            "step": i,
            "skill": skill_key,
            "skill_name": skill.get("name", skill_key),
            "action": skill.get("description", ""),
            "script": skill.get("scripts", {}).get("main", ""),
        }
        plan.append(step)

    # 마지막에 memory-manager로 학습 기록 추가 (이미 포함되어 있지 않으면)
    if "memory-manager" not in pipeline["pipeline"]:
        plan.append({
            "step": len(plan) + 1,
            "skill": "memory-manager",
            "skill_name": "Memory Manager",
            "action": "작업 결과 및 학습 내용 기록",
            "script": SKILL_REGISTRY["memory-manager"]["scripts"]["main"],
        })

    return plan


def main():
    parser = argparse.ArgumentParser(description="Skill Router — 자율 라우팅 엔진")
    parser.add_argument("task", nargs="?", help="작업 설명")
    parser.add_argument("--list-skills", action="store_true", help="등록된 스킬 목록")
    parser.add_argument("--list-pipelines", action="store_true", help="파이프라인 패턴 목록")
    parser.add_argument("--json", action="store_true", help="JSON 출력")
    args = parser.parse_args()

    if args.list_skills:
        print("\n등록된 스킬:")
        for key, skill in SKILL_REGISTRY.items():
            print(f"  [{skill['layer']:9s}] {key:20s} — {skill['description']}")
        return

    if args.list_pipelines:
        print("\n파이프라인 패턴:")
        for key, pattern in PIPELINE_PATTERNS.items():
            print(f"  {key:20s} — {pattern['name']}")
            print(f"    {pattern['description']}")
            print(f"    체인: {' → '.join(pattern['pipeline'])}")
        return

    if not args.task:
        print("작업 설명을 입력해주세요.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    result = analyze_task(args.task)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  Skill Router — 자율 라우팅 결과")
        print(f"{'='*60}")
        print(f"\n작업: {result['task']}\n")

        if result["matched_skills"]:
            print("[매칭된 스킬]")
            for skill, info in sorted(result["matched_skills"].items(),
                                       key=lambda x: x[1]["score"], reverse=True):
                print(f"  ★{'★' * info['score']} {skill} "
                      f"(트리거: {', '.join(info['triggers'])})")
            print()

        if result["recommended_pipeline"]:
            pipe = result["recommended_pipeline"]
            print(f"[추천 파이프라인] {pipe['name']}")
            print(f"  {pipe.get('description', '')}\n")

        if result["execution_plan"]:
            print("[실행 계획]")
            for step in result["execution_plan"]:
                print(f"  Step {step['step']}: {step.get('skill_name', '')} — {step['action']}")
                if step.get("script"):
                    print(f"         → {step['script']}")
            print()


if __name__ == "__main__":
    main()
