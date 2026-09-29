; Build with build.ps1; version is read from the active add-in source.
#ifndef AppVersion
  #error Run installer/build.ps1 to supply AppVersion from version.py
#endif

[Setup]
AppId={{1D69E956-5380-4F80-9383-6D89CEBB0493}
AppName=HelixPathPilot
AppVersion={#AppVersion}
AppPublisher=Know-How-Schmiede
AppPublisherURL=https://www.know-how-schmiede.de
AppSupportURL=https://github.com/know-how-schmiede/HelixPathPilot/issues
DefaultDirName={code:GetAddInDir}
AppendDefaultDirName=no
DisableDirPage=no
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
MinVersion=10.0
OutputDir=dist
OutputBaseFilename=HelixPathPilot-{#AppVersion}-Windows-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
LicenseFile=..\LICENSE
CloseApplications=no
RestartApplications=no
UninstallDisplayName=HelixPathPilot {#AppVersion}
VersionInfoVersion={#AppVersion}.0
SetupLogging=yes

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"; InfoBeforeFile: "install-en.txt"; InfoAfterFile: "finish-en.txt"
Name: "de"; MessagesFile: "compiler:Languages\German.isl"; InfoBeforeFile: "install-de.txt"; InfoAfterFile: "finish-de.txt"

[Files]
Source: "..\Fusion_addin\HelixPathPilot\*"; DestDir: "{app}"; Excludes: "__pycache__,*.pyc,*.pyo,.gitkeep,.vscode,.idea,.git,presets\user\*"; Flags: ignoreversion recursesubdirs
Source: "..\LICENSE"; DestDir: "{app}"; DestName: "LICENSE.txt"; Flags: ignoreversion

[Code]
function GetAddInDir(Param: String): String;
var
  Modern, Legacy: String;
begin
  Modern := ExpandConstant('{userappdata}\Autodesk\Autodesk Fusion\API\AddIns');
  Legacy := ExpandConstant('{userappdata}\Autodesk\Autodesk Fusion 360\API\AddIns');
  if FileExists(Modern + '\HelixPathPilot\HelixPathPilot.manifest') then
    Result := Modern
  else if FileExists(Legacy + '\HelixPathPilot\HelixPathPilot.manifest') then
    Result := Legacy
  else if DirExists(Modern) then
    Result := Modern
  else if DirExists(Legacy) then
    Result := Legacy
  else
    Result := Modern;
  Result := Result + '\HelixPathPilot';
  Log('Detected Fusion add-in destination: ' + Result);
end;
