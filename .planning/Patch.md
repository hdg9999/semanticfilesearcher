# Patch History
## [2026-02-02] 이슈 조치 및 기능 고도화
- GUI 블로킹 문제 해결 (QThread 백그라운드 작업 도입)
- 하단 진행률 표시줄 및 상세 상태 정보 UI 추가
- 앱 시작 시 사용자 기본 폴더 인덱싱 권장 팝업 추가
- LLM 기반 자동 태그 엔진 외부화 및 추상화 (OpenAI, Gemini, Ollama, HuggingFace 지원)
- BFloat16 관련 텐서 변환 오류 수정

## [2026-02-02] 검색 기능 정상화 및 UI 고도화
- 벡터 데이터베이스(FAISS) 연동 누락 수정 (검색 실패 해결)
- 메인 윈도우 상단 메뉴 바 추가 ([파일] -> [설정])
- 설정 다이얼로그 구현 (폴더 관리, LLM 설정, 태그 조회)
- 다이얼로그 창 가시성 문제 해결 (글로벌 다크 테마 적용)
- QMessageBox 및 QMenu 다크 테마 보완 및 CSS 오타 수정
- 글로벌 QSS(Style Sheet) 시스템 도입 및 드롭다운(QComboBox) 가시성 해결
- main.py 실행 오류 수정 (os 임포트 및 indexer 초기화 누락 복구)

## [2026-02-02] UI/UX 대규모 고도화 및 백엔드 연동
- [UI] 목록형(List) / 아이콘형(Grid) 보기 모드 전환 기능 추가
- [UI] 우측 상세 정보 패널(Detail Pane) 추가 (단일 클릭 시 활성화)
- [UI] 검색 필터 강화 (검색 모드 드롭다운, 확장자 텍스트 필터 및 초기화 버튼)
- [UI] 파일 더블 클릭 시 연결 프로그램 실행 기능 추가
- [UI] 마우스 호버 시 '폴더 열기' 및 '추가 메뉴' 팝업 버튼 구현
- [Backend] ConfigManager 도입 (폴더 목록 및 LLM 설정 실시간 저장/복구)
- [Backend] 실시간 파일 변경 감지(Watchdog) 및 검색 필터 로직 보완

## [2026-02-02] 폴더 관리 기능 정상화
- [UI] 설정 창 폴더 관리 탭의 [추가], [삭제] 버튼 기능 구현
- [Core] 폴더 변경 감지 해제 로직(remove_path) 추가 및 연동
- [Fix] 이슈 #7 폴더 추가 미동작 문제 해결

## [2026-02-02] 파일 인덱싱 성능 개선 (Indexing Performance Improvement)
- `core/indexing/queue_manager.py`: 우선순위 큐(Priority Queue) 관리자 추가 (삭제 우선, 중복 제거).
- `core/indexing/monitor.py`: Watchdog 이벤트 처리 시 동기 실행 제거, 콜백 방식 적용.
- `core/indexer.py`: 백그라운드 워커 스레드 도입, UI 블로킹 방지.
  - (추가 수정) `index_folder` 메서드 내 동기식 스캔 로직을 비동기 스레드 + 큐 방식으로 변경하여 폴더 추가 시 프리징 현상 해결.
- `ui/queue_dialog.py`: 인덱싱 대기열 창에 현재 진행 중인 작업 표시 및 스피너(Spinner) 애니메이션 추가.
- `ui/main_window.py`: 인덱싱 대기열 상태 확인 UI 및 버튼 추가.

## [2026-02-02] 태그 관리 기능 구현 및 안정화
- `core/database/sqlite_manager.py`: 태그 CRUD(생성/조회/수정/삭제) 및 파일-태그 연동 API 구현. `contextlib` 도입으로 DB 연결 자원 누수(File Lock) 해결.
- `ui/tag_dialog.py`: 파일별 태그 선택 및 신규 태그 추가를 위한 전용 다이얼로그(TagSelectionDialog) 추가.
- `ui/settings_dialog.py`: 태그 관리 탭(전역 태그 추가/삭제/이름변경) 구현 및 LLM 설정 실시간 저장 로직 추가.
- `ui/main_window.py` 및 `ui/components/result_item.py`: 검색 결과 리스트에서 컨텍스트 메뉴를 통한 '태그 관리' 기능 연동.

## [2026-02-02] 태그 자동생성 엔진 개선
- `core/indexer.py`: 런타임 설정 변경 시 태그 생성기(Tagger)를 재초기화하는 `reload_tagger` 기능 추가.
- `ui/settings_dialog.py`: 설정 저장 시점에 자동으로 `reload_tagger`를 호출하여 LLM 설정 변경 사항 즉시 반영.
- `core/tagging/auto_tagger.py`: 태그 생성 실패 시 예외 처리 및 디버깅용 로그 출력 강화.

## [2026-02-02] LLM 패키지 마이그레이션
- Deprecated 된 `google-generativeai` 패키지를 최신 `google-genai` 패키지로 의존성 교체.
- `GeminiAdapter`를 `google-genai` SDK 인터페이스에 맞춰 리팩토링.

## [2026-02-02] 파일 감지 및 인덱싱 로직 최적화 (File Detection Logic Optimization)
- **중복/불필요 인덱싱 방지**
    - `core/database/sqlite_manager.py`: 메타데이터 조회 API (`get_file_metadata`) 추가.
    - `core/indexing/scanner.py`: 파일 처리(`process_file`) 시 DB에 저장된 수정 시간과 비교하여 변경이 없는 경우 **임베딩 생성 및 DB 업데이트 생략**.
    - `core/indexer.py`: 변경 감지 이벤트(`modified`) 수신 시 **큐에 작업을 추가하기 전에** DB 메타데이터를 확인하여, 단순 파일 액세스(Read)로 인한 **불필요한 대기열 진입 차단**.
- **검증**: `tests/test_file_skip.py` 및 `tests/test_queue_skip.py`를 통해 시나리오별(최초, 변경 없음, 내용 변경) 동작 검증 완료.

## [2026-02-03] 검색 결과 UI 개선 및 LLM 설정 고도화
- **UI 개선**: `ui/components/result_item.py`에서 `QFileIconProvider`를 도입하여 검색 결과의 파일 아이콘을 시스템 기본 아이콘으로 변경, 사용자 경험 개선.
- **LLM 설정 고도화**:
    - `ui/settings_dialog.py`: 설정 창에 `Base URL` 입력 필드 추가.
    - `core/config.py`: `Base URL` 값의 저장 및 로드 로직 구현.
    - `core/tagging/llm_adapters.py`: OpenAI 및 Ollama 어댑터가 사용자 정의 `Base URL`을 지원하도록 개선 (로컬 LLM, 프록시 등 다양한 환경 지원).
    - `core/indexer.py`: 인덱서 초기화 시 설정된 `Base URL`을 어댑터에 전달하도록 연동.

## [2026-02-03] 아이콘 보기 모드 레이아웃 개선 (Icon View Improvement)
- **반응형 그리드 레이아웃(FlowLayout) 도입**
    - `ui/components/flow_layout.py`: 창 크기에 따라 아이템을 자동으로 줄바꿈하여 배치하는 커스텀 레이아웃 구현.
    - `ui/main_window.py`: 보기 모드 전환(List/Icon)에 따라 `QVBoxLayout`과 `FlowLayout`을 동적으로 교체하는 로직 적용.
- **아이콘 뷰 스타일 개선**
    - `ui/components/result_item.py` 수정: 아이콘 모드 시 고정 크기(120x140) 적용 및 파일명 중앙 정렬, 줄바꿈 처리.

## [2026-02-03] UI/UX 개선 및 버그 수정 (UI/UX Improvements & Bug Fixes)
- **검색 결과(Search Result) UI 개선**
    - **클릭 선택 방식 도입**: 기존 호버(Hover) 시 하이라이트/버튼 표시 방식을 **클릭(Click)** 시 선택 상태로 변경하여 오동작 방지 및 명확한 UX 제공 (`ui/components/result_item.py`).
    - **우클릭 컨텍스트 메뉴(Context Menu) 추가**: 항목 우클릭 시 '파일 정보 보기', '태그 관리', '파일 삭제' 메뉴 표시 및 누락된 메뉴 항목 복구.
    - **상태 관리 개선**: `selected_item` 속성을 통해 단일 항목 선택 상태 관리 및 UI 동기화 (`ui/main_window.py`).

- **상세 정보 패널(Detail Pane) 고도화**
    - **크기 조절(Resizable) 기능**: `QSplitter`를 도입하여 사용자가 상세 패널의 너비를 자유롭게 조절 가능하도록 개선.
    - **초기 너비 최적화**: 검색 결과 영역과 상세 패널의 비율을 **9:1**로 설정하고 상세 패널 최소 너비를 180px로 축소하여 쾌적한 화면 구성.
    - **토글(Toggle) 기능 개선**: 토글 버튼을 텍스트에서 직관적인 **사이드바 아이콘(`sidebar_toggle_white.svg`)**으로 교체.
    - **아이콘 연동**: 파일 선택 시 상세 패널 헤더에 해당 파일의 시스템 아이콘을 표시하도록 연동.

- **대기열 대화상자(Queue Dialog) UI 수정**
    - **창 이동 및 크기 조절**: `Frameless` 스타일을 유지하면서 헤더 드래그로 **창 이동** 및 우측 하단 그립으로 **크기 조절** 기능 구현 (`ui/queue_dialog.py`).
    - **한글화(Localization)**: 대화상자의 모든 레이블(영어)을 **한글**로 번역 ("Indexing Queue" -> "대기열" 등).
    - **버그 수정**: 중복 생성되던 로딩 스피너 제거 및 닫기 버튼 스타일(흰색) 수정으로 가시성 확보.

- **레이아웃(Layout) 버그 수정**
    - 메인 윈도우 스플리터에 `stretch factor`를 적용하여 하단 공백 문제를 해결하고 검색 결과 리스트가 정상적으로 확장되도록 수정.

## [2026-02-04] 태그 검색 UI 및 로직 고도화
- **UI 개선**:
    - **TagInputWidget 도입**: 태그 입력을 위한 전용 위젯 구현. Tagify 스타일의 직관적인 UI 제공.
        - **기능**: 태그 자동완성, 태그 칩(Pill) 시각화, x 버튼 및 백스페이스를 이용한 간편 삭제.
        - **UX**: 입력창 가시성 및 포커스 문제 해결 (부모 위젯 설정 및 레이아웃 크기 계산 수정).
    - **검색창 레이아웃 변경**: 기존 '태그 검색' 모드를 제거하고, 메인 검색창 하단에 **태그 입력 전용 행(Row)** 추가.
        - AND/OR 논리 선택 드롭다운과 태그 입력창을 배치하여 접근성 향상.

- **Backend 개선**:
    - **멀티 태그 검색 필터링**: search_by_tags 메서드를 통해 다중 태그에 대한 AND/OR 검색 로직 구현.
    - **하이브리드 검색**: 텍스트 검색(Vector Search) 결과에 태그 필터를 결합하여 더욱 정밀한 검색 지원.

## [2026-02-04] 태그 관리(Tag Management) 설정 UI 안정화 및 기능 개선
- **가시성(Visibility) 및 레이아웃(Layout) 개선**
  - **태그 칩(Chip) 가시성 확보**: 배경색 밝기(Luminance)를 분석하여 텍스트 색상을 자동으로 `Black` 또는 `White`로 반전시키는 알고리즘 적용. 밝은 배경의 태그도 텍스트가 명확하게 보임 (`ui/settings_dialog.py`).
  - **목록 레이아웃 최적화**: 글로벌 스타일(`style.qss`)의 과도한 패딩(10px)이 리스트 아이템 높이를 잠식하는 문제 해결.
    - 태그 목록 위젯에만 인라인 스타일로 패딩을 축소(`2px`)하고, 아이템 높이를 `50px`로 확장하여 태그 텍스트가 잘리지 않고 온전하게 표시되도록 수정.
    - `min-width` 제약을 완화하고 `Preferred` 정책을 사용하여 태그 길이에 따라 칩 크기가 유연하게 늘어나도록 개선.

- **데이터 동기화(Synchronization) 및 지속성(Persistence) 강화**
  - **색상 변경 즉시 반영**: 설정 창에서 태그 색상 변경 시, 메인 윈도우의 태그 자동완성 목록 및 이미 입력된 태그 칩에도 변경된 색상을 실시간으로 전파하는 로직 추가 (`TagInputWidget.update_color`).
  - **색상 초기화 버그 수정**: 태그를 지우거나 앱을 재시작했을 때 태그 색상이 기본값(파란색)으로 초기화되는 버그 수정. 태그 생성(`add_tag`) 시 DB 및 메모리에 저장된 색상 정보를 우선 조회하여 일관성 유지.

## [2026-02-05] 태그 입력 UI 가시성 수정 (Tag Input UI Visibility Fix)
- `ui/components/tag_input.py`:
    - **태그 높이 증가**: 24px -> 28px로 변경하여 텍스트 잘림 현상 해결 및 수직 정렬 개선.
    - **디자인 개선**: Border Radius를 14px로 증가시켜 더 부드러운 알약(Pill) 형태로 변경.
    - **가시성 버그 수정**:
        - 닫기 버튼(x): `background-color: transparent` 강제 적용 및 글로벌 스타일(`padding`) 초기화로 텍스트 잘림 해결. `font-size: 14px`로 가독성 확보.
        - 태그 텍스트: `QLabel`에 `background-color: transparent`를 명시하여 불필요한 배경색 제거.
        - **[Hotfix]** 리팩토링 중 누락된 `QLabel` 초기화 코드(`self.label = QLabel(text)`) 복구하여 `AttributeError` 해결.
    - **자동완성 목록 가시성 개선**: `QCompleter` 팝업 뷰(`QListView`)에 다크 테마 스타일시트 적용(배경 `#252526`, 텍스트 `#cccccc`, 선택 시 `#007acc`).
    - **태그 텍스트 가시성 개선**: 태그 텍스트 하단에 미세한 검은 줄이 보이는 문제 해결을 위해 `TagLabel`에 `border: none` 및 `QLabel`에 `text-decoration: none` 명시적 적용.

## [2026-02-05] 스타일 시트 리팩토링 (Stylesheet Refactoring)
- **시스템 도입**: `ui/style_manager.py`를 통한 스타일 로딩 중앙 관리 구현.
- **구조 변경**: `ui/resources/styles/` 내 `themes`와 `components`로 QSS 파일 분리 및 모듈화.
- **리팩토링**: `main.py`, `ui/main_window.py`, `ui/components/tag_input.py`, `ui/components/result_item.py` 내의 하드코딩된 스타일을 모두 제거하고 외부 QSS 파일로 이관.
- **개선**: `FileResultWidget`의 선택 상태(Selected)를 동적 속성(Property) 기반으로 변경하여 스타일 관리 효율성 증대.

## [2026-02-05] Hotfix: 검색 결과창(QScrollArea) 배경색 버그 수정
- `ui/main_window.py`: 결과 컨테이너 위젯(`result_container`)에 `setObjectName("resultContainer")` 추가
- `ui/resources/styles/components/main_window.qss`: `QWidget#resultContainer` 스타일 추가 (`background-color: #252526`)

## [2026-02-05] QueueStatusDialog 스타일 리팩토링
- `ui/queue_dialog.py`의 인라인 스타일을 `ui/resources/styles/components/queue_dialog.qss`로 이동
- 커스텀 헤더 및 스피너 스타일은 유지하되 QSS로 이관
- 다이얼로그 본문에 글로벌 스타일 적용 (`StyleManager` 연동)

## [2026-02-05] 테마 선택 기능 추가 (Theme Selection Feature)
- **라이트 모드(Light Mode) 지원**
    - `ui/resources/styles/themes/light.qss`: 라이트 테마 스타일시트 신규 생성 (기존 다크 테마 색상 반전).
    - `ui/resources/icons/`: 라이트 모드용 다크 아이콘(`sidebar_toggle.svg`, `queue.svg` 등) 추가.
- **테마 전환 기능 구현**
    - `ui/style_manager.py`: `current_theme` 관리 및 아이콘 접미사(`_white` vs none) 반환 로직 추가.
        - [Fix] Singleton 패턴 초기화 버그 수정 (`__init__` -> `__new__`).
    - `ui/main_window.py`: 상단 메뉴바에 [편집] -> [테마] 메뉴 추가.
        - 테마 변경 시 스타일시트 재로딩 및 아이콘(View Mode, Sidebar, Queue) 즉시 갱신 구현.

- **[Improvement] 라이트 모드 스타일링 고도화 (Light Mode Refinement)**
    - **컴포넌트 스타일 통합**: 개별 QSS 파일(`tag_input.qss`, `result_item.qss` 등)에 하드코딩된 색상 정보를 제거하고, `dark.qss` 및 `light.qss`로 통합하여 **글로벌 테마 적용** 구조로 개선.
    - **상세 패널(DetailPane) 개선**: 파이썬 코드 내 하드코딩된 스타일(`setStyleSheet`)을 제거하고 `setProperty`와 QSS Selector 방식으로 전환하여 테마별 스타일 자동 적용 구현.
    - **레이아웃 배경색 수정**: `MainWindow`의 주요 컨테이너(`topContainer`, `controlContainer`, `resultContainer`) 및 `ScrollArea`에 테마별 적절한 배경색(`dark` vs `light`) 지정.

- **[HotFix] 태그 관리 기능 오류 수정**
    - **UI 크래시 수정**: `ui/tag_dialog.py`에서 `QListWidgetItem` 생성 시 태그 정보(튜플)를 그대로 전달하여 발생한 `TypeError` 수정 (튜플 언패킹 적용).
    - **태그 저장 실패 수정**: `core/database/sqlite_manager.py`의 `update_file_tags` 함수에서 대상 파일이 DB에 없을 경우(`files` 테이블 누락) 태그 저장이 무시되던 문제를 해결하기 위해, 파일이 존재하면 자동으로 등록(Upsert)하도록 로직 개선.

## [2026-02-05] AutoTagger 태그 생성 오류 수정
- **버그 수정**: `indexer.py`에서 AutoTagger 호출 시 태그 목록을 튜플 리스트(`[(name, color), ...]`) 그대로 전달하여 TypeError가 발생하는 문제 수정.
- **개선**: `db.get_all_tags()`의 반환값에서 태그 이름만 추출하여 AutoTagger에 전달하도록 변경 (`[tag[0] for tag in tags]`).

## [2026-02-05] 검색 결과 태그 표시 기능 추가
- 검색 결과(목록형)에 태그 칩 표시 (최대 6개)
- 태그 클릭 시 검색 조건에 추가
- DB 색상 연동

## [2026-02-05] 태그 표시 가시성 개선
- 검색 결과의 태그 목록을 최대 2줄로 나누어 표시 (한 줄 당 3개)

## [2026-02-05] 태그 레이아웃 개선
- 목록형 보기에서 태그 정보가 파일명/경로와 시각적으로 정렬되도록 3단 레이아웃 적용
