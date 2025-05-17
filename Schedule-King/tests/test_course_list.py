import sys
import os
import unittest
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.components.course_list import CourseList
from src.models.course import Course
from src.models.time_slot import TimeSlot

class TestCourseList(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication instance for testing Qt widgets
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.course_list = CourseList()
        # Create some test courses with correct day values
        self.course1 = Course("Introduction to Programming", "CS101", "Dr. Smith", 
                            [TimeSlot("2", "09:00", "10:30", "101", "BuildingA")])
        self.course2 = Course("Data Structures", "CS201", "Dr. Johnson",
                            [TimeSlot("3", "11:00", "12:30", "202", "BuildingB")])
        self.course3 = Course("Algorithms", "CS301", "Dr. Brown",
                            [TimeSlot("4", "13:00", "14:30", "303", "BuildingC")])
        
        # Populate the course list
        self.course_list.populate_courses([self.course1, self.course2, self.course3])
        # Process events to ensure UI is updated
        self.app.processEvents()

    def test_search_preserves_selection(self):
        # Simulate selecting a course
        self.course_list.selected_course_codes = {self.course1.course_code}
        self.course_list._update_course_list(self.course_list.filtered_courses)
        initial_selection = self.course_list.get_selected_courses()
        print('initial_selection:', [c.course_code for c in initial_selection])
        
        # Perform a search that should keep the selected course visible
        self.course_list.filter_courses("Programming")
        self.app.processEvents()
        time.sleep(0.1)  # Small delay to ensure filtering is processed
        
        # Verify the selection is preserved
        final_selection = self.course_list.get_selected_courses()
        self.assertEqual(len(final_selection), len(initial_selection))
        self.assertEqual(final_selection[0].course_code, initial_selection[0].course_code)

    def test_search_preserves_multiple_selections(self):
        # Simulate selecting multiple courses
        self.course_list.selected_course_codes = {self.course1.course_code, self.course2.course_code}
        self.course_list._update_course_list(self.course_list.filtered_courses)
        initial_selection = self.course_list.get_selected_courses()
        
        # Perform a search that should keep both selected courses visible
        self.course_list.filter_courses("CS")
        self.app.processEvents()
        time.sleep(0.1)  # Small delay to ensure filtering is processed
        
        # Verify the selections are preserved
        final_selection = self.course_list.get_selected_courses()
        self.assertEqual(len(final_selection), len(initial_selection))
        self.assertEqual(set(c.course_code for c in final_selection),
                        set(c.course_code for c in initial_selection))

    def test_search_preserves_selection_when_course_hidden(self):
        # Simulate selecting a course
        self.course_list.selected_course_codes = {self.course1.course_code}
        self.course_list._update_course_list(self.course_list.filtered_courses)
        initial_selection = self.course_list.get_selected_courses()
        selected_code = initial_selection[0].course_code
        
        # Perform a search that should hide the selected course
        self.course_list.filter_courses("Algorithms")
        self.app.processEvents()
        time.sleep(0.1)  # Small delay to ensure filtering is processed
        
        # Verify the selection is preserved even though the course is not visible
        final_selection = self.course_list.get_selected_courses()
        self.assertIn(selected_code, [c.course_code for c in final_selection])
        # Also check that the visible list widget does not show the hidden course
        visible_codes = [self.course_list.list_widget.item(i).data(Qt.UserRole) for i in range(self.course_list.list_widget.count())]
        self.assertNotIn(selected_code, visible_codes)

if __name__ == '__main__':
    unittest.main() 