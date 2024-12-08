$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $token"
}
$body = @{
    "role" = "admin"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/user/update" -Method PUT -Headers $headers -Body $body
