; Скрипт для Inno Setup Compiler

[Setup]
; Название установщика
AppName=Password Generator V2
; Название программы
AppVersion=2.5
; Издатель (ваше имя или компания)
AppPublisher=Your Company
; Сайт издателя
AppPublisherURL=https://example.com
; Поддержка
AppSupportURL=https://example.com/support
; Обновления
AppUpdatesURL=https://example.com/updates
; Папка по умолчанию для установки
DefaultDirName={pf}\PasswordGeneratorV2
; Имя группы в меню "Пуск"
DefaultGroupName=Password Generator V2
; Иконка установщика
SetupIconFile= dist\PasswordGeneratorV2\app_icon.ico
; Выходной файл установщика
OutputBaseFilename=PasswordGeneratorV2Installer
; Сжатие файлов
Compression=lzma2
SolidCompression=yes
; Архитектура (x86, x64 или все)
ArchitecturesAllowed=x86 x64
ArchitecturesInstallIn64BitMode=x64

[Files]
; Файлы для установки
Source: "dist\PasswordGeneratorV2\PasswordGeneratorV2.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\PasswordGeneratorV2\app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\PasswordGeneratorV2\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Ярлык в меню "Пуск"
Name: "{group}\Password Generator V2"; Filename: "{app}\PasswordGeneratorV2.exe"; IconFilename: "{app}\app_icon.ico"
; Ярлык на рабочем столе
Name: "{commondesktop}\Password Generator V2"; Filename: "{app}\PasswordGeneratorV2.exe"; IconFilename: "{app}\app_icon.ico"

[Run]
; Запуск программы после установки (опционально)
Filename: "{app}\PasswordGeneratorV2.exe"; Description: "Запустить Password Generator V2"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Удаление дополнительных файлов при деинсталляции (опционально)
Type: filesandordirs; Name: "{app}\other_files"