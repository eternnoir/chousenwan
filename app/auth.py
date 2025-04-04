import hmac
import base64
import hashlib
import os
from typing import Optional

API_SECRET = os.getenv("API_SECRET")

def generate_token(session_id: str) -> Optional[str]:
    """
    基於 API_SECRET 和 session_id 生成一個 token。
    如果 API_SECRET 未設定，則返回 None（表示不啟用驗證）。
    
    Args:
        session_id: 會話 ID
        
    Returns:
        str | None: 生成的 token 或 None（如果 API_SECRET 未設定）
    """
    if not API_SECRET:
        return None
        
    signature = hmac.new(
        API_SECRET.encode(),
        session_id.encode(),
        hashlib.sha256
    ).digest()
    
    token = base64.urlsafe_b64encode(signature).decode().rstrip('=')
    return token

def validate_token(session_id: str, token: str) -> bool:
    """
    驗證提供的 token 是否有效。
    
    Args:
        session_id: 會話 ID
        token: 待驗證的 token
        
    Returns:
        bool: token 是否有效
    """
    if not API_SECRET:
        return True  # 如果 API_SECRET 未設定，則所有 token 都視為有效
        
    expected_token = generate_token(session_id)
    if not expected_token:
        return True
        
    return hmac.compare_digest(expected_token, token)
