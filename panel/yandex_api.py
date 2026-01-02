"""
Yandex Direct API v5 Client.
Enhanced version with all methods for audit and management.
"""
import requests
import time
from typing import Optional


class YandexDirectAPI:
    """
    A comprehensive wrapper for the Yandex.Direct API v5.
    Supports all major services for campaign management and auditing.
    """
    API_URL = "https://api.direct.yandex.com/json/v5/"
    SANDBOX_URL = "https://api-sandbox.direct.yandex.com/json/v5/"

    def __init__(self, token: str, login: str, use_sandbox: bool = False):
        """
        Initialize the API client.

        Args:
            token: OAuth token for authentication
            login: Yandex.Direct login of the user
            use_sandbox: Use sandbox API for testing
        """
        self.token = token
        self.login = login
        self.base_url = self.SANDBOX_URL if use_sandbox else self.API_URL
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Client-Login": self.login,
            "Accept-Language": "ru",
            "Content-Type": "application/json; charset=utf-8",
            "returnMoneyInMicros": "false"
        }

    def _request(self, service: str, method: str, params: dict) -> dict:
        """Make a request to the Yandex.Direct API."""
        url = self.base_url + service
        body = {
            "method": method,
            "params": params
        }
        response = requests.post(url, json=body, headers=self.headers)
        response.raise_for_status()
        return response.json()

    # ============== Campaigns ==============

    def get_campaigns(self, states: list = None, statuses: list = None,
                      campaign_ids: list = None) -> dict:
        """
        Get campaigns with optional filtering.

        Args:
            states: Filter by states (ARCHIVED, CONVERTED, ENDED, OFF, ON, SUSPENDED)
            statuses: Filter by statuses (ACCEPTED, DRAFT, MODERATION, REJECTED)
            campaign_ids: Filter by specific IDs
        """
        selection = {}
        if campaign_ids:
            selection["Ids"] = campaign_ids
        if states:
            selection["States"] = states
        if statuses:
            selection["Statuses"] = statuses

        params = {
            "SelectionCriteria": selection,
            "FieldNames": [
                "Id", "Name", "Status", "State", "Type",
                "StartDate", "EndDate", "DailyBudget", "Statistics"
            ],
            "TextCampaignFieldNames": [
                "BiddingStrategy", "Settings"
            ]
        }
        return self._request("campaigns", "get", params)

    def get_campaign_stats(self, campaign_ids: list) -> dict:
        """Get detailed statistics for campaigns."""
        params = {
            "SelectionCriteria": {"Ids": campaign_ids},
            "FieldNames": ["Id", "Name", "Statistics"]
        }
        return self._request("campaigns", "get", params)

    # ============== Ad Groups ==============

    def get_adgroups(self, campaign_ids: list = None, adgroup_ids: list = None) -> dict:
        """
        Get ad groups with optional filtering.

        Args:
            campaign_ids: Filter by campaign IDs
            adgroup_ids: Filter by specific ad group IDs
        """
        selection = {}
        if campaign_ids:
            selection["CampaignIds"] = campaign_ids
        if adgroup_ids:
            selection["Ids"] = adgroup_ids

        params = {
            "SelectionCriteria": selection,
            "FieldNames": [
                "Id", "Name", "CampaignId", "Status", "Type",
                "RegionIds", "NegativeKeywords"
            ]
        }
        return self._request("adgroups", "get", params)

    # ============== Ads ==============

    def get_ads(self, adgroup_ids: list = None, ad_ids: list = None,
                campaign_ids: list = None) -> dict:
        """
        Get ads with optional filtering.

        Args:
            adgroup_ids: Filter by ad group IDs
            ad_ids: Filter by specific ad IDs
            campaign_ids: Filter by campaign IDs
        """
        selection = {}
        if adgroup_ids:
            selection["AdGroupIds"] = adgroup_ids
        if ad_ids:
            selection["Ids"] = ad_ids
        if campaign_ids:
            selection["CampaignIds"] = campaign_ids

        params = {
            "SelectionCriteria": selection,
            "FieldNames": [
                "Id", "AdGroupId", "CampaignId", "State", "Status",
                "Type", "StatusClarification"
            ],
            "TextAdFieldNames": [
                "Title", "Title2", "Text", "Href", "DisplayUrlPath",
                "SitelinkSetId", "VCardId", "AdImageHash", "AdExtensionIds"
            ]
        }
        return self._request("ads", "get", params)

    # ============== Keywords ==============

    def get_keywords(self, adgroup_ids: list = None, keyword_ids: list = None,
                     campaign_ids: list = None) -> dict:
        """
        Get keywords with optional filtering.

        Args:
            adgroup_ids: Filter by ad group IDs
            keyword_ids: Filter by specific keyword IDs
            campaign_ids: Filter by campaign IDs
        """
        selection = {}
        if adgroup_ids:
            selection["AdGroupIds"] = adgroup_ids
        if keyword_ids:
            selection["Ids"] = keyword_ids
        if campaign_ids:
            selection["CampaignIds"] = campaign_ids

        params = {
            "SelectionCriteria": selection,
            "FieldNames": [
                "Id", "Keyword", "AdGroupId", "CampaignId",
                "State", "Status", "Bid", "ContextBid", "StrategyPriority",
                "StatisticsSearch", "StatisticsNetwork"
            ]
        }
        return self._request("keywords", "get", params)

    # ============== Bids ==============

    def get_bids(self, keyword_ids: list = None, adgroup_ids: list = None,
                 campaign_ids: list = None) -> dict:
        """Get bid information for keywords."""
        selection = {}
        if keyword_ids:
            selection["KeywordIds"] = keyword_ids
        if adgroup_ids:
            selection["AdGroupIds"] = adgroup_ids
        if campaign_ids:
            selection["CampaignIds"] = campaign_ids

        params = {
            "SelectionCriteria": selection,
            "FieldNames": [
                "KeywordId", "AdGroupId", "CampaignId",
                "Bid", "ContextBid", "StrategyPriority"
            ]
        }
        return self._request("bids", "get", params)

    def set_bids(self, bids: list) -> dict:
        """
        Set bids for keywords.

        Args:
            bids: List of {"KeywordId": id, "Bid": value} or with ContextBid
        """
        params = {"Bids": bids}
        return self._request("bids", "set", params)

    # ============== Bid Modifiers ==============

    def get_bid_modifiers(self, campaign_ids: list = None,
                          adgroup_ids: list = None) -> dict:
        """Get bid modifiers."""
        selection = {}
        if campaign_ids:
            selection["CampaignIds"] = campaign_ids
        if adgroup_ids:
            selection["AdGroupIds"] = adgroup_ids

        params = {
            "SelectionCriteria": selection,
            "FieldNames": [
                "Id", "CampaignId", "AdGroupId", "Type"
            ],
            "MobileAdjustmentFieldNames": ["BidModifier"],
            "DemographicsAdjustmentFieldNames": ["Gender", "Age", "BidModifier"],
            "RetargetingAdjustmentFieldNames": ["RetargetingConditionId", "BidModifier"],
            "RegionalAdjustmentFieldNames": ["RegionId", "BidModifier"],
            "VideoAdjustmentFieldNames": ["BidModifier"],
            "SmartAdAdjustmentFieldNames": ["BidModifier"]
        }
        return self._request("bidmodifiers", "get", params)

    # ============== Sitelinks ==============

    def get_sitelinks(self, sitelink_ids: list = None) -> dict:
        """Get sitelink sets."""
        selection = {}
        if sitelink_ids:
            selection["Ids"] = sitelink_ids

        params = {
            "SelectionCriteria": selection,
            "FieldNames": ["Id", "Sitelinks"]
        }
        return self._request("sitelinks", "get", params)

    # ============== VCards ==============

    def get_vcards(self, vcard_ids: list = None, campaign_ids: list = None) -> dict:
        """Get vcards (business cards)."""
        selection = {}
        if vcard_ids:
            selection["Ids"] = vcard_ids
        if campaign_ids:
            selection["CampaignIds"] = campaign_ids

        params = {
            "SelectionCriteria": selection,
            "FieldNames": [
                "Id", "CampaignId", "Country", "City", "Street",
                "House", "CompanyName", "Phone", "WorkTime", "ContactEmail"
            ]
        }
        return self._request("vcards", "get", params)

    # ============== Ad Images ==============

    def get_adimages(self, image_hashes: list = None, associated: str = None) -> dict:
        """Get ad images."""
        selection = {}
        if image_hashes:
            selection["AdImageHashes"] = image_hashes
        if associated:
            selection["Associated"] = associated

        params = {
            "SelectionCriteria": selection,
            "FieldNames": [
                "AdImageHash", "Name", "Type", "OriginalUrl",
                "PreviewUrl", "Associated"
            ]
        }
        return self._request("adimages", "get", params)

    # ============== Ad Extensions (Callouts) ==============

    def get_adextensions(self, extension_ids: list = None,
                         types: list = None, states: list = None) -> dict:
        """Get ad extensions (callouts)."""
        selection = {}
        if extension_ids:
            selection["Ids"] = extension_ids
        if types:
            selection["Types"] = types
        if states:
            selection["States"] = states

        params = {
            "SelectionCriteria": selection,
            "FieldNames": ["Id", "Type", "State", "Status", "Associated"],
            "CalloutFieldNames": ["CalloutText"]
        }
        return self._request("adextensions", "get", params)

    # ============== Audience Targets ==============

    def get_audience_targets(self, campaign_ids: list = None,
                             adgroup_ids: list = None) -> dict:
        """Get audience targets."""
        selection = {}
        if campaign_ids:
            selection["CampaignIds"] = campaign_ids
        if adgroup_ids:
            selection["AdGroupIds"] = adgroup_ids

        params = {
            "SelectionCriteria": selection,
            "FieldNames": [
                "Id", "AdGroupId", "CampaignId", "RetargetingListId",
                "InterestId", "State", "ContextBid", "StrategyPriority"
            ]
        }
        return self._request("audiencetargets", "get", params)

    # ============== Retargeting Lists ==============

    def get_retargeting_lists(self, list_ids: list = None) -> dict:
        """Get retargeting lists."""
        selection = {}
        if list_ids:
            selection["Ids"] = list_ids

        params = {
            "SelectionCriteria": selection,
            "FieldNames": ["Id", "Name", "Type", "IsAvailable", "Description"]
        }
        return self._request("retargetinglists", "get", params)

    # ============== Negative Keywords ==============

    def get_negative_keyword_shared_sets(self, set_ids: list = None) -> dict:
        """Get shared negative keyword sets."""
        selection = {}
        if set_ids:
            selection["Ids"] = set_ids

        params = {
            "SelectionCriteria": selection,
            "FieldNames": ["Id", "Name", "NegativeKeywords", "Associated"]
        }
        return self._request("negativekeywordsharedsets", "get", params)

    # ============== Reports ==============

    def get_report(self, report_definition: dict,
                   max_retries: int = 10, return_format: str = "TSV") -> str:
        """
        Create and retrieve a report from the Yandex.Direct API.
        Handles both online and offline report generation.

        Args:
            report_definition: Report parameters
            max_retries: Maximum retry attempts for offline reports
            return_format: TSV or other format

        Returns:
            Report data as string
        """
        reports_url = self.base_url + "reports"
        body = {"params": report_definition}

        for attempt in range(max_retries):
            response = requests.post(reports_url, json=body, headers=self.headers)
            response.raise_for_status()

            if response.status_code == 200:
                return response.text
            elif response.status_code in [201, 202]:
                retry_in = int(response.headers.get("retryIn", 30))
                print(f"Report generating... Retry in {retry_in}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_in)
            else:
                raise Exception(f"Unexpected status: {response.status_code}\n{response.text}")

        raise Exception("Failed to retrieve report after maximum retries")

    def get_campaign_performance_report(self, date_range: str = "LAST_30_DAYS",
                                        campaign_ids: list = None) -> str:
        """
        Get campaign performance report.

        Args:
            date_range: LAST_7_DAYS, LAST_30_DAYS, THIS_MONTH, etc.
            campaign_ids: Optional filter by campaigns
        """
        selection = {}
        if campaign_ids:
            selection["Filter"] = [{"Field": "CampaignId", "Operator": "IN", "Values": [str(c) for c in campaign_ids]}]

        report_def = {
            "ReportName": "Campaign Performance Report",
            "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
            "DateRangeType": date_range,
            "Format": "TSV",
            "IncludeVAT": "NO",
            "IncludeDiscount": "NO",
            "SelectionCriteria": selection,
            "FieldNames": [
                "Date", "CampaignId", "CampaignName", "CampaignType",
                "Impressions", "Clicks", "Ctr", "Cost", "AvgCpc",
                "Conversions", "CostPerConversion", "ConversionRate"
            ]
        }
        return self.get_report(report_def)

    def get_keyword_performance_report(self, date_range: str = "LAST_30_DAYS",
                                        campaign_ids: list = None) -> str:
        """Get keyword performance report."""
        selection = {}
        if campaign_ids:
            selection["Filter"] = [{"Field": "CampaignId", "Operator": "IN", "Values": [str(c) for c in campaign_ids]}]

        report_def = {
            "ReportName": "Keyword Performance Report",
            "ReportType": "SEARCH_QUERY_PERFORMANCE_REPORT",
            "DateRangeType": date_range,
            "Format": "TSV",
            "IncludeVAT": "NO",
            "SelectionCriteria": selection,
            "FieldNames": [
                "Date", "CampaignId", "CampaignName", "AdGroupId", "AdGroupName",
                "Criterion", "CriterionId", "CriterionType", "Query",
                "Impressions", "Clicks", "Ctr", "Cost", "AvgCpc"
            ]
        }
        return self.get_report(report_def)

    def get_ad_performance_report(self, date_range: str = "LAST_30_DAYS",
                                  campaign_ids: list = None) -> str:
        """Get ad performance report."""
        selection = {}
        if campaign_ids:
            selection["Filter"] = [{"Field": "CampaignId", "Operator": "IN", "Values": [str(c) for c in campaign_ids]}]

        report_def = {
            "ReportName": "Ad Performance Report",
            "ReportType": "AD_PERFORMANCE_REPORT",
            "DateRangeType": date_range,
            "Format": "TSV",
            "IncludeVAT": "NO",
            "SelectionCriteria": selection,
            "FieldNames": [
                "Date", "CampaignId", "CampaignName", "AdGroupId", "AdGroupName",
                "AdId", "Impressions", "Clicks", "Ctr", "Cost", "AvgCpc"
            ]
        }
        return self.get_report(report_def)

    # ============== Account Info ==============

    def get_clients(self) -> dict:
        """Get client info (for agency accounts)."""
        params = {
            "FieldNames": [
                "Login", "ClientId", "ClientInfo", "AccountQuality", "Archived",
                "CountryId", "CreatedAt", "Currency", "Grants", "Notification",
                "OverdraftSumAvailable", "Phone", "Representatives",
                "Restrictions", "Settings", "Type", "VatRate"
            ]
        }
        return self._request("agencyclients", "get", params)

    def check_dictionaries(self) -> dict:
        """Get API dictionaries (regions, currencies, etc.)."""
        params = {
            "DictionaryNames": [
                "Currencies",
                "MetroStations",
                "GeoRegions",
                "TimeZones",
                "Constants",
                "AdCategories",
                "OperationSystemVersions",
                "ProductivityAssertions",
                "SupplySidePlatforms",
                "Interests",
                "AudienceCriteriaTypes"
            ]
        }
        return self._request("dictionaries", "get", params)


class YandexDirectAPIError(Exception):
    """Custom exception for Yandex Direct API errors."""

    def __init__(self, message: str, error_code: int = None, error_detail: str = None):
        self.message = message
        self.error_code = error_code
        self.error_detail = error_detail
        super().__init__(self.message)
