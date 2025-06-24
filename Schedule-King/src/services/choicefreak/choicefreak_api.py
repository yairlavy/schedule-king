from collections import defaultdict
import ast
import json
import requests
from src.services.choicefreak.choicefreak_cookies import ChoiceFreakSessionManager
import re
import diskcache

cache = diskcache.Cache('.cfreak_cache')

class ChoiceFreakApi:
    # Standard browser-like headers to avoid being blocked by user-agent checks
    HEADERS = {
        "User-Agent": "Mozilla/5.0"
    }

    # Mapping academic year/semester strings to internal period codes
    PERIODS = {
        "2025-2": '3',
        "2025-1": '2',
        "2024-2": '1',
        "2024-1": '0'
    }

    @staticmethod
    def period_to_code(university: str, period: str) -> str:
        """ Converts a period string (e.g., "2025-2") to its corresponding code."""
        base = int(ChoiceFreakApi.PERIODS.get(period, '0'))
        if university == 'bgu':
            base += 4
        elif university == 'tech':
            base += 3
        elif university == 'tau':
            base += 3
        return str(base)
    
    # A single session manager that lazily loads or triggers login if needed
    session_manager = ChoiceFreakSessionManager()

    @staticmethod
    @cache.memoize(expire=60 * 60 * 24 * 7)
    def get_courses_by_category(university: str, period: str = "2025-2"):
        """
        Fetches the full list of courses and groups them by category.

        Args:
            university (str): University code (e.g., 'biu')
        Returns:
            dict[str, list[dict]]: Dictionary mapping category names to course lists
        """
        period_code = ChoiceFreakApi.period_to_code(university, period)
        index_url = f"https://choicefreak.appspot.com/{university}/index.js?period={period_code}"
        print(f"Fetching course index from {index_url}")
        cookie_str = ChoiceFreakApi.session_manager.get_cookie()
        res = requests.get(index_url)
        if res.status_code != 200:
            raise Exception("Failed to fetch course index")
        data_str = res.content.decode('utf-8').split('=', 1)[1].rsplit(';', 1)[0]
        print(data_str[:1000])  # Print first 100 characters for debugging
        pattern = r"&#\d+;"
        data_str = re.sub(pattern, "", data_str)
        json_str = data_str.replace("'", '"')
        courses = json.loads(json_str)
        print(f"Fetched {len(courses)} courses from index")
        grouped = defaultdict(list)
        for course in courses:
            grouped[course['category']].append(course)
        return grouped

    @staticmethod
    @cache.memoize(expire=60 * 60 * 24 * 7)
    def get_courses_details(university: str, period: str, courses_ids: list[str]):
        """
        Fetches detailed schedule info for a list of course IDs in a specific semester.

        Args:
            university (str): University code (e.g., 'biu')
            period (str): e.g., "2025-2"
            courses_ids (list[str]): List of course ID strings
        Returns:
            list[dict]: Detailed info about the specified courses
        """
        period_code = ChoiceFreakApi.period_to_code(university, period)

        courses_str = ':'.join(courses_ids)
        details_url = f"https://choicefreak.appspot.com/{university}/movies/?period={period_code}&ids={courses_str}"
        cookie_str = ChoiceFreakApi.session_manager.get_cookie()
        cookies = ChoiceFreakApi.session_manager.cookie_dict(cookie_str)
        res = requests.get(details_url, headers=ChoiceFreakApi.HEADERS, cookies=cookies)
        return res.json() if res.status_code == 200 else []
