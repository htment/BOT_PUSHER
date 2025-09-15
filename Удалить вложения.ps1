# Параметры подключения
$baseUrl = "https://sd.v-serv.ru/jira"
$issueKey = "PLAT-110405"
$token = "ваш токен"

# Настройка обработки SSL/TLS (для обхода проверки сертификата)
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
Add-Type @"
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

# Получаем информацию о задаче и вложениях
$issueUrl = "$baseUrl/rest/api/2/issue/$issueKey"
try {
    $response = Invoke-RestMethod -Uri $issueUrl -Headers $headers -Method Get
    $attachments = $response.fields.attachment
}
catch {
    Write-Host "Ошибка при получении информации о задаче: $_" -ForegroundColor Red
    exit
}

if (-not $attachments -or $attachments.Count -eq 0) {
    Write-Host "В задаче $issueKey нет вложений для удаления" -ForegroundColor Yellow
    exit
}

# Удаляем каждое вложение
foreach ($attachment in $attachments) {
    $attachmentId = $attachment.id
    $fileName = $attachment.filename
    $deleteUrl = "$baseUrl/rest/api/2/attachment/$attachmentId"
    
    Write-Host "Удаляю вложение $fileName (ID: $attachmentId)..."
    
    try {
        $result = Invoke-RestMethod -Uri $deleteUrl -Headers $headers -Method Delete
        Write-Host "Вложение $fileName успешно удалено" -ForegroundColor Green
    }
    catch {
        Write-Host "Ошибка при удалении вложения $fileName : $_" -ForegroundColor Red
    }
}

Write-Host "Обработка вложений задачи $issueKey завершена" -ForegroundColor Cyan