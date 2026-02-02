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
