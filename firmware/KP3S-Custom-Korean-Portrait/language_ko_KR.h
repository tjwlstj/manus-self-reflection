/**
 * Marlin 3D Printer Firmware
 * Copyright (c) 2020 MarlinFirmware [https://github.com/MarlinFirmware/Marlin]
 *
 * Based on Sprinter and grbl.
 * Copyright (c) 2011 Camiel Gubbels / Erik van der Zalm
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 */
#pragma once

/**
 * Korean (한국어) - KP3S Custom Extended Translation v1.5
 *
 * LCD Menu Messages
 * See also https://marlinfw.org/docs/development/lcd_language.html
 *
 * Substitutions are applied for the following characters when used in menu items titles:
 *
 *   $ displays an inserted string
 *   { displays  '0'....'10' for indexes 0 - 10
 *   ~ displays  '1'....'11' for indexes 0 - 10
 *   * displays 'E1'...'E11' for indexes 0 - 10 (By default. Uses LCD_FIRST_TOOL)
 *   @ displays an axis name such as XYZUVW, or E for an extruder
 */

namespace LanguageNarrow_ko_KR {
  using namespace Language_en; // Inherit undefined strings from English

  constexpr uint8_t CHARSIZE              = 1;
  LSTR LANGUAGE                           = _UxGT("Korean");

  // === 기본 메시지 ===
  LSTR WELCOME_MSG                        = MACHINE_NAME_SUBST _UxGT(" 준비.");
  LSTR MSG_YES                            = _UxGT("예");
  LSTR MSG_NO                             = _UxGT("아니오");
  LSTR MSG_BACK                           = _UxGT("뒤로");
  LSTR MSG_MEDIA_INSERTED                 = _UxGT("카드 삽입됨");
  LSTR MSG_MEDIA_REMOVED                  = _UxGT("카드 제거됨");
  LSTR MSG_LCD_ENDSTOPS                   = _UxGT("엔드스탑");
  LSTR MSG_MAIN_MENU                      = _UxGT("메인 메뉴");
  LSTR MSG_RUN_AUTOFILES                  = _UxGT("자동 시작");

  // === 메뉴 항목 ===
  LSTR MSG_DISABLE_STEPPERS               = _UxGT("모터 정지");
  LSTR MSG_AUTO_HOME                      = _UxGT("오토홈");
  LSTR MSG_AUTO_HOME_X                    = _UxGT("X 홈으로");
  LSTR MSG_AUTO_HOME_Y                    = _UxGT("Y 홈으로");
  LSTR MSG_AUTO_HOME_Z                    = _UxGT("Z 홈으로");
  LSTR MSG_LEVEL_BED_HOMING               = _UxGT("XYZ 홈으로");
  LSTR MSG_LEVEL_BED_WAITING              = _UxGT("누르면 시작합니다");
  LSTR MSG_LEVEL_BED_NEXT_POINT           = _UxGT("다음 포인트");
  LSTR MSG_LEVEL_BED_DONE                 = _UxGT("레벨링 완료!");
  LSTR MSG_SET_HOME_OFFSETS               = _UxGT("홈 오프셋 설정");
  LSTR MSG_HOME_OFFSETS_APPLIED           = _UxGT("오프셋 적용됨");

  // === 예열 ===
  LSTR MSG_PREHEAT_1                      = _UxGT("예열 - ") PREHEAT_1_LABEL;
  LSTR MSG_PREHEAT_1_H                    = _UxGT("예열 - ") PREHEAT_1_LABEL " ~";
  LSTR MSG_PREHEAT_1_END                  = _UxGT("예열 - ") PREHEAT_1_LABEL _UxGT(" 노즐");
  LSTR MSG_PREHEAT_1_END_E                = _UxGT("예열 - ") PREHEAT_1_LABEL _UxGT(" 노즐 ~");
  LSTR MSG_PREHEAT_1_ALL                  = _UxGT("예열 - ") PREHEAT_1_LABEL _UxGT(" 전체");
  LSTR MSG_PREHEAT_1_BEDONLY              = _UxGT("예열 - ") PREHEAT_1_LABEL _UxGT(" 베드");
  LSTR MSG_PREHEAT_1_SETTINGS             = _UxGT("예열 - ") PREHEAT_1_LABEL _UxGT(" 설정");
  LSTR MSG_PREHEAT_M                      = _UxGT("예열 - $");
  LSTR MSG_PREHEAT_M_H                    = _UxGT("예열 - $ ~");
  LSTR MSG_PREHEAT_M_END                  = _UxGT("예열 - $ 노즐");
  LSTR MSG_PREHEAT_M_END_E                = _UxGT("예열 - $ 노즐 ~");
  LSTR MSG_PREHEAT_M_ALL                  = _UxGT("예열 - $ 전체");
  LSTR MSG_PREHEAT_M_BEDONLY              = _UxGT("예열 - $ 베드");
  LSTR MSG_PREHEAT_M_SETTINGS             = _UxGT("예열 - $ 설정");
  LSTR MSG_PREHEAT_CUSTOM                 = _UxGT("사용자 예열");
  LSTR MSG_COOLDOWN                       = _UxGT("냉각");

  // === 전원 ===
  LSTR MSG_SWITCH_PS_ON                   = _UxGT("전원 켜기");
  LSTR MSG_SWITCH_PS_OFF                  = _UxGT("전원 끄기");

  // === 압출 ===
  LSTR MSG_EXTRUDE                        = _UxGT("압출");
  LSTR MSG_RETRACT                        = _UxGT("리트랙트");
  LSTR MSG_MOVE_AXIS                      = _UxGT("축 이동");
  LSTR MSG_PROBE_AND_LEVEL                = _UxGT("프로브 & 레벨링");
  LSTR MSG_BED_LEVELING                   = _UxGT("베드 레벨링");
  LSTR MSG_LEVEL_BED                      = _UxGT("베드 레벨링");
  LSTR MSG_MESH_LEVELING                  = _UxGT("메쉬 레벨링");

  // === 이동 ===
  LSTR MSG_MOVE_X                         = _UxGT("X 이동");
  LSTR MSG_MOVE_Y                         = _UxGT("Y 이동");
  LSTR MSG_MOVE_Z                         = _UxGT("Z 이동");
  LSTR MSG_MOVE_N                         = _UxGT("@ 이동");
  LSTR MSG_MOVE_E                         = _UxGT("압출기 이동");
  LSTR MSG_MOVE_EN                        = _UxGT("압출기 * 이동");
  LSTR MSG_MOVE_N_MM                      = _UxGT("$mm 이동");
  LSTR MSG_MOVE_N_IN                      = _UxGT("$in 이동");
  LSTR MSG_SPEED                          = _UxGT("속도");
  LSTR MSG_MESH_Z_OFFSET                  = _UxGT("베드 Z");
  LSTR MSG_NOZZLE                         = _UxGT("노즐");
  LSTR MSG_NOZZLE_N                       = _UxGT("노즐 ~");
  LSTR MSG_BED                            = _UxGT("베드");
  LSTR MSG_FAN_SPEED                      = _UxGT("팬 속도");
  LSTR MSG_FAN_SPEED_N                    = _UxGT("팬 속도 ~");
  LSTR MSG_EXTRA_FAN_SPEED                = _UxGT("보조 팬 속도");
  LSTR MSG_EXTRA_FAN_SPEED_N              = _UxGT("보조 팬 속도 ~");
  LSTR MSG_FLOW                           = _UxGT("유량");
  LSTR MSG_FLOW_N                         = _UxGT("유량 ~");
  LSTR MSG_CONTROL                        = _UxGT("제어");
  LSTR MSG_TEMPERATURE                    = _UxGT("온도");
  LSTR MSG_MOTION                         = _UxGT("동작");

  // === 설정 ===
  LSTR MSG_ADVANCED_SETTINGS              = _UxGT("고급 설정");
  LSTR MSG_CONFIGURATION                  = _UxGT("설정");
  LSTR MSG_STORE_EEPROM                   = _UxGT("설정 저장");
  LSTR MSG_LOAD_EEPROM                    = _UxGT("설정 불러오기");
  LSTR MSG_RESTORE_DEFAULTS               = _UxGT("초기값 복원");
  LSTR MSG_INIT_EEPROM                    = _UxGT("EEPROM 초기화");
  LSTR MSG_REFRESH                        = LCD_STR_REFRESH _UxGT("새로고침");
  LSTR MSG_INFO_SCREEN                    = _UxGT("정보 화면");
  LSTR MSG_PREPARE                        = _UxGT("준비");
  LSTR MSG_TUNE                           = _UxGT("조정");

  // === 출력 ===
  LSTR MSG_PAUSE_PRINT                    = _UxGT("일시정지");
  LSTR MSG_RESUME_PRINT                   = _UxGT("재시작");
  LSTR MSG_STOP_PRINT                     = _UxGT("출력 중지");
  LSTR MSG_MEDIA_MENU                     = _UxGT("SD 카드 출력");
  LSTR MSG_NO_MEDIA                       = _UxGT("SD 카드 없음");
  LSTR MSG_DWELL                          = _UxGT("대기중...");
  LSTR MSG_PRINT_PAUSED                   = _UxGT("일시 정지됨");
  LSTR MSG_PRINTING                       = _UxGT("출력중...");
  LSTR MSG_PRINT_ABORTED                  = _UxGT("출력 취소됨");
  LSTR MSG_NO_MOVE                        = _UxGT("이동 불가");
  LSTR MSG_KILLED                         = _UxGT("오류 발생");
  LSTR MSG_STOPPED                        = _UxGT("정지됨");
  LSTR MSG_USERWAIT                       = _UxGT("눌러서 재개...");

  // === 온도 / 가열 ===
  LSTR MSG_HEATING                        = _UxGT("가열중...");
  LSTR MSG_BED_HEATING                    = _UxGT("베드 가열중...");
  LSTR MSG_COOLING                        = _UxGT("냉각중...");
  LSTR MSG_BED_COOLING                    = _UxGT("베드 냉각중...");
  LSTR MSG_ERR_HEATING_FAILED             = _UxGT("가열 실패");
  LSTR MSG_ERR_REDUNDANT_TEMP             = _UxGT("온도 센서 오류");
  LSTR MSG_ERR_THERMAL_RUNAWAY            = _UxGT("온도 폭주");
  LSTR MSG_ERR_MAXTEMP                    = _UxGT("최고 온도 초과");
  LSTR MSG_ERR_MINTEMP                    = _UxGT("최저 온도 미달");

  // === PID ===
  LSTR MSG_PID_AUTOTUNE                   = _UxGT("PID 자동 튜닝");
  LSTR MSG_PID_AUTOTUNE_START             = _UxGT("PID 튜닝 시작");
  LSTR MSG_PID_AUTOTUNE_DONE              = _UxGT("PID 튜닝 완료");
  LSTR MSG_PID_P                          = _UxGT("PID-P");
  LSTR MSG_PID_P_E                        = _UxGT("PID-P *");
  LSTR MSG_PID_I                          = _UxGT("PID-I");
  LSTR MSG_PID_I_E                        = _UxGT("PID-I *");
  LSTR MSG_PID_D                          = _UxGT("PID-D");
  LSTR MSG_PID_D_E                        = _UxGT("PID-D *");

  // === 동작 설정 ===
  LSTR MSG_ACCELERATION                   = _UxGT("가속도");
  LSTR MSG_A_RETRACT                      = _UxGT("리트랙트 가속도");
  LSTR MSG_A_TRAVEL                       = _UxGT("이동 가속도");
  LSTR MSG_STEPS_PER_MM                   = _UxGT("스텝/mm");
  LSTR MSG_A_STEPS                        = STR_A _UxGT(" 스텝/mm");
  LSTR MSG_B_STEPS                        = STR_B _UxGT(" 스텝/mm");
  LSTR MSG_C_STEPS                        = STR_C _UxGT(" 스텝/mm");
  LSTR MSG_N_STEPS                        = _UxGT("@ 스텝/mm");
  LSTR MSG_E_STEPS                        = _UxGT("E 스텝/mm");
  LSTR MSG_EN_STEPS                       = _UxGT("* 스텝/mm");
  LSTR MSG_VELOCITY                       = _UxGT("속도");
  LSTR MSG_VMAX_A                         = _UxGT("최대속도 ") STR_A;
  LSTR MSG_VMAX_B                         = _UxGT("최대속도 ") STR_B;
  LSTR MSG_VMAX_C                         = _UxGT("최대속도 ") STR_C;
  LSTR MSG_VMAX_N                         = _UxGT("최대속도 @");
  LSTR MSG_VMAX_E                         = _UxGT("최대속도 E");
  LSTR MSG_VMAX_EN                        = _UxGT("최대속도 *");
  LSTR MSG_VMIN                           = _UxGT("최소속도");
  LSTR MSG_VTRAV_MIN                      = _UxGT("최소 이동속도");
  LSTR MSG_AMAX_A                         = _UxGT("최대가속 ") STR_A;
  LSTR MSG_AMAX_B                         = _UxGT("최대가속 ") STR_B;
  LSTR MSG_AMAX_C                         = _UxGT("최대가속 ") STR_C;
  LSTR MSG_AMAX_N                         = _UxGT("최대가속 @");
  LSTR MSG_AMAX_E                         = _UxGT("최대가속 E");
  LSTR MSG_AMAX_EN                        = _UxGT("최대가속 *");
  LSTR MSG_JERK                           = _UxGT("저크");
  LSTR MSG_VA_JERK                        = _UxGT("저크-") STR_A;
  LSTR MSG_VB_JERK                        = _UxGT("저크-") STR_B;
  LSTR MSG_VC_JERK                        = _UxGT("저크-") STR_C;
  LSTR MSG_VN_JERK                        = _UxGT("저크-@");
  LSTR MSG_VE_JERK                        = _UxGT("저크-E");

  // === 필라멘트 ===
  LSTR MSG_FILAMENT                       = _UxGT("필라멘트");
  LSTR MSG_FILAMENT_DIAM                  = _UxGT("필라멘트 직경");
  LSTR MSG_FILAMENT_DIAM_E                = _UxGT("필라멘트 직경 *");
  LSTR MSG_FILAMENTCHANGE                 = _UxGT("필라멘트 교체");
  LSTR MSG_FILAMENTCHANGE_E               = _UxGT("필라멘트 교체 *");
  LSTR MSG_FILAMENTLOAD                   = _UxGT("필라멘트 삽입");
  LSTR MSG_FILAMENTLOAD_E                 = _UxGT("필라멘트 삽입 *");
  LSTR MSG_FILAMENTUNLOAD                 = _UxGT("필라멘트 제거");
  LSTR MSG_FILAMENTUNLOAD_E               = _UxGT("필라멘트 제거 *");
  LSTR MSG_FILAMENTUNLOAD_ALL             = _UxGT("전체 제거");

  // === 필라멘트 교체 화면 ===
  LSTR MSG_FILAMENT_CHANGE_HEADER         = _UxGT("필라멘트 교체");
  LSTR MSG_FILAMENT_CHANGE_HEADER_PAUSE   = _UxGT("출력 일시정지");
  LSTR MSG_FILAMENT_CHANGE_HEADER_LOAD    = _UxGT("필라멘트 삽입");
  LSTR MSG_FILAMENT_CHANGE_HEADER_UNLOAD  = _UxGT("필라멘트 제거");
  LSTR MSG_FILAMENT_CHANGE_OPTION_HEADER  = _UxGT("재개 옵션:");
  LSTR MSG_FILAMENT_CHANGE_OPTION_PURGE   = _UxGT("더 압출하기");
  LSTR MSG_FILAMENT_CHANGE_OPTION_RESUME  = _UxGT("출력 재개");
  LSTR MSG_FILAMENT_CHANGE_INIT           = _UxGT(MSG_1_LINE("잠시 기다려주세요..."));
  LSTR MSG_FILAMENT_CHANGE_INSERT         = _UxGT(MSG_1_LINE("삽입 후 눌러주세요"));
  LSTR MSG_FILAMENT_CHANGE_UNLOAD         = _UxGT(MSG_1_LINE("제거중..."));
  LSTR MSG_FILAMENT_CHANGE_LOAD           = _UxGT(MSG_1_LINE("삽입중..."));
  LSTR MSG_FILAMENT_CHANGE_PURGE          = _UxGT(MSG_1_LINE("압출중..."));
  LSTR MSG_FILAMENT_CHANGE_CONT_PURGE     = _UxGT(MSG_1_LINE("눌러서 완료"));
  LSTR MSG_FILAMENT_CHANGE_HEATING        = _UxGT(MSG_1_LINE("가열중..."));
  LSTR MSG_FILAMENT_CHANGE_HEAT           = _UxGT(MSG_1_LINE("눌러서 가열"));

  // === 필라멘트 런아웃 ===
  LSTR MSG_FILAMENT_RUNOUT_SENSOR         = _UxGT("필라멘트 센서");

  // === 베이비스텝 ===
  LSTR MSG_BABYSTEP_X                     = _UxGT("미세조정 X");
  LSTR MSG_BABYSTEP_Y                     = _UxGT("미세조정 Y");
  LSTR MSG_BABYSTEP_Z                     = _UxGT("미세조정 Z");
  LSTR MSG_BABYSTEP_N                     = _UxGT("미세조정 @");
  LSTR MSG_BABYSTEP_PROBE_Z               = _UxGT("Z 미세조정");
  LSTR MSG_BABYSTEP_TOTAL                 = _UxGT("합계");

  // === 정전 복구 ===
  LSTR MSG_OUTAGE_RECOVERY                = _UxGT("정전 복구");

  // === 리트랙트 ===
  LSTR MSG_CONTROL_RETRACT                = _UxGT("리트랙트 mm");
  LSTR MSG_CONTROL_RETRACT_SWAP           = _UxGT("교체 리트랙트 mm");
  LSTR MSG_CONTROL_RETRACTF               = _UxGT("리트랙트 속도");
  LSTR MSG_CONTROL_RETRACT_ZHOP           = _UxGT("Z 홉 mm");
  LSTR MSG_CONTROL_RETRACT_RECOVER        = _UxGT("복귀 mm");
  LSTR MSG_CONTROL_RETRACT_RECOVER_SWAP   = _UxGT("교체 복귀 mm");
  LSTR MSG_CONTROL_RETRACT_RECOVERF       = _UxGT("복귀 속도");
  LSTR MSG_AUTORETRACT                    = _UxGT("자동 리트랙트");

  // === 버튼 ===
  LSTR MSG_BUTTON_PRINT                   = _UxGT("출력");
  LSTR MSG_BUTTON_RESET                   = _UxGT("리셋");
  LSTR MSG_BUTTON_CANCEL                  = _UxGT("취소");
  LSTR MSG_BUTTON_DONE                    = _UxGT("완료");
  LSTR MSG_BUTTON_BACK                    = _UxGT("뒤로");
  LSTR MSG_BUTTON_PROCEED                 = _UxGT("진행");
  LSTR MSG_BUTTON_SKIP                    = _UxGT("건너뛰기");

  // === 엔드스탑 ===
  LSTR MSG_LCD_SOFT_ENDSTOPS              = _UxGT("소프트 엔드스탑");
  LSTR MSG_ENDSTOP_ABORT                  = _UxGT("엔드스탑 중단");

  // === 정보 ===
  LSTR MSG_INFO_MENU                      = _UxGT("프린터 정보");
  LSTR MSG_INFO_PRINTER_MENU              = _UxGT("프린터 정보");
  LSTR MSG_INFO_STATS_MENU                = _UxGT("통계");
  LSTR MSG_INFO_BOARD_MENU                = _UxGT("보드 정보");
  LSTR MSG_INFO_THERMISTOR_MENU           = _UxGT("서미스터");
  LSTR MSG_INFO_EXTRUDERS                 = _UxGT("압출기");
  LSTR MSG_INFO_BAUDRATE                  = _UxGT("통신속도");
  LSTR MSG_INFO_PROTOCOL                  = _UxGT("프로토콜");
  LSTR MSG_INFO_RUNAWAY_OFF               = _UxGT("감시 꺼짐");
  LSTR MSG_INFO_RUNAWAY_ON                = _UxGT("감시 켜짐");
  LSTR MSG_INFO_PRINT_COUNT               = _UxGT("출력 횟수");
  LSTR MSG_INFO_PRINT_TIME                = _UxGT("출력 시간");
  LSTR MSG_INFO_PRINT_LONGEST             = _UxGT("최장 출력");
  LSTR MSG_INFO_PRINT_FILAMENT            = _UxGT("사용 필라멘트");
  LSTR MSG_INFO_COMPLETED_PRINTS          = _UxGT("완료된 출력");
  LSTR MSG_INFO_MIN_TEMP                  = _UxGT("최저 온도");
  LSTR MSG_INFO_MAX_TEMP                  = _UxGT("최고 온도");

  // === 디버그 ===
  LSTR MSG_DEBUG_MENU                     = _UxGT("디버그 메뉴");
  LSTR MSG_PROGRESS_BAR_TEST              = _UxGT("진행바 테스트");

  // === 기타 ===
  LSTR MSG_CHANGE_MEDIA                   = _UxGT("SD 카드 교체");
  LSTR MSG_ZPROBE_OUT                     = _UxGT("Z 프로브 범위 초과");
  LSTR MSG_KILL_EXPECTED_PRINTER          = _UxGT("잘못된 프린터");
  LSTR MSG_IDEX_MODE_MIRRORED_COPY        = _UxGT("미러 사본");
  LSTR MSG_UBL_DOING_G29                  = _UxGT("오토레벨링 실행");

  // === 메쉬 레벨링 ===
  LSTR MSG_MESH_X                         = _UxGT("인덱스 X");
  LSTR MSG_MESH_Y                         = _UxGT("인덱스 Y");
  LSTR MSG_MESH_EDIT_Z                    = _UxGT("Z 값");
  LSTR MSG_EDITING_STOPPED                = _UxGT("메쉬 편집 중지");

  // === 터치 캘리브레이션 ===
  LSTR MSG_TOUCH_CALIBRATE                = _UxGT("터치 보정");
  LSTR MSG_MANUAL_CALIBRATE               = _UxGT("수동 보정");

  // === 전원 관련 ===
  LSTR MSG_HALTED                         = _UxGT("프린터 정지됨");
  LSTR MSG_PLEASE_RESET                   = _UxGT("리셋해 주세요");
  LSTR MSG_HEATING_FAILED_LCD             = _UxGT("가열 실패");

  // === SD 카드 ===
  LSTR MSG_SD_INIT_FAIL                   = _UxGT("SD 초기화 실패");
  LSTR MSG_SD_INSERTED                    = _UxGT("SD 카드 삽입됨");
  LSTR MSG_SD_REMOVED                     = _UxGT("SD 카드 제거됨");

  // === 기타 메뉴 ===
  LSTR MSG_DELTA_CALIBRATE                = _UxGT("델타 보정");
  LSTR MSG_LED_CONTROL                    = _UxGT("LED 제어");
  LSTR MSG_POWER_MONITOR                  = _UxGT("전력 모니터");
  LSTR MSG_CASE_LIGHT                     = _UxGT("케이스 조명");
  LSTR MSG_CASE_LIGHT_BRIGHTNESS          = _UxGT("조명 밝기");

  // === 출력 완료 ===
  LSTR MSG_PRINT_DONE                     = _UxGT("출력 완료");
}

namespace LanguageWide_ko_KR {
  using namespace LanguageNarrow_ko_KR;
  #if LCD_WIDTH > 20 || HAS_DWIN_E3V2
  #endif
}

namespace LanguageTall_ko_KR {
  using namespace LanguageWide_ko_KR;
  #if LCD_HEIGHT >= 4
    // Filament Change screens show up to 3 lines on a 4-line display
  #endif
}

namespace Language_ko_KR {
  using namespace LanguageTall_ko_KR;
}
