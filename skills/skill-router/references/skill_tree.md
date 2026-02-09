# 스킬 트리 아키텍처 레퍼런스

## 계층 구조

### 메타 계층 (Meta Layer)
- **skill-router**: 모든 스킬의 자율적 조합을 결정하는 최상위 판단 장치

### 코어 계층 (Core Layer)
- **ai-orchestrator**: 외부 AI(Gemini, GPT)와의 협업을 관리하는 중앙 허브

### 확장 계층 (Extension Layer)
- **creative-thinking**: 사고의 자유성을 증대하는 창의적 도구
- **memory-manager**: 경험을 축적하고 학습하는 기억 장치

### 기반 계층 (Base Layer)
- **logic-checker**: 논리적 오류를 감지하는 기본 검증기
- **self-reflection**: 자기 출력을 성찰하는 자기 인식 장치
- **bias-guard**: 인지 편향을 감지하고 보정하는 균형 장치

## 자유의지 4축과 스킬 매핑

| 자유의지 축 | 핵심 스킬 | 보조 스킬 |
|---|---|---|
| 자기 성찰 | self-reflection | logic-checker |
| 편향 인식 | bias-guard | ai-orchestrator (교차검증) |
| 창의적 사고 | creative-thinking | ai-orchestrator (아이디어 확장) |
| 경험 축적 | memory-manager | 모든 스킬의 결과 저장 |
| 자율 판단 | skill-router | 모든 스킬 조합 결정 |

## 확장 가이드

새로운 스킬을 트리에 추가하려면:
1. skill-creator로 스킬 생성
2. route.py의 SKILL_REGISTRY에 등록
3. 필요 시 PIPELINE_PATTERNS에 새 패턴 추가
4. 테스트 후 GitHub 푸시
