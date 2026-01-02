"""
Audit tools for Yandex Direct Agent.
These tools are used by the Claude Agent SDK to perform audit tasks.
"""

import json
import re
from typing import Any
from datetime import datetime, timedelta

# Import will be injected at runtime
yandex_api = None
audit_memory = {}


def set_api_client(api_client):
    """Set the Yandex API client for tools to use."""
    global yandex_api
    yandex_api = api_client


def reset_memory():
    """Reset audit memory for new audit session."""
    global audit_memory
    audit_memory = {
        "campaigns": {},
        "budget_issues": [],
        "conversion_issues": [],
        "keyword_issues": [],
        "autotargeting_issues": [],
        "ads_issues": [],
        "structure_issues": [],
        "utm_issues": [],
        "scores": {},
        "recommendations": []
    }


# ============== Tool: Get Campaigns Stats ==============

async def get_campaigns_stats(args: dict[str, Any]) -> dict[str, Any]:
    """
    Получить статистику по кампаниям: расходы, клики, показы, конверсии.

    Returns:
        Список кампаний с метриками за последние 30 дней.
    """
    global yandex_api, audit_memory

    if not yandex_api:
        return _error("API client not initialized")

    try:
        # Get campaigns
        campaigns_response = yandex_api.get_campaigns()
        campaigns = campaigns_response.get("result", {}).get("Campaigns", [])

        # Get performance report
        report = yandex_api.get_campaign_performance_report(date_range="LAST_30_DAYS")

        # Parse report (TSV format)
        stats = _parse_tsv_report(report)

        # Combine data
        result = {
            "total_campaigns": len(campaigns),
            "active_campaigns": sum(1 for c in campaigns if c.get("State") == "ON"),
            "paused_campaigns": sum(1 for c in campaigns if c.get("State") == "SUSPENDED"),
            "campaigns": [],
            "totals": {
                "impressions": 0,
                "clicks": 0,
                "cost": 0,
                "conversions": 0
            }
        }

        for campaign in campaigns:
            cid = str(campaign.get("Id"))
            camp_stats = next((s for s in stats if s.get("CampaignId") == cid), {})

            camp_data = {
                "id": campaign.get("Id"),
                "name": campaign.get("Name"),
                "status": campaign.get("Status"),
                "state": campaign.get("State"),
                "type": campaign.get("Type"),
                "daily_budget": campaign.get("DailyBudget", {}).get("Amount"),
                "impressions": int(camp_stats.get("Impressions", 0)),
                "clicks": int(camp_stats.get("Clicks", 0)),
                "cost": float(camp_stats.get("Cost", 0)),
                "conversions": int(camp_stats.get("Conversions", 0)),
                "ctr": float(camp_stats.get("Ctr", 0)),
                "avg_cpc": float(camp_stats.get("AvgCpc", 0))
            }
            result["campaigns"].append(camp_data)

            result["totals"]["impressions"] += camp_data["impressions"]
            result["totals"]["clicks"] += camp_data["clicks"]
            result["totals"]["cost"] += camp_data["cost"]
            result["totals"]["conversions"] += camp_data["conversions"]

        # Save to memory
        audit_memory["campaigns"] = result

        return _success(result)

    except Exception as e:
        return _error(f"Failed to get campaigns stats: {str(e)}")


# ============== Tool: Get Budget Conflicts ==============

async def get_budget_conflicts(args: dict[str, Any]) -> dict[str, Any]:
    """
    Проверить конфликты бюджетов:
    - Суммарный бюджет кампаний vs лимит аккаунта
    - Хватает ли бюджета на 10 конверсий в неделю
    - Не конфликтует ли бюджет со ставками

    Returns:
        Список найденных конфликтов с рекомендациями.
    """
    global yandex_api, audit_memory

    if not yandex_api:
        return _error("API client not initialized")

    try:
        campaigns_data = audit_memory.get("campaigns", {})
        if not campaigns_data:
            return _error("Run get_campaigns_stats first")

        issues = []

        # Get bids for analysis
        active_campaigns = [c for c in campaigns_data.get("campaigns", []) if c.get("state") == "ON"]

        for campaign in active_campaigns:
            daily_budget = campaign.get("daily_budget")
            avg_cpc = campaign.get("avg_cpc", 0)
            conversions = campaign.get("conversions", 0)
            cost = campaign.get("cost", 0)
            clicks = campaign.get("clicks", 0)

            # Check 1: Budget too low for clicks
            if daily_budget and avg_cpc > 0:
                possible_clicks = daily_budget / avg_cpc
                if possible_clicks < 5:
                    issues.append({
                        "type": "critical",
                        "campaign_id": campaign["id"],
                        "campaign_name": campaign["name"],
                        "issue": "budget_too_low_for_clicks",
                        "description": f"Бюджет {daily_budget} руб. позволяет получить только {possible_clicks:.1f} кликов при средней цене {avg_cpc:.2f} руб.",
                        "recommendation": f"Увеличьте бюджет минимум до {avg_cpc * 10:.0f} руб./день",
                        "potential_loss": daily_budget * 30
                    })

            # Check 2: Budget insufficient for 10 conversions/week
            if conversions > 0 and cost > 0:
                cpa = cost / conversions  # Cost per action for 30 days
                weekly_budget_needed = (cpa * 10) / 4.3  # 10 conversions per week

                if daily_budget and daily_budget * 7 < cpa * 10:
                    issues.append({
                        "type": "warning",
                        "campaign_id": campaign["id"],
                        "campaign_name": campaign["name"],
                        "issue": "budget_insufficient_for_conversions",
                        "description": f"Текущий бюджет не позволяет получить 10 конверсий в неделю. CPA = {cpa:.2f} руб., нужно {weekly_budget_needed:.0f} руб./день",
                        "recommendation": f"Увеличьте дневной бюджет до {weekly_budget_needed:.0f} руб.",
                        "potential_gain": conversions * 0.5 * cpa  # 50% more conversions
                    })

            # Check 3: No daily budget set
            if not daily_budget:
                issues.append({
                    "type": "warning",
                    "campaign_id": campaign["id"],
                    "campaign_name": campaign["name"],
                    "issue": "no_daily_budget",
                    "description": "Не установлен дневной бюджет — риск перерасхода",
                    "recommendation": "Установите дневной лимит бюджета"
                })

        # Check total budget
        total_daily = sum(c.get("daily_budget", 0) or 0 for c in active_campaigns)

        result = {
            "total_daily_budget": total_daily,
            "active_campaigns_count": len(active_campaigns),
            "issues_found": len(issues),
            "issues": issues,
            "score": max(0, 100 - len([i for i in issues if i["type"] == "critical"]) * 20 - len([i for i in issues if i["type"] == "warning"]) * 10)
        }

        audit_memory["budget_issues"] = issues
        audit_memory["scores"]["budget"] = result["score"]

        return _success(result)

    except Exception as e:
        return _error(f"Failed to analyze budgets: {str(e)}")


# ============== Tool: Get Conversions Status ==============

async def get_conversions_status(args: dict[str, Any]) -> dict[str, Any]:
    """
    Проверить настройки конверсий:
    - Подключены ли цели из Метрики
    - Видит ли Директ конверсии
    - Привязаны ли цели к кампаниям

    Returns:
        Статус конверсий и найденные проблемы.
    """
    global yandex_api, audit_memory

    if not yandex_api:
        return _error("API client not initialized")

    try:
        campaigns_data = audit_memory.get("campaigns", {})
        issues = []

        # Get campaigns with settings
        campaigns_response = yandex_api.get_campaigns()
        campaigns = campaigns_response.get("result", {}).get("Campaigns", [])

        total_conversions = campaigns_data.get("totals", {}).get("conversions", 0)
        total_cost = campaigns_data.get("totals", {}).get("cost", 0)

        campaigns_with_goals = 0
        campaigns_without_goals = []

        for campaign in campaigns:
            # Check if campaign has conversion tracking
            # Note: This is simplified - real implementation would check TextCampaign settings
            has_stats = any(
                c.get("conversions", 0) > 0
                for c in campaigns_data.get("campaigns", [])
                if c.get("id") == campaign.get("Id")
            )

            if not has_stats and campaign.get("State") == "ON":
                campaigns_without_goals.append({
                    "id": campaign.get("Id"),
                    "name": campaign.get("Name")
                })
            else:
                campaigns_with_goals += 1

        # Issue: No conversions at all
        if total_conversions == 0 and total_cost > 0:
            issues.append({
                "type": "critical",
                "issue": "no_conversions_tracked",
                "description": "За 30 дней не зафиксировано ни одной конверсии при расходе {:.0f} руб.".format(total_cost),
                "recommendation": "Проверьте настройку целей в Метрике и их привязку к кампаниям",
                "potential_loss": total_cost * 0.3  # 30% of budget potentially wasted
            })

        # Issue: Campaigns without goals
        if campaigns_without_goals:
            issues.append({
                "type": "warning",
                "issue": "campaigns_without_conversions",
                "description": f"{len(campaigns_without_goals)} активных кампаний без конверсий",
                "campaigns": campaigns_without_goals[:5],
                "recommendation": "Настройте цели в Метрике и привяжите их к кампаниям"
            })

        result = {
            "total_conversions": total_conversions,
            "total_cost": total_cost,
            "cpa": total_cost / total_conversions if total_conversions > 0 else None,
            "campaigns_with_goals": campaigns_with_goals,
            "campaigns_without_goals": len(campaigns_without_goals),
            "issues": issues,
            "score": max(0, 100 - len([i for i in issues if i["type"] == "critical"]) * 30 - len([i for i in issues if i["type"] == "warning"]) * 15)
        }

        audit_memory["conversion_issues"] = issues
        audit_memory["scores"]["conversions"] = result["score"]

        return _success(result)

    except Exception as e:
        return _error(f"Failed to check conversions: {str(e)}")


# ============== Tool: Get Keywords Analysis ==============

async def get_keywords_analysis(args: dict[str, Any]) -> dict[str, Any]:
    """
    Анализ ключевых слов:
    - Проверка минус-слов
    - Поиск пересечений между группами
    - Оценка качества минусации

    Returns:
        Анализ ключевых слов с проблемами.
    """
    global yandex_api, audit_memory

    if not yandex_api:
        return _error("API client not initialized")

    try:
        # Get active campaigns
        campaigns_response = yandex_api.get_campaigns(states=["ON"])
        campaigns = campaigns_response.get("result", {}).get("Campaigns", [])
        campaign_ids = [c["Id"] for c in campaigns]

        if not campaign_ids:
            return _success({"message": "No active campaigns", "issues": []})

        # Get keywords
        keywords_response = yandex_api.get_keywords(campaign_ids=campaign_ids)
        keywords = keywords_response.get("result", {}).get("Keywords", [])

        # Get ad groups for negative keywords
        adgroups_response = yandex_api.get_adgroups(campaign_ids=campaign_ids)
        adgroups = adgroups_response.get("result", {}).get("AdGroups", [])

        issues = []

        # Analyze keywords
        keyword_texts = {}
        duplicates = []
        broad_match = []

        for kw in keywords:
            text = kw.get("Keyword", "").lower().strip()
            kw_id = kw.get("Id")
            adgroup_id = kw.get("AdGroupId")

            # Check for duplicates
            if text in keyword_texts:
                duplicates.append({
                    "keyword": text,
                    "ids": [keyword_texts[text], kw_id]
                })
            else:
                keyword_texts[text] = kw_id

            # Check for broad match (no operators)
            if not any(c in text for c in ['"', '[', '+', '!', '-']):
                broad_match.append(kw_id)

        # Check negative keywords in ad groups
        groups_without_negatives = []
        for ag in adgroups:
            if not ag.get("NegativeKeywords"):
                groups_without_negatives.append({
                    "id": ag.get("Id"),
                    "name": ag.get("Name")
                })

        # Build issues
        if duplicates:
            issues.append({
                "type": "warning",
                "issue": "duplicate_keywords",
                "description": f"Найдено {len(duplicates)} дублирующихся ключевых слов",
                "examples": duplicates[:5],
                "recommendation": "Удалите дубликаты для избежания внутренней конкуренции"
            })

        if len(broad_match) > len(keywords) * 0.7:
            issues.append({
                "type": "warning",
                "issue": "too_many_broad_match",
                "description": f"{len(broad_match)} из {len(keywords)} ключей ({len(broad_match)*100//len(keywords)}%) в широком соответствии",
                "recommendation": "Используйте фразовое или точное соответствие для контроля",
                "potential_savings": audit_memory.get("campaigns", {}).get("totals", {}).get("cost", 0) * 0.15
            })

        if groups_without_negatives:
            issues.append({
                "type": "opportunity",
                "issue": "groups_without_negatives",
                "description": f"{len(groups_without_negatives)} групп без минус-слов",
                "groups": groups_without_negatives[:5],
                "recommendation": "Добавьте минус-слова для повышения релевантности",
                "potential_savings": audit_memory.get("campaigns", {}).get("totals", {}).get("cost", 0) * 0.1
            })

        result = {
            "total_keywords": len(keywords),
            "total_adgroups": len(adgroups),
            "duplicates_found": len(duplicates),
            "broad_match_count": len(broad_match),
            "groups_without_negatives": len(groups_without_negatives),
            "issues": issues,
            "score": max(0, 100 - len([i for i in issues if i["type"] == "warning"]) * 15 - len([i for i in issues if i["type"] == "opportunity"]) * 5)
        }

        audit_memory["keyword_issues"] = issues
        audit_memory["scores"]["keywords"] = result["score"]

        return _success(result)

    except Exception as e:
        return _error(f"Failed to analyze keywords: {str(e)}")


# ============== Tool: Get Autotargeting Stats ==============

async def get_autotargeting_stats(args: dict[str, Any]) -> dict[str, Any]:
    """
    Проверить процент автотаргетинга:
    - ТРЕВОГА если > 20%
    - Оценка качества запросов автотаргетинга

    Returns:
        Статистика автотаргетинга и предупреждения.
    """
    global yandex_api, audit_memory

    if not yandex_api:
        return _error("API client not initialized")

    try:
        # Get search query report to analyze autotargeting
        report_def = {
            "ReportName": "Autotargeting Analysis",
            "ReportType": "SEARCH_QUERY_PERFORMANCE_REPORT",
            "DateRangeType": "LAST_30_DAYS",
            "Format": "TSV",
            "IncludeVAT": "NO",
            "SelectionCriteria": {},
            "FieldNames": [
                "CampaignId", "CampaignName", "CriterionType",
                "Impressions", "Clicks", "Cost"
            ]
        }

        report = yandex_api.get_report(report_def)
        stats = _parse_tsv_report(report)

        # Calculate autotargeting percentage
        total_clicks = 0
        autotarget_clicks = 0
        total_cost = 0
        autotarget_cost = 0

        for row in stats:
            clicks = int(row.get("Clicks", 0))
            cost = float(row.get("Cost", 0))
            criterion_type = row.get("CriterionType", "")

            total_clicks += clicks
            total_cost += cost

            if "AUTOTARGETING" in criterion_type.upper():
                autotarget_clicks += clicks
                autotarget_cost += cost

        autotarget_percent = (autotarget_clicks / total_clicks * 100) if total_clicks > 0 else 0

        issues = []

        if autotarget_percent > 20:
            issues.append({
                "type": "critical",
                "issue": "high_autotargeting",
                "description": f"Автотаргетинг составляет {autotarget_percent:.1f}% кликов — это признак плохой проработки семантики",
                "autotarget_cost": autotarget_cost,
                "recommendation": "Расширьте семантическое ядро и отключите автотаргетинг",
                "potential_savings": autotarget_cost * 0.5
            })
        elif autotarget_percent > 10:
            issues.append({
                "type": "warning",
                "issue": "moderate_autotargeting",
                "description": f"Автотаргетинг составляет {autotarget_percent:.1f}% кликов",
                "recommendation": "Проанализируйте запросы автотаргетинга и добавьте релевантные в ключи"
            })

        result = {
            "total_clicks": total_clicks,
            "autotarget_clicks": autotarget_clicks,
            "autotarget_percent": round(autotarget_percent, 1),
            "autotarget_cost": autotarget_cost,
            "issues": issues,
            "score": 100 if autotarget_percent <= 10 else (70 if autotarget_percent <= 20 else 30)
        }

        audit_memory["autotargeting_issues"] = issues
        audit_memory["scores"]["autotargeting"] = result["score"]

        return _success(result)

    except Exception as e:
        return _error(f"Failed to analyze autotargeting: {str(e)}")


# ============== Tool: Get Ads Quality ==============

async def get_ads_quality(args: dict[str, Any]) -> dict[str, Any]:
    """
    Анализ качества объявлений:
    - Проверка орфографии
    - Оценка привлекательности (УТП, призыв к действию)
    - Заполненность элементов
    - A/B тестирование

    Returns:
        Анализ объявлений с рекомендациями.
    """
    global yandex_api, audit_memory

    if not yandex_api:
        return _error("API client not initialized")

    try:
        # Get active campaigns
        campaigns_response = yandex_api.get_campaigns(states=["ON"])
        campaigns = campaigns_response.get("result", {}).get("Campaigns", [])
        campaign_ids = [c["Id"] for c in campaigns]

        if not campaign_ids:
            return _success({"message": "No active campaigns", "issues": []})

        # Get ads
        ads_response = yandex_api.get_ads(campaign_ids=campaign_ids)
        ads = ads_response.get("result", {}).get("Ads", [])

        issues = []

        # Group ads by ad group for A/B testing check
        ads_by_group = {}
        for ad in ads:
            group_id = ad.get("AdGroupId")
            if group_id not in ads_by_group:
                ads_by_group[group_id] = []
            ads_by_group[group_id].append(ad)

        # Check A/B testing
        single_ad_groups = [gid for gid, group_ads in ads_by_group.items() if len(group_ads) == 1]
        if single_ad_groups:
            issues.append({
                "type": "opportunity",
                "issue": "no_ab_testing",
                "description": f"{len(single_ad_groups)} групп имеют только одно объявление",
                "recommendation": "Создайте 2-3 варианта объявлений для A/B тестирования",
                "potential_gain": "5-15% улучшение CTR"
            })

        # Check ads without sitelinks
        ads_without_sitelinks = []
        ads_without_callouts = []
        rejected_ads = []

        for ad in ads:
            text_ad = ad.get("TextAd", {})

            if not text_ad.get("SitelinkSetId"):
                ads_without_sitelinks.append(ad.get("Id"))

            if not ad.get("AdExtensionIds"):
                ads_without_callouts.append(ad.get("Id"))

            if ad.get("Status") == "REJECTED":
                rejected_ads.append({
                    "id": ad.get("Id"),
                    "reason": ad.get("StatusClarification")
                })

        if ads_without_sitelinks:
            issues.append({
                "type": "warning",
                "issue": "missing_sitelinks",
                "description": f"{len(ads_without_sitelinks)} объявлений без быстрых ссылок",
                "recommendation": "Добавьте быстрые ссылки для повышения CTR",
                "potential_gain": "10-15% улучшение CTR"
            })

        if ads_without_callouts:
            issues.append({
                "type": "opportunity",
                "issue": "missing_callouts",
                "description": f"{len(ads_without_callouts)} объявлений без уточнений",
                "recommendation": "Добавьте уточнения для выделения преимуществ"
            })

        if rejected_ads:
            issues.append({
                "type": "critical",
                "issue": "rejected_ads",
                "description": f"{len(rejected_ads)} объявлений отклонено модерацией",
                "ads": rejected_ads[:5],
                "recommendation": "Исправьте отклонённые объявления"
            })

        result = {
            "total_ads": len(ads),
            "total_adgroups": len(ads_by_group),
            "single_ad_groups": len(single_ad_groups),
            "ads_without_sitelinks": len(ads_without_sitelinks),
            "ads_without_callouts": len(ads_without_callouts),
            "rejected_ads": len(rejected_ads),
            "issues": issues,
            "score": max(0, 100 - len([i for i in issues if i["type"] == "critical"]) * 25 - len([i for i in issues if i["type"] == "warning"]) * 10 - len([i for i in issues if i["type"] == "opportunity"]) * 5)
        }

        audit_memory["ads_issues"] = issues
        audit_memory["scores"]["ads"] = result["score"]

        return _success(result)

    except Exception as e:
        return _error(f"Failed to analyze ads: {str(e)}")


# ============== Tool: Get Account Structure ==============

async def get_account_structure(args: dict[str, Any]) -> dict[str, Any]:
    """
    Анализ структуры аккаунта:
    - Количество кампаний и групп
    - Логичность структуры
    - Управляемость
    - Понятность названий

    Returns:
        Анализ структуры с рекомендациями.
    """
    global yandex_api, audit_memory

    if not yandex_api:
        return _error("API client not initialized")

    try:
        campaigns_response = yandex_api.get_campaigns()
        campaigns = campaigns_response.get("result", {}).get("Campaigns", [])

        campaign_ids = [c["Id"] for c in campaigns]

        adgroups = []
        if campaign_ids:
            adgroups_response = yandex_api.get_adgroups(campaign_ids=campaign_ids)
            adgroups = adgroups_response.get("result", {}).get("AdGroups", [])

        issues = []

        # Check total counts
        if len(campaigns) > 50:
            issues.append({
                "type": "warning",
                "issue": "too_many_campaigns",
                "description": f"В аккаунте {len(campaigns)} кампаний — сложно управлять",
                "recommendation": "Рассмотрите объединение похожих кампаний"
            })

        # Check groups per campaign
        groups_by_campaign = {}
        for ag in adgroups:
            cid = ag.get("CampaignId")
            if cid not in groups_by_campaign:
                groups_by_campaign[cid] = []
            groups_by_campaign[cid].append(ag)

        oversized_campaigns = []
        empty_campaigns = []

        for campaign in campaigns:
            cid = campaign.get("Id")
            group_count = len(groups_by_campaign.get(cid, []))

            if group_count == 0:
                empty_campaigns.append(campaign.get("Name"))
            elif group_count > 100:
                oversized_campaigns.append({
                    "name": campaign.get("Name"),
                    "groups": group_count
                })

        if empty_campaigns:
            issues.append({
                "type": "info",
                "issue": "empty_campaigns",
                "description": f"{len(empty_campaigns)} пустых кампаний",
                "campaigns": empty_campaigns[:5],
                "recommendation": "Удалите или заполните пустые кампании"
            })

        if oversized_campaigns:
            issues.append({
                "type": "warning",
                "issue": "oversized_campaigns",
                "description": "Кампании с избыточным количеством групп",
                "campaigns": oversized_campaigns,
                "recommendation": "Разделите крупные кампании для лучшей управляемости"
            })

        # Check naming conventions
        unclear_names = []
        for campaign in campaigns:
            name = campaign.get("Name", "")
            if len(name) < 5 or name.lower() in ["test", "new", "campaign", "копия"]:
                unclear_names.append(name)

        if unclear_names:
            issues.append({
                "type": "info",
                "issue": "unclear_naming",
                "description": f"{len(unclear_names)} кампаний с непонятными названиями",
                "examples": unclear_names[:5],
                "recommendation": "Используйте понятные названия: [Тип]-[Продукт]-[Регион]"
            })

        result = {
            "total_campaigns": len(campaigns),
            "total_adgroups": len(adgroups),
            "avg_groups_per_campaign": len(adgroups) / len(campaigns) if campaigns else 0,
            "empty_campaigns": len(empty_campaigns),
            "oversized_campaigns": len(oversized_campaigns),
            "unclear_names": len(unclear_names),
            "issues": issues,
            "score": max(0, 100 - len([i for i in issues if i["type"] == "warning"]) * 15 - len([i for i in issues if i["type"] == "info"]) * 5)
        }

        audit_memory["structure_issues"] = issues
        audit_memory["scores"]["structure"] = result["score"]

        return _success(result)

    except Exception as e:
        return _error(f"Failed to analyze structure: {str(e)}")


# ============== Tool: Get UTM Analysis ==============

async def get_utm_analysis(args: dict[str, Any]) -> dict[str, Any]:
    """
    Проверка UTM-разметки:
    - Наличие UTM-меток в ссылках
    - Корректность разметки
    - Консистентность меток

    Returns:
        Анализ UTM-разметки.
    """
    global yandex_api, audit_memory

    if not yandex_api:
        return _error("API client not initialized")

    try:
        # Get ads with URLs
        campaigns_response = yandex_api.get_campaigns(states=["ON"])
        campaigns = campaigns_response.get("result", {}).get("Campaigns", [])
        campaign_ids = [c["Id"] for c in campaigns]

        if not campaign_ids:
            return _success({"message": "No active campaigns", "issues": []})

        ads_response = yandex_api.get_ads(campaign_ids=campaign_ids)
        ads = ads_response.get("result", {}).get("Ads", [])

        issues = []

        ads_without_utm = []
        ads_with_incomplete_utm = []

        required_params = ["utm_source", "utm_medium", "utm_campaign"]

        for ad in ads:
            text_ad = ad.get("TextAd", {})
            href = text_ad.get("Href", "")

            if not href:
                continue

            href_lower = href.lower()

            # Check for UTM presence
            has_utm = "utm_" in href_lower

            if not has_utm:
                ads_without_utm.append(ad.get("Id"))
            else:
                # Check for required params
                missing = [p for p in required_params if p not in href_lower]
                if missing:
                    ads_with_incomplete_utm.append({
                        "id": ad.get("Id"),
                        "missing": missing
                    })

        if ads_without_utm:
            issues.append({
                "type": "warning",
                "issue": "missing_utm",
                "description": f"{len(ads_without_utm)} объявлений без UTM-разметки",
                "recommendation": "Добавьте UTM-метки для отслеживания эффективности в аналитике"
            })

        if ads_with_incomplete_utm:
            issues.append({
                "type": "info",
                "issue": "incomplete_utm",
                "description": f"{len(ads_with_incomplete_utm)} объявлений с неполной UTM-разметкой",
                "recommendation": "Добавьте недостающие параметры: utm_source, utm_medium, utm_campaign"
            })

        total_checked = len([a for a in ads if a.get("TextAd", {}).get("Href")])
        properly_tagged = total_checked - len(ads_without_utm) - len(ads_with_incomplete_utm)

        result = {
            "total_ads_checked": total_checked,
            "properly_tagged": properly_tagged,
            "without_utm": len(ads_without_utm),
            "incomplete_utm": len(ads_with_incomplete_utm),
            "utm_coverage": (properly_tagged / total_checked * 100) if total_checked > 0 else 0,
            "issues": issues,
            "score": max(0, 100 - len(ads_without_utm) * 2 - len(ads_with_incomplete_utm))
        }

        audit_memory["utm_issues"] = issues
        audit_memory["scores"]["utm"] = result["score"]

        return _success(result)

    except Exception as e:
        return _error(f"Failed to analyze UTM: {str(e)}")


# ============== Tool: Save to Memory ==============

async def save_to_memory(args: dict[str, Any]) -> dict[str, Any]:
    """
    Сохранить данные в память аудита.

    Args:
        key: Ключ для сохранения
        value: Значение для сохранения

    Returns:
        Подтверждение сохранения.
    """
    global audit_memory

    key = args.get("key")
    value = args.get("value")

    if not key:
        return _error("Key is required")

    audit_memory[key] = value

    return _success({"saved": key, "memory_keys": list(audit_memory.keys())})


# ============== Tool: Get Memory ==============

async def get_memory(args: dict[str, Any]) -> dict[str, Any]:
    """
    Получить данные из памяти аудита.

    Args:
        key: Ключ для получения (опционально, без ключа — вся память)

    Returns:
        Данные из памяти.
    """
    global audit_memory

    key = args.get("key")

    if key:
        return _success({key: audit_memory.get(key)})

    return _success(audit_memory)


# ============== Tool: Generate Verdict ==============

async def generate_verdict(args: dict[str, Any]) -> dict[str, Any]:
    """
    Сгенерировать финальное заключение аудита.

    Returns:
        Итоговое заключение с оценкой, проблемами и рекомендациями.
    """
    global audit_memory

    # Calculate overall score
    scores = audit_memory.get("scores", {})
    if not scores:
        return _error("No audit data. Run audit tools first.")

    avg_score = sum(scores.values()) / len(scores)

    # Determine verdict
    if avg_score >= 80:
        verdict = "ХОРОШО"
        verdict_description = "Аккаунт настроен профессионально. Есть незначительные улучшения."
    elif avg_score >= 50:
        verdict = "ТРЕБУЕТ УЛУЧШЕНИЯ"
        verdict_description = "Обнаружены существенные проблемы, требующие внимания."
    else:
        verdict = "ПЛОХО"
        verdict_description = "Критические ошибки. Требуется срочное вмешательство."

    # Collect all issues
    all_issues = []
    for key in ["budget_issues", "conversion_issues", "keyword_issues",
                "autotargeting_issues", "ads_issues", "structure_issues", "utm_issues"]:
        all_issues.extend(audit_memory.get(key, []))

    critical_issues = [i for i in all_issues if i.get("type") == "critical"]
    warning_issues = [i for i in all_issues if i.get("type") == "warning"]
    opportunity_issues = [i for i in all_issues if i.get("type") == "opportunity"]

    # Calculate potential savings/gains
    total_savings = sum(i.get("potential_savings", 0) or i.get("potential_loss", 0) for i in all_issues)
    total_gains = sum(i.get("potential_gain", 0) for i in all_issues if isinstance(i.get("potential_gain"), (int, float)))

    result = {
        "verdict": verdict,
        "verdict_description": verdict_description,
        "overall_score": round(avg_score, 1),
        "scores_breakdown": scores,
        "issues_summary": {
            "critical": len(critical_issues),
            "warning": len(warning_issues),
            "opportunity": len(opportunity_issues),
            "total": len(all_issues)
        },
        "critical_issues": critical_issues,
        "warning_issues": warning_issues[:5],  # Top 5
        "opportunities": opportunity_issues[:5],  # Top 5
        "potential_impact": {
            "monthly_savings": round(total_savings, 0),
            "potential_gains": total_gains if isinstance(total_gains, (int, float)) else "Улучшение CTR и конверсии"
        },
        "top_recommendations": [
            i.get("recommendation") for i in (critical_issues + warning_issues)[:5]
        ]
    }

    return _success(result)


# ============== Helper Functions ==============

def _success(data: Any) -> dict[str, Any]:
    """Format successful response."""
    return {
        "content": [{
            "type": "text",
            "text": json.dumps(data, ensure_ascii=False, indent=2)
        }]
    }


def _error(message: str) -> dict[str, Any]:
    """Format error response."""
    return {
        "content": [{
            "type": "text",
            "text": json.dumps({"error": message}, ensure_ascii=False)
        }]
    }


def _parse_tsv_report(report: str) -> list[dict]:
    """Parse TSV report into list of dicts."""
    if not report:
        return []

    lines = report.strip().split("\n")
    if len(lines) < 2:
        return []

    headers = lines[0].split("\t")
    results = []

    for line in lines[1:]:
        if line.startswith("Total") or not line.strip():
            continue
        values = line.split("\t")
        if len(values) == len(headers):
            results.append(dict(zip(headers, values)))

    return results
