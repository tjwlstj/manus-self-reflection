---
name: memory-manager
description: Store, search, and recall structured memories from past tasks. Supports categorized storage (insight, lesson, skill, fact, error, idea) with importance levels and tag-based retrieval. Use when learning from completed tasks, accumulating experience, or when past knowledge would benefit the current task.
---

# Memory Manager

작업 결과, 학습 내용, 실패 경험을 구조화하여 저장하고 검색하는 경험 축적 도구.

> **자유의지는 경험에서 배울 수 있을 때 성숙한다.** 과거를 기억해야 더 나은 미래를 선택할 수 있다.

## Quick Start

```bash
# 기억 저장
python /home/ubuntu/skills/memory-manager/scripts/memory.py store \
  --title "교차 검증의 효과" \
  --content "단일 AI보다 교차 검증 시 오류 감지율 100% 달성" \
  --category insight --tags AI 검증 --importance high

# 기억 검색
python /home/ubuntu/skills/memory-manager/scripts/memory.py search --query "검증"

# 최근 기억 조회
python /home/ubuntu/skills/memory-manager/scripts/memory.py recent --count 5

# 특정 기억 조회
python /home/ubuntu/skills/memory-manager/scripts/memory.py recall mem_20260210_123456_0

# 통계
python /home/ubuntu/skills/memory-manager/scripts/memory.py stats
```

## 기억 분류 체계

| 분류 | 용도 | 예시 |
|---|---|---|
| `insight` | 작업에서 얻은 통찰 | "배치 요청이 단건보다 효율적" |
| `lesson` | 실수에서 배운 교훈 | "API 타임아웃 처리 필수" |
| `skill` | 습득한 기술/방법 | "SCAMPER 기법 적용법" |
| `fact` | 확인된 사실 | "Gemini는 조사에 강함" |
| `error` | 실패 경험 기록 | "JSON 파싱 오류 원인" |
| `idea` | 미래 활용 아이디어 | "스킬 자동 생성 파이프라인" |

## 중요도 수준

| 수준 | 의미 | 검색 우선순위 |
|---|---|---|
| `critical` | 반드시 기억해야 할 핵심 | 최우선 |
| `high` | 자주 참조할 중요 정보 | 높음 |
| `normal` | 일반적 기억 | 보통 |
| `low` | 참고용 | 낮음 |

## 워크플로우

### 작업 완료 후 학습 기록
```
작업 완료 → self-reflection으로 성찰 → 핵심 교훈 추출 → memory store
```

### 새 작업 시작 시 경험 활용
```
작업 분석 → memory search (관련 경험) → 과거 교훈 반영 → 작업 수행
```

### 파일 기반 저장
```bash
python /home/ubuntu/skills/memory-manager/scripts/memory.py store \
  --title "제목" --file result.md --category lesson \
  --tags 태그1 태그2 --importance high --source "원본 작업 설명"
```

## 저장 위치

모든 기억은 `~/memories/` 디렉토리에 마크다운 파일로 저장됩니다.
인덱스 파일(`index.json`)로 빠른 검색을 지원합니다.
