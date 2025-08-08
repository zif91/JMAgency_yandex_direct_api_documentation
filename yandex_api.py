import requests
import time

class YandexDirectAPI:
    """
    A wrapper for the Yandex.Direct API v5.
    """
    API_URL = "https://api.direct.yandex.com/json/v5/"

    def __init__(self, token: str, login: str):
        """
        Initializes the API client.

        :param token: The OAuth token for authentication.
        :param login: The Yandex.Direct login of the user.
        """
        self.token = token
        self.login = login
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Client-Login": self.login,
            "Accept-Language": "ru",
            "Content-Type": "application/json; charset=utf-8",
            "returnMoneyInMicros": "false"
        }

    def _request(self, service: str, method: str, params: dict) -> dict:
        """
        Makes a request to the Yandex.Direct API.
        """
        url = self.API_URL + service
        body = {
            "method": method,
            "params": params
        }
        response = requests.post(url, json=body, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_campaigns(self) -> dict:
        """
        Gets a list of all campaigns for the user.
        """
        params = {
            "SelectionCriteria": {},
            "FieldNames": ["Id", "Name", "Status", "State", "Type"]
        }
        return self._request("campaigns", "get", params)

    def get_adgroups(self, campaign_ids: list[int]) -> dict:
        """
        Gets ad groups for the specified campaigns.
        """
        params = {
            "SelectionCriteria": {
                "CampaignIds": campaign_ids
            },
            "FieldNames": ["Id", "Name", "CampaignId", "Status"]
        }
        return self._request("adgroups", "get", params)

    def get_ads(self, adgroup_ids: list[int]) -> dict:
        """
        Gets ads for the specified ad groups.
        """
        params = {
            "SelectionCriteria": {
                "AdGroupIds": adgroup_ids
            },
            "FieldNames": ["Id", "AdGroupId", "CampaignId", "State", "Status", "Type"]
        }
        return self._request("ads", "get", params)

    def get_keywords(self, adgroup_ids: list[int]) -> dict:
        """
        Gets keywords for the specified ad groups.
        """
        params = {
            "SelectionCriteria": {
                "AdGroupIds": adgroup_ids
            },
            "FieldNames": ["Id", "Keyword", "AdGroupId", "CampaignId", "State", "Status"]
        }
        return self._request("keywords", "get", params)

    def get_report(self, report_definition: dict) -> str:
        """
        Creates and retrieves a report from the Yandex.Direct API.
        Handles both online and offline report generation.
        """
        reports_url = self.API_URL + "reports"
        body = {"params": report_definition}

        max_retries = 5
        for attempt in range(max_retries):
            response = requests.post(reports_url, json=body, headers=self.headers)
            response.raise_for_status()

            if response.status_code == 200:
                # Online report is ready
                return response.text
            elif response.status_code in [201, 202]:
                # Offline report is being generated
                retry_in = int(response.headers.get("retryIn", 30))
                print(f"Report is being generated. Waiting for {retry_in} seconds. (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_in)
            else:
                raise Exception(f"Unexpected status code: {response.status_code}\n{response.text}")

        raise Exception("Failed to retrieve report after several retries.")
