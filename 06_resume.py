import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async def main():
    session_id = None

    async for message in query(
        prompt="auth 모듈 분석 및 개선점 제안",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep"],
        ),
    ):
        if isinstance(message, ResultMessage):
            session_id = message.session_id
            if message.subtype == "success":
                print(message.result)
    
    print(f"세션 ID: {session_id}")
    return session_id

session_id = asyncio.run(main())

async def Resume():
    async for message in query(
        prompt="제안한 리팩토링을 이제 구현해줘",
        options=ClaudeAgentOptions(
            resume=session_id,
            allowed_tools=["Read", "Edit", "Write", "Glob", "Grep"],
        ),
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)