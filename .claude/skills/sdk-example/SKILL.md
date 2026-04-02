---
name: sdk-example
description: claude_agent_sdk를 사용하는 Python 예제 코드를 작성할 때 반드시 이 스킬을 사용할 것. query(), ClaudeSDKClient, ClaudeAgentOptions, HookMatcher, 스트리밍, 세션 재개 등 SDK 기능 구현 시 트리거. SDK API 레퍼런스와 코드 패턴을 제공한다.
---

## 핵심 임포트

```python
from claude_agent_sdk import (
    query,                  # 단발성 또는 에이전트 루프
    ClaudeSDKClient,        # 멀티턴 대화 세션
    ClaudeAgentOptions,     # 옵션 설정
    AssistantMessage,       # Claude 응답 메시지
    ResultMessage,          # 최종 결과
    TextBlock,              # 텍스트 블록
    HookMatcher,            # 훅 매처
)
from claude_agent_sdk.types import StreamEvent  # 스트리밍 이벤트
```

---

## ClaudeAgentOptions 주요 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `allowed_tools` | `list[str]` | Claude가 사용할 수 있는 도구 목록 (자동 승인) |
| `permission_mode` | `str` | `"acceptEdits"` — 파일 편집 자동 승인 |
| `system_prompt` | `str` | 시스템 프롬프트 설정 |
| `max_turns` | `int` | 최대 턴 수 제한 |
| `effort` | `str` | `"high"` — 고품질 모드 |
| `setting_sources` | `list[str]` | `["user"]`, `["project"]`, `["user", "project"]` — CLAUDE.md, 스킬, 훅 로드 |
| `resume` | `str` | 이전 세션 ID — 세션 재개 |
| `continue_conversation` | `bool` | `True` — 직전 세션 이어가기 |
| `include_partial_messages` | `bool` | `True` — 스트리밍 이벤트 포함 |
| `hooks` | `dict` | PreToolUse/PostToolUse 훅 설정 |
| `max_budget_usd` | `float` | 비용 한도 (달러) |

---

## 패턴 1: 기본 query() — 에이전트 루프

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

async def main():
    async for message in query(
        prompt="작업 내용",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Glob"],
            permission_mode="acceptEdits",
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"완료: {message.subtype}")
            if message.total_cost_usd is not None:
                print(f"비용: ${message.total_cost_usd:.4f}")

asyncio.run(main())
```

---

## 패턴 2: 세션 재개 (resume)

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async def main():
    session_id = None

    # 1단계: 첫 번째 세션
    async for message in query(
        prompt="분석 작업",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Grep"]),
    ):
        if isinstance(message, ResultMessage):
            session_id = message.session_id
            print(f"세션 ID: {session_id}")

    # 2단계: 세션 재개
    async for message in query(
        prompt="이어서 수정 작업",
        options=ClaudeAgentOptions(
            resume=session_id,
            allowed_tools=["Read", "Edit"],
        ),
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)

asyncio.run(main())
```

---

## 패턴 3: ClaudeSDKClient — 멀티턴 대화

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock

async def main():
    options = ClaudeAgentOptions(allowed_tools=["Read", "Edit"])
    async with ClaudeSDKClient(options=options) as client:

        await client.query("첫 번째 요청")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
            elif isinstance(message, ResultMessage):
                print(f"완료: {message.subtype}")

        await client.query("두 번째 요청 (컨텍스트 유지)")
        async for message in client.receive_response():
            if isinstance(message, ResultMessage):
                print(message.result)

asyncio.run(main())
```

---

## 패턴 4: 스트리밍 이벤트 처리

```python
import asyncio
import sys
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
from claude_agent_sdk.types import StreamEvent

async def main():
    options = ClaudeAgentOptions(
        include_partial_messages=True,   # 스트리밍 활성화 필수
        allowed_tools=["Read", "Bash"],
    )

    in_tool = False
    async for message in query(prompt="작업", options=options):
        if isinstance(message, StreamEvent):
            event = message.event
            event_type = event.get("type")

            if event_type == "content_block_start":
                block = event.get("content_block", {})
                if block.get("type") == "tool_use":
                    print(f"\n[{block.get('name')} 실행 중...]", end="", flush=True)
                    in_tool = True

            elif event_type == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "text_delta" and not in_tool:
                    sys.stdout.write(delta.get("text", ""))
                    sys.stdout.flush()

            elif event_type == "content_block_stop":
                if in_tool:
                    print(" 완료", flush=True)
                    in_tool = False

        elif isinstance(message, ResultMessage):
            print("\n--- 완료 ---")

asyncio.run(main())
```

---

## 패턴 5: PreToolUse 훅

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher, ResultMessage

async def audit_hook(input_data, tool_use_id, context):
    command = input_data.get("tool_input", {}).get("command", "")
    if "rm -rf" in command:
        return {"decision": "block", "reason": "파괴적 명령어 차단"}
    return {}  # 빈 dict = 허용

async def main():
    async for message in query(
        prompt="작업",
        options=ClaudeAgentOptions(
            setting_sources=["project"],
            hooks={
                "PreToolUse": [
                    HookMatcher(matcher="Bash", hooks=[audit_hook]),
                ]
            },
        ),
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)

asyncio.run(main())
```

---

## 패턴 6: 스트리밍 입력 (ClaudeSDKClient)

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

async def main():
    async def message_generator():
        yield {"type": "user", "message": {"role": "user", "content": "첫 번째 메시지"}}
        await asyncio.sleep(1)
        yield {"type": "user", "message": {"role": "user", "content": "두 번째 메시지"}}

    async with ClaudeSDKClient(ClaudeAgentOptions(max_turns=10)) as client:
        await client.query(message_generator())
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

asyncio.run(main())
```

---

## ResultMessage 서브타입

| subtype | 의미 | 대응 |
|---------|------|------|
| `"success"` | 정상 완료 | `message.result` 출력 |
| `"error_max_turns"` | 턴 초과 | `resume=session_id`로 재개 |
| `"error_max_budget_usd"` | 비용 초과 | 예산 재확인 |
| 기타 | 기타 오류 | `message.subtype` 출력 |

## 주요 allowed_tools 값

`"Read"`, `"Edit"`, `"Write"`, `"Glob"`, `"Grep"`, `"Bash"`, `"Skill"`, `"Agent"`, `"WebFetch"`, `"WebSearch"`
