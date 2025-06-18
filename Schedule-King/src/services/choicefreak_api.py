from collections import defaultdict
import ast
import requests
from src.services.choicefreak_cookies import ChoiceFreakSessionManager

class ChoiceFreakApi:
    INDEX_URL = "https://choicefreak.appspot.com/biu/index.js"
    DETAILS_URL = "https://choicefreak.appspot.com/biu/movies/?period={period}&ids={course_id}"
    PERIODS = {"2025-2": '3', "2025-1": '2', "2024-2": '1', "2024-1": '0'}
    HEADERS = {
        "User-Agent": "Mozilla/5.0"
    }
    session_manager = ChoiceFreakSessionManager()

    def get_courses_by_category(self):
        res = requests.get(self.INDEX_URL)
        data_str = res.text.split('=', 1)[1].rsplit(';', 1)[0]
        courses = ast.literal_eval(data_str)
        grouped = defaultdict(list)
        for course in courses:
            grouped[course['category']].append(course)
        return grouped

    def get_courses_details(self, period: str, courses_ids: list):
        period_code = self.PERIODS.get(period, '0')
        courses_str = ':'.join(courses_ids)
        url = self.DETAILS_URL.format(period=period_code, course_id=courses_str)
        cookie_str = self.session_manager.get_cookie()
        cookies = self.session_manager.cookie_dict(cookie_str)
        res = requests.get(url, headers=self.HEADERS, cookies=cookies)
        return res.json() if res.status_code == 200 else []
