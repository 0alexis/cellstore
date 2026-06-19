#define MyAppName "CellStore"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Alexis"
#define MyAppExeName "CellStore.exe"

[Setup]
AppId={{8D3ABF47-7C2A-4B2D-B6C7-0E38D967B90A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\CellStore
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer-dist
OutputBaseFilename=CellStoreInstaller
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}

[Dirs]
Name: "{commonappdata}\CellStore"
Name: "{commonappdata}\CellStore\data"
Name: "{commonappdata}\CellStore\uploads"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "install_service.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "packaging\windows\configure_cellstore.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "packaging\windows\remove_cellstore.ps1"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\CellStore"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar CellStore"; Filename: "{uninstallexe}"

[Run]
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File \"{app}\configure_cellstore.ps1\" -InstallDir \"{app}\" -ProgramDataDir \"{commonappdata}\CellStore\""; Flags: runhidden waituntilterminated

[UninstallRun]
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File \"{app}\remove_cellstore.ps1\" -InstallDir \"{app}\""; Flags: runhidden waituntilterminated