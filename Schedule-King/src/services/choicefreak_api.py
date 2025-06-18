from collections import defaultdict
import ast
import requests
from src.services.choicefreak_cookies import ChoiceFreakSessionManager

class ChoiceFreakApi:
    # URL to the JS file containing the course index
    INDEX_URL = "https://choicefreak.appspot.com/biu/index.js"

    # URL template to fetch course details based on period and course IDs
    DETAILS_URL = "https://choicefreak.appspot.com/biu/movies/?period={period}&ids={course_id}"

    # Mapping academic year/semester strings to internal period codes
    PERIODS = {
        "2025-2": '3',
        "2025-1": '2',
        "2024-2": '1',
        "2024-1": '0'
    }

    # Standard browser-like headers to avoid being blocked by user-agent checks
    HEADERS = {
        "User-Agent": "Mozilla/5.0"
    }

    # A single session manager that lazily loads or triggers login if needed
    session_manager = ChoiceFreakSessionManager()

    @classmethod
    def get_courses_by_category(cls):
        """
        Fetches the full list of courses and groups them by category.

        Returns:
            dict[str, list[dict]]: Dictionary mapping category names to course lists
        """
        # Request the JS file that contains a large object literal of courses
        res = requests.get(cls.INDEX_URL)
        if res.status_code != 200:
            raise Exception("Failed to fetch course index")

        # Extract just the object from the JS (strip `var courses = ...;`)
        data_str = res.text.split('=', 1)[1].rsplit(';', 1)[0]

        # Safely parse the object as Python literal
        courses = ast.literal_eval(data_str)

        # Group courses by their 'category' field
        grouped = defaultdict(list)
        for course in courses:
            grouped[course['category']].append(course)

        return grouped

    @classmethod
    def get_courses_details(cls, period: str, courses_ids: list[str]):
        """
        Fetches detailed schedule info for a list of course IDs in a specific semester.

        Args:
            period (str): e.g., "2025-2"
            courses_ids (list[str]): List of course ID strings

        Returns:
            list[dict]: Detailed info about the specified courses
        """
        # Convert external period string to internal code
        period_code = cls.PERIODS.get(period, '0')

        # Concatenate course IDs as required by the API format
        courses_str = ':'.join(courses_ids)

        # Construct the final URL
        url = cls.DETAILS_URL.format(period=period_code, course_id=courses_str)

        # Lazily fetch valid cookie (may trigger login popup if missing or invalid)
        cookie_str = cls.session_manager.get_cookie()
        cookies = cls.session_manager.cookie_dict(cookie_str)

        # Make the request with cookies and headers
        res = requests.get(url, headers=cls.HEADERS, cookies=cookies)

        # Return parsed JSON if successful, otherwise return empty list
        return res.json() if res.status_code == 200 else []
