from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

async def test():
    async for message in query(
        prompt="auth 모듈 리팩토링 도와줘",
        options=ClaudeAgentOptions(
            setting_sources=["user", "project"],
            allowed_tools=["Skill", "Read", "Edit", "Bash"],
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)
        if isinstance(message, ResultMessage)
            print(f"\nResult: {message.result}")

