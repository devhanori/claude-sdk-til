"""커스텀 MCP 도구 예제.

`@tool` 데코레이터와 `create_sdk_mcp_server`를 사용하여
인-프로세스 MCP 서버를 만들고 Claude 에이전트에 연결하는 패턴을 시연한다.

시나리오: 간단한 메모 관리 도구 (추가 / 목록 / 검색)를 정의하고,
Claude가 이 도구들을 호출하여 메모를 관리하도록 한다.
"""

import asyncio
from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)

# ---------------------------------------------------------------------------
# 애플리케이션 상태 -- 인메모리 메모 저장소
# MCP 도구 핸들러가 같은 프로세스에서 이 상태에 직접 접근할 수 있다.
# ---------------------------------------------------------------------------
memos: list[dict[str, str]] = []


# ---------------------------------------------------------------------------
# 커스텀 MCP 도구 정의
# ---------------------------------------------------------------------------

@tool("add_memo", "메모를 추가한다", {"title": str, "content": str})
async def add_memo(args: dict) -> dict:
    """제목과 내용으로 메모를 추가한다."""
    memo = {"title": args["title"], "content": args["content"]}
    memos.append(memo)
    return {
        "content": [
            {"type": "text", "text": f"메모가 추가되었습니다: {memo['title']}"}
        ]
    }


@tool("list_memos", "저장된 모든 메모 목록을 반환한다", {})
async def list_memos(args: dict) -> dict:
    """현재 저장된 모든 메모를 반환한다."""
    if not memos:
        return {"content": [{"type": "text", "text": "저장된 메모가 없습니다."}]}

    lines = []
    for i, memo in enumerate(memos, 1):
        lines.append(f"{i}. [{memo['title']}] {memo['content']}")

    return {"content": [{"type": "text", "text": "\n".join(lines)}]}


@tool("search_memos", "키워드로 메모를 검색한다", {"keyword": str})
async def search_memos(args: dict) -> dict:
    """키워드가 제목 또는 내용에 포함된 메모를 검색한다."""
    keyword = args["keyword"].lower()
    results = [
        memo for memo in memos
        if keyword in memo["title"].lower() or keyword in memo["content"].lower()
    ]

    if not results:
        return {
            "content": [
                {"type": "text", "text": f"'{args['keyword']}'에 해당하는 메모가 없습니다."}
            ]
        }

    lines = []
    for memo in results:
        lines.append(f"- [{memo['title']}] {memo['content']}")

    return {"content": [{"type": "text", "text": "\n".join(lines)}]}


# ---------------------------------------------------------------------------
# MCP 서버 생성 및 에이전트 실행
# ---------------------------------------------------------------------------

# 도구들을 하나의 인-프로세스 MCP 서버로 묶는다
memo_server = create_sdk_mcp_server(
    name="memo_server",
    version="1.0.0",
    tools=[add_memo, list_memos, search_memos],
)


async def main():
    options = ClaudeAgentOptions(
        # 커스텀 MCP 서버 등록
        mcp_servers={"memo": memo_server},
        # 커스텀 도구를 허용 목록에 추가
        allowed_tools=["add_memo", "list_memos", "search_memos"],
        max_turns=10,
    )

    async for message in query(
        prompt=(
            "다음 메모 3개를 추가한 뒤, 전체 목록을 보여주고, "
            "'회의'라는 키워드로 검색해줘.\n"
            "1. 제목: 회의 안건, 내용: Q2 로드맵 논의\n"
            "2. 제목: 점심 메뉴, 내용: 팀 회식 장소 투표\n"
            "3. 제목: 회의록, 내용: 디자인 리뷰 결과 정리"
        ),
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

        if isinstance(message, ResultMessage):
            if message.subtype == "success":
                print(f"\n완료 (비용: ${message.total_cost_usd:.4f})"
                      if message.total_cost_usd is not None
                      else "\n완료")
            else:
                print(f"\n종료: {message.subtype} - {message.result}")


asyncio.run(main())
