from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
from claude_agent_sdk.types import StreamEvent
import asyncio
import sys


async def streaming_ui():
    options = ClaudeAgentOptions(
        include_partial_messages=True,
        allowed_tools=["Read", "Bash", "Grep"],
    )

    # 현재 도구 호출 중인지 추적
    in_tool = False

    async for message in query(
        prompt="코드베이스에서 모든 TODO 주석을 찾아줘", options=options
    ):
        if isinstance(message, StreamEvent):
            event = message.event
            event_type = event.get("type")

            if event_type == "content_block_start":
                content_block = event.get("content_block", {})
                if content_block.get("type") == "tool_use":
                    # 도구 호출 시작 - 상태 표시기 표시
                    tool_name = content_block.get("name")
                    print(f"\n[{tool_name} 사용 중...]", end="", flush=True)
                    in_tool = True

            elif event_type == "content_block_delta":
                delta = event.get("delta", {})
                # 도구 실행 중이 아닐 때만 텍스트 스트리밍
                if delta.get("type") == "text_delta" and not in_tool:
                    sys.stdout.write(delta.get("text", ""))
                    sys.stdout.flush()

            elif event_type == "content_block_stop":
                if in_tool:
                    # 도구 호출 완료
                    print(" 완료", flush=True)
                    in_tool = False

        elif isinstance(message, ResultMessage):
            # 에이전트 작업 완료
            print(f"\n\n--- 완료 ---")


asyncio.run(streaming_ui())