; Мастер установки TVD Rally из проверенного публичного архива.
#ifndef AppVer
  #define AppVer "dev"
#endif
#define UninstKey "Software\Microsoft\Windows\CurrentVersion\Uninstall\TVDRally"

[Setup]
AppId={{6E2B1C3A-7D4F-4C8E-9A51-TVDRALLY0003}
AppName=TVD Rally
AppVersion={#AppVer}
VersionInfoVersion={#AppVer}.0
VersionInfoTextVersion={#AppVer}
VersionInfoProductVersion={#AppVer}.0
VersionInfoProductTextVersion={#AppVer}
AppVerName=TVD Rally {#AppVer}
AppPublisher=TVD Rally Club
AppPublisherURL=https://tvdrally.online
AppSupportURL=https://tvdrally.online
DefaultDirName={autopf}\TVD Rally
DisableWelcomePage=no
DisableDirPage=no
DisableReadyPage=no
DisableProgramGroupPage=yes
UsePreviousAppDir=yes
OutputDir=..\Output
OutputBaseFilename=TVD-Rally-Setup-{#AppVer}
SetupIconFile=..\dist\TVD Rally\app\icon.ico
PrivilegesRequired=admin
Uninstallable=no
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
Compression=lzma2/max
SolidCompression=yes
CloseApplications=yes

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "Ярлык на рабочем столе"; GroupDescription: "Ярлыки:"

[InstallDelete]
; код прошлой версии — целиком, чтобы не осталось лишних файлов
Type: filesandordirs; Name: "{app}\app"

[Files]
Source: "..\dist\TVD Rally\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[INI]
; признак «установленная копия» (иначе двойной щелчок по exe считал бы папку распакованным архивом)
Filename: "{app}\installed.ini"; Section: "TVD Rally"; Key: "version"; String: "{#AppVer}"

[Icons]
Name: "{autoprograms}\TVD Rally"; Filename: "{app}\TVD Rally.exe"; WorkingDir: "{app}"; IconFilename: "{app}\app\icon.ico"; Comment: "TVD Rally — лаунчер DiRT Rally 2.0"
Name: "{autodesktop}\TVD Rally"; Filename: "{app}\TVD Rally.exe"; WorkingDir: "{app}"; IconFilename: "{app}\app\icon.ico"; Comment: "TVD Rally — лаунчер DiRT Rally 2.0"; Tasks: desktopicon

[Registry]
Root: HKA; Subkey: "{#UninstKey}"; ValueType: string; ValueName: "DisplayName"; ValueData: "TVD Rally"
Root: HKA; Subkey: "{#UninstKey}"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "{#AppVer}"
Root: HKA; Subkey: "{#UninstKey}"; ValueType: string; ValueName: "Publisher"; ValueData: "TVD Rally Club"
Root: HKA; Subkey: "{#UninstKey}"; ValueType: string; ValueName: "DisplayIcon"; ValueData: "{app}\app\icon.ico"
Root: HKA; Subkey: "{#UninstKey}"; ValueType: string; ValueName: "InstallLocation"; ValueData: "{app}"
Root: HKA; Subkey: "{#UninstKey}"; ValueType: string; ValueName: "URLInfoAbout"; ValueData: "https://tvdrally.online"
Root: HKA; Subkey: "{#UninstKey}"; ValueType: string; ValueName: "UninstallString"; ValueData: """{app}\TVD Rally.exe"" ""{app}\app\tvd_client.py"" --uninstall"
Root: HKA; Subkey: "{#UninstKey}"; ValueType: dword; ValueName: "NoModify"; ValueData: 1
Root: HKA; Subkey: "{#UninstKey}"; ValueType: dword; ValueName: "NoRepair"; ValueData: 1

[Run]
; от имени обычного пользователя, не администратора (иначе окно/журнал/профиль Edge станут «админскими»)
Filename: "{app}\TVD Rally.exe"; WorkingDir: "{app}"; Description: "Запустить TVD Rally"; Flags: nowait postinstall skipifsilent runasoriginaluser
