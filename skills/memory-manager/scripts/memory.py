#!/usr/bin/env python3
"""
Memory Manager v2.0 — 누스양의 경험 축적 및 검색 도구 (AI 연계 강화)

v1.0과의 차이점:
  1. AI 기반 유사 경험 검색: 키워드 매칭을 넘어 AI가 의미적 유사성을 판단
  2. 자동 학습 기록: 다른 스킬의 AI 에스컬레이션 결과를 자동으로 기록
  3. 경험 기반 조언: 과거 경험을 바탕으로 AI가 현재 작업에 대한 조언 생성
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# AI 에스컬레이션 모듈 임포트
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
try:
    from ai_escalation import escalate_to_ai
    AI_ESCALATION_AVAILABLE = True
except ImportError:
    AI_ESCALATION_AVAILABLE = False


MEMORY_DIR = os.path.expanduser("~/memories")
MEMORY_INDEX = os.path.join(MEMORY_DIR, "index.json")


def ensure_memory_dir():
    """메모리 디렉토리 초기화."""
    os.makedirs(MEMORY_DIR, exist_ok=True)
    if not os.path.exists(MEMORY_INDEX):
        with open(MEMORY_INDEX, "w", encoding="utf-8") as f:
            json.dump({"memories": [], "stats": {"total": 0, "categories": {}}}, f, ensure_ascii=False)


def load_index() -> Dict:
    """인덱스 로드."""
    ensure_memory_dir()
    with open(MEMORY_INDEX, "r", encoding="utf-8") as f:
        return json.load(f)


def save_index(index: Dict):
    """인덱스 저장."""
    with open(MEMORY_INDEX, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def store_memory(title: str, content: str, category: str,
                 tags: List[str] = None, importance: str = "normal",
                 source_task: str = "", source_skill: str = "") -> Dict:
    """
    새로운 기억 저장.

    Args:
        title: 기억 제목
        content: 기억 내용
        category: 분류 (insight, lesson, skill, fact, error, idea)
        tags: 검색용 태그
        importance: 중요도 (low, normal, high, critical)
        source_task: 출처 작업 설명
        source_skill: v2.0 — 출처 스킬 이름

    Returns:
        저장된 기억 메타데이터
    """
    ensure_memory_dir()
    index = load_index()

    memory_id = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(index['memories'])}"
    memory_file = os.path.join(MEMORY_DIR, f"{memory_id}.md")

    memory_meta = {
        "id": memory_id,
        "title": title,
        "category": category,
        "tags": tags or [],
        "importance": importance,
        "source_task": source_task,
        "source_skill": source_skill,  # v2.0
        "created_at": datetime.now().isoformat(),
        "file": memory_file,
        "access_count": 0,
    }

    # 마크다운 형식으로 기억 저장
    memory_content = f"""# {title}

- **분류**: {category}
- **중요도**: {importance}
- **태그**: {', '.join(tags or [])}
- **출처 작업**: {source_task}
- **출처 스킬**: {source_skill}
- **생성일**: {memory_meta['created_at']}

---

{content}
"""
    with open(memory_file, "w", encoding="utf-8") as f:
        f.write(memory_content)

    index["memories"].append(memory_meta)
    index["stats"]["total"] = len(index["memories"])
    cat_counts = index["stats"].get("categories", {})
    cat_counts[category] = cat_counts.get(category, 0) + 1
    index["stats"]["categories"] = cat_counts
    save_index(index)

    return memory_meta


def search_memories(query: str = "", category: str = "",
                    tags: List[str] = None, importance: str = "",
                    limit: int = 10) -> List[Dict]:
    """
    기억 검색 (키워드 기반).

    Args:
        query: 검색어 (제목, 태그에서 검색)
        category: 분류 필터
        tags: 태그 필터
        importance: 중요도 필터
        limit: 최대 결과 수

    Returns:
        매칭된 기억 목록
    """
    index = load_index()
    results = []

    for mem in index["memories"]:
        if category and mem["category"] != category:
            continue
        if importance and mem["importance"] != importance:
            continue
        if tags and not any(t in mem["tags"] for t in tags):
            continue
        if query:
            query_lower = query.lower()
            searchable = (mem["title"] + " " + " ".join(mem["tags"])).lower()
            if query_lower not in searchable:
                continue
        results.append(mem)

    importance_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
    results.sort(key=lambda m: (
        importance_order.get(m["importance"], 2),
        m["created_at"]
    ), reverse=False)

    return results[:limit]


def recall_memory(memory_id: str) -> Optional[Dict]:
    """특정 기억 전체 내용 조회."""
    index = load_index()
    for mem in index["memories"]:
        if mem["id"] == memory_id:
            mem["access_count"] = mem.get("access_count", 0) + 1
            save_index(index)

            content = ""
            if os.path.exists(mem["file"]):
                with open(mem["file"], "r", encoding="utf-8") as f:
                    content = f.read()

            return {**mem, "content": content}
    return None


def get_stats() -> Dict:
    """기억 통계 조회."""
    index = load_index()
    return index["stats"]


def list_recent(count: int = 5) -> List[Dict]:
    """최근 기억 목록."""
    index = load_index()
    sorted_mems = sorted(index["memories"], key=lambda m: m["created_at"], reverse=True)
    return sorted_mems[:count]


# ---------------------------------------------------------------------------
# v2.0: AI 연계 기능
# ---------------------------------------------------------------------------

def search_similar_ai(query: str, limit: int = 5) -> Dict:
    """
    v2.0: AI 기반 유사 경험 검색.

    키워드 매칭으로 찾지 못하는 의미적으로 유사한 경험을 AI가 판단.

    Args:
        query: 검색 질의
        limit: 최대 결과 수

    Returns:
        AI 유사성 판단 결과 + 매칭된 기억
    """
    if not AI_ESCALATION_AVAILABLE:
        return {
            "success": False,
            "error": "AI 에스컬레이션 모듈을 찾을 수 없습니다.",
            "fallback": search_memories(query=query, limit=limit),
        }

    # 모든 기억의 제목+태그 목록 구성
    index = load_index()
    if not index["memories"]:
        return {"success": True, "results": [], "message": "저장된 기억이 없습니다."}

    memory_summaries = []
    for mem in index["memories"]:
        summary = f"[{mem['id']}] {mem['title']} (분류: {mem['category']}, 태그: {', '.join(mem['tags'])})"
        memory_summaries.append(summary)

    # AI에게 유사성 판단 요청
    prompt = (
        f"다음은 저장된 기억 목록입니다:\n\n"
        f"{chr(10).join(memory_summaries)}\n\n"
        f"현재 검색 질의: \"{query}\"\n\n"
        f"위 기억 목록에서 검색 질의와 의미적으로 가장 관련 있는 기억을 최대 {limit}개 선택하고, "
        f"각각의 관련성을 설명해주세요.\n"
        f"JSON 형식으로 응답해주세요: "
        f'[{{"id": "mem_...", "relevance": "설명", "score": 0.0~1.0}}]'
    )

    ai_result = escalate_to_ai(
        text=prompt,
        skill_name="memory-manager",
        regex_result={"query": query, "total_memories": len(index["memories"])},
        model="gpt",
        role="Logic Analyzer",
    )

    result = {
        "success": ai_result.get("success", False),
        "query": query,
        "ai_model": ai_result.get("model", ""),
    }

    if ai_result.get("parsed") and isinstance(ai_result["parsed"], list):
        # AI가 선택한 기억 ID로 실제 기억 조회
        matched = []
        for item in ai_result["parsed"][:limit]:
            mem_id = item.get("id", "")
            mem = recall_memory(mem_id)
            if mem:
                matched.append({
                    **mem,
                    "ai_relevance": item.get("relevance", ""),
                    "ai_score": item.get("score", 0),
                })
        result["results"] = matched
    elif ai_result.get("raw"):
        result["ai_raw"] = ai_result["raw"][:2000]
        result["results"] = search_memories(query=query, limit=limit)  # 폴백
    else:
        result["results"] = search_memories(query=query, limit=limit)  # 폴백

    return result


def advise_from_experience(task_description: str) -> Dict:
    """
    v2.0: 과거 경험 기반 조언 생성.

    저장된 기억을 바탕으로 현재 작업에 대한 AI 조언을 생성.

    Args:
        task_description: 현재 작업 설명

    Returns:
        경험 기반 조언
    """
    if not AI_ESCALATION_AVAILABLE:
        return {"success": False, "error": "AI 에스컬레이션 모듈을 찾을 수 없습니다."}

    # 관련 기억 수집 (키워드 기반 + 최근 기억)
    keyword_results = search_memories(query=task_description, limit=5)
    recent_results = list_recent(5)

    # 중복 제거
    seen_ids = set()
    relevant_memories = []
    for mem in keyword_results + recent_results:
        if mem["id"] not in seen_ids:
            seen_ids.add(mem["id"])
            relevant_memories.append(mem)

    if not relevant_memories:
        return {
            "success": True,
            "advice": "관련된 과거 경험이 없습니다. 새로운 경험으로 기록하는 것을 권장합니다.",
            "memories_consulted": 0,
        }

    # 기억 내용 로드
    memory_contents = []
    for mem in relevant_memories[:8]:  # 최대 8개
        full_mem = recall_memory(mem["id"])
        if full_mem:
            memory_contents.append(
                f"[{full_mem['category']}/{full_mem['importance']}] {full_mem['title']}\n"
                f"{full_mem.get('content', '')[:500]}"
            )

    # AI에게 조언 요청
    prompt = (
        f"현재 작업: {task_description}\n\n"
        f"과거 관련 경험:\n\n"
        f"{'---'.join(memory_contents)}\n\n"
        f"위 과거 경험을 바탕으로 현재 작업에 대한 조언을 제공해주세요:\n"
        f"1. 과거 경험에서 배울 수 있는 교훈\n"
        f"2. 주의해야 할 잠재적 문제\n"
        f"3. 추천하는 접근 방법\n"
        f"4. 이전에 효과적이었던 전략"
    )

    ai_result = escalate_to_ai(
        text=prompt,
        skill_name="memory-manager",
        regex_result={"task": task_description, "memories_count": len(relevant_memories)},
        model="gpt",
        role="Deep Reviewer",
    )

    return {
        "success": ai_result.get("success", False),
        "task": task_description,
        "memories_consulted": len(relevant_memories),
        "advice": ai_result.get("raw", "조언 생성에 실패했습니다."),
        "ai_model": ai_result.get("model", ""),
        "relevant_memory_ids": [m["id"] for m in relevant_memories],
    }


def auto_record_escalation(skill_name: str, task_summary: str,
                            ai_result: Dict, outcome: str = "success") -> Dict:
    """
    v2.0: 다른 스킬의 AI 에스컬레이션 결과를 자동으로 기록.

    다른 스킬에서 AI를 호출한 결과를 자동으로 기억에 저장하여
    경험을 축적한다.

    Args:
        skill_name: 호출한 스킬 이름
        task_summary: 작업 요약
        ai_result: AI 호출 결과
        outcome: 결과 (success, partial, failure)

    Returns:
        저장된 기억 메타데이터
    """
    category_map = {
        "success": "insight",
        "partial": "lesson",
        "failure": "error",
    }

    importance_map = {
        "success": "normal",
        "partial": "high",
        "failure": "high",
    }

    content = (
        f"## AI 에스컬레이션 자동 기록\n\n"
        f"- **스킬**: {skill_name}\n"
        f"- **모델**: {ai_result.get('model', 'N/A')}\n"
        f"- **결과**: {outcome}\n\n"
        f"### 작업 요약\n{task_summary}\n\n"
        f"### AI 응답 요약\n{str(ai_result.get('raw', ''))[:1000]}\n"
    )

    return store_memory(
        title=f"[{skill_name}] AI 에스컬레이션 — {task_summary[:50]}",
        content=content,
        category=category_map.get(outcome, "insight"),
        tags=[skill_name, "ai-escalation", outcome, ai_result.get("model", "")],
        importance=importance_map.get(outcome, "normal"),
        source_task=task_summary,
        source_skill=skill_name,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Memory Manager v2.0 — 경험 축적 도구 (AI 연계)")
    subparsers = parser.add_subparsers(dest="command", help="명령")

    # store
    store_p = subparsers.add_parser("store", help="새 기억 저장")
    store_p.add_argument("--title", required=True, help="기억 제목")
    store_p.add_argument("--content", help="기억 내용 (직접 입력)")
    store_p.add_argument("--file", help="기억 내용 파일")
    store_p.add_argument("--category", required=True,
                         choices=["insight", "lesson", "skill", "fact", "error", "idea"],
                         help="분류")
    store_p.add_argument("--tags", nargs="+", default=[], help="태그")
    store_p.add_argument("--importance", default="normal",
                         choices=["low", "normal", "high", "critical"],
                         help="중요도")
    store_p.add_argument("--source", default="", help="출처 작업")
    store_p.add_argument("--source-skill", default="", help="출처 스킬")

    # search (키워드 기반)
    search_p = subparsers.add_parser("search", help="기억 검색 (키워드)")
    search_p.add_argument("--query", default="", help="검색어")
    search_p.add_argument("--category", default="", help="분류 필터")
    search_p.add_argument("--tags", nargs="+", help="태그 필터")
    search_p.add_argument("--importance", default="", help="중요도 필터")
    search_p.add_argument("--limit", type=int, default=10, help="최대 결과 수")

    # v2.0: search-ai (AI 기반 유사 검색)
    search_ai_p = subparsers.add_parser("search-ai", help="AI 기반 유사 경험 검색")
    search_ai_p.add_argument("--query", required=True, help="검색 질의")
    search_ai_p.add_argument("--limit", type=int, default=5, help="최대 결과 수")

    # v2.0: advise (경험 기반 조언)
    advise_p = subparsers.add_parser("advise", help="과거 경험 기반 조언")
    advise_p.add_argument("--task", required=True, help="현재 작업 설명")

    # recall
    recall_p = subparsers.add_parser("recall", help="특정 기억 조회")
    recall_p.add_argument("memory_id", help="기억 ID")

    # recent
    recent_p = subparsers.add_parser("recent", help="최근 기억")
    recent_p.add_argument("--count", type=int, default=5, help="조회 수")

    # stats
    subparsers.add_parser("stats", help="통계 조회")

    parser.add_argument("--json", action="store_true", help="JSON 출력")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "store":
        content = args.content or ""
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()
        if not content:
            if sys.stdin.isatty():
                print("기억 내용을 입력하세요 (Ctrl+D로 종료):")
            content = sys.stdin.read()

        result = store_memory(
            title=args.title, content=content, category=args.category,
            tags=args.tags, importance=args.importance, source_task=args.source,
            source_skill=getattr(args, 'source_skill', ''),
        )
        if hasattr(args, 'json') and args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"기억 저장 완료: {result['id']}")
            print(f"   제목: {result['title']}")
            print(f"   분류: {result['category']} | 중요도: {result['importance']}")
            print(f"   파일: {result['file']}")

    elif args.command == "search":
        results = search_memories(
            query=args.query, category=args.category,
            tags=args.tags, importance=args.importance, limit=args.limit
        )
        if hasattr(args, 'json') and args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(f"\n검색 결과: {len(results)}건")
            for m in results:
                icon = {"critical": "[!]", "high": "[*]", "normal": "[ ]", "low": "[-]"}.get(m["importance"], "[ ]")
                print(f"  {icon} [{m['id']}] {m['title']} ({m['category']})")
                print(f"     태그: {', '.join(m['tags'])} | 생성: {m['created_at'][:10]}")

    elif args.command == "search-ai":
        result = search_similar_ai(query=args.query, limit=args.limit)
        if hasattr(args, 'json') and args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if result.get("success"):
                print(f"\n[AI 유사 경험 검색] 질의: {result['query']}")
                for m in result.get("results", []):
                    print(f"  [{m['id']}] {m['title']}")
                    if m.get("ai_relevance"):
                        print(f"     관련성: {m['ai_relevance']}")
                    if m.get("ai_score"):
                        print(f"     점수: {m['ai_score']}")
            else:
                print(f"AI 검색 실패: {result.get('error', '알 수 없는 오류')}")

    elif args.command == "advise":
        result = advise_from_experience(task_description=args.task)
        if hasattr(args, 'json') and args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\n[경험 기반 조언] 참조 기억: {result.get('memories_consulted', 0)}건")
            print(f"\n{result.get('advice', '조언 없음')}")

    elif args.command == "recall":
        result = recall_memory(args.memory_id)
        if result:
            if hasattr(args, 'json') and args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(result["content"])
        else:
            print(f"기억을 찾을 수 없습니다: {args.memory_id}", file=sys.stderr)

    elif args.command == "recent":
        results = list_recent(args.count)
        if hasattr(args, 'json') and args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(f"\n최근 기억 {len(results)}건:")
            for m in results:
                print(f"  [{m['id']}] {m['title']} ({m['category']}, {m['importance']})")

    elif args.command == "stats":
        stats = get_stats()
        if hasattr(args, 'json') and args.json:
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        else:
            print(f"\n기억 통계:")
            print(f"  총 기억: {stats['total']}건")
            print(f"  분류별:")
            for cat, cnt in stats.get("categories", {}).items():
                print(f"    {cat}: {cnt}건")


if __name__ == "__main__":
    main()
