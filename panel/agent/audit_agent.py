"""
Yandex Direct Audit Agent using Claude Agent SDK.

This agent performs comprehensive audits of Yandex Direct accounts
using AI-powered analysis and custom tools.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, asdict

# Try to import Claude Agent SDK
try:
    from claude_agent_sdk import (
        tool,
        create_sdk_mcp_server,
        ClaudeSDKClient,
        ClaudeAgentOptions,
        AssistantMessage,
        TextBlock
    )
    CLAUDE_SDK_AVAILABLE = True
except ImportError:
    CLAUDE_SDK_AVAILABLE = False
    # Fallback imports for basic Anthropic API
    try:
        import anthropic
        ANTHROPIC_AVAILABLE = True
    except ImportError:
        ANTHROPIC_AVAILABLE = False

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from yandex_api import YandexDirectAPI
from agent.tools import audit_tools


# Default model - Claude Haiku 4.5 (latest as of Oct 2025)
DEFAULT_MODEL = "claude-haiku-4-5-20251022"


@dataclass
class AuditConfig:
    """Configuration for audit agent."""
    model: str = DEFAULT_MODEL
    max_tokens: int = 4096
    temperature: float = 0.3
    use_sdk: bool = True  # Use Claude Agent SDK if available


@dataclass
class AuditResult:
    """Result of an audit run."""
    verdict: str
    score: float
    issues_count: int
    critical_count: int
    potential_savings: float
    full_report: dict
    raw_messages: list

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class YandexDirectAuditAgent:
    """
    AI-powered audit agent for Yandex Direct accounts.
    Uses Claude Agent SDK with custom tools for comprehensive analysis.
    """

    def __init__(
        self,
        yandex_token: str,
        yandex_login: str,
        account_name: str,
        anthropic_api_key: str = None,
        config: AuditConfig = None
    ):
        """
        Initialize the audit agent.

        Args:
            yandex_token: OAuth token for Yandex Direct API
            yandex_login: Yandex Direct login
            account_name: Friendly name for the account
            anthropic_api_key: Anthropic API key (or use env var)
            config: Audit configuration
        """
        self.yandex_token = yandex_token
        self.yandex_login = yandex_login
        self.account_name = account_name
        self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.config = config or AuditConfig()

        # Initialize Yandex API client
        self.yandex_api = YandexDirectAPI(
            token=yandex_token,
            login=yandex_login
        )

        # Set API client for tools
        audit_tools.set_api_client(self.yandex_api)

        # Load system prompt
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load system prompt from file."""
        prompt_path = Path(__file__).parent / "prompts" / "system.md"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """Get default system prompt if file not found."""
        return """Ты — эксперт-аудитор рекламных кампаний Яндекс Директ.
Проведи полный аудит аккаунта, используя доступные инструменты.
Выдай заключение: ХОРОШО / ТРЕБУЕТ УЛУЧШЕНИЯ / ПЛОХО."""

    async def run_audit(self) -> AuditResult:
        """
        Run a complete audit of the Yandex Direct account.

        Returns:
            AuditResult with findings and recommendations.
        """
        # Reset memory for new audit
        audit_tools.reset_memory()

        if CLAUDE_SDK_AVAILABLE and self.config.use_sdk:
            return await self._run_with_sdk()
        elif ANTHROPIC_AVAILABLE:
            return await self._run_with_anthropic_api()
        else:
            raise RuntimeError("Neither Claude Agent SDK nor Anthropic library available")

    async def _run_with_sdk(self) -> AuditResult:
        """Run audit using Claude Agent SDK."""

        # Define tools using SDK decorator
        @tool("get_campaigns_stats", "Получить статистику по кампаниям: расходы, клики, показы, конверсии за 30 дней", {})
        async def sdk_get_campaigns_stats(args: dict[str, Any]) -> dict[str, Any]:
            return await audit_tools.get_campaigns_stats(args)

        @tool("get_budget_conflicts", "Проверить конфликты бюджетов: лимиты, достаточность для конверсий, соответствие ставкам", {})
        async def sdk_get_budget_conflicts(args: dict[str, Any]) -> dict[str, Any]:
            return await audit_tools.get_budget_conflicts(args)

        @tool("get_conversions_status", "Проверить настройки конверсий: цели из Метрики, привязка к кампаниям", {})
        async def sdk_get_conversions_status(args: dict[str, Any]) -> dict[str, Any]:
            return await audit_tools.get_conversions_status(args)

        @tool("get_keywords_analysis", "Анализ ключевых слов: минус-слова, пересечения, типы соответствия", {})
        async def sdk_get_keywords_analysis(args: dict[str, Any]) -> dict[str, Any]:
            return await audit_tools.get_keywords_analysis(args)

        @tool("get_autotargeting_stats", "Проверить процент автотаргетинга (ТРЕВОГА если >20%)", {})
        async def sdk_get_autotargeting_stats(args: dict[str, Any]) -> dict[str, Any]:
            return await audit_tools.get_autotargeting_stats(args)

        @tool("get_ads_quality", "Анализ объявлений: орфография, привлекательность, A/B тестирование, расширения", {})
        async def sdk_get_ads_quality(args: dict[str, Any]) -> dict[str, Any]:
            return await audit_tools.get_ads_quality(args)

        @tool("get_account_structure", "Анализ структуры: количество кампаний/групп, логичность, названия", {})
        async def sdk_get_account_structure(args: dict[str, Any]) -> dict[str, Any]:
            return await audit_tools.get_account_structure(args)

        @tool("get_utm_analysis", "Проверка UTM-разметки в ссылках объявлений", {})
        async def sdk_get_utm_analysis(args: dict[str, Any]) -> dict[str, Any]:
            return await audit_tools.get_utm_analysis(args)

        @tool("save_to_memory", "Сохранить данные в память аудита", {"key": str, "value": str})
        async def sdk_save_to_memory(args: dict[str, Any]) -> dict[str, Any]:
            return await audit_tools.save_to_memory(args)

        @tool("get_memory", "Получить данные из памяти аудита", {"key": str})
        async def sdk_get_memory(args: dict[str, Any]) -> dict[str, Any]:
            return await audit_tools.get_memory(args)

        @tool("generate_verdict", "Сгенерировать финальное заключение аудита", {})
        async def sdk_generate_verdict(args: dict[str, Any]) -> dict[str, Any]:
            return await audit_tools.generate_verdict(args)

        # Create MCP server with all tools
        audit_server = create_sdk_mcp_server(
            name="yandex_direct_audit",
            version="1.0.0",
            tools=[
                sdk_get_campaigns_stats,
                sdk_get_budget_conflicts,
                sdk_get_conversions_status,
                sdk_get_keywords_analysis,
                sdk_get_autotargeting_stats,
                sdk_get_ads_quality,
                sdk_get_account_structure,
                sdk_get_utm_analysis,
                sdk_save_to_memory,
                sdk_get_memory,
                sdk_generate_verdict
            ]
        )

        # Configure agent options
        options = ClaudeAgentOptions(
            system_prompt=self.system_prompt,
            model=self.config.model,
            mcp_servers={"audit": audit_server},
            allowed_tools=[
                "mcp__audit__get_campaigns_stats",
                "mcp__audit__get_budget_conflicts",
                "mcp__audit__get_conversions_status",
                "mcp__audit__get_keywords_analysis",
                "mcp__audit__get_autotargeting_stats",
                "mcp__audit__get_ads_quality",
                "mcp__audit__get_account_structure",
                "mcp__audit__get_utm_analysis",
                "mcp__audit__save_to_memory",
                "mcp__audit__get_memory",
                "mcp__audit__generate_verdict"
            ]
        )

        messages = []

        # Run the agent
        async with ClaudeSDKClient(options=options) as client:
            await client.query(
                f"Проведи полный аудит аккаунта Яндекс Директ '{self.account_name}' (логин: {self.yandex_login}). "
                "Последовательно выполни все проверки и в конце выдай заключение."
            )

            async for message in client.receive_response():
                messages.append(message)
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(f"Agent: {block.text[:200]}...")

        return self._parse_result(messages)

    async def _run_with_anthropic_api(self) -> AuditResult:
        """Run audit using basic Anthropic API (fallback)."""
        client = anthropic.Anthropic(api_key=self.api_key)

        # Define tools for API
        tools = [
            {
                "name": "get_campaigns_stats",
                "description": "Получить статистику по кампаниям: расходы, клики, показы, конверсии за 30 дней",
                "input_schema": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "get_budget_conflicts",
                "description": "Проверить конфликты бюджетов: лимиты, достаточность для конверсий",
                "input_schema": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "get_conversions_status",
                "description": "Проверить настройки конверсий: цели из Метрики",
                "input_schema": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "get_keywords_analysis",
                "description": "Анализ ключевых слов: минус-слова, типы соответствия",
                "input_schema": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "get_autotargeting_stats",
                "description": "Проверить процент автотаргетинга",
                "input_schema": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "get_ads_quality",
                "description": "Анализ качества объявлений",
                "input_schema": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "get_account_structure",
                "description": "Анализ структуры аккаунта",
                "input_schema": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "get_utm_analysis",
                "description": "Проверка UTM-разметки",
                "input_schema": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "generate_verdict",
                "description": "Сгенерировать финальное заключение",
                "input_schema": {"type": "object", "properties": {}, "required": []}
            }
        ]

        tool_handlers = {
            "get_campaigns_stats": audit_tools.get_campaigns_stats,
            "get_budget_conflicts": audit_tools.get_budget_conflicts,
            "get_conversions_status": audit_tools.get_conversions_status,
            "get_keywords_analysis": audit_tools.get_keywords_analysis,
            "get_autotargeting_stats": audit_tools.get_autotargeting_stats,
            "get_ads_quality": audit_tools.get_ads_quality,
            "get_account_structure": audit_tools.get_account_structure,
            "get_utm_analysis": audit_tools.get_utm_analysis,
            "generate_verdict": audit_tools.generate_verdict
        }

        messages = [
            {
                "role": "user",
                "content": f"Проведи полный аудит аккаунта Яндекс Директ '{self.account_name}' (логин: {self.yandex_login}). "
                           "Последовательно выполни все проверки и в конце выдай заключение."
            }
        ]

        all_messages = []

        # Agentic loop
        while True:
            response = client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                system=self.system_prompt,
                tools=tools,
                messages=messages
            )

            all_messages.append(response)

            # Check if we need to handle tool calls
            if response.stop_reason == "tool_use":
                # Process tool calls
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input

                        print(f"Calling tool: {tool_name}")

                        # Execute tool
                        handler = tool_handlers.get(tool_name)
                        if handler:
                            result = await handler(tool_input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result["content"][0]["text"]
                            })

                # Add assistant message and tool results
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

            else:
                # End of conversation
                break

        return self._parse_result(all_messages)

    def _parse_result(self, messages: list) -> AuditResult:
        """Parse messages into AuditResult."""
        # Get final verdict from memory
        verdict_data = audit_tools.audit_memory.get("scores", {})

        avg_score = sum(verdict_data.values()) / len(verdict_data) if verdict_data else 0

        if avg_score >= 80:
            verdict = "ХОРОШО"
        elif avg_score >= 50:
            verdict = "ТРЕБУЕТ УЛУЧШЕНИЯ"
        else:
            verdict = "ПЛОХО"

        # Count issues
        all_issues = []
        for key in ["budget_issues", "conversion_issues", "keyword_issues",
                    "autotargeting_issues", "ads_issues", "structure_issues", "utm_issues"]:
            all_issues.extend(audit_tools.audit_memory.get(key, []))

        critical_count = len([i for i in all_issues if i.get("type") == "critical"])

        # Calculate savings
        total_savings = sum(
            i.get("potential_savings", 0) or i.get("potential_loss", 0)
            for i in all_issues
        )

        return AuditResult(
            verdict=verdict,
            score=round(avg_score, 1),
            issues_count=len(all_issues),
            critical_count=critical_count,
            potential_savings=round(total_savings, 0),
            full_report={
                "scores": verdict_data,
                "issues": all_issues,
                "campaigns": audit_tools.audit_memory.get("campaigns", {})
            },
            raw_messages=[str(m) for m in messages]
        )


async def run_audit(
    yandex_token: str,
    yandex_login: str,
    account_name: str,
    anthropic_api_key: str = None
) -> AuditResult:
    """
    Convenience function to run an audit.

    Args:
        yandex_token: Yandex OAuth token
        yandex_login: Yandex Direct login
        account_name: Account display name
        anthropic_api_key: Optional Anthropic API key

    Returns:
        AuditResult with findings
    """
    agent = YandexDirectAuditAgent(
        yandex_token=yandex_token,
        yandex_login=yandex_login,
        account_name=account_name,
        anthropic_api_key=anthropic_api_key
    )
    return await agent.run_audit()


# CLI for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Yandex Direct Audit Agent")
    parser.add_argument("--token", required=True, help="Yandex OAuth token")
    parser.add_argument("--login", required=True, help="Yandex Direct login")
    parser.add_argument("--name", default="Test Account", help="Account name")

    args = parser.parse_args()

    result = asyncio.run(run_audit(
        yandex_token=args.token,
        yandex_login=args.login,
        account_name=args.name
    ))

    print("\n" + "=" * 50)
    print(f"VERDICT: {result.verdict}")
    print(f"Score: {result.score}/100")
    print(f"Issues: {result.issues_count} (Critical: {result.critical_count})")
    print(f"Potential savings: {result.potential_savings} руб/мес")
    print("=" * 50)
