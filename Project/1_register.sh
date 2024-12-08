$headers = @{
    "Content-Type" = "application/json"
}
$body = @{
    "username" = "testuser2"
    "email" = "testuser2@example.com"
    "password" = "password1234"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/register" -Method POST -Headers $headers -Body $body
