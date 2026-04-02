# 예제 구현 명세: 11_custom_mcp_tools.py

## 목적
`claude_agent_sdk`의 `create_sdk_mcp_server`와 `@tool` 데코레이터를 사용하여
인-프로세스 커스텀 MCP 도구를 정의하고 Claude 에이전트에 연결하는 패턴을 시연한다.

## 파일
- 파일명: `C:/00_workspace/claude-agent-sdk/11_custom_mcp_tools.py`
- 번호: 11 (기존 02~10 다음)

## 사용할 SDK 기능
1. `@tool` 데코레이터 -- 커스텀 도구 정의
2. `create_sdk_mcp_server` -- MCP 서버 생성
3. `query()` -- 에이전트 실행
4. `ClaudeAgentOptions` -- `mcp_servers` 옵션으로 커스텀 서버 연결, `allowed_tools`에 커스텀 도구 등록
5. `ResultMessage`, `AssistantMessage`, `TextBlock` -- 응답 처리

## 예제 시나리오
간단한 메모 관리 도구 (add_memo, list_memos, search_memos)를 만들어서
Claude가 메모를 추가하고 검색할 수 있도록 한다.

## 구현 요구사항
1. `@tool` 데코레이터로 3개의 도구를 정의:
   - `add_memo`: 메모 제목과 내용을 추가 (입력: `{"title": str, "content": str}`)
   - `list_memos`: 현재 저장된 모든 메모 목록 반환 (입력: `{}` 또는 빈 dict)
   - `search_memos`: 키워드로 메모 검색 (입력: `{"keyword": str}`)
2. 인메모리 리스트로 메모 저장 (애플리케이션 상태 공유 시연)
3. `create_sdk_mcp_server("memo_server", tools=[add_memo, list_memos, search_memos])`
4. `ClaudeAgentOptions(mcp_servers={"memo": memo_server}, allowed_tools=[...])`
5. `query()`로 에이전트 실행, 결과 출력

## 스타일 컨벤션 (기존 예제 참고)
- `import asyncio` 사용
- `async def main():` 패턴
- `asyncio.run(main())` 으로 실행
- 한글 주석 사용
- `isinstance()` 기반 메시지 타입 분기
- 파일 상단에 필요한 import만 선언

## 참고 파일
- `05_claude_sdk_client.py` -- 응답 처리 패턴
- SDK `__init__.py`의 `create_sdk_mcp_server` / `@tool` docstring -- API 사용법
