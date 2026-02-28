# Semantic File Searcher

## 프로젝트 개요
antigravity와 함께 적극적인 바이브 코딩으로 개발하는 윈도우용 파일 검색 데스크탑 앱.
파일명 검색 뿐 아니라 파일 내용도 자연어로 검색 할 수 있도록 함.

현재 개발 중임.

## 라이선스 고지
이 프로그램은 오픈소스 소프트웨어 및 모델(Qwen)을 사용하였으며, 자세한 라이선스 정보는 `OPENSOURCE_LICENSES.txt` 파일에서 확인할 수 있습니다.

## 빌드 및 실행 방법

1. 프로젝트 의존성 설치 (`uv` 활용)
```bash
uv sync --extra cpu
```

2. 빌드 스크립트 실행 (PowerShell 이용, 포터블 및 인스톨러 자동 생성)
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_app.ps1
```
빌드 결과물(`.zip`, `Installer.exe` 등)은 `dist\` 폴더에 생성됩니다.