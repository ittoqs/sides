@echo off
echo Memasang SI-DESAKU dan membuat shortcut di Desktop...

:: Mendapatkan lokasi folder saat ini
SET "APP_DIR=%~dp0"
SET "TARGET_EXE=%APP_DIR%SI-DESAKU.exe"

:: Cek apakah file exe ada
IF NOT EXIST "%TARGET_EXE%" (
    echo Peringatan: File SI-DESAKU.exe tidak ditemukan di folder ini!
    echo Pastikan Anda mengekstrak semua isi ZIP ke dalam satu folder.
    pause
    exit /b
)

:: Lokasi script VBS sementara
SET "VBS_SCRIPT=%temp%\buat_shortcut_desaku.vbs"

:: Membuat script VBScript untuk membuat shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\SI-DESAKU.lnk" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "%TARGET_EXE%" >> "%VBS_SCRIPT%"
echo oLink.WorkingDirectory = "%APP_DIR%" >> "%VBS_SCRIPT%"
echo oLink.Description = "Aplikasi Pelayanan Desa Otomatis" >> "%VBS_SCRIPT%"
echo oLink.Save >> "%VBS_SCRIPT%"

:: Menjalankan script VBS dan menghapusnya
cscript /nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%"

echo.
echo Berhasil! Shortcut SI-DESAKU telah ditambahkan ke Desktop Anda.
echo Anda sekarang dapat menutup jendela ini dan membuka aplikasi melalui Desktop.
pause
