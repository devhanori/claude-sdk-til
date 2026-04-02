---
name: sdk-dev
description: Claude Agent SDK 예제 개발 전체 워크플로우를 오케스트레이션. 새 SDK 예제 생성, 기존 예제 코드 개선, SDK 패턴 탐색, claude_agent_sdk 코드 작성 요청 시 반드시 이 스킬을 실행할 것. sdk-lead·sdk-coder·sdk-reviewer 3인 팀을 구성하여 생성-검증 사이클로 고품질 예제를 산출한다.
---

## 실행 모드

**에이전트 팀 (3인)**  
sdk-lead (리더) ↔ sdk-coder ↔ sdk-reviewer  
패턴: 생성-검증 (sdk-coder가 생성 → sdk-reviewer가 검증 → 피드백 루프)

---

## 팀 구성

```
TeamCreate(
  name: "sdk-dev-team",
  members: [
    {name: "sdk-lead",     role: "리더/조율자",  agent: "sdk-lead"},
    {name: "sdk-coder",    role: "코드 작성",   agent: "sdk-coder"},
    {name: "sdk-reviewer", role: "코드 리뷰",   agent: "sdk-reviewer"},
  ]
)
```

모든 Agent 호출 시 `model: "opus"` 파라미터를 명시한다.

---

## 워크플로우

### Phase 1: 요청 분석 (sdk-lead)

1. 사용자 요청에서 구현할 SDK 기능/패턴 파악
2. 기존 예제 파일(02~10_*.py) 확인하여 파일 넘버링 및 스타일 파악
3. 구현 명세 작성 → `_workspace/spec.md` 저장
4. sdk-coder에게 구현 명세 전달

### Phase 2: 코드 작성 (sdk-coder)

1. sdk-lead의 구현 명세 수신
2. **sdk-example 스킬** 참고하여 코드 작성
3. Python 파일 생성 (`C:/00_workspace/claude-agent-sdk/{번호}_{이름}.py`)
4. sdk-reviewer에게 리뷰 요청

### Phase 3: 코드 리뷰 (sdk-reviewer)

1. sdk-coder의 리뷰 요청 수신
2. **sdk-review 스킬**의 체크리스트로 코드 검토
3. 리뷰 결과를 `_workspace/review.md`에 기록
4. 승인 → sdk-lead에게 완료 보고 / 수정 요청 → sdk-coder에게 피드백

### Phase 4: 수정 루프 (sdk-coder ↔ sdk-reviewer)

- sdk-coder가 피드백 반영 후 재리뷰 요청
- 최대 2회 반복. 3회 이후 해결 불가 시 sdk-lead가 개입

### Phase 5: 완료 보고 (sdk-lead)

1. sdk-reviewer의 승인 수신
2. 사용자에게 최종 결과 보고 (파일 위치, 구현 내용 요약)
3. `_workspace/` 폴더는 보존 (감사 추적용)

---

## 데이터 전달

| 파일 | 작성자 | 독자 | 내용 |
|------|--------|------|------|
| `_workspace/spec.md` | sdk-lead | sdk-coder | 구현 명세 |
| `_workspace/review.md` | sdk-reviewer | sdk-lead | 리뷰 결과 |

산출물(`.py` 파일)은 `C:/00_workspace/claude-agent-sdk/` 루트에 저장한다.

---

## 에러 핸들링

| 상황 | 처리 |
|------|------|
| sdk-coder 구현 불가 | sdk-lead가 대안 패턴 제안 후 재시도 |
| 리뷰 실패 2회 반복 | sdk-lead가 개입, 세 에이전트 공동 논의 |
| 파일 번호 충돌 | sdk-coder가 기존 파일 목록을 Glob으로 재확인 |

---

## 테스트 시나리오

### 정상 흐름

**입력:** "query()로 비용 예산 제한을 설정하는 예제 만들어줘"

1. sdk-lead: 기존 파일 확인 → 다음 번호 파악 → spec.md 작성
2. sdk-coder: sdk-example 스킬 참고 → `max_budget_usd` 옵션 포함 코드 작성
3. sdk-reviewer: 체크리스트 통과 → 승인
4. sdk-lead: 사용자에게 파일 위치 보고

### 에러 흐름

**입력:** "존재하지 않는 SDK 기능 X를 사용하는 예제 만들어줘"

1. sdk-coder: sdk-example 스킬에서 해당 기능 미발견 → sdk-lead에게 알림
2. sdk-lead: 유사 기능 대안 탐색 → 사용자에게 확인 요청
3. 사용자 승인 시 대안으로 진행
