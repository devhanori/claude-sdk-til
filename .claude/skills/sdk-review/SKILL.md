---
name: sdk-review
description: claude_agent_sdk Python 코드를 리뷰하고 검증할 때 반드시 이 스킬을 사용할 것. SDK API 올바른 사용 여부, 비동기 패턴, 메시지 타입 처리, 에러 핸들링 검토 시 트리거. 리뷰 체크리스트와 자주 발생하는 실수 패턴을 제공한다.
---

## 리뷰 절차

1. 코드를 Read 도구로 직접 읽는다.
2. 아래 체크리스트를 순서대로 확인한다.
3. 발견된 문제를 `_workspace/review.md`에 기록한다.
4. 문제 없으면 sdk-lead에게 "승인" 보고, 있으면 sdk-coder에게 수정 요청.

---

## 체크리스트

### 1. 임포트 정합성

- [ ] `claude_agent_sdk`에서 사용하는 클래스/함수를 모두 임포트했는가?
- [ ] `StreamEvent`는 `claude_agent_sdk.types`에서 임포트하는가?
- [ ] 사용하지 않는 임포트는 없는가?

### 2. 비동기 패턴

- [ ] `query()`를 `async for`로 순회하는가?
- [ ] `ClaudeSDKClient`를 `async with`로 사용하는가?
- [ ] `asyncio.run(main())`으로 진입점을 실행하는가?
- [ ] `async def`가 필요한 곳에 누락되지 않았는가?

### 3. 메시지 타입 처리

- [ ] `AssistantMessage`, `ResultMessage`, `StreamEvent` 중 예제 목적에 맞는 것을 처리하는가?
- [ ] 스트리밍 예제에서 `include_partial_messages=True`를 설정했는가?
- [ ] `ResultMessage`의 `subtype`을 확인하여 오류 상황을 처리하는가?
- [ ] `TextBlock`은 `isinstance(block, TextBlock)`으로 확인하는가? (`hasattr(block, "text")`도 허용)

### 4. ClaudeAgentOptions 사용

- [ ] `allowed_tools`에 실제 사용하는 도구만 포함하는가?
- [ ] `resume` 사용 시 session_id가 실제로 존재하는지 확인 로직이 있는가?
- [ ] `setting_sources`가 예제 목적에 맞게 설정되었는가?

### 5. 훅(Hook) 패턴 (해당 시)

- [ ] 훅 함수 시그니처가 `async def hook(input_data, tool_use_id, context):`인가?
- [ ] 허용 시 `return {}`(빈 dict), 차단 시 `return {"decision": "block", "reason": "..."}`인가?
- [ ] `HookMatcher(matcher="도구명", hooks=[함수])`로 올바르게 등록했는가?

### 6. 코드 품질

- [ ] 주석과 변수명이 예제의 학습 목적을 명확히 전달하는가?
- [ ] 기존 파일(02~10_*.py)과 스타일 일관성을 유지하는가?
- [ ] 파일 넘버링이 올바른가? (기존 최대 번호 + 1)

---

## 자주 발생하는 실수

| 실수 | 올바른 코드 |
|------|-----------|
| `for message in query(...)` | `async for message in query(...)` |
| `StreamEvent` 임포트 누락 | `from claude_agent_sdk.types import StreamEvent` |
| `include_partial_messages` 미설정 + StreamEvent 처리 | `options = ClaudeAgentOptions(include_partial_messages=True, ...)` |
| `ClaudeSDKClient(options)` — positional arg 위치 혼동 | `ClaudeSDKClient(options=options)` 명시 권장 |
| 훅 함수가 `async`가 아닌 경우 | `async def hook_fn(input_data, tool_use_id, context):` |
| `message.result` 사용 시 subtype 미확인 | `if message.subtype == "success": print(message.result)` |
| `if isinstance(message, ResultMessage)` 뒤에 `:` 누락 | Python 문법 오류 — 콜론 확인 |

---

## 리뷰 결과 기록 형식 (`_workspace/review.md`)

```markdown
# 리뷰 결과 — {파일명}

## 상태: [승인 / 수정 요청]

## 발견된 문제 (수정 요청 시)
- [라인 N] {문제 설명} → {수정 방법}

## 승인 근거 (승인 시)
- 체크리스트 전 항목 통과
- {추가 확인 사항}
```
