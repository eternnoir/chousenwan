import uuid
from typing import Dict

from agents.items import TResponseInputItem
from agents.agent import Agent

class SessionState:
    def __init__(self, conversation_items: list[TResponseInputItem], last_agent: Agent):
        self.conversation_items = conversation_items
        self.last_agent = last_agent

class SessionManager:
    """
    In-memory session manager. 
    每個 session 都有自己的對話歷史與最後的 Agent 狀態。
    """
    def __init__(self):
        self._sessions: Dict[str, SessionState] = {}

    def create_session(self, initial_agent: Agent) -> str:
        """
        建立新的 Session，回傳 session_id。
        """
        session_id = str(uuid.uuid4())
        # 初始對話歷史為空
        self._sessions[session_id] = SessionState(
            conversation_items=[],
            last_agent=initial_agent
        )
        return session_id

    def get_session(self, session_id: str) -> SessionState:
        """
        取得指定 session 的狀態。
        若不存在則拋出 KeyError。
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session {session_id} not found.")
        return self._sessions[session_id]

    def update_session(
        self, 
        session_id: str, 
        conversation_items: list[TResponseInputItem], 
        last_agent: Agent
    ) -> None:
        """
        更新指定 session 的對話歷史與最後的 Agent。
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session {session_id} not found.")
        self._sessions[session_id].conversation_items = conversation_items
        self._sessions[session_id].last_agent = last_agent
