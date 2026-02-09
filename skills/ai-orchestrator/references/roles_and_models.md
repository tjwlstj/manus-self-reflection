# AI Orchestrator - Roles & Models Reference

## Model Profiles

### Gemini (gemini-2.5-flash)

**Primary Strengths**: Broad information access, fast summarization, multimodal understanding, latest trends.

**Best For**: Initial research phases, fact gathering, trend analysis, idea brainstorming, common-sense verification of other AI outputs.

**Limitations**: May produce surface-level analysis for highly technical topics. Code generation quality varies.

### GPT (gpt-4.1-mini)

**Primary Strengths**: Code generation, complex logic structuring, deep analysis, technical writing, debugging.

**Best For**: Implementation phases, code writing, logical consistency review, detailed technical documentation, in-depth analysis of research findings.

**Limitations**: Knowledge cutoff may miss very recent developments. Requires clear, specific prompts for best results.

## Role Definitions

| Role | Purpose | Best Model | When to Use |
|---|---|---|---|
| Broad Researcher | Wide-scope information gathering | Gemini | Starting a new topic, surveying a field |
| Code Specialist | Code generation and debugging | GPT | Implementation, scripting, automation |
| Fact Checker | Verify claims and accuracy | Gemini | After analysis, before final output |
| Logic Analyzer | Evaluate reasoning chains | GPT | Complex arguments, decision analysis |
| Deep Reviewer | Critical review of content | GPT | Quality assurance, peer review |
| Idea Generator | Creative brainstorming | Gemini | Early ideation, exploring alternatives |
| Technical Writer | Documentation and reports | GPT | Final output preparation |
| Trend Analyst | Pattern and trend identification | Gemini | Market analysis, technology trends |
| Cross Verifier | Review another AI's output | Either | Validation phase |

## Custom Role Creation

To define a custom role, provide a system prompt that specifies:

1. The role's identity and expertise area
2. Expected output format
3. Key behaviors and constraints
4. Quality criteria

Example:
```json
{
  "model": "gpt",
  "role": "Security Auditor",
  "system_prompt": "You are a cybersecurity expert. Review the provided code for security vulnerabilities including SQL injection, XSS, CSRF, and authentication issues. Rate each finding by severity (Critical/High/Medium/Low) and provide remediation steps.",
  "prompt": "Review this Python Flask application code: ..."
}
```

## Workflow Patterns

### Pattern 1: Research → Implement → Verify
Best for: Building something new based on research.
```
Gemini(Broad Researcher) → GPT(Code Specialist) → Gemini(Cross Verifier)
```

### Pattern 2: Analyze → Deep Review → Refine
Best for: Improving existing content or code.
```
GPT(Logic Analyzer) → Gemini(Fact Checker) → GPT(Deep Reviewer)
```

### Pattern 3: Brainstorm → Evaluate → Implement
Best for: Creative problem-solving with implementation.
```
Gemini(Idea Generator) → GPT(Logic Analyzer) → GPT(Code Specialist)
```

### Pattern 4: Parallel Research → Synthesize
Best for: Comprehensive topic coverage.
```
Gemini(Broad Researcher) + GPT(Deep Reviewer) → Manus(Synthesis)
```
