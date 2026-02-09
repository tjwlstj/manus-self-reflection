# 논리 오류 유형 레퍼런스

LLM이 범하기 쉬운 10가지 논리적 오류 패턴과 감지 기준.

## 현재 감지 가능 (5종)

| 오류 | 핵심 패턴 | 심각도 |
|---|---|---|
| 순환논증 (Circular Reasoning) | 결론이 전제를 반복 | high |
| 허수아비 논증 (Straw Man) | 상대 주장 왜곡 후 공격 | medium |
| 거짓 이분법 (False Dichotomy) | 양자택일만 제시 | medium |
| 성급한 일반화 (Hasty Generalization) | 불충분한 근거로 보편화 | high |
| 권위에의 호소 (Appeal to Authority) | 권위자 언급만으로 정당화 | low |

## 확장 예정 (5종)

| 오류 | 설명 | 감지 난이도 |
|---|---|---|
| 미끄러운 경사면 (Slippery Slope) | 극단적 결과를 근거 없이 연쇄 추론 | medium |
| 인신공격 (Ad Hominem) | 주장 대신 사람을 공격 | medium |
| 붉은 청어 (Red Herring) | 논점 이탈로 주의 분산 | hard |
| 확증 편향 (Confirmation Bias) | 기존 믿음에 부합하는 증거만 선택 | hard |
| 거짓 원인 (False Cause) | 상관관계를 인과관계로 오인 | hard |

## 감지 한계

- 현재 구현은 정규식 기반 휴리스틱으로, 문맥적 이해가 필요한 오류는 감지 어려움
- NER, 의미 유사도 분석 등 고급 NLP 기법 통합 시 정확도 향상 가능
- ai-orchestrator와 연계하여 Gemini/GPT에게 심층 분석을 위임하는 하이브리드 접근 권장
