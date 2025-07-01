"""
Integration test for the full ChoiceFreak workflow.
This test simulates user interactions from the CourseWindow to fetching course details
via the CourseController and ChoiceFreak API mocks.
"""
import unittest
from unittest.mock import patch, MagicMock

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QEventLoop, Qt

from src.views.course_window import CourseWindow
from src.controllers.CourseController import CourseController
from src.models.course import Course
from src.services.schedule_api import ScheduleAPI

# It's good practice to have a QApplication instance for widget tests
app = QApplication.instance()
if app is None:
    app = QApplication([])

class TestChoiceFreakIntegration(unittest.TestCase):
    """Tests the integration between CourseWindow, CourseController, and ChoiceFreak services."""

    def setUp(self):
        """Set up the test environment."""
        # Mock the API for the controller
        self.mock_schedule_api = MagicMock(spec=ScheduleAPI)
        
        # The components to be tested
        self.course_controller = CourseController(api=self.mock_schedule_api)
        self.course_window = CourseWindow()

        # Wire them up as they would be in the main application
        self.course_window.choicefreakSelectionMade.connect(self.handle_choicefreak_selection)
        self.course_controller.courses_updated.connect(self.course_window.displayCourses)
        self.course_window.on_continue = self.course_controller.set_selected_courses
        
        # For filling courses
        self.course_controller.update_ui_course_filled = self.handle_course_filled
        self.course_controller.start_thread()

    def tearDown(self):
        """Clean up after the test."""
        if self.course_controller.running:
            self.course_controller.thread.quit()
            self.course_controller.thread.wait()

    def handle_choicefreak_selection(self, university, period):
        """Simulates what a main controller would do to fetch and display courses."""
        courses = self.course_controller.fetch_choicefreak_courses(university, period)
        self.course_controller.courses = courses
        self.course_controller.courses_updated.emit(courses)

    def handle_course_filled(self, course, error=None):
        """Callback to acknowledge a course has been filled."""
        # This is a placeholder for potential UI updates.
        pass

    @patch('src.services.choicefreak.choicefreak_api.ChoiceFreakApi.get_courses_by_category')
    @patch('src.services.choicefreak.choicefreak_api.ChoiceFreakApi.get_courses_details')
    @patch('src.services.choicefreak.choicefreak_cookies.ChoiceFreakSessionManager.get_cookie')
    def test_full_choicefreak_flow(self, mock_get_cookie, mock_get_details, mock_get_by_category):
        """
        Tests the entire flow:
        1. Load courses from ChoiceFreak.
        2. Display them in the UI.
        3. Select a course.
        4. Submit and trigger detail fetching.
        5. Verify the course is updated.
        """
        # --- ARRANGE ---
        
        # 1. Mock API responses
        mock_get_cookie.return_value = "mock_cookie"
        
        mock_category_response = {
            "Computer Science": [
                {"title": "Intro to CS", "id": "101", "category": "Computer Science"},
                {"title": "Data Structures", "id": "102", "category": "Computer Science"},
            ],
            "Mathematics": [
                {"title": "Calculus 1", "id": "201", "category": "Mathematics"},
            ]
        }
        mock_get_by_category.return_value = mock_category_response

        mock_details_response = [
            {
                "id": "101", "title": "Intro to CS", "shows": [
                    {"kind": "הרצאה", "groupping_id": "1", "when": "2025-03-02T10:00:00", "duration": 90,
                     "where": {"building": "Bld A", "room": "101"}, "details": {"who": {"name": "Dr. Smith"}}}
                ]
            }
        ]
        mock_get_details.return_value = mock_details_response

        # --- ACT ---

        # 2. Simulate user selecting ChoiceFreak to load courses
        # We call the handler directly to bypass the 1-second QTimer in the UI code.
        self.handle_choicefreak_selection("biu", "2025-2")
        QApplication.processEvents()

        # 3. Verify that the course list in the UI is populated
        all_courses_in_list = self.course_window.courseSelector.get_all_courses()
        print(all_courses_in_list)
        self.assertEqual(len(all_courses_in_list), 3)
        self.assertEqual(all_courses_in_list[0].name, "Intro to CS")

        # 4. Simulate user selecting a course ("Intro to CS")
        course_to_select = all_courses_in_list[0]
        list_widget = self.course_window.courseSelector.course_list
        
        # Get the QListWidgetItem from the internal lookup
        item_to_select = list_widget._item_lookup.get(course_to_select.course_code)
        self.assertIsNotNone(item_to_select, "Course item not found in lookup")
        
        # Programmatically select the item
        item_to_select.setSelected(True)
        # Manually trigger the handler because programmatic selection doesn't auto-trigger it
        list_widget._handle_selection_changed()
        QApplication.processEvents()

        # 5. Simulate user submitting the selection
        self.course_window.navigateToSchedulesWindow()
        QApplication.processEvents()
        
        selected_courses = self.course_controller.get_selected_courses()
        self.assertEqual(len(selected_courses), 1)
        self.assertEqual(selected_courses[0].course_code, "101")

        # 6. Trigger the course filling process
        self.course_controller.fill_courses(selected_courses)

        # Wait for the async worker to finish by checking if the course is detailed
        loop = QEventLoop()
        QTimer.singleShot(3000, loop.quit) # 3-second timeout
        
        original_course = selected_courses[0]
        
        def check_if_filled():
            if original_course.is_detailed:
                loop.quit()

        timer = QTimer()
        timer.timeout.connect(check_if_filled)
        timer.start(100) # Check every 100ms
        loop.exec_()
        timer.stop()

        # --- ASSERT ---

        # 7. Verify that the details were fetched via the API
        mock_get_details.assert_called_once_with("biu", "2025-2", ["101"])

        # 8. Verify that the course object is updated with details
        self.assertTrue(original_course.is_detailed)
        self.assertEqual(len(original_course.lectures), 1)
        self.assertEqual(original_course.instructor, "Dr. Smith")

if __name__ == '__main__':
    unittest.main()
