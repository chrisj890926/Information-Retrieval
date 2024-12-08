$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $token"
}

Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/admin" -Method GET -Headers $headers
