# 기억 스키마 레퍼런스

## 인덱스 구조 (index.json)

```json
{
  "memories": [
    {
      "id": "mem_20260210_123456_0",
      "title": "기억 제목",
      "category": "insight",
      "tags": ["태그1", "태그2"],
      "importance": "high",
      "source_task": "원본 작업 설명",
      "created_at": "2026-02-10T12:34:56",
      "file": "/home/ubuntu/memories/mem_20260210_123456_0.md",
      "access_count": 3
    }
  ],
  "stats": {
    "total": 1,
    "categories": {"insight": 1}
  }
}
```

## 기억 파일 형식 (.md)

각 기억은 독립적인 마크다운 파일로 저장되어 사람이 직접 읽고 편집할 수 있다.

## 검색 우선순위

1. 중요도 (critical > high > normal > low)
2. 생성일 (최신 우선)
3. 접근 횟수 (자주 참조된 기억 우선)

## 다른 스킬과의 연계

- **self-reflection** → 성찰 결과를 `lesson`으로 저장
- **bias-guard** → 편향 감지 패턴을 `insight`로 저장
- **creative-thinking** → 아이디어를 `idea`로 저장
- **logic-checker** → 오류 패턴을 `error`로 저장
- **ai-orchestrator** → 효과적인 역할 배분을 `skill`로 저장
