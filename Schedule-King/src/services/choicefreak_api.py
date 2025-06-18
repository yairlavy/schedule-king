import requests
import ast
from collections import defaultdict

class ChoiceFreakApi:
    # Cookie string for authentication/session management
    COOKIE = ""
    # HTTP headers for requests
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    # URL to fetch the index of courses
    INDEX_URL = "https://choicefreak.appspot.com/biu/index.js"
    # URL template to fetch course details
    DETAILS_URL = "https://choicefreak.appspot.com/biu/movies/?period={period}&ids={course_id}"

    # Mapping of period strings to period codes
    PERIODS = {
        "2025-2" : '3',
        "2025-1" : '2',
        "2024-2" : '1',
        "2024-1" : '0',
    }

    @staticmethod
    def get_courses_by_category():
        """
        Fetches all courses and groups them by category.

        Returns:
            dict: A dictionary where keys are categories and values are lists of courses.
        """
        res = requests.get(ChoiceFreakApi.INDEX_URL)
        # Extract the data part from the JS file
        data_str = res.text.split('=', 1)[1].rsplit(';', 1)[0]
        courses = ast.literal_eval(data_str)
        courses_by_category = defaultdict(list)
        for course in courses:
            course_category = course['category']
            courses_by_category[course_category].append(course)
        return courses_by_category

    @staticmethod
    def get_courses_details(period : str, courses_ids: list):
        """
        Fetches details for a list of course IDs for a given period.

        Args:
            period (str): 2025-2 = semester 2, 2025
            courses_ids (list): List of course ID strings.

        Returns:
            list: List of course details (parsed from JSON).
        """
        courses_ids_str = ':'.join(courses_ids)
        period = ChoiceFreakApi.PERIODS.get(period, '0')
        url = ChoiceFreakApi.DETAILS_URL.format(period=period, course_id=courses_ids_str)
        # Pass cookies and headers with the request
        res = requests.get(url, cookies={"cookie": ChoiceFreakApi.COOKIE}, headers=ChoiceFreakApi.HEADERS)
        data = []
        if res.status_code == 200:
            data = res.json()
        return data
