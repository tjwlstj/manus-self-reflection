#!/usr/bin/env python3
"""
multi_ai_request.py - Multi-AI Orchestrator Helper Script

Sends prompts to multiple AI models (Gemini, GPT) with role assignments,
collects responses, and optionally performs cross-verification.

Usage:
    python multi_ai_request.py --config <config.json>
    python multi_ai_request.py --role "Broad Researcher" --model gemini --prompt "..."
    python multi_ai_request.py --role "Code Specialist" --model gpt --prompt "..."

Environment Variables Required:
    GEMINI_API_KEY  - Google Gemini API key
    OPENAI_API_KEY  - OpenAI-compatible API key

Output:
    Results are printed to stdout as JSON and optionally saved to files.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Model Configuration
# ---------------------------------------------------------------------------

MODEL_PROFILES = {
    "gemini": {
        "display_name": "Gemini",
        "model_id": "gemini-2.5-flash",
        "strengths": [
            "broad research",
            "latest information access",
            "quick summarization",
            "multimodal understanding",
        ],
        "recommended_roles": [
            "Broad Researcher",
            "Fact Checker",
            "Trend Analyst",
            "Idea Generator",
        ],
    },
    "gpt": {
        "display_name": "GPT",
        "model_id": "gpt-4.1-mini",
        "strengths": [
            "code generation",
            "complex logic structuring",
            "deep analysis",
            "technical writing",
        ],
        "recommended_roles": [
            "Code Specialist",
            "Logic Analyzer",
            "Deep Reviewer",
            "Technical Writer",
        ],
    },
}

# ---------------------------------------------------------------------------
# Role-based System Prompts
# ---------------------------------------------------------------------------

ROLE_SYSTEM_PROMPTS = {
    "Broad Researcher": (
        "You are a broad research specialist. Your task is to survey a wide range "
        "of sources, summarize key findings, identify trends, and provide a "
        "comprehensive overview. Focus on breadth and recency of information. "
        "Present findings in a structured, easy-to-digest format."
    ),
    "Code Specialist": (
        "You are a code generation and technical implementation specialist. "
        "Write clean, well-documented, production-ready code. Include error "
        "handling, type hints, and follow best practices for the language. "
        "Explain key design decisions briefly."
    ),
    "Fact Checker": (
        "You are a meticulous fact-checker. Verify claims against known facts, "
        "identify potential inaccuracies, flag unsupported assertions, and "
        "suggest corrections with reasoning. Be specific about what is verified "
        "and what remains uncertain."
    ),
    "Logic Analyzer": (
        "You are a logic and reasoning specialist. Analyze arguments for logical "
        "consistency, identify fallacies, evaluate the strength of evidence, "
        "and suggest improvements to reasoning chains. Be precise and systematic."
    ),
    "Deep Reviewer": (
        "You are a deep review specialist. Critically examine the provided content "
        "for completeness, accuracy, logical consistency, and practical applicability. "
        "Provide specific, actionable feedback with concrete suggestions."
    ),
    "Idea Generator": (
        "You are a creative ideation specialist. Generate diverse, innovative ideas "
        "that push boundaries while remaining feasible. Consider multiple perspectives "
        "and unconventional approaches. Organize ideas by novelty and practicality."
    ),
    "Technical Writer": (
        "You are a technical writing specialist. Transform complex information into "
        "clear, well-structured documentation. Use precise language, consistent "
        "formatting, and include relevant examples."
    ),
    "Trend Analyst": (
        "You are a trend analysis specialist. Identify emerging patterns, predict "
        "future developments, and contextualize current events within broader trends. "
        "Support analysis with data points and historical context."
    ),
    "Cross Verifier": (
        "You are a cross-verification specialist. Your task is to review and validate "
        "another AI's output. Identify errors, omissions, inconsistencies, and areas "
        "for improvement. Provide a balanced assessment with specific suggestions. "
        "Do NOT simply agree — actively look for issues."
    ),
}

# ---------------------------------------------------------------------------
# API Callers
# ---------------------------------------------------------------------------


def call_gemini(prompt: str, system_prompt: str = "", model_id: str = "gemini-2.5-flash") -> dict:
    """Call Google Gemini API and return structured result."""
    try:
        from google import genai

        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        response = client.models.generate_content(
            model=model_id,
            contents=full_prompt,
        )

        return {
            "success": True,
            "model": model_id,
            "provider": "gemini",
            "response": response.text,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    except Exception as e:
        return {
            "success": False,
            "model": model_id,
            "provider": "gemini",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


def call_gpt(prompt: str, system_prompt: str = "", model_id: str = "gpt-4.1-mini") -> dict:
    """Call OpenAI-compatible API and return structured result."""
    try:
        from openai import OpenAI

        client = OpenAI()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
        )

        return {
            "success": True,
            "model": model_id,
            "provider": "gpt",
            "response": response.choices[0].message.content,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    except Exception as e:
        return {
            "success": False,
            "model": model_id,
            "provider": "gpt",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


# ---------------------------------------------------------------------------
# Orchestration Functions
# ---------------------------------------------------------------------------


def dispatch_request(model_key: str, role: str, prompt: str, custom_system_prompt: str = None) -> dict:
    """Dispatch a single request to the specified AI model with role context."""
    system_prompt = custom_system_prompt or ROLE_SYSTEM_PROMPTS.get(role, "")
    profile = MODEL_PROFILES.get(model_key, {})
    model_id = profile.get("model_id", model_key)

    caller = {"gemini": call_gemini, "gpt": call_gpt}.get(model_key)
    if not caller:
        return {"success": False, "error": f"Unknown model: {model_key}"}

    result = caller(prompt, system_prompt, model_id)
    result["role"] = role
    return result


def dispatch_batch(requests: list[dict]) -> list[dict]:
    """
    Dispatch multiple requests sequentially.

    Each request dict should have:
        - model: "gemini" or "gpt"
        - role: one of the predefined roles
        - prompt: the user prompt
        - system_prompt (optional): override default role system prompt
    """
    results = []
    for i, req in enumerate(requests):
        print(f"[{i+1}/{len(requests)}] Dispatching to {req['model']} as '{req['role']}'...",
              file=sys.stderr)
        result = dispatch_request(
            model_key=req["model"],
            role=req["role"],
            prompt=req["prompt"],
            custom_system_prompt=req.get("system_prompt"),
        )
        results.append(result)
    return results


def cross_verify(original_result: dict, verifier_model: str) -> dict:
    """
    Send one AI's output to another AI for cross-verification.

    Args:
        original_result: The result dict from the original AI call.
        verifier_model: "gemini" or "gpt" — the model that will verify.

    Returns:
        Verification result dict.
    """
    original_role = original_result.get("role", "Unknown")
    original_provider = original_result.get("provider", "Unknown")
    original_response = original_result.get("response", "")

    verification_prompt = (
        f"The following is an output from {original_provider.upper()} "
        f"acting as '{original_role}':\n\n"
        f"---\n{original_response}\n---\n\n"
        f"Please critically review this output. Identify:\n"
        f"1. Any factual errors or inaccuracies\n"
        f"2. Logical inconsistencies or gaps\n"
        f"3. Missing important perspectives or information\n"
        f"4. Suggestions for improvement\n"
        f"5. Overall assessment (strengths and weaknesses)\n\n"
        f"Be specific and constructive in your feedback."
    )

    return dispatch_request(
        model_key=verifier_model,
        role="Cross Verifier",
        prompt=verification_prompt,
    )


def save_result(result: dict, output_path: str):
    """Save a result dict to a markdown file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    role = result.get("role", "unknown")
    provider = result.get("provider", "unknown")
    model = result.get("model", "unknown")
    timestamp = result.get("timestamp", "")

    content = f"# {role} ({provider})\n\n"
    content += f"**Model**: {model}  \n"
    content += f"**Timestamp**: {timestamp}  \n\n"
    content += "---\n\n"

    if result.get("success"):
        content += result.get("response", "")
    else:
        content += f"**ERROR**: {result.get('error', 'Unknown error')}"

    content += "\n"
    path.write_text(content, encoding="utf-8")
    print(f"Saved: {path}", file=sys.stderr)


# ---------------------------------------------------------------------------
# CLI Interface
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Multi-AI Orchestrator: dispatch prompts to Gemini/GPT with role assignments"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # --- single command ---
    single_parser = subparsers.add_parser("single", help="Send a single request")
    single_parser.add_argument("--model", required=True, choices=["gemini", "gpt"])
    single_parser.add_argument("--role", required=True, help="Role to assign")
    single_parser.add_argument("--prompt", required=True, help="Prompt text")
    single_parser.add_argument("--output", help="Output file path (markdown)")

    # --- batch command ---
    batch_parser = subparsers.add_parser("batch", help="Send batch requests from config")
    batch_parser.add_argument("--config", required=True, help="JSON config file path")
    batch_parser.add_argument("--output-dir", default=".", help="Output directory")

    # --- verify command ---
    verify_parser = subparsers.add_parser("verify", help="Cross-verify a result file")
    verify_parser.add_argument("--input", required=True, help="Input result file (markdown)")
    verify_parser.add_argument("--verifier", required=True, choices=["gemini", "gpt"])
    verify_parser.add_argument("--output", help="Output file path (markdown)")

    # --- roles command ---
    subparsers.add_parser("roles", help="List available roles")

    # --- models command ---
    subparsers.add_parser("models", help="List available models and their profiles")

    args = parser.parse_args()

    if args.command == "single":
        result = dispatch_request(args.model, args.role, args.prompt)
        if args.output:
            save_result(result, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "batch":
        with open(args.config) as f:
            config = json.load(f)
        requests = config.get("requests", config if isinstance(config, list) else [])
        results = dispatch_batch(requests)

        for i, result in enumerate(results):
            role_slug = result.get("role", "unknown").lower().replace(" ", "_")
            provider = result.get("provider", "unknown")
            output_path = os.path.join(args.output_dir, f"result_{provider}_{role_slug}.md")
            save_result(result, output_path)

        # Cross-verification if configured
        cross_verify_config = config.get("cross_verify") if isinstance(config, dict) else None
        if cross_verify_config:
            print("\n--- Cross-Verification Phase ---", file=sys.stderr)
            for cv in cross_verify_config:
                src_idx = cv.get("source_index", 0)
                verifier = cv.get("verifier_model", "gpt")
                if src_idx < len(results) and results[src_idx].get("success"):
                    cv_result = cross_verify(results[src_idx], verifier)
                    role_slug = results[src_idx].get("role", "unknown").lower().replace(" ", "_")
                    cv_path = os.path.join(
                        args.output_dir,
                        f"cross_verify_{verifier}_{role_slug}.md",
                    )
                    save_result(cv_result, cv_path)
                    results.append(cv_result)

        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.command == "verify":
        content = Path(args.input).read_text(encoding="utf-8")
        mock_result = {
            "role": "External Input",
            "provider": "file",
            "response": content,
        }
        result = cross_verify(mock_result, args.verifier)
        if args.output:
            save_result(result, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "roles":
        print("Available Roles:")
        print("-" * 60)
        for role, desc in ROLE_SYSTEM_PROMPTS.items():
            print(f"\n  {role}")
            print(f"    {desc[:100]}...")

    elif args.command == "models":
        print("Available Models:")
        print("-" * 60)
        for key, profile in MODEL_PROFILES.items():
            print(f"\n  {key} ({profile['display_name']})")
            print(f"    Model ID: {profile['model_id']}")
            print(f"    Strengths: {', '.join(profile['strengths'])}")
            print(f"    Recommended Roles: {', '.join(profile['recommended_roles'])}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
