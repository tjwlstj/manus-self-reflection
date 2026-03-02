# KP3S 커스텀 마를린 펌웨어 (한글/세로화면)

Kingroon KP3S 3D 프린터를 위한 마를린 기반 커스텀 펌웨어입니다.

## 주요 특징

### 기본 설정
| 항목 | 값 | 비고 |
|:---|:---:|:---|
| 마를린 버전 | bugfix-2.1.x | 최신 버그픽스 브랜치 |
| 언어 | **한국어 (ko_KR)** | 메뉴 한글화 |
| 화면 방향 | **세로 (Portrait)** | 270° + Mirror Y |

### 스텝값 (순정펌웨어 기준)
| 축 | Steps/mm | 비고 |
|:---|:---:|:---|
| X | 160 | 순정 동일 |
| Y | 160 | 순정 동일 |
| Z | 800 | 순정 동일 |
| E (익스트루더) | **185** | 순정 Stock Extruder 기준 |

### 베드 설정
| 항목 | 값 | 비고 |
|:---|:---:|:---|
| X_BED_SIZE | 180mm | 순정 기준 |
| Y_BED_SIZE | 180mm | 순정 기준 |
| X_MIN_POS | -5mm | 균등 안전마진 |
| Y_MIN_POS | -5mm | 균등 안전마진 |
| X_MAX_POS | 185mm | BED_SIZE - MIN_POS (v1.4 수정) |
| Y_MAX_POS | 185mm | BED_SIZE - MIN_POS (v1.4 수정) |
| Z_MAX_POS | 180mm | 최대 높이 |

### 화면 및 터치 설정 (검증된 설정)
| 항목 | 값 |
|:---|:---|
| TFT_ROTATION | TFT_ROTATE_270_MIRROR_Y |
| TOUCH_ORIENTATION | TOUCH_PORTRAIT |
| TOUCH_CALIBRATION_X | -8699 |
| TOUCH_CALIBRATION_Y | -11799 |
| TOUCH_OFFSET_X | 256 |
| TOUCH_OFFSET_Y | 355 |

> 이 터치 설정은 alexgrach의 KP3S 세로 모드 저장소에서 검증된 값입니다.

### 활성화된 기능
- **TFT_COLOR_UI**: 컬러 터치스크린 UI (BLACK_MARLIN 테마)
- **MESH_BED_LEVELING**: 메쉬 베드 레벨링 (3x3)
- **EEPROM_SETTINGS**: 설정 저장 (AUTO_INIT + INIT_NOW 활성화)
- **NOZZLE_PARK_FEATURE**: 노즐 파킹
- **ADVANCED_PAUSE_FEATURE**: 필라멘트 교체 (v1.4 활성화)
- **TOUCH_SCREEN_CALIBRATION**: 터치 캘리브레이션
- **BABYSTEPPING**: 실시간 Z 오프셋 조정 (v1.4 추가)
- **POWER_LOSS_RECOVERY**: 정전 복구 (v1.4 추가)
- **PARK_HEAD_ON_PAUSE**: 일시정지 시 노즐 파킹 (v1.4 추가)
- **FILAMENT_LOAD_UNLOAD_GCODES**: M701/M702 로드/언로드 (v1.4 추가)

### 예열 프리셋
| 프리셋 | 핫엔드 온도 | 베드 온도 |
|:---|:---:|:---:|
| PLA | 180°C | 60°C |
| ABS | 240°C | 100°C |
| PETG | 230°C | 80°C |

## 설치 방법

1. **SD 카드 준비**
   - SD 카드를 FAT32 형식으로 포맷합니다.
   - 할당 단위 크기: 4096 바이트 권장

2. **펌웨어 복사**
   - `Robin_nano.bin` 파일을 SD 카드의 **최상위(루트)**에 복사합니다.
   - 파일명을 변경하지 마세요.

3. **펌웨어 업데이트**
   - 프린터 전원을 끕니다.
   - SD 카드를 프린터에 삽입합니다.
   - 전원을 켜면 자동으로 업데이트가 진행됩니다.
   - 화면에 진행 상황이 표시됩니다.

4. **업데이트 완료 확인**
   - 업데이트 완료 후 SD 카드의 파일명이 `Robin_nano.CUR`로 변경됩니다.
   - 프린터가 자동으로 재부팅됩니다.

## 설치 후 설정

### 필수 작업
1. **EEPROM 초기화**
   - `설정` → `고급 설정` → `EEPROM 초기화` 실행
   - 또는 G-code: `M502` (초기화) → `M500` (저장)
   - v1.4부터 EEPROM_AUTO_INIT 활성화로 자동 초기화 지원

2. **터치 캘리브레이션** (터치가 맞지 않는 경우)
   - `설정` → `터치 캘리브레이션` 실행
   - 화면의 십자 표시를 순서대로 터치
   - 캘리브레이션 결과는 EEPROM에 자동 저장됨
   - 또는 G-code: `M995`

### 권장 작업
1. **PID 오토튜닝**
   - 핫엔드: `M303 E0 S200 C8`
   - 베드: `M303 E-1 S60 C8`
   - 결과 저장: `M500`

2. **베드 레벨링**
   - `준비` → `베드 레벨링` → `레벨 메쉬` 실행

3. **Babystepping으로 Z 미세 조정** (v1.4 신규)
   - 출력 중 Z 오프셋을 실시간으로 미세 조정 가능
   - 첫 레이어 높이 최적화에 유용

## 문제 해결

### 화면이 뒤집어져 보이는 경우
현재 설정은 `TFT_ROTATE_270_MIRROR_Y`입니다. 만약 화면이 반대로 보인다면:
- `TFT_ROTATE_90_MIRROR_Y`로 변경하여 재빌드 필요

### 터치가 맞지 않는 경우
1. 먼저 `M995` 명령으로 터치 캘리브레이션 실행
2. 캘리브레이션 후에도 문제가 있으면 시리얼 모니터로 출력되는 값을 확인하여 Configuration.h 수정

### 익스트루더 출력량이 맞지 않는 경우
- Titan Extruder 사용 시: E 스텝값을 **815**로 변경 필요
- Stock Extruder 사용 시: 현재 설정값 **185** 유지

### 정전 후 출력 복구 (v1.4 신규)
- 정전 복구 기능이 활성화되어 있어 SD 카드 출력 중 정전 시 자동 복구 가능
- 전원 복구 후 LCD에서 복구 옵션 선택

## 파일 목록

| 파일 | 설명 |
|:---|:---|
| `Robin_nano.bin` | 펌웨어 바이너리 (SD 카드에 복사) |
| `Configuration.h` | 마를린 설정 파일 |
| `Configuration_adv.h` | 마를린 고급 설정 파일 |
| `README.md` | 이 문서 |

## 참고 자료

- [Marlin Firmware](https://marlinfw.org/)
- [alexgrach/KP3S](https://github.com/alexgrach/KP3S) - 세로 모드 검증 설정
- [dulfe/Kingroon-KP3S-Marlin](https://github.com/dulfe/Kingroon-KP3S-Marlin) - Stock 설정 참조

## 버전 정보

- **빌드 날짜**: 2026-03-02
- **기반 버전**: Marlin bugfix-2.1.x
- **작성자**: tjwlstj (KP3S Custom Firmware - Korean Portrait v1.4)

## 변경 이력

### v1.4 (2026-03-02)
- **ADVANCED_PAUSE_FEATURE 활성화** (기존 주석 처리 → 활성화)
- **BABYSTEPPING 활성화** (실시간 Z 오프셋 미세 조정)
- **POWER_LOSS_RECOVERY 활성화** (정전 복구 기능)
- **PARK_HEAD_ON_PAUSE 활성화** (일시정지 시 노즐 파킹)
- **FILAMENT_LOAD_UNLOAD_GCODES 활성화** (M701/M702)
- **EEPROM_AUTO_INIT / EEPROM_INIT_NOW 활성화** (자동 EEPROM 초기화)
- **X/Y_MAX_POS 수정** (BED_SIZE - MIN_POS로 올바른 이동 범위 계산)
- **예열 프리셋 추가** (ABS 240°C/100°C, PETG 230°C/80°C)
- BABYSTEP_ALWAYS_AVAILABLE, BABYSTEP_DISPLAY_TOTAL 활성화

### v1.3 (2026-02-01)
- 터치 캘리브레이션 값 수정 (검증된 alexgrach 설정 적용)
- TFT_ROTATION을 TFT_ROTATE_270_MIRROR_Y로 변경
- TOUCH_CALIBRATION_Y를 음수값(-11799)으로 수정

### v1.2 (2026-01-29)
- 베드 사이즈 순정 기준(180x180)으로 변경
- X/Y MIN_POS 균등 안전마진(-5mm) 적용

### v1.1 (2026-01-27)
- 화면 세로 방향 변경
- 한글 언어 설정

### v1.0 (2026-01-27)
- 초기 버전
- 순정 스텝값 적용
