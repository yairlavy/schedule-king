import os
import json
import unittest
from unittest.mock import patch

from src.services.choicefreak.choicefreak_parser import ChoiceFreakParser
from src.models.course import Course

class TestChoiceFreakParser(unittest.TestCase):
    def setUp(self):
        self.parser = ChoiceFreakParser()
        self.mock_course_id = ["89132"]
        self.mock_university = "biu"
        self.mock_period = "2025-2"

        # Load mock response from file
        test_dir = os.path.dirname(os.path.dirname(__file__))
        test_files_dir = os.path.join(test_dir, 'test_files')
        file_path = os.path.join(test_files_dir, 'choicefreak_linear.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            self.mock_api_response = json.load(f)

    @patch("src.services.choicefreak.choicefreak_parser.ChoiceFreakApi.get_courses_details")
    def test_parse_by_ids(self, mock_get_courses_details):
        # Arrange
        mock_get_courses_details.return_value = self.mock_api_response

        # Act
        courses = self.parser.parse_by_ids(
            self.mock_course_id,
            self.mock_university,
            self.mock_period
        )

        # Assert
        self.assertEqual(len(courses), 1)
        course = courses[0]
        self.assertIsInstance(course, Course)
        self.assertEqual(course.name, "חשבון אינפיניטסימלי 1")
        self.assertEqual(course.course_code, "89132")

        instructors = course.instructor
        self.assertIn("אלעד עטייא", instructors)
        self.assertIn("ארז שיינר", instructors)
        self.assertIn("גל בן עמי", instructors)
        self.assertIn("שילה אביטל", instructors)
        self.assertIn("ניר שרייבר", instructors)

        # Debug output
        print(len(course.lectures), len(course.tirguls))
        print(course.lectures, course.tirguls)

        self.assertGreater(len(course.lectures), 0)
        lecture_slots = course.lectures
        lecture_days = [slot.day for slot in lecture_slots[0]]
        lecture_rooms = [slot.room for slot in lecture_slots[0]]
        self.assertIn("1", lecture_days)
        self.assertIn("2", lecture_days)
        self.assertIn("4", lecture_rooms)

        self.assertGreater(len(course.tirguls), 0)
        tirgul_slots = course.tirguls
        tirgul_rooms = [slot.room for slot in tirgul_slots[0]]
        self.assertIn("105", tirgul_rooms)

