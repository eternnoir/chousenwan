import random
from datetime import datetime
from typing import Any

from agents import (
    Agent,
    function_tool,
    handoff
)
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from agents.handoffs import handoff
#
# === Function Tools ===
#
@function_tool
def calc_sum(a: int, b: int) -> int:
    """
    計算兩個整數的總和。

    Args:
        a: 整數 a
        b: 整數 b
    """
    return a + b


@function_tool
def get_time() -> str:
    """
    回傳目前的日期與時間 (UTC)。
    """
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


#
# === Sub-Agents ===
#
math_agent = Agent(
    name="MathAgent",
    instructions=prompt_with_handoff_instructions(
        "你只負責數學相關的需求，並可以使用 `calc_sum` 工具幫忙計算加總。"
        "你的回答應該保持簡潔而精準。"
    ),
    tools=[calc_sum],
    model="gpt-4o"
)

time_agent = Agent(
    name="TimeAgent",
    instructions=prompt_with_handoff_instructions(
        "你只負責時間/時區相關的需求，並可以使用 `get_time` 工具告知目前時間。"
    ),
    tools=[get_time],
    model="gpt-4o"
)

#
# === Triage (主) Agent ===
#   透過 prompt_with_handoff_instructions 讓 Agent 理解可 handoff 到其他子 Agent 的機制。
#
triage_agent = Agent(
    name="TriageAgent",
    instructions=prompt_with_handoff_instructions(
        "你是總管，用來判斷使用者的需求並決定要如何回答：\n"
        "- 如果使用者想做簡單數學運算，就 handoff 給 MathAgent\n"
        "- 如果使用者想查詢時間，則 handoff 給 TimeAgent\n"
        "若你能直接回答也可直接回答，但若和數學或時間相關，應適度使用 handoff。"
    ),
    model="gpt-4o",
    handoffs=[
        handoff(math_agent),
        handoff(time_agent),
    ],
)

time_agent.handoffs=[
        handoff(triage_agent)
    ]
math_agent.handoffs=[
        handoff(triage_agent)
    ]