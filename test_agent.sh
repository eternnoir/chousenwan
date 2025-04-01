#!/usr/bin/env bash

# --------------- 參數可自行調整 ------------------
BASE_URL="http://127.0.0.1:8000"
# -------------------------------------------------

echo "==== 1) 建立新 Session ===="
SESSION_JSON=$(curl -s -X POST "${BASE_URL}/sessions" -H "Content-Type: application/json")
echo "Session creation response: $SESSION_JSON"

# 使用 jq 從回傳結果中取出 session_id
SESSION_ID=$(echo "$SESSION_JSON" | jq -r '.session_id')

if [ "$SESSION_ID" = "null" ] || [ -z "$SESSION_ID" ]; then
  echo "無法取得 session_id，請檢查 API 回傳結果或服務是否啟動。"
  exit 1
fi
echo "已取得 session_id: $SESSION_ID"


echo
echo "==== 2) 對此 Session 發送訊息 - 一次回覆 ===="
# 傳送「請幫我算 2 + 3」這句話給 Agent
NON_STREAM_RESP=$(curl -s -X POST "${BASE_URL}/sessions/${SESSION_ID}/chat" \
                    -H "Content-Type: application/json" \
                    -d '{"message": "請幫我算 2 + 3"}')

echo "API 回傳："
echo "$NON_STREAM_RESP"


echo
echo "==== 3) 再發送另一句訊息 - 一次回覆 ===="
# 傳送「現在幾點了？」到同一個 Session
NON_STREAM_RESP2=$(curl -s -X POST "${BASE_URL}/sessions/${SESSION_ID}/chat" \
                     -H "Content-Type: application/json" \
                     -d '{"message": "現在幾點了？"}')

echo "API 回傳："
echo "$NON_STREAM_RESP2"


echo
echo "==== 4) 使用串流模式 (stream = true) ===="
echo "以下將以 SSE (Server-Sent Events) 方式回傳多筆 data："
# 使用 -N 參數讓 curl 即時輸出接收到的資料
curl -N -X POST "${BASE_URL}/sessions/${SESSION_ID}/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "測試串流回覆，幫我講個笑話吧", "stream": true}'

echo
echo "==== 結束 ===="
