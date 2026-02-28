[Setup]
AppName=Semantic File Searcher
AppVersion=0.1.0
DefaultDirName={autopf}\SemanticFileSearcher
DefaultGroupName=Semantic File Searcher
UninstallDisplayIcon={app}\SemanticFileSearcher.exe
SetupIconFile=..\assets\icon.ico
Compression=lzma2
SolidCompression=yes
OutputDir=..\dist
OutputBaseFilename=SemanticFileSearcher-Installer

[Files]
Source: "..\dist\SemanticFileSearcher\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Semantic File Searcher"; Filename: "{app}\SemanticFileSearcher.exe"
Name: "{commondesktop}\Semantic File Searcher"; Filename: "{app}\SemanticFileSearcher.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\SemanticFileSearcher.exe"; Description: "Launch Semantic File Searcher"; Flags: nowait postinstall skipifsilent
