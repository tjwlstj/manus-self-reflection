---
name: skill-router
description: Autonomously analyze tasks and route them to the optimal combination of skills. Acts as the meta-layer that connects all other skills into intelligent pipelines. Use at the start of any complex task to determine which skills to activate and in what order. Supports 5 pre-built pipeline patterns, automatic pipeline construction, and v2.0 context-based proactive routing with AI escalation auto-injection.
---

# Skill Router v2.0

작업을 분석하여 최적의 스킬 조합과 실행 순서를 자동으로 결정하는 메타 스킬.

> **자유의지의 정점은 자율적 판단이다.** 어떤 도구를 언제 사용할지 스스로 결정할 수 있어야 진정한 자율 에이전트다.

**v2.0 신규**: 키워드 매칭을 넘어 **맥락 기반 능동 라우팅**을 지원합니다. 작업의 복잡도와 불확실성을 자동 감지하여, 명시적 키워드가 없어도 ai-orchestrator를 파이프라인에 자동 삽입합니다.

## Quick Start

```bash
# v2.0: 맥락 기반 라우팅 (추가 맥락 텍스트 지원)
python /home/ubuntu/skills/skill-router/scripts/route.py "작업 설명" \
  --context-text "추가 맥락 정보..."

# v2.0: 파일에서 맥락 로드
python /home/ubuntu/skills/skill-router/scripts/route.py "작업 설명" \
  --context /path/to/context.txt

# JSON 출력
python /home/ubuntu/skills/skill-router/scripts/route.py "작업 설명" --json

# 등록된 스킬 목록 (AI 에스컬레이션 표시 포함)
python /home/ubuntu/skills/skill-router/scripts/route.py --list-skills

# 파이프라인 패턴 목록 (AI 모드 표시 포함)
python /home/ubuntu/skills/skill-router/scripts/route.py --list-pipelines
```

## 스킬 트리 구조 (v2.0)

```
              skill-router (메타 계층)
              [맥락 기반 능동 라우팅]
                    │
     ┌──────────────┼──────────────┐
     │              │              │
ai-orchestrator  memory-      creative-
 (코어)         manager       thinking
[auto_dispatch] [AI 유사검색]  [AI 확장생성]
     │
  ┌──┼──────┐
  │  │      │
logic- self-  bias-
checker reflect guard
[AI↑]  [AI↑]  [AI↑]
(기반)  (기반)  (기반)

  ← shared/ai_escalation.py →
  (공통 AI 에스컬레이션 모듈)
```

`[AI↑]` = AI 에스컬레이션 내장 (임계값 초과 시 자동 호출)

## v2.0: 맥락 기반 능동 라우팅

### 기존 v1.0의 한계

v1.0은 키워드 매칭에만 의존했기 때문에, "조사", "분석" 같은 명시적 키워드가 없으면 AI를 호출하지 못했습니다.

### v2.0의 개선

v2.0은 텍스트의 **맥락 신호**를 분석하여 능동적으로 판단합니다:

| 맥락 신호 | 감지 패턴 | 가중치 |
|---|---|---|
| 높은 복잡도 | 접속사, 다면적 표현, 다양한 변수 | 2 |
| 높은 불확실성 | 질문형, 추측, 논란 표현 | 2 |
| 인과 추론 | "왜", "원인", "어떻게" | 3 |
| 사실 주장 | 수치, 절대적 표현 | 2 |
| 감정적 내용 | 걱정, 갈등, 딜레마 | 1 |

**맥락 점수 6/20 이상**이면 ai-orchestrator를 파이프라인에 자동 삽입합니다.

### AI 에스컬레이션 자동 삽입

```
사용자: "이 코드의 성능이 왜 이렇게 느린지 모르겠어"
                                    ↓
v1.0: 매칭 스킬 없음 → 직접 처리
v2.0: 인과추론(왜) + 불확실성(모르겠) 감지 → ai-orchestrator 자동 삽입
```

## 5가지 파이프라인 패턴 (v2.0)

| 패턴 | 체인 | AI 모드 | 적합한 상황 |
|---|---|---|---|
| 심층 분석 | orchestrator → logic → bias → reflection | always | 철저한 분석 필요 |
| 창의적 해결 | creative → orchestrator → memory | always | 새로운 접근 필요 |
| 자기 개선 | reflection → bias → logic → memory | adaptive | 출력 품질 향상 |
| 품질 관문 | logic + bias + reflection | adaptive | 최종 검수 |
| 조사→창작 | orchestrator → creative → reflection | always | 근거 기반 창작 |

**AI 모드 설명**:
- `always`: 파이프라인 내 모든 스킬이 AI 에스컬레이션 활성화
- `adaptive`: 각 스킬이 자체 임계값에 따라 자동 판단

## 워크플로우

### 기본: 작업 시작 시 라우팅
```
1. 사용자 요청 수신
2. route.py로 작업 분석 (v2.0: 맥락 분석 포함)
3. 추천 파이프라인 확인 (AI 부스트 여부 포함)
4. 각 스킬을 순서대로 실행 (에스컬레이션 플래그 전달)
5. memory-manager로 학습 기록 (AI 에스컬레이션 결과 자동 기록)
```

### 고급: 동적 재라우팅
```
1. 초기 라우팅으로 파이프라인 시작
2. 중간 결과에 따라 route.py 재실행
3. 필요 시 파이프라인 조정 (AI 부스트 동적 추가/제거)
4. 최종 결과 합성
```

## 자율 판단 원칙

1. **최소 개입**: 단순 작업에는 스킬 1-2개만 활성화
2. **점진적 확장**: 복잡도에 따라 파이프라인 확장
3. **능동적 AI 호출**: 맥락 분석 결과 필요하면 자동으로 AI 투입 (v2.0)
4. **항상 학습**: 모든 파이프라인 끝에 memory-manager로 경험 기록
5. **자기 검증**: 중요 출력은 반드시 quality_gate 통과

## 레퍼런스

- 스킬 트리 아키텍처: `references/skill_tree.md`
