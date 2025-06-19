from collections import defaultdict
import ast
import requests
from src.services.choicefreak.choicefreak_cookies import ChoiceFreakSessionManager

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

    # A single session manager that lazily loads or triggers login if needed
    session_manager = ChoiceFreakSessionManager()

    @staticmethod
    def get_courses_by_category(university: str):
        """
        Fetches the full list of courses and groups them by category.

        Args:
            university (str): University code (e.g., 'biu')
        Returns:
            dict[str, list[dict]]: Dictionary mapping category names to course lists
        """
        index_url = f"https://choicefreak.appspot.com/{university}/index.js"
        res = requests.get(index_url)
        if res.status_code != 200:
            raise Exception("Failed to fetch course index")
        data_str = res.text.split('=', 1)[1].rsplit(';', 1)[0]
        courses = ast.literal_eval(data_str)
        grouped = defaultdict(list)
        for course in courses:
            grouped[course['category']].append(course)
        return grouped

    @staticmethod
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
        period_code = ChoiceFreakApi.PERIODS.get(period, '0')
        courses_str = ':'.join(courses_ids)
        details_url = f"https://choicefreak.appspot.com/{university}/movies/?period={period_code}&ids={courses_str}"
        cookie_str = ChoiceFreakApi.session_manager.get_cookie()
        cookies = ChoiceFreakApi.session_manager.cookie_dict(cookie_str)
        res = requests.get(details_url, headers=ChoiceFreakApi.HEADERS, cookies=cookies)
        return res.json() if res.status_code == 200 else []
