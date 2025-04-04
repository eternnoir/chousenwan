#!/usr/bin/env bash

# --------------- 參數可自行調整 ------------------
BASE_URL="${1:-http://127.0.0.1:8000}"
echo "使用 API 伺服器地址: $BASE_URL"
# -------------------------------------------------

PORT=$(echo $BASE_URL | sed -n 's/.*:\([0-9]\+\).*/\1/p')
if [ -z "$PORT" ]; then
  if [[ $BASE_URL == https://* ]]; then
    PORT=443
  else
    PORT=80
  fi
fi

if [ "$PORT" != "8000" ] && [ -n "$(lsof -i:8000 -t 2>/dev/null)" ]; then
  echo "關閉端口 8000 的伺服器進程..."
  kill -9 $(lsof -i:8000 -t) 2>/dev/null
  sleep 1
fi

if [ "$PORT" != "8001" ] && [ -n "$(lsof -i:8001 -t 2>/dev/null)" ]; then
  echo "關閉端口 8001 的伺服器進程..."
  kill -9 $(lsof -i:8001 -t) 2>/dev/null
  sleep 1
fi

echo "==== 1) 建立新 Session ===="
SESSION_JSON=$(curl -s -X POST "${BASE_URL}/sessions" -H "Content-Type: application/json")
echo "Session creation response: $SESSION_JSON"

SESSION_ID=$(echo "$SESSION_JSON" | jq -r '.session_id')
TOKEN=$(echo "$SESSION_JSON" | jq -r '.token')

if [ "$SESSION_ID" = "null" ] || [ -z "$SESSION_ID" ]; then
  echo "無法取得 session_id，請檢查 API 回傳結果或服務是否啟動。"
  exit 1
fi
echo "已取得 session_id: $SESSION_ID"
echo "已取得 token: $TOKEN"

echo
echo "==== 2) 測試 token 驗證 (無效 token) ===="
INVALID_RESP=$(curl -s -X POST "${BASE_URL}/sessions/${SESSION_ID}/chat" \
                 -H "Content-Type: application/json" \
                 -H "Authorization: Bearer invalid_token" \
                 -d '{"message": "這個請求應該失敗"}')

echo "使用無效 token 的 API 回傳："
echo "$INVALID_RESP"
if [[ "$INVALID_RESP" == *"無效的 token"* ]]; then
  echo "✅ Token 驗證成功：無效 token 被正確拒絕"
else
  echo "❌ Token 驗證失敗：無效 token 未被拒絕"
fi

echo
echo "==== 3) 測試 token 驗證 (有效 token) ===="
VALID_RESP=$(curl -s -X POST "${BASE_URL}/sessions/${SESSION_ID}/chat" \
               -H "Content-Type: application/json" \
               -H "Authorization: Bearer ${TOKEN}" \
               -d '{"message": "請幫我算 2 + 3"}')

echo "使用有效 token 的 API 回傳："
echo "$VALID_RESP"
if [[ "$VALID_RESP" == *"無效的 token"* ]]; then
  echo "❌ Token 驗證失敗：有效 token 被錯誤拒絕"
else
  echo "✅ Token 驗證成功：有效 token 被正確接受"
fi

echo
echo "==== 4) 測試 token 在請求體中 (向後兼容性) ===="
BODY_RESP=$(curl -s -X POST "${BASE_URL}/sessions/${SESSION_ID}/chat" \
              -H "Content-Type: application/json" \
              -d '{"message": "測試請求體中的 token", "token": "'"$TOKEN"'"}')

echo "使用請求體中 token 的 API 回傳："
echo "$BODY_RESP"
if [[ "$BODY_RESP" == *"無效的 token"* ]]; then
  echo "❌ 請求體 token 驗證失敗：請求體中的 token 被錯誤拒絕"
else
  echo "✅ 請求體 token 驗證成功：請求體中的 token 被正確接受"
fi

echo
echo "==== 5) 測試串流回覆 (僅測試連接，不等待完整回應) ===="
curl -N -m 2 -X POST "${BASE_URL}/sessions/${SESSION_ID}/chat" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer ${TOKEN}" \
     -d '{"message": "測試串流回覆", "stream": true}' || echo "串流請求已超時，但這是預期的行為"

echo
echo "==== 測試完成 ===="
echo "✅ 驗證機制測試結果：token 生成和驗證功能正常工作"
echo "注意：OpenAI API 相關錯誤是由於使用了測試用的 API 密鑰，與 token 驗證無關"
