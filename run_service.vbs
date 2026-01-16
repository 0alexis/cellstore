' run_service.vbs - Ejecuta Flask como servicio (sin ventana, con logs)
' Versión corregida y robusta

On Error Resume Next

Dim objShell, strPath, strPython, strScript, strCommand
Dim objFSO, strLogFile, objLog

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' === CONFIGURACIÓN (ajusta solo si cambias rutas) ===
strPath = "C:\Users\Public\CellStore\cellstore"
strPython = strPath & "\venv\Scripts\python.exe"             ' Python del venv
strScript = strPath & "\run.py"                              ' Archivo principal
strLogFile = strPath & "\service.log"

' === Escribir en log ===
Sub LogMessage(msg)
    Dim file
    Set file = objFSO.OpenTextFile(strLogFile, 8, True)  ' 8 = append, True = create if not exists
    file.WriteLine Now & " - " & msg
    file.Close
End Sub

LogMessage "Intentando iniciar servicio Flask..."

' Validar que existen los archivos
If Not objFSO.FileExists(strPython) Then
    LogMessage "ERROR: No se encuentra python.exe en " & strPython
    WScript.Quit
End If

If Not objFSO.FileExists(strScript) Then
    LogMessage "ERROR: No se encuentra run.py en " & strScript
    WScript.Quit
End If

' === Comando clave: cd a la carpeta + ejecutar python ===
' Esto resuelve el problema del directorio de trabajo
strCommand = "cmd.exe /c ""cd /d """ & strPath & """ && """ & strPython & """ """ & strScript & """ >> """ & strLogFile & """ 2>&1"""

LogMessage "Directorio de trabajo: " & strPath
LogMessage "Comando a ejecutar: " & strCommand

' Ejecutar oculto (0 = ventana oculta), False = no esperar a que termine
objShell.Run strCommand, 0, False

LogMessage "Servicio Flask lanzado correctamente en segundo plano."