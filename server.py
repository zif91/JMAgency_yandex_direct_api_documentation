#!/usr/bin/env python3
"""
Yandex Direct MCP Client
MCP server that connects to remote Yandex Direct API
"""

import asyncio
import json
import os
import sys
from typing import Any, Optional

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server


# Remote API Configuration
DIRECT_API_URL = os.getenv("DIRECT_API_URL", "https://direct.jmagency.ru")
DIRECT_API_KEY = os.getenv("DIRECT_API_KEY", "")


class DirectAPIClient:
    """Client for remote Yandex Direct API"""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key

    async def make_request(self, endpoint: str, method: str = "GET", data: Optional[dict] = None) -> dict:
        """Make a request to remote API"""
        url = f"{self.api_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=300.0) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            else:
                response = await client.post(url, json=data, headers=headers)

            response.raise_for_status()

            # Handle text responses (like TSV reports)
            content_type = response.headers.get('content-type', '')
            if 'text/tab-separated-values' in content_type:
                return {"report": response.text, "type": "tsv"}

            return response.json()


# Create MCP server
app = Server("yandex-direct-api")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for Yandex Direct API"""
    return [
        Tool(
            name="get_campaigns",
            description="Получить список рекламных кампаний из Яндекс.Директ",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_adgroups",
            description="Получить группы объявлений для указанных кампаний",
            inputSchema={
                "type": "object",
                "required": ["campaign_ids"],
                "properties": {
                    "campaign_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Список ID кампаний"
                    }
                }
            }
        ),
        Tool(
            name="get_ads",
            description="Получить объявления для указанных групп объявлений",
            inputSchema={
                "type": "object",
                "required": ["adgroup_ids"],
                "properties": {
                    "adgroup_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Список ID групп объявлений"
                    }
                }
            }
        ),
        Tool(
            name="get_keywords",
            description="Получить ключевые фразы для указанных групп объявлений",
            inputSchema={
                "type": "object",
                "required": ["adgroup_ids"],
                "properties": {
                    "adgroup_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Список ID групп объявлений"
                    }
                }
            }
        ),
        Tool(
            name="get_report",
            description="Сформировать и получить статистический отчет из Яндекс.Директ. Поддерживает различные типы отчетов: по кампаниям, группам объявлений, объявлениям, ключевым фразам и поисковым запросам.",
            inputSchema={
                "type": "object",
                "required": ["ReportName", "ReportType", "DateRangeType", "FieldNames"],
                "properties": {
                    "ReportName": {
                        "type": "string",
                        "description": "Название отчета (должно быть уникальным для офлайн-отчетов)"
                    },
                    "ReportType": {
                        "type": "string",
                        "enum": [
                            "ACCOUNT_PERFORMANCE_REPORT",
                            "CAMPAIGN_PERFORMANCE_REPORT",
                            "ADGROUP_PERFORMANCE_REPORT",
                            "AD_PERFORMANCE_REPORT",
                            "CRITERIA_PERFORMANCE_REPORT",
                            "CUSTOM_REPORT",
                            "SEARCH_QUERY_PERFORMANCE_REPORT"
                        ],
                        "description": "Тип отчета"
                    },
                    "DateRangeType": {
                        "type": "string",
                        "enum": [
                            "TODAY", "YESTERDAY", "LAST_7_DAYS", "LAST_30_DAYS",
                            "LAST_90_DAYS", "THIS_MONTH", "LAST_MONTH", "ALL_TIME",
                            "CUSTOM_DATE", "AUTO"
                        ],
                        "description": "Период для отчета"
                    },
                    "FieldNames": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Список полей (столбцов) для включения в отчет. Примеры: Date, CampaignName, Impressions, Clicks, Cost, Ctr"
                    },
                    "SelectionCriteria": {
                        "type": "object",
                        "description": "Критерии отбора данных с фильтрами (опционально)",
                        "properties": {
                            "DateFrom": {
                                "type": "string",
                                "description": "Дата начала для CUSTOM_DATE (YYYY-MM-DD)"
                            },
                            "DateTo": {
                                "type": "string",
                                "description": "Дата окончания для CUSTOM_DATE (YYYY-MM-DD)"
                            },
                            "Filter": {
                                "type": "array",
                                "description": "Массив фильтров",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "Field": {"type": "string"},
                                        "Operator": {
                                            "type": "string",
                                            "enum": ["EQUALS", "IN", "GREATER_THAN", "LESS_THAN", "NOT_IN"]
                                        },
                                        "Values": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "Format": {
                        "type": "string",
                        "enum": ["TSV"],
                        "default": "TSV",
                        "description": "Формат отчета (по умолчанию TSV)"
                    },
                    "IncludeVAT": {
                        "type": "string",
                        "enum": ["YES", "NO"],
                        "default": "NO",
                        "description": "Включать ли НДС в денежные значения"
                    }
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    if not DIRECT_API_KEY:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "DIRECT_API_KEY не установлен. Пожалуйста, укажите API ключ в переменной окружения DIRECT_API_KEY."
            }, indent=2, ensure_ascii=False)
        )]

    client = DirectAPIClient(DIRECT_API_URL, DIRECT_API_KEY)

    try:
        if name == "get_campaigns":
            result = await client.make_request("/api/campaigns", "GET")

        elif name == "get_adgroups":
            result = await client.make_request(
                "/api/adgroups",
                "POST",
                {"campaign_ids": arguments["campaign_ids"]}
            )

        elif name == "get_ads":
            result = await client.make_request(
                "/api/ads",
                "POST",
                {"adgroup_ids": arguments["adgroup_ids"]}
            )

        elif name == "get_keywords":
            result = await client.make_request(
                "/api/keywords",
                "POST",
                {"adgroup_ids": arguments["adgroup_ids"]}
            )

        elif name == "get_report":
            # Prepare report definition
            report_def = {
                "ReportName": arguments["ReportName"],
                "ReportType": arguments["ReportType"],
                "DateRangeType": arguments["DateRangeType"],
                "Format": arguments.get("Format", "TSV"),
                "IncludeVAT": arguments.get("IncludeVAT", "NO"),
                "FieldNames": arguments["FieldNames"]
            }

            # Add optional SelectionCriteria
            if "SelectionCriteria" in arguments:
                report_def["SelectionCriteria"] = arguments["SelectionCriteria"]

            result = await client.make_request("/api/reports", "POST", report_def)

            # Handle TSV report format
            if result.get("type") == "tsv":
                return [TextContent(
                    type="text",
                    text=f"Отчет успешно сформирован:\n\n{result['report']}"
                )]

        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Неизвестный инструмент: {name}"}, indent=2, ensure_ascii=False)
            )]

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]

    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        try:
            error_json = e.response.json()
            error_detail = json.dumps(error_json, indent=2, ensure_ascii=False)
        except:
            pass

        return [TextContent(
            type="text",
            text=json.dumps({
                "error": f"HTTP ошибка {e.response.status_code}",
                "detail": error_detail,
                "tool": name,
                "arguments": arguments
            }, indent=2, ensure_ascii=False)
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "tool": name,
                "arguments": arguments
            }, indent=2, ensure_ascii=False)
        )]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
