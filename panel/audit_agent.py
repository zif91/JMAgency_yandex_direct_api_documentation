"""
AI Audit Agent for Yandex Direct campaigns.
Analyzes campaigns and provides recommendations for optimization.
"""
import json
import os
from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from yandex_api import YandexDirectAPI


class AuditType(Enum):
    FULL = "full"
    CAMPAIGNS = "campaigns"
    ADGROUPS = "adgroups"
    ADS = "ads"
    KEYWORDS = "keywords"
    BIDS = "bids"
    BUDGET = "budget"
    STRUCTURE = "structure"


class IssueSeverity(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    OPPORTUNITY = "opportunity"


@dataclass
class AuditIssue:
    """Represents a single audit issue or recommendation."""
    severity: str
    category: str
    title: str
    description: str
    recommendation: str
    affected_items: list = None
    potential_impact: str = None

    def to_dict(self):
        return asdict(self)


@dataclass
class AuditResult:
    """Complete audit result."""
    audit_type: str
    account_name: str
    yandex_login: str
    summary: dict
    issues: list
    recommendations: list
    metrics: dict
    raw_data: dict = None

    def to_dict(self):
        return {
            "audit_type": self.audit_type,
            "account_name": self.account_name,
            "yandex_login": self.yandex_login,
            "summary": self.summary,
            "issues": [i.to_dict() if isinstance(i, AuditIssue) else i for i in self.issues],
            "recommendations": self.recommendations,
            "metrics": self.metrics
        }

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class AuditAgent:
    """
    AI-powered audit agent for Yandex Direct campaigns.
    Combines rule-based analysis with AI recommendations.
    """

    def __init__(self, api: YandexDirectAPI, account_name: str,
                 anthropic_api_key: str = None):
        """
        Initialize audit agent.

        Args:
            api: Configured YandexDirectAPI client
            account_name: Name of the account being audited
            anthropic_api_key: Optional API key for Claude AI recommendations
        """
        self.api = api
        self.account_name = account_name
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")

        if self.anthropic_api_key and ANTHROPIC_AVAILABLE:
            self.ai_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        else:
            self.ai_client = None

    def run_audit(self, audit_type: str = "full") -> AuditResult:
        """
        Run a complete audit of the account.

        Args:
            audit_type: Type of audit to run (full, campaigns, keywords, etc.)

        Returns:
            AuditResult with findings and recommendations
        """
        issues = []
        metrics = {}
        raw_data = {}

        # Collect data based on audit type
        if audit_type in ["full", "campaigns"]:
            campaigns_data = self._audit_campaigns()
            issues.extend(campaigns_data["issues"])
            metrics.update(campaigns_data["metrics"])
            raw_data["campaigns"] = campaigns_data["raw"]

        if audit_type in ["full", "adgroups"]:
            adgroups_data = self._audit_adgroups()
            issues.extend(adgroups_data["issues"])
            metrics.update(adgroups_data["metrics"])
            raw_data["adgroups"] = adgroups_data["raw"]

        if audit_type in ["full", "ads"]:
            ads_data = self._audit_ads()
            issues.extend(ads_data["issues"])
            metrics.update(ads_data["metrics"])
            raw_data["ads"] = ads_data["raw"]

        if audit_type in ["full", "keywords"]:
            keywords_data = self._audit_keywords()
            issues.extend(keywords_data["issues"])
            metrics.update(keywords_data["metrics"])
            raw_data["keywords"] = keywords_data["raw"]

        if audit_type in ["full", "structure"]:
            structure_data = self._audit_structure()
            issues.extend(structure_data["issues"])
            metrics.update(structure_data["metrics"])

        # Generate summary
        summary = self._generate_summary(issues, metrics)

        # Get AI recommendations if available
        recommendations = self._generate_ai_recommendations(issues, metrics, raw_data)

        return AuditResult(
            audit_type=audit_type,
            account_name=self.account_name,
            yandex_login=self.api.login,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics=metrics,
            raw_data=raw_data
        )

    def _audit_campaigns(self) -> dict:
        """Audit campaigns for issues."""
        issues = []
        metrics = {}

        try:
            campaigns_response = self.api.get_campaigns()
            campaigns = campaigns_response.get("result", {}).get("Campaigns", [])
        except Exception as e:
            return {
                "issues": [AuditIssue(
                    severity=IssueSeverity.CRITICAL.value,
                    category="api_error",
                    title="Failed to fetch campaigns",
                    description=str(e),
                    recommendation="Check API credentials and permissions"
                )],
                "metrics": {},
                "raw": []
            }

        metrics["total_campaigns"] = len(campaigns)
        metrics["active_campaigns"] = sum(1 for c in campaigns if c.get("State") == "ON")
        metrics["paused_campaigns"] = sum(1 for c in campaigns if c.get("State") == "SUSPENDED")
        metrics["ended_campaigns"] = sum(1 for c in campaigns if c.get("State") == "ENDED")

        # Check for issues
        for campaign in campaigns:
            # Check for campaigns without daily budget
            if not campaign.get("DailyBudget"):
                issues.append(AuditIssue(
                    severity=IssueSeverity.WARNING.value,
                    category="budget",
                    title="Campaign without daily budget limit",
                    description=f"Campaign '{campaign.get('Name')}' (ID: {campaign.get('Id')}) has no daily budget set",
                    recommendation="Set a daily budget to control spending",
                    affected_items=[campaign.get("Id")]
                ))

            # Check for rejected campaigns
            if campaign.get("Status") == "REJECTED":
                issues.append(AuditIssue(
                    severity=IssueSeverity.CRITICAL.value,
                    category="moderation",
                    title="Campaign rejected by moderation",
                    description=f"Campaign '{campaign.get('Name')}' was rejected",
                    recommendation="Review rejection reason and make necessary changes",
                    affected_items=[campaign.get("Id")]
                ))

            # Check for draft campaigns
            if campaign.get("Status") == "DRAFT":
                issues.append(AuditIssue(
                    severity=IssueSeverity.INFO.value,
                    category="status",
                    title="Campaign in draft status",
                    description=f"Campaign '{campaign.get('Name')}' is still a draft",
                    recommendation="Complete setup and send for moderation",
                    affected_items=[campaign.get("Id")]
                ))

        # Check if no active campaigns
        if metrics["active_campaigns"] == 0 and metrics["total_campaigns"] > 0:
            issues.append(AuditIssue(
                severity=IssueSeverity.WARNING.value,
                category="status",
                title="No active campaigns",
                description="All campaigns are paused or ended",
                recommendation="Review and activate campaigns if advertising is needed"
            ))

        return {"issues": issues, "metrics": metrics, "raw": campaigns}

    def _audit_adgroups(self) -> dict:
        """Audit ad groups for issues."""
        issues = []
        metrics = {}

        try:
            # Get active campaigns first
            campaigns_response = self.api.get_campaigns(states=["ON"])
            campaigns = campaigns_response.get("result", {}).get("Campaigns", [])
            campaign_ids = [c["Id"] for c in campaigns]

            if not campaign_ids:
                return {"issues": [], "metrics": {"total_adgroups": 0}, "raw": []}

            adgroups_response = self.api.get_adgroups(campaign_ids=campaign_ids)
            adgroups = adgroups_response.get("result", {}).get("AdGroups", [])
        except Exception as e:
            return {
                "issues": [AuditIssue(
                    severity=IssueSeverity.CRITICAL.value,
                    category="api_error",
                    title="Failed to fetch ad groups",
                    description=str(e),
                    recommendation="Check API credentials and permissions"
                )],
                "metrics": {},
                "raw": []
            }

        metrics["total_adgroups"] = len(adgroups)
        metrics["active_adgroups"] = sum(1 for ag in adgroups if ag.get("Status") == "ACCEPTED")

        # Check for ad groups without negative keywords
        groups_without_negatives = []
        for adgroup in adgroups:
            if not adgroup.get("NegativeKeywords"):
                groups_without_negatives.append(adgroup.get("Id"))

        if groups_without_negatives:
            issues.append(AuditIssue(
                severity=IssueSeverity.OPPORTUNITY.value,
                category="keywords",
                title="Ad groups without negative keywords",
                description=f"{len(groups_without_negatives)} ad groups have no negative keywords",
                recommendation="Add negative keywords to improve targeting and reduce wasted spend",
                affected_items=groups_without_negatives[:10],
                potential_impact="10-30% cost reduction"
            ))

        return {"issues": issues, "metrics": metrics, "raw": adgroups}

    def _audit_ads(self) -> dict:
        """Audit ads for issues."""
        issues = []
        metrics = {}

        try:
            # Get active campaigns
            campaigns_response = self.api.get_campaigns(states=["ON"])
            campaigns = campaigns_response.get("result", {}).get("Campaigns", [])
            campaign_ids = [c["Id"] for c in campaigns]

            if not campaign_ids:
                return {"issues": [], "metrics": {"total_ads": 0}, "raw": []}

            ads_response = self.api.get_ads(campaign_ids=campaign_ids)
            ads = ads_response.get("result", {}).get("Ads", [])
        except Exception as e:
            return {
                "issues": [AuditIssue(
                    severity=IssueSeverity.CRITICAL.value,
                    category="api_error",
                    title="Failed to fetch ads",
                    description=str(e),
                    recommendation="Check API credentials and permissions"
                )],
                "metrics": {},
                "raw": []
            }

        metrics["total_ads"] = len(ads)
        metrics["rejected_ads"] = sum(1 for ad in ads if ad.get("Status") == "REJECTED")
        metrics["draft_ads"] = sum(1 for ad in ads if ad.get("Status") == "DRAFT")

        # Group ads by ad group
        ads_by_group = {}
        for ad in ads:
            group_id = ad.get("AdGroupId")
            if group_id not in ads_by_group:
                ads_by_group[group_id] = []
            ads_by_group[group_id].append(ad)

        # Check for ad groups with single ad (no A/B testing)
        single_ad_groups = [gid for gid, group_ads in ads_by_group.items() if len(group_ads) == 1]
        if single_ad_groups:
            issues.append(AuditIssue(
                severity=IssueSeverity.OPPORTUNITY.value,
                category="testing",
                title="Ad groups with single ad",
                description=f"{len(single_ad_groups)} ad groups have only one ad (no A/B testing)",
                recommendation="Create 2-3 ad variations per group to enable testing",
                affected_items=single_ad_groups[:10],
                potential_impact="5-20% CTR improvement"
            ))

        # Check for rejected ads
        rejected_ads = [ad.get("Id") for ad in ads if ad.get("Status") == "REJECTED"]
        if rejected_ads:
            issues.append(AuditIssue(
                severity=IssueSeverity.CRITICAL.value,
                category="moderation",
                title="Rejected ads",
                description=f"{len(rejected_ads)} ads were rejected by moderation",
                recommendation="Review rejection reasons and fix ad content",
                affected_items=rejected_ads[:10]
            ))

        # Check for ads without sitelinks
        ads_without_sitelinks = []
        for ad in ads:
            text_ad = ad.get("TextAd", {})
            if not text_ad.get("SitelinkSetId"):
                ads_without_sitelinks.append(ad.get("Id"))

        if ads_without_sitelinks:
            issues.append(AuditIssue(
                severity=IssueSeverity.OPPORTUNITY.value,
                category="extensions",
                title="Ads without sitelinks",
                description=f"{len(ads_without_sitelinks)} ads don't have sitelinks",
                recommendation="Add sitelinks to improve CTR and ad visibility",
                affected_items=ads_without_sitelinks[:10],
                potential_impact="10-15% CTR improvement"
            ))

        return {"issues": issues, "metrics": metrics, "raw": ads}

    def _audit_keywords(self) -> dict:
        """Audit keywords for issues."""
        issues = []
        metrics = {}

        try:
            # Get active campaigns
            campaigns_response = self.api.get_campaigns(states=["ON"])
            campaigns = campaigns_response.get("result", {}).get("Campaigns", [])
            campaign_ids = [c["Id"] for c in campaigns]

            if not campaign_ids:
                return {"issues": [], "metrics": {"total_keywords": 0}, "raw": []}

            keywords_response = self.api.get_keywords(campaign_ids=campaign_ids)
            keywords = keywords_response.get("result", {}).get("Keywords", [])
        except Exception as e:
            return {
                "issues": [AuditIssue(
                    severity=IssueSeverity.CRITICAL.value,
                    category="api_error",
                    title="Failed to fetch keywords",
                    description=str(e),
                    recommendation="Check API credentials and permissions"
                )],
                "metrics": {},
                "raw": []
            }

        metrics["total_keywords"] = len(keywords)
        metrics["active_keywords"] = sum(1 for kw in keywords if kw.get("State") == "ON")
        metrics["suspended_keywords"] = sum(1 for kw in keywords if kw.get("State") == "SUSPENDED")

        # Check for keywords with low bids
        low_bid_keywords = []
        for kw in keywords:
            bid = kw.get("Bid", 0)
            if bid and bid < 1000000:  # Less than 1 unit (in micros)
                low_bid_keywords.append(kw.get("Id"))

        if low_bid_keywords:
            issues.append(AuditIssue(
                severity=IssueSeverity.WARNING.value,
                category="bids",
                title="Keywords with very low bids",
                description=f"{len(low_bid_keywords)} keywords have bids below 1 unit",
                recommendation="Review and adjust bids for better ad positions",
                affected_items=low_bid_keywords[:10]
            ))

        # Check for duplicate keywords (basic check)
        keyword_texts = {}
        duplicates = []
        for kw in keywords:
            text = kw.get("Keyword", "").lower().strip()
            if text in keyword_texts:
                duplicates.append(kw.get("Id"))
            else:
                keyword_texts[text] = kw.get("Id")

        if duplicates:
            issues.append(AuditIssue(
                severity=IssueSeverity.WARNING.value,
                category="keywords",
                title="Potential duplicate keywords",
                description=f"Found {len(duplicates)} potential duplicate keywords",
                recommendation="Review and remove duplicates to avoid internal competition",
                affected_items=duplicates[:10]
            ))

        # Check for broad match keywords (no operators)
        broad_match_keywords = []
        for kw in keywords:
            text = kw.get("Keyword", "")
            if not any(c in text for c in ['"', '[', '+', '!', '-']):
                broad_match_keywords.append(kw.get("Id"))

        if broad_match_keywords and len(broad_match_keywords) > len(keywords) * 0.7:
            issues.append(AuditIssue(
                severity=IssueSeverity.OPPORTUNITY.value,
                category="keywords",
                title="High percentage of broad match keywords",
                description=f"{len(broad_match_keywords)} keywords ({len(broad_match_keywords) * 100 // len(keywords)}%) use broad match",
                recommendation="Consider using phrase or exact match for better control",
                affected_items=broad_match_keywords[:10],
                potential_impact="15-40% cost reduction"
            ))

        return {"issues": issues, "metrics": metrics, "raw": keywords}

    def _audit_structure(self) -> dict:
        """Audit account structure."""
        issues = []
        metrics = {}

        try:
            # Get campaigns
            campaigns_response = self.api.get_campaigns()
            campaigns = campaigns_response.get("result", {}).get("Campaigns", [])

            # Get ad groups for all campaigns
            campaign_ids = [c["Id"] for c in campaigns]
            if campaign_ids:
                adgroups_response = self.api.get_adgroups(campaign_ids=campaign_ids)
                adgroups = adgroups_response.get("result", {}).get("AdGroups", [])
            else:
                adgroups = []

        except Exception:
            return {"issues": [], "metrics": {}}

        # Group ad groups by campaign
        groups_by_campaign = {}
        for ag in adgroups:
            cid = ag.get("CampaignId")
            if cid not in groups_by_campaign:
                groups_by_campaign[cid] = []
            groups_by_campaign[cid].append(ag)

        # Check for campaigns with too many ad groups
        for campaign in campaigns:
            cid = campaign.get("Id")
            group_count = len(groups_by_campaign.get(cid, []))
            metrics[f"campaign_{cid}_adgroups"] = group_count

            if group_count > 100:
                issues.append(AuditIssue(
                    severity=IssueSeverity.WARNING.value,
                    category="structure",
                    title="Campaign with too many ad groups",
                    description=f"Campaign '{campaign.get('Name')}' has {group_count} ad groups",
                    recommendation="Consider splitting into multiple campaigns for better management",
                    affected_items=[cid]
                ))

        # Check for empty campaigns
        empty_campaigns = [c.get("Id") for c in campaigns if len(groups_by_campaign.get(c.get("Id"), [])) == 0]
        if empty_campaigns:
            issues.append(AuditIssue(
                severity=IssueSeverity.INFO.value,
                category="structure",
                title="Empty campaigns",
                description=f"{len(empty_campaigns)} campaigns have no ad groups",
                recommendation="Add ad groups or remove empty campaigns",
                affected_items=empty_campaigns
            ))

        return {"issues": issues, "metrics": metrics}

    def _generate_summary(self, issues: list, metrics: dict) -> dict:
        """Generate audit summary."""
        severity_counts = {
            IssueSeverity.CRITICAL.value: 0,
            IssueSeverity.WARNING.value: 0,
            IssueSeverity.INFO.value: 0,
            IssueSeverity.OPPORTUNITY.value: 0
        }

        categories = {}
        for issue in issues:
            if isinstance(issue, AuditIssue):
                severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
                categories[issue.category] = categories.get(issue.category, 0) + 1
            elif isinstance(issue, dict):
                severity_counts[issue.get("severity", "info")] = severity_counts.get(issue.get("severity", "info"), 0) + 1
                categories[issue.get("category", "other")] = categories.get(issue.get("category", "other"), 0) + 1

        # Calculate health score (0-100)
        health_score = 100
        health_score -= severity_counts[IssueSeverity.CRITICAL.value] * 15
        health_score -= severity_counts[IssueSeverity.WARNING.value] * 5
        health_score -= severity_counts[IssueSeverity.INFO.value] * 1
        health_score = max(0, min(100, health_score))

        return {
            "total_issues": len(issues),
            "severity_breakdown": severity_counts,
            "categories": categories,
            "health_score": health_score,
            "key_metrics": {
                "campaigns": metrics.get("total_campaigns", 0),
                "active_campaigns": metrics.get("active_campaigns", 0),
                "adgroups": metrics.get("total_adgroups", 0),
                "ads": metrics.get("total_ads", 0),
                "keywords": metrics.get("total_keywords", 0)
            }
        }

    def _generate_ai_recommendations(self, issues: list, metrics: dict,
                                     raw_data: dict) -> list:
        """Generate AI-powered recommendations using Claude."""
        if not self.ai_client:
            return self._generate_rule_based_recommendations(issues, metrics)

        # Prepare context for AI
        context = {
            "metrics": metrics,
            "issues_summary": [
                {
                    "severity": i.severity if isinstance(i, AuditIssue) else i.get("severity"),
                    "category": i.category if isinstance(i, AuditIssue) else i.get("category"),
                    "title": i.title if isinstance(i, AuditIssue) else i.get("title"),
                    "description": i.description if isinstance(i, AuditIssue) else i.get("description")
                }
                for i in issues[:20]  # Limit to first 20 issues
            ]
        }

        prompt = f"""You are a Yandex Direct advertising expert. Analyze this audit data and provide 5-10 actionable recommendations in Russian.

Account metrics:
- Total campaigns: {metrics.get('total_campaigns', 0)}
- Active campaigns: {metrics.get('active_campaigns', 0)}
- Total ad groups: {metrics.get('total_adgroups', 0)}
- Total keywords: {metrics.get('total_keywords', 0)}

Issues found:
{json.dumps(context['issues_summary'], ensure_ascii=False, indent=2)}

Provide recommendations as a JSON array with objects containing:
- "priority": 1-10 (1 = highest)
- "title": short title in Russian
- "description": detailed description in Russian
- "expected_impact": expected improvement

Respond with ONLY the JSON array, no other text."""

        try:
            response = self.ai_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group())
                return recommendations
        except Exception as e:
            print(f"AI recommendation error: {e}")

        return self._generate_rule_based_recommendations(issues, metrics)

    def _generate_rule_based_recommendations(self, issues: list, metrics: dict) -> list:
        """Generate recommendations based on rules (fallback when AI is unavailable)."""
        recommendations = []

        # Check for critical issues
        critical_issues = [i for i in issues if (isinstance(i, AuditIssue) and i.severity == IssueSeverity.CRITICAL.value) or (isinstance(i, dict) and i.get("severity") == IssueSeverity.CRITICAL.value)]
        if critical_issues:
            recommendations.append({
                "priority": 1,
                "title": "Устраните критические проблемы",
                "description": f"Обнаружено {len(critical_issues)} критических проблем. Рекомендуется исправить их в первую очередь.",
                "expected_impact": "Восстановление работоспособности рекламы"
            })

        # Check for opportunities
        opportunities = [i for i in issues if (isinstance(i, AuditIssue) and i.severity == IssueSeverity.OPPORTUNITY.value) or (isinstance(i, dict) and i.get("severity") == IssueSeverity.OPPORTUNITY.value)]
        if opportunities:
            recommendations.append({
                "priority": 2,
                "title": "Используйте возможности оптимизации",
                "description": f"Найдено {len(opportunities)} возможностей для улучшения эффективности рекламы.",
                "expected_impact": "Повышение CTR и снижение стоимости клика"
            })

        # Check campaign structure
        if metrics.get("active_campaigns", 0) == 0:
            recommendations.append({
                "priority": 1,
                "title": "Активируйте рекламные кампании",
                "description": "Нет активных кампаний. Проверьте статус и бюджет кампаний.",
                "expected_impact": "Начало показа рекламы"
            })

        # Check for A/B testing
        if metrics.get("total_ads", 0) > 0 and metrics.get("total_adgroups", 0) > 0:
            avg_ads_per_group = metrics.get("total_ads", 0) / max(1, metrics.get("total_adgroups", 1))
            if avg_ads_per_group < 2:
                recommendations.append({
                    "priority": 3,
                    "title": "Добавьте вариации объявлений",
                    "description": "В среднем менее 2 объявлений на группу. Создайте дополнительные вариации для A/B тестирования.",
                    "expected_impact": "Улучшение CTR на 5-15%"
                })

        # Check keywords
        if metrics.get("total_keywords", 0) < 10:
            recommendations.append({
                "priority": 3,
                "title": "Расширьте семантическое ядро",
                "description": "Мало ключевых слов. Добавьте релевантные запросы для увеличения охвата.",
                "expected_impact": "Увеличение трафика"
            })

        return recommendations


def run_quick_audit(token: str, login: str, account_name: str,
                    anthropic_key: str = None) -> AuditResult:
    """
    Convenience function to run a quick audit.

    Args:
        token: Yandex OAuth token
        login: Yandex Direct login
        account_name: Friendly name for the account
        anthropic_key: Optional Anthropic API key for AI recommendations

    Returns:
        AuditResult with findings
    """
    api = YandexDirectAPI(token=token, login=login)
    agent = AuditAgent(api=api, account_name=account_name,
                       anthropic_api_key=anthropic_key)
    return agent.run_audit(audit_type="full")
