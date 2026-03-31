from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
import asyncio

async def single_message_example():

    # query() 함수로 단순 단발성 쿼리
    async for message in query(
        prompt="인증 흐름을 설명해줘",
        options=ClaudeAgentOptions(max_turns=1, allowed_tools=["Read", "Grep"])
    ):
        if isinstance(message, ResultMessage):
            print(message.result)
    
    # 세션 관리로 대화 이어가기
    async for message in query(
        prompt="이제 인가(authorization) 과정을 설명해줘",
        options=ClaudeAgentOptions(continue_conversation=True, max_turns=1),
    ):
        if isinstance(message, ResultMessage):
            print(message.result)

asyncio.run(single_message_example())