#!/usr/bin/env python3
"""
role_advisor.py - AI Role Assignment Advisor

Analyzes a task description and recommends which AI model should handle
which sub-task, based on model strengths and task characteristics.

Usage:
    python role_advisor.py --task "Build a real-time chat app with WebSocket"
    python role_advisor.py --task-file task_description.txt

Output:
    JSON with recommended role assignments for each sub-task.
"""

import argparse
import json
import os
import sys
import time

# ---------------------------------------------------------------------------
# Task Classification Keywords
# ---------------------------------------------------------------------------

TASK_SIGNALS = {
    "gemini_primary": {
        "keywords": [
            "조사", "research", "survey", "찾아", "검색", "search",
            "최신", "latest", "trend", "동향", "요약", "summarize",
            "개요", "overview", "비교", "compare", "정리", "organize",
            "아이디어", "idea", "brainstorm", "발상", "탐색", "explore",
        ],
        "roles": ["Broad Researcher", "Trend Analyst", "Idea Generator", "Fact Checker"],
    },
    "gpt_primary": {
        "keywords": [
            "코드", "code", "구현", "implement", "프로그래밍", "programming",
            "스크립트", "script", "함수", "function", "클래스", "class",
            "분석", "analyze", "논리", "logic", "검증", "verify",
            "리뷰", "review", "디버그", "debug", "수정", "fix",
            "문서", "document", "작성", "write", "보고서", "report",
        ],
        "roles": ["Code Specialist", "Logic Analyzer", "Deep Reviewer", "Technical Writer"],
    },
}


def analyze_task(task_description: str) -> dict:
    """
    Analyze a task description and recommend AI model/role assignments.

    Returns a dict with:
        - primary_model: recommended primary AI
        - secondary_model: recommended secondary AI
        - recommended_workflow: list of workflow steps
        - confidence: how confident the recommendation is
    """
    task_lower = task_description.lower()

    gemini_score = sum(
        1 for kw in TASK_SIGNALS["gemini_primary"]["keywords"] if kw in task_lower
    )
    gpt_score = sum(
        1 for kw in TASK_SIGNALS["gpt_primary"]["keywords"] if kw in task_lower
    )

    total = gemini_score + gpt_score
    if total == 0:
        confidence = "low"
        primary = "gemini"
        secondary = "gpt"
    elif gemini_score > gpt_score:
        confidence = "high" if gemini_score >= 3 else "medium"
        primary = "gemini"
        secondary = "gpt"
    elif gpt_score > gemini_score:
        confidence = "high" if gpt_score >= 3 else "medium"
        primary = "gpt"
        secondary = "gemini"
    else:
        confidence = "medium"
        primary = "gemini"
        secondary = "gpt"

    # Build recommended workflow
    workflow = []

    # Phase 1: Always start with research/understanding
    workflow.append({
        "phase": 1,
        "title": "Information Gathering",
        "model": "gemini",
        "role": "Broad Researcher",
        "description": "Conduct broad research to establish context and gather relevant information.",
    })

    # Phase 2: Deep dive based on primary model
    if primary == "gpt":
        workflow.append({
            "phase": 2,
            "title": "Implementation / Deep Analysis",
            "model": "gpt",
            "role": _select_best_role(task_lower, TASK_SIGNALS["gpt_primary"]["roles"]),
            "description": "Perform deep analysis or implementation based on gathered information.",
        })
    else:
        workflow.append({
            "phase": 2,
            "title": "Detailed Research & Synthesis",
            "model": "gemini",
            "role": _select_best_role(task_lower, TASK_SIGNALS["gemini_primary"]["roles"]),
            "description": "Conduct detailed research and synthesize findings.",
        })

    # Phase 3: Cross-verification
    workflow.append({
        "phase": 3,
        "title": "Cross-Verification",
        "model": secondary,
        "role": "Cross Verifier",
        "description": f"Have {secondary.upper()} review and verify {primary.upper()}'s output.",
    })

    # Phase 4: Refinement
    workflow.append({
        "phase": 4,
        "title": "Refinement & Finalization",
        "model": primary,
        "role": _select_best_role(task_lower, TASK_SIGNALS[f"{primary}_primary"]["roles"]),
        "description": "Incorporate verification feedback and produce final output.",
    })

    return {
        "task": task_description,
        "analysis": {
            "gemini_relevance_score": gemini_score,
            "gpt_relevance_score": gpt_score,
            "confidence": confidence,
        },
        "recommendation": {
            "primary_model": primary,
            "secondary_model": secondary,
            "workflow": workflow,
        },
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _select_best_role(task_lower: str, candidate_roles: list[str]) -> str:
    """Select the most relevant role from candidates based on task keywords."""
    role_keywords = {
        "Broad Researcher": ["조사", "research", "찾아", "검색", "survey"],
        "Code Specialist": ["코드", "code", "구현", "implement", "스크립트"],
        "Fact Checker": ["검증", "verify", "확인", "check", "사실"],
        "Logic Analyzer": ["논리", "logic", "분석", "analyze", "추론"],
        "Deep Reviewer": ["리뷰", "review", "검토", "평가", "비판"],
        "Idea Generator": ["아이디어", "idea", "brainstorm", "발상", "창의"],
        "Technical Writer": ["문서", "document", "작성", "write", "보고서"],
        "Trend Analyst": ["동향", "trend", "최신", "latest", "트렌드"],
    }

    best_role = candidate_roles[0]
    best_score = 0

    for role in candidate_roles:
        keywords = role_keywords.get(role, [])
        score = sum(1 for kw in keywords if kw in task_lower)
        if score > best_score:
            best_score = score
            best_role = role

    return best_role


def generate_batch_config(analysis: dict) -> dict:
    """
    Generate a batch config JSON that can be fed to multi_ai_request.py.

    The user should fill in the actual prompts.
    """
    workflow = analysis["recommendation"]["workflow"]
    requests = []

    for step in workflow:
        requests.append({
            "model": step["model"],
            "role": step["role"],
            "prompt": f"[TODO: Fill in prompt for Phase {step['phase']}: {step['title']}]",
            "_description": step["description"],
        })

    config = {
        "task": analysis["task"],
        "requests": requests,
        "cross_verify": [
            {
                "source_index": 1,
                "verifier_model": analysis["recommendation"]["secondary_model"],
            }
        ],
    }

    return config


def main():
    parser = argparse.ArgumentParser(description="AI Role Assignment Advisor")
    parser.add_argument("--task", help="Task description string")
    parser.add_argument("--task-file", help="File containing task description")
    parser.add_argument("--generate-config", action="store_true",
                        help="Also generate a batch config template")
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    if args.task_file:
        task = open(args.task_file).read().strip()
    elif args.task:
        task = args.task
    else:
        print("Error: Provide --task or --task-file", file=sys.stderr)
        sys.exit(1)

    analysis = analyze_task(task)

    output = {"analysis": analysis}

    if args.generate_config:
        output["batch_config"] = generate_batch_config(analysis)

    result_json = json.dumps(output, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(result_json)
        print(f"Saved to: {args.output}", file=sys.stderr)

    print(result_json)


if __name__ == "__main__":
    main()
