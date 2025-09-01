# Script per aggiungere Wireshark/Tshark al PATH di Windows

$wiresharkPath = "C:\Program Files\Wireshark" #oppure sostituire con la cartella pertinente

# Controlla se tshark.exe esiste
if (Test-Path "$wiresharkPath\tshark.exe") {
    Write-Output "Trovato tshark.exe in: $wiresharkPath"
} else {
    Write-Output "tshark.exe non trovato in $wiresharkPath. Modifica il percorso nello script."
    exit
}

# Legge le variabili di sistema e aggiunge il percorso di Tshark solo se non è già presente
$oldPath = [Environment]::GetEnvironmentVariable("Path", "Machine")

if ($oldPath -notlike "*$wiresharkPath*") {
    $newPath = "$oldPath;$wiresharkPath"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
    Write-Output "Aggiunto $wiresharkPath al PATH di sistema."
    Write-Output "Riavvia il terminale per applicare le modifiche."
} else {
    Write-Output "Il percorso è già presente nel PATH."
}
