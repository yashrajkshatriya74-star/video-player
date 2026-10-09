; Yashraj Player - Windows Installer Script (built automatically by GitHub Actions)
; Registers the video formats so the player shows up in "Open with" and in
; Settings > Apps > Default apps.

#define MyAppName "Yashraj Player"
#define MyAppVersion "1.0"
#define MyAppExeName "YashrajPlayer.exe"

[Setup]
AppId={{7E3B8A52-4C1D-4F6A-9B27-5D8E1A0C3F94}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=YashrajPlayer_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=yashraj.ico
ChangesAssociations=yes
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\YashrajPlayer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKA; Subkey: "Software\Classes\YashrajPlayer.Video"; ValueType: string; ValueData: "Video file"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\YashrajPlayer.Video\DefaultIcon"; ValueType: string; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\YashrajPlayer.Video\shell\open\command"; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}"; ValueType: string; ValueName: "FriendlyAppName"; ValueData: "{#MyAppName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\shell\open\command"; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\YashrajPlayer\Capabilities"; ValueType: string; ValueName: "ApplicationName"; ValueData: "{#MyAppName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\YashrajPlayer\Capabilities"; ValueType: string; ValueName: "ApplicationDescription"; ValueData: "Fast video player with built-in tools"
Root: HKA; Subkey: "Software\YashrajPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mp4"; ValueData: "YashrajPlayer.Video"
Root: HKA; Subkey: "Software\Classes\.mp4\OpenWithProgids"; ValueType: string; ValueName: "YashrajPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\YashrajPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mkv"; ValueData: "YashrajPlayer.Video"
Root: HKA; Subkey: "Software\Classes\.mkv\OpenWithProgids"; ValueType: string; ValueName: "YashrajPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\YashrajPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".avi"; ValueData: "YashrajPlayer.Video"
Root: HKA; Subkey: "Software\Classes\.avi\OpenWithProgids"; ValueType: string; ValueName: "YashrajPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\YashrajPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mov"; ValueData: "YashrajPlayer.Video"
Root: HKA; Subkey: "Software\Classes\.mov\OpenWithProgids"; ValueType: string; ValueName: "YashrajPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\YashrajPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".wmv"; ValueData: "YashrajPlayer.Video"
Root: HKA; Subkey: "Software\Classes\.wmv\OpenWithProgids"; ValueType: string; ValueName: "YashrajPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\YashrajPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".flv"; ValueData: "YashrajPlayer.Video"
Root: HKA; Subkey: "Software\Classes\.flv\OpenWithProgids"; ValueType: string; ValueName: "YashrajPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\YashrajPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".webm"; ValueData: "YashrajPlayer.Video"
Root: HKA; Subkey: "Software\Classes\.webm\OpenWithProgids"; ValueType: string; ValueName: "YashrajPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\YashrajPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".m4v"; ValueData: "YashrajPlayer.Video"
Root: HKA; Subkey: "Software\Classes\.m4v\OpenWithProgids"; ValueType: string; ValueName: "YashrajPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\YashrajPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".ts"; ValueData: "YashrajPlayer.Video"
Root: HKA; Subkey: "Software\Classes\.ts\OpenWithProgids"; ValueType: string; ValueName: "YashrajPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\YashrajPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".m2ts"; ValueData: "YashrajPlayer.Video"
Root: HKA; Subkey: "Software\Classes\.m2ts\OpenWithProgids"; ValueType: string; ValueName: "YashrajPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\YashrajPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mpg"; ValueData: "YashrajPlayer.Video"
Root: HKA; Subkey: "Software\Classes\.mpg\OpenWithProgids"; ValueType: string; ValueName: "YashrajPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\YashrajPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mpeg"; ValueData: "YashrajPlayer.Video"
Root: HKA; Subkey: "Software\Classes\.mpeg\OpenWithProgids"; ValueType: string; ValueName: "YashrajPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\YashrajPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".3gp"; ValueData: "YashrajPlayer.Video"
Root: HKA; Subkey: "Software\Classes\.3gp\OpenWithProgids"; ValueType: string; ValueName: "YashrajPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\YashrajPlayer\Capabilities\FileAssociations"; ValueType: string; ValueName: ".ogv"; ValueData: "YashrajPlayer.Video"
Root: HKA; Subkey: "Software\Classes\.ogv\OpenWithProgids"; ValueType: string; ValueName: "YashrajPlayer.Video"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\RegisteredApplications"; ValueType: string; ValueName: "YashrajPlayer"; ValueData: "Software\YashrajPlayer\Capabilities"; Flags: uninsdeletevalue

Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\DefaultIcon"; ValueType: string; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".mp4"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".mkv"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".avi"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".mov"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".wmv"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".flv"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".webm"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".m4v"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".ts"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".m2ts"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".mpg"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".mpeg"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".3gp"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".ogv"; ValueData: ""

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
