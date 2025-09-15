# Параметры подключения
$baseUrl = "https://sd.v-serv.ru/jira"
$issueKey = "PLAT-110405"
$token = "ODE2NjI3MzkyMjM5OlNgw93E++MP7i56u47A2pOJ3Pne"

# Добавляем обработку SSL/TLS (обход проверки сертификата)
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
add-type @"
    using System.Net;
    using System.Security.Cryptography.X509Certificates;
    public class TrustAllCertsPolicy : ICertificatePolicy {
        public bool CheckValidationResult(
            ServicePoint srvPoint, X509Certificate certificate,
            WebRequest request, int certificateProblem) {
            return true;
        }
    }
"@
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy

# Заголовки для запросов
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# Получаем информацию о задаче
$issueUrl = "$baseUrl/rest/api/2/issue/$issueKey"
try {
    $response = Invoke-RestMethod -Uri $issueUrl -Headers $headers -Method Get
}
catch {
    Write-Host "Ошибка при получении информации о задаче: $_" -ForegroundColor Red
    exit
}

# Создаем папку для сохранения вложений
$downloadFolder = "C:\Jira_Attachments\$issueKey"
if (-not (Test-Path -Path $downloadFolder)) {
    New-Item -ItemType Directory -Path $downloadFolder | Out-Null
}

# Скачиваем каждое вложение
foreach ($attachment in $response.fields.attachment) {
    $fileName = $attachment.filename
    $filePath = Join-Path -Path $downloadFolder -ChildPath $fileName
    $downloadUrl = $attachment.content
    
    Write-Host "Скачиваю $fileName..."
    
    try {
        Invoke-RestMethod -Uri $downloadUrl -Headers $headers -Method Get -OutFile $filePath
        Write-Host "Файл $fileName успешно сохранен" -ForegroundColor Green
    }
    catch {
        Write-Host "Ошибка при скачивании $fileName : $_" -ForegroundColor Red
    }
}

Write-Host "Все вложения сохранены в папку $downloadFolder" -ForegroundColor Cyan