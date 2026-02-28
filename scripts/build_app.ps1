param (
    [switch]$SkipTest = $false
)

$ErrorActionPreference = "Stop"

Write-Host "========================================="
Write-Host "  Semantic File Searcher Build Script"
Write-Host "========================================="

if (-not $SkipTest) {
    Write-Host "`n[1/4] Running Core Features Test..."
    uv run python scripts/test_core_features.py
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Core features test failed. Stopping build."
        exit 1
    }
    Write-Host "Test passed successfully."
} else {
    Write-Host "`n[1/4] Skipping Core Features Test."
}

Write-Host "`n[2/4] Building app with PyInstaller..."
# uv 런타임에서 pyinstaller 실행
# 기존에 설치 안 되어 있다면 uv pip install pyinstaller 실행 필요할 수 있음
uv run pyinstaller SemanticFileSearcher.spec --clean -y
if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller build failed."
    exit 1
}

Write-Host "`n[3/4] Creating Portable Zip Archive..."
$DistDir = "dist\SemanticFileSearcher"
$ZipPath = "dist\SemanticFileSearcher-Portable.zip"

if (Test-Path $ZipPath) {
    Remove-Item -Path $ZipPath -Force
}

# 기본 라이선스 파일들 복사
if (Test-Path "OPENSOURCE_LICENSES.txt") {
    Copy-Item "OPENSOURCE_LICENSES.txt" -Destination $DistDir
}
if (Test-Path "README.md") {
    Copy-Item "README.md" -Destination $DistDir
}

Compress-Archive -Path "$DistDir\*" -DestinationPath $ZipPath -Force
Write-Host "Portable Zip created at: $ZipPath"

Write-Host "`n[4/4] Building Installer with Inno Setup..."
# Inno Setup CLI 실행 (iscc)
$IsccTool = "C:\Program Files (x86)\Inno Setup 6\iscc.exe"
if (Test-Path $IsccTool) {
    & $IsccTool "scripts\installer.iss"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Inno Setup compilation failed."
        exit 1
    }
    Write-Host "Installer created successfully."
} else {
    Write-Host "[WARNING] Inno Setup (iscc.exe) not found at standard path. Skipping installer build."
}

Write-Host "`n========================================="
Write-Host "  Build completed successfully!"
Write-Host "========================================="
