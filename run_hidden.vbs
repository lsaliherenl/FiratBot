' FiratBot - run_check.bat'i pencere acmadan (gizli) calistirir.
' Gorev Zamanlayici bunu cagirir; ekranda cmd penceresi flaslamaz.
Set fso = CreateObject("Scripting.FileSystemObject")
folder = fso.GetParentFolderName(WScript.ScriptFullName)
Set sh = CreateObject("WScript.Shell")
sh.Run """" & folder & "\run_check.bat""", 0, False
