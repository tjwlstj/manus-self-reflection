#!/usr/bin/env python3
"""
Memory Manager — 누스양의 경험 축적 및 검색 도구
작업 결과, 학습 내용, 실패 경험을 구조화하여 저장하고 검색한다.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

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
                 source_task: str = "") -> Dict:
    """
    새로운 기억 저장.

    Args:
        title: 기억 제목
        content: 기억 내용
        category: 분류 (insight, lesson, skill, fact, error, idea)
        tags: 검색용 태그
        importance: 중요도 (low, normal, high, critical)
        source_task: 출처 작업 설명

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
        "created_at": datetime.now().isoformat(),
        "file": memory_file,
        "access_count": 0,
    }

    # 마크다운 형식으로 기억 저장
    memory_content = f"""# {title}

- **분류**: {category}
- **중요도**: {importance}
- **태그**: {', '.join(tags or [])}
- **출처**: {source_task}
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
    기억 검색.

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
        # 필터 적용
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

    # 중요도 순 → 최신순 정렬
    importance_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
    results.sort(key=lambda m: (
        importance_order.get(m["importance"], 2),
        m["created_at"]
    ), reverse=False)

    return results[:limit]


def recall_memory(memory_id: str) -> Optional[Dict]:
    """
    특정 기억 전체 내용 조회.
    """
    index = load_index()
    for mem in index["memories"]:
        if mem["id"] == memory_id:
            # 접근 횟수 증가
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


def main():
    parser = argparse.ArgumentParser(description="Memory Manager — 경험 축적 도구")
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

    # search
    search_p = subparsers.add_parser("search", help="기억 검색")
    search_p.add_argument("--query", default="", help="검색어")
    search_p.add_argument("--category", default="", help="분류 필터")
    search_p.add_argument("--tags", nargs="+", help="태그 필터")
    search_p.add_argument("--importance", default="", help="중요도 필터")
    search_p.add_argument("--limit", type=int, default=10, help="최대 결과 수")

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
            tags=args.tags, importance=args.importance, source_task=args.source
        )
        if hasattr(args, 'json') and args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"✅ 기억 저장 완료: {result['id']}")
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
                icon = {"critical": "🔴", "high": "🟠", "normal": "🟢", "low": "⚪"}.get(m["importance"], "⚪")
                print(f"  {icon} [{m['id']}] {m['title']} ({m['category']})")
                print(f"     태그: {', '.join(m['tags'])} | 생성: {m['created_at'][:10]}")

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
