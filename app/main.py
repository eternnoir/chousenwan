import os
import asyncio
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Response, Header
from fastapi.responses import StreamingResponse

from agents import Runner
from agents.items import TResponseInputItem
from agents.run_context import RunContextWrapper

# 載入我們定義的檔案
from .agent_config import triage_agent
from .session_manager import SessionManager
from .schemas import CreateSessionResponse, ChatRequest, ChatResponse
from .auth import generate_token, validate_token


app = FastAPI(title="Multi-Agent Conversation API")

# 建立全域的 session manager
session_manager = SessionManager()

# 建立 API Key 驗證 (可自行擴充)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("警告：未設定 OPENAI_API_KEY，請先在環境變數中設定。")

API_SECRET = os.getenv("API_SECRET")
if not API_SECRET:
    print("警告：未設定 API_SECRET，API 將不會進行 token 驗證。")


@app.post("/sessions", response_model=CreateSessionResponse)
def create_session():
    """
    建立一個新的對話 Session，並回傳 session_id。
    """
    session_id = session_manager.create_session(initial_agent=triage_agent)
    token = generate_token(session_id)
    return CreateSessionResponse(session_id=session_id, token=token)


@app.post("/sessions/{session_id}/chat")
async def chat_with_agent(
    session_id: str, 
    request: ChatRequest, 
    authorization: str = Header(None)
):
    """
    與對話 Session 進行互動，並得到 AI 回覆。
    - message: 使用者輸入
    - stream: 是否以串流方式回應 (Server-Sent Events)
    - authorization: 驗證 token (HTTP Header)
    """
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
    else:
        token = request.token
        
    if API_SECRET and not validate_token(session_id, token or ""):
        raise HTTPException(status_code=401, detail="無效的 token。")
        
    # 取得 Session
    try:
        session_state = session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found.")

    # 將使用者輸入加到既有對話歷史
    # 這裡使用 Agents SDK "TResponseInputItem" 格式
    conversation_items = list(session_state.conversation_items)  # shallow copy
    conversation_items.append({"role": "user", "content": request.message})

    # 取得目前的 Agent
    current_agent = session_state.last_agent

    # 決定要一次回覆或串流回覆
    if request.stream:
        return StreamingResponse(
            content=_stream_response(session_id, conversation_items, current_agent),
            media_type="text/event-stream"
        )
    else:
        # 直接一次跑完
        result = await Runner.run(
            starting_agent=current_agent,
            input=conversation_items,
            context=None  # 也可以放自定義 RunContextWrapper
        )
        # 更新 session 狀態
        new_history = result.to_input_list()
        session_manager.update_session(session_id, new_history, result.last_agent)

        return ChatResponse(response=result.final_output)


async def _stream_response(
    session_id: str,
    conversation_items: list[TResponseInputItem],
    current_agent
) -> AsyncGenerator[str, None]:
    """
    以 SSE (text/event-stream) 格式串流回覆。
    我們使用 `Runner.run_streamed()` 取得 run_result，
    再從 `run_result.stream_events()` 逐步輸出 token。
    """
    # 注意：在 SSE 透過 yield 逐段輸出時，格式一般為：
    #   "data: <some_text>\n\n"
    # 或者根據前端需求自訂格式

    run_result_streamed = Runner.run_streamed(
        starting_agent=current_agent,
        input=conversation_items,
        context=None
    )

    # stream events
    async for event in run_result_streamed.stream_events():
        # 我們可以根據 event 類型決定如何顯示。這邊簡單示範對 "response.output_text.delta" 做 streaming。
        if event.type == "raw_response_event":
            # event.data 可能是 openai.types.responses.ResponseTextDeltaEvent
            # 我們只抓其中的 delta 來輸出
            delta = getattr(event.data, "delta", "")
            if delta:
                # SSE 格式
                yield f"data: {delta}\n\n"
        # 也可監聽其它 type (tool call, agent update, reasoning 等)，看要如何顯示

    # 最終完整資料
    # 更新 session 狀態
    new_history = run_result_streamed.to_input_list()
    session_manager.update_session(session_id, new_history, run_result_streamed.last_agent)


#
# 若你需要直接用命令啟動 (如: python -m app.main)，可以在此定義 entry point:
#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
