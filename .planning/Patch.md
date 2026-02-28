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

## [2026-02-05] 검색 결과 아이템 스타일 개선
- **목록형(List) 보기 최적화**:
    - **높이 고정**: 검색 결과 아이템의 높이를 `60px`로 고정하여 결과가 적을 때 과도한 공백 방지.
    - **가운데 정렬**: 파일명, 경로, 태그 칩 등 내부 요소가 세로 방향으로 중앙에 위치하도록 정렬 수정 (`addStretch` 제거, `AlignVCenter` 적용).

## [2026-02-05] 태그 관리 대화상자 UI 개선
- **태그 칩(Chip) 적용**: `ui/tag_dialog.py`의 리스트 위젯을 `CheckableTagChip`(`ui/components/tag_input.py`) 기반의 `FlowLayout`으로 변경하여 시인성 개선.
- **태그 필터링 기능**: 상단 검색바를 추가하여 실시간으로 태그 목록 필터링 지원.
- **통합 디자인**: 기존 DB 색상 연동 및 선택 상태 시각화 강화.

## [2026-02-07] 앱 아이콘 적용
- **아이콘 생성**: 사용자가 제공한 `Image (1).webp` (투명 배경) 파일을 `assets/icon.png`로 변환하여 적용
- **UI 적용**: `MainWindow` 제목 표시줄에 생성된 아이콘 (`assets/icon.png`) 적용

### 아이콘 적용 이슈 해결
- `ui/main_window.py`: 아이콘 경로를 절대 경로(실행 파일 기준)로 탐색하도록 수정하여 로딩 안정성 확보.
- `main.py`: Windows 작업 표시줄에 아이콘이 정상적으로 표시되도록 `AppUserModelID` 설정 코드 추가.

## [2026-02-08] 파일 탐색 기능 추가 (File Explorer Feature)
- **사이드바(Sidebar) 구현**:
    - `ui/components/sidebar.py`: `QFileSystemModel` 기반의 폴더 트리 뷰 구현.
    - `ui/main_window.py`: 좌측 사이드바와 우측 콘텐츠 영역을 `QSplitter`로 분할하여 통합.
- **경로 표시줄(Path Bar) 추가**:
    - `ui/components/path_bar.py`: Breadcrumb(버튼) 방식의 경로 탐색 및 직접 입력(Edit) 모드 지원.
    - 상단 경로 바를 통해 상위 폴더 이동 및 새로고침 기능 구현.
- **파일 목록 및 등록 상태 표시**:
    - `ui/main_window.py`: 폴더 선택 시 `os.scandir`를 사용하여 파일 목록을 로드하고 DB 인덱싱 여부 확인.
    - `ui/main_window.py`: 폴더 선택 시 `os.scandir`를 사용하여 파일 목록을 로드하고 DB 인덱싱 여부 확인.
    - `ui/components/result_item.py`: DB에 등록되지 않은 파일의 경우 태그 위치에 **"미등록 파일"** 라벨 표시.
- **버그 수정**:
    - `ui/components/path_bar.py`: `eventFilter`에서 `QEvent` 속성 접근 오류(`AttributeError`) 수정.
    - `ui/main_window.py`: 파일 클릭 시 발생할 수 있는 잠재적 오류에 대한 예외 처리 및 안전한 리소스 접근 로직 추가.
    - `ui/main_window.py`: 폴더 이동(`load_directory`) 시 기존 선택된 항목(`selected_item`) 참조를 초기화하지 않아 발생하는 `RuntimeError` (deleted object access) 수정.
    - `ui/resources/icons/refresh_white.svg`: 누락된 새로고침 아이콘 파일 생성 및 적용.
    - `ui/main_window.py`: DB와 OS 간의 경로 구분자(Slash vs Backslash) 및 대소문자 불일치로 인해 발생하는 '미등록 파일' 표시 오류를 해결하기 위해 `load_directory`의 파일 조회 로직을 `LIKE` 쿼리 및 정규화(`normcase`) 기반으로 전면 수정.
    - `core/indexing/scanner.py`, `core/indexing/monitor.py`: 파일 인덱싱 및 변경 감지 시 OS 기본 경로 구분자(Windows: `\`)로 경로를 정규화하여 DB에 저장하도록 수정.
    - [마이그레이션]: 기존 DB에 저장된 비표준 경로(Slash 혼용 등)를 OS 표준 경로 포맷으로 일괄 변환하는 마이그레이션 작업 수행 완료 (20개 경로 수정됨).
    - `ui/components/path_bar.py`: 라이트 모드에서 새로고침 아이콘이 보이지 않는 문제 해결을 위해 테마별 아이콘 변경(`update_icons`) 기능 추가 및 하드코딩된 스타일 제거(QSS로 이관).
    - `ui/resources/icons/refresh.svg`: 라이트 모드용(어두운 색) 새로고침 아이콘 추가.

## 2026-02-08
### 사이드바 및 보기 모드 버그 수정
- **버그 수정**: 사이드바 탐색 중 보기 모드(목록/아이콘) 변경 시 검색 결과로 초기화되는 문제 해결. `current_context` 변수를 추가하여 현재 상태(검색 결과 vs 폴더 탐색)를 추적하도록 개선.
- **기능 추가**: 검색 실행 시 주소 표시줄에 "'{검색어}' 검색 결과"가 표시되도록 기능 추가. 검색 결과를 명확히 인지할 수 있게 됨.

## 2026-02-08
### 모니터링 관리 기능 추가 (Monitoring Management via Context Menu)
- **컨텍스트 메뉴 개선**: 메인 패널의 파일 항목 및 사이드바의 폴더 항목에서 우클릭 시 **'모니터링에 추가'** 또는 **'모니터링 해제'** 메뉴 제공.
- **모니터링 예외 처리 로직 구현**:
    - **상위 폴더가 모니터링 중일 때**: 하위 폴더/파일을 모니터링에서 제외할 수 있도록 `monitoring_exceptions` 설정 추가 (`core/config.py`).
    - **파일 감지 필터링**: `Indexer`의 변경 감지 로직(`_on_change`)에서 예외 경로를 필터링하여 불필요한 인덱싱 방지.
- **설정 창(Settings Dialog) 개선**:
    - **예외 목록 관리**: [폴더 관리] 탭에 '모니터링 예외' 리스트 추가. 사이드바/컨텍스트 메뉴에서 제외시킨 하위 폴더 목록을 확인 가능.
    - **예외 해제**: 예외 목록에서 항목 선택 후 '예외 해제 (다시 모니터링)' 버튼을 클릭하여 모니터링 재개 기능 구현.
- **버그 수정**:
    - **검색 노출 문제 해결**: 모니터링에서 해제되었거나 예외 처리된 파일이 검색 결과에 노출되는 문제를 해결. `Indexer.search` 메서드에 `is_monitored` 필터링 로직 추가.
    - **DB 정리 로직 강화**: 폴더 모니터링 해제(`remove_from_monitoring`) 시, DB에서 정확히 일치하는 파일 및 하위 파일을 삭제하는 쿼리를 개선하여 접두사가 유사한 다른 폴더가 오삭제되거나 잔존하는 문제 방지.
    - **설정 창 삭제 로직 수정**: [폴더 관리]에서 '폴더 삭제' 시 DB 데이터가 남아있는 문제 해결. `remove_from_monitoring`을 호출하여 DB 정리까지 수행하도록 변경.
    - **경로 구분자 비교 로직 개선**: 설정 파일과 실행 환경 간의 경로 구분자 차이(예: `/` vs `\`)로 인해 삭제 대상 폴더를 찾지 못하던 문제 해결. `config.get_folders()` 목록 비교 시 `os.path.normpath` 적용.
    - **인덱싱 누락 방지**: 텍스트 추출 실패(예: 스캔된 PDF) 시 파일 자체가 DB에 저장되지 않던 문제 해결. 메타데이터(파일명) 인덱싱을 강제하여 검색 가능성 보장.
- **UI/UX**: 모니터링 해제 시 경고 팝업을 통해 사용자 실수 방지. 상태 바(Status Bar)에 작업 결과 실시간 피드백 제공.
- **안정성**: `test_monitoring.py`, `test_bug_repro.py`, `test_db_cleanup.py`를 통해 모니터링 추가/해제, 예외 처리, 검색 필터링 로직 검증 완료.

## 2026-02-09
### 벡터 DB 구조 개선 및 중복 검색 해결
- **중복 검색 해결**: `SemanticIndexer.search`에 파일 경로 기반 중복 제거 로직을 추가하여 동일 파일이 여러 번 노출되는 문제 해결.
- **벡터 DB 고도화**:
    - `faiss.IndexFlatIP` (Cosine Similarity) 및 `IndexIDMap` 도입으로 벡터 ID 관리 및 유사도 검색 정확도 향상.
    - `file_vectors` 테이블(SQLite)을 신설하여 파일과 벡터 ID 간의 매핑 관계 관리.
- **삭제 로직 완성**:
    - 파일 수정/삭제 시 RDB에서 벡터 ID를 조회하여 Vector DB(`vector.faiss`)에서 해당 벡터를 물리적으로 삭제하는 로직 구현.
    - 폴더 모니터링 해제(`remove_from_monitoring`) 시에도 연관된 모든 벡터 데이터를 정리하도록 개선.
- **검증**: `verify_vector_db.py` 스크립트를 통해 파일 추가, 삭제, 수정, 재등록 시나리오에서 데이터 무결성 및 중복 방지 동작 검증 완료.
- **[Hotfix] 검색 오류 수정**: 벡터 DB 구조 변경 후 `search` 메서드에서 파일 경로를 찾지 못해 발생하던 오류(`KeyError`)를 해결하기 위해, `file_vectors` 테이블을 조회하여 `vector_id`를 `file_path`로 변환하는 로직 추가.

## [2026-02-10] CUDA 가속 환경 설정
- **.venv-gpu 생성**: CUDA 13.0 지원 가상환경 추가 (Python 3.13).
- **Torch GPU**: `torch 2.10.0+cu130` 설치 완료 (RTX 5090 감지).
- **Faiss**: Windows/Python 3.13 환경에서 `faiss-gpu` 패키지(PyPI) 미지원으로 인해 `faiss-cpu_1.13.2`로 대체 설치. (기능 동작 가능, GPU 가속 불가)
- **pyproject.toml**: `cpu`, `gpu` optional dependencies 분리.

## [2026-02-21] 브라우저 직접 다운로드 시 파일 인덱싱 누락 버그 수정
- **버그 해결**: 브라우저 다운로드 과정에서 일시적으로 생성되는 파일(`crdownload` 등)의 이름 변경 이벤트 누락 및 매우 짧은 시간 내의 파일 삭제 후 재생성 처리 중 덮어쓰기가 안되는 문제 개선
- **세부 조치**:
    - `core/indexing/monitor.py`: 파일 이름 변경을 감지하는 `on_moved` 이벤트 핸들러 추가하여 다운로드 후 확장자 변경에 따른 원본 파일 생성 감지 보완
    - `core/indexing/queue_manager.py`: 삭제 대기 큐에 있던 파일에 대해 다시 처리 요청(업데이트)이 올 경우, 해당 파일이 실제 OS 상에 존재한다면 업데이트 작업을 삭제 작업으로 덮어쓰지 않고 우선적으로 수행하도록 로직 수정
    - `core/indexer.py`: 이벤트 과부하 방지를 위해 워치독 단계에서 다운로드 임시 파일 확장자(`.crdownload`, `.part`, `.tmp`)를 무시하도록 필터링 로직 추가

## [2026-02-21] LanceDB 마이그레이션 및 OpenSSL 버그 픽스
- **VectorDB 교체**: FAISS에서 LanceDB로 성공적으로 마이그레이션 스크립트 실행 및 교체 완료 (troubleshooting.md 확인 및 implementation_plan.md 작성 포함)

## [2026-02-21] 임베딩 로직 고도화 및 품질 개선
- **텍스트 청킹(Chunking) 유틸리티 도입**:
    - `core/indexing/chunker.py`: `TextChunker`를 구현하여 긴 텍스트(문서, 소스코드 등)를 재귀적으로 분할(최대 길이에 맞춤). 컨텍스트 길이 초과 문제 해결.
- **다중 임베딩 벡터 저장 지원**:
    - `core/indexing/scanner.py`: 파일 하나당 다수의 청크가 생성될 때 다수의 벡터를 추출하여 배치 단위로 VectorDB에 인덱싱하도록 개선 (`get_vector_ids` 및 다중 삭제 지원).
- **실제 이미지 멀티모달 프롬프트 적용 (Mocking 제거)**:
    - `core/embedding/qwen_adapter.py`: 이미지 임베딩 요청 시 무작위 텐서(`np.random.randn`)를 반환하던 임시 코드를 삭제하고, `AutoProcessor` 및 `model.get_image_features`를 활용한 실제 추론 로직으로 교체.

## [2026-02-22] 이미지 임베딩 성능 및 검색 품질 검증
- **문제 확인**: '강아지' 검색 시 '자동차/사람' 관련 이미지가 상위에 노출되는 등 이미지 검색 품질이 저하되는 현상 조사.
- **원인 분석**: 애플리케이션의 정렬 로직(LanceDB 코사인 유사도 점수 내림차순 정렬)은 확인 결과 정상적으로 구동 중임. 실제 원인은 현재 사용중인 이미지 임베딩 모델(`Qwen/Qwen3-VL-Embedding-2B`)이 생성한 텍스트-이미지 유사도 추출 점수에 노이즈가 심하고 직교(-0.05 ~ 0.03)에 가까운 값으로 출력되어 랭킹이 반대로 나타나는 모델 성능/추출 방식의 한계로 확인.
- **결과 및 조치**: 원인 분석 결과를 문서(`troubleshooting.md`)에 정리 및 공유 완료. 현재 소스코드 상에서의 정렬 버그는 없으며, 사용자가 직접 임베딩 품질 테스트 및 문제 상황을 확인할 수 있도록 `test_embedding.py` 스크립트를 작성하여 전달.
- **[추가 조치] 8B 모델 및 LanceDB 연동 재검증 (1차 실패)**:
    - **조치**: 모델 차원을 4096으로 상향(`Qwen/Qwen3-VL-Embedding-8B` 적용)하여 `qwen_adapter.py` 업데이트 및 DB 매핑 개선 (`vector_db.search` 이용).
    - **결과 확인**: 초기 시도에서는 여전히 이미지-텍스트 유사도 점수가 낮게 나왔음.
- **[최종 해결] Qwen-VL 공식 지원 포맷팅 및 버그 픽스 적용**:
    - **원인 분석**:
        1. 첫째, 기존 코드에서는 `test_embedding.py` 등 내부 구동 중 `transformers` 최신 패키지 버그(`video_processing_auto` 내 NoneType 버그)와 `torchvision` 미설치로 인해 `AutoProcessor`가 작동하지 않고 조용하게 실패(Fail)하여 무작위 가짜 벡터(Mock data: `np.random.randn`)를 반환하도록 되어 있었습니다. 즉 사용자는 **그동안 랜덤 벡터 해시를 검색**하고 있었습니다.
        2. 둘째, Qwen3-VL-Embedding 모델은 입력을 무조건 `Chat Template`으로 포맷팅하고, Instruction Prompt(`Represent the user's input.`)를 제공해야 하며, 전체 토큰의 평균이 아닌 **Last Token Pooling** 방식을 써야만 정답 텐서가 추출되는데 이 구조들이 적용되지 않았었습니다.
        3. 셋째, LanceDB에서 이미 코사인 메트릭 내부 연산 중에 정규화(L2 Normalization)를 진행하므로 파이썬 영역의 강제 L2 처리는 중복이자 오류일 가능성이 있었습니다.
    - **조치 내역**:
        - `pyproject.toml` 기반 Python 가상환경 내 `torchvision` 및 `qwen-vl-utils` 수동 구성.
        - `qwen_adapter.py` 최상단에 `transformers`의 비디오 프로세서 관련 버그 우회를 위한 몽키 패치(Monkey Patch: `vpa.VIDEO_PROCESSOR_MAPPING_NAMES` None 예외 처리) 삽입.
        - `encode_text` 및 `encode_image` 함수 내에 공식 구현체와 동일하게 `apply_chat_template` 도입, 인스트럭션 프롬프트 강제화 및 `_pooling_last` 메서드 구현.
        - `vector_db.py` 코사인 유사도 검색 최적화를 위해 불필요한 L2 정규화 로직 제거.
    - **검증 결과 (성공)**: 코드가 최종 보완된 후 다시 원래 목표였던 `Qwen3-VL-Embedding-2B` 모델로 파라미터를 낮추고 DB를 초기화해 `test_embedding.py` 측정을 진행한 결과, 
        - `'강아지'` 쿼리 점수가 상위로 `진도개1.jpg(0.35)`, `진도개3.jpg(0.33)`가 등장
        - `'car'` 쿼리 시 `자동차2.jpg(0.20)`, `XM3 자동차.jpg(0.17)`가 정확히 상단 랭크
        - 정상적이고 유의미한 시맨틱 유사도 검색이 가벼운 2B 모델에서도 충분히 구현됨을 최종 입증했습니다.

## [2026-02-28] 파일 인덱싱 중복 생성 버그 해결
- **Vector DB 중복 데이터 생성 및 고아 데이터 적재 이슈 완전 수정**:
    - `core/database/sqlite_manager.py`: `upsert_file` 메서드 내부에서 `INSERT ... ON CONFLICT DO UPDATE` 구문 실행 시, SQLite의 `lastrowid`가 충돌 업데이트 이후 엉뚱한 이전 시점의 ID를 반환하는 버그 발견 및 명시적인 `SELECT id` 조회를 통한 정확한 파일 ID 반환 구현으로 해결.
    - `core/indexing/scanner.py`: DB 저장 메타데이터 및 OS 타임스탬프 간 변경 감지 로직의 파이썬 객체-문자열 비교 파편화를 방지하고 강건하게 비교하도록 명시적인 `str()` 캐스팅 비교 확정 적용.

## [2026-02-28] 가상환경 실행 오류 수정 및 의존성 추가
- **증상**: 파이썬 가상환경(`uv` 등)에서 애플리케이션 실행 시 `OPENSSL_Uplink(...): no OPENSSL_Applink` 에러 발생과 함께 즉시 종료되는 현상.
- **원인**: 사용자의 시스템 환경(AhnLab Safe Transaction 등 보안 프로그램 추정)에서 시스템 전역으로 주입된 `SSLKEYLOGFILE` (예: `\\.\nllMonFltProxy\...`) 환경 변수 때문에, 내부 파이썬 wrapper가 OpenSSL 키 로그를 기록하려다 C 런타임 Applink 심볼이 없어 충돌이 발생한 것.
- **해결**: `main.py` 실행 최상단에서 `os.environ.pop("SSLKEYLOGFILE", None)`를 호출하여 프로세스 환경 내에서 해당 변수만 제거해 OpenSSL 크래시를 근본적으로 차단함.
- **추가 수정**: `uv` 환경에서 숨어있던 `torchvision` 모듈 미인식 에러를 확인하고 `uv pip install torchvision`을 통해 의존성 트리를 정상으로 복구하여 앱 구동 성공.

## [2026-02-28] 태그 입력 창 및 표시 버그 수정
- **태그 창 검색 버그 해결**: 검색어가 입력되지 않고 태그 칩만 있는 상태에서 입력창에서 엔터키를 누를 때 검색이 실행되지 않던 오류(`ui/main_window.py`의 `perform_search` 내 조기 리턴 로직)를 조건부 수행으로 개선하여 수정. 이제 시스템이 상황에 맞게 자동으로 태그 검색 및 안내('태그 검색 중...')를 제공합니다.
    - **태그 전용 검색 시 태그 표시 누락 해결**: `core/indexer.py`의 `search` 메서드에서 검색 문자열 없이 태그로만 조회할 때 태그 정보를 함께 반환하도록 수정하여 검색 결과 UI에 파일 썸네일 우측에 태그 칩이 정상 노출되도록 조치.
- **태그 중복 출력 버그 해결**: `ui/components/tag_input.py`에서 QCompleter(자동완성)를 이용해 태그를 선택한 뒤 남은 텍스트가 입력 필드에 복사/잔류하던 문제를 QTimer 기반의 비동기 초기화(`clear()`) 로직을 추가하여 깨끗하게 지워지도록 조치완료.

## [2026-02-28] PyMuPDF 라이브러리 교체 (AGPL 라이선스 회피)
- 빌드 배포를 앞두고, 카피레프트 의무(AGPL 3.0)가 있는 pymupdf(fitz)를 제거함.
- 텍스트 및 이미지 추출 확장에 유리한 MIT 라이선스 기반의 pdfplumber를 도입함.
- pyproject.toml, equirements.txt 업데이트 (uv sync 실행완료).
- core/indexing/scanner.py 파일 내 PDF 텍스트 추출 로직 교체.
- OPENSOURCE_LICENSES.txt 파일 신규 생성 및 README.md에 참조 문구 추가.
