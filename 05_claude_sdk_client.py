import asyncio
from claude_agent_sdk import(
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock
)

def print_response(message):
    """메시지에서 사람이 읽을 수 있는 부분만 출력."""
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)
    elif isinstance(message, ResultMessage):
        cost = (
            f"${message.total_cost_usd:.4f}"
            if message.total_cost_usd is not None
            else "N/A"
        )
        print(f"완료: {message.subtype}, 비용: {cost}")


async def main():
    opthions = ClaudeAgentOptions(
        allowed_tools=["Read", "Edit", "Glob", "Grep"],
    )
    async with ClaudeSDKClient(options=opthions) as client:

        await client.query("auth 모듈을 분석해줘")
        async for message in client.receive_response():
            print_response(message)

        await client.query("이제 JWT를 사용하도록 리팩토링해줘")
        async for message in client.receive_response():
            print_response(message)

asyncio.run(main())
