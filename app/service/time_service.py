import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# World Time API 대신 Time Zone DB API
class TimeService:
    BASE_URL = "https://api.timezonedb.com/v2.1/get-time-zone"

    def __init__(self):
        api_key = os.getenv("TIME_API_KEY")
        if not api_key:
            raise ValueError("TIME_API_KEY environment variable is required")

        self.api_key = api_key

    def get_current_time(self, timezone: str):
        params = {
            "key": self.api_key,
            "format": "json",
            "by": "zone",
            "zone": timezone,
        }

        try:
            res = requests.get(self.BASE_URL, params=params, timeout=5)
            res.raise_for_status()
            data = res.json()
        except requests.RequestException as e:
            raise RuntimeError(f"TimeZoneDB API error: {e}")

        return json.dumps({
            "datetime": data["formatted"],
            "timezone": data["zoneName"],
            "gmt_offset": data["gmtOffset"]
        })