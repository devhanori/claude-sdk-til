from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher, ResultMessage

async def audit_bash(input_data, tool_use_id, context):
    command = input_data.get("tool_input", {}).get("command", "")
    if "rm -rf" in command:
        return {"decision": "block", "reason":"파괴적인 명령어 차단"}
    return {}

async def main():
    async for message in query(
        prompt="auth 모듈 리팩토링",
        options=ClaudeAgentOptions(
            setting_sources=["project"],
            hooks={
                "PreToolUse":[
                    HookMatcher(matcher="Bash", hooks=[audit_bash]),
                ]
            },
        ),
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)
