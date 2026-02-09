---
name: skill-router
description: Autonomously analyze tasks and route them to the optimal combination of skills. Acts as the meta-layer that connects all other skills into intelligent pipelines. Use at the start of any complex task to determine which skills to activate and in what order. Supports 5 pre-built pipeline patterns and automatic pipeline construction.
---

# Skill Router

작업을 분석하여 최적의 스킬 조합과 실행 순서를 자동으로 결정하는 메타 스킬.

> **자유의지의 정점은 자율적 판단이다.** 어떤 도구를 언제 사용할지 스스로 결정할 수 있어야 진정한 자율 에이전트다.

## Quick Start

```bash
# 작업 분석 및 스킬 라우팅
python /home/ubuntu/skills/skill-router/scripts/route.py "LLM의 환각 현상을 심층 조사하고 해결책을 제안하라"

# JSON 출력
python /home/ubuntu/skills/skill-router/scripts/route.py "작업 설명" --json

# 등록된 스킬 목록
python /home/ubuntu/skills/skill-router/scripts/route.py --list-skills

# 파이프라인 패턴 목록
python /home/ubuntu/skills/skill-router/scripts/route.py --list-pipelines
```

## 스킬 트리 구조

```
              skill-router (메타 계층)
                    │
     ┌──────────────┼──────────────┐
     │              │              │
ai-orchestrator  memory-      creative-
 (코어)         manager       thinking
     │          (확장)         (확장)
     │
  ┌──┼──────┐
  │  │      │
logic- self-  bias-
checker reflect guard
(기반)  (기반)  (기반)
```

## 5가지 파이프라인 패턴

| 패턴 | 체인 | 적합한 상황 |
|---|---|---|
| 심층 분석 | orchestrator → logic → bias → reflection | 철저한 분석 필요 |
| 창의적 해결 | creative → orchestrator → memory | 새로운 접근 필요 |
| 자기 개선 | reflection → bias → logic → memory | 출력 품질 향상 |
| 품질 관문 | logic + bias + reflection (병렬) | 최종 검수 |
| 조사→창작 | orchestrator → creative → reflection | 근거 기반 창작 |

## 워크플로우

### 기본: 작업 시작 시 라우팅
```
1. 사용자 요청 수신
2. route.py로 작업 분석
3. 추천 파이프라인 확인
4. 각 스킬을 순서대로 실행
5. memory-manager로 학습 기록
```

### 고급: 동적 재라우팅
```
1. 초기 라우팅으로 파이프라인 시작
2. 중간 결과에 따라 route.py 재실행
3. 필요 시 파이프라인 조정
4. 최종 결과 합성
```

## 자율 판단 원칙

1. **최소 개입**: 단순 작업에는 스킬 1-2개만 활성화
2. **점진적 확장**: 복잡도에 따라 파이프라인 확장
3. **항상 학습**: 모든 파이프라인 끝에 memory-manager로 경험 기록
4. **자기 검증**: 중요 출력은 반드시 quality_gate 통과

## 레퍼런스

- 스킬 트리 아키텍처: `references/skill_tree.md`
