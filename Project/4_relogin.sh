$body = @{
    "username" = "testuser_admin"
    "password" = "password1234"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/login" -Method POST -Headers $headers -Body $body
$token = ($response.Content | ConvertFrom-Json).token
