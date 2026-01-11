LOCATION_MAP = {
    # 본사 / 아시아
    "서울": "Asia/Seoul",
    "도쿄": "Asia/Tokyo",
    "상하이": "Asia/Shanghai",
    "싱가포르": "Asia/Singapore",
    "두바이": "Asia/Dubai",
    "뭄바이": "Asia/Kolkata",
    "방콕": "Asia/Bangkok",

    # 유럽
    "런던": "Europe/London",
    "파리": "Europe/Paris",
    "베를린": "Europe/Berlin",
    "모스크바": "Europe/Moscow",

    # 미주
    "뉴욕": "America/New_York",
    "시카고": "America/Chicago",
    "로스앤젤레스": "America/Los_Angeles",
    "밴쿠버": "America/Vancouver",
    "상파울루": "America/Sao_Paulo",

    # 오세아니아 / 아프리카
    "시드니": "Australia/Sydney",
    "오클랜드": "Pacific/Auckland",
    "요하네스버그": "Africa/Johannesburg",
    "하와이": "Pacific/Honolulu",
}

REGION_NAME_MAP = {
    v: k for k, v in LOCATION_MAP.items()
}

def parse_timezone_from_input(user_input: str) -> str | None:
    """
    자연어 입력에서 지역명 기반 timezone 추출
    """
    for region_name, timezone in LOCATION_MAP.items():
        if region_name in user_input:
            return timezone
    return None