from src.models.course import Course

class CourseWindow:
    def __init__(self, schedule_api):
        """
        Window for displaying and selecting courses.
        """
        self.schedule_api = schedule_api
        self.available_courses: list[Course] = []
        self.selected_courses: list[Course] = []

    def load_courses(self) -> None:
        """
        Load courses from the file via ScheduleAPI.
        """
        self.available_courses = self.schedule_api.get_courses()

    def display_courses(self) -> None:
        """
        Display the list of available courses.
        """
        print("\nAvailable Courses:")
        for index, course in enumerate(self.available_courses, 1):
            print(f"{index}. {course.name} (Code: {course.course_code})")
        print()

    def handle_selection(self, course_codes: list[str] = None) -> None:
        """
        Handle user selection of courses.
        """
        code_to_course = {course.course_code: course for course in self.available_courses}
        print("Please select between 1 and 7 valid courses.")

        while True:
            if course_codes is None:
                self.display_courses()
                raw_input_line = input("Enter course codes (space-separated): ")
                course_codes = raw_input_line.strip().split()

            # Check for duplicates
            seen = set()
            duplicates = [code for code in course_codes if code in seen or seen.add(code)]
            if duplicates:
                print(f"Error: Duplicate course codes found: {', '.join(duplicates)}. Please try again.")
                course_codes = None
                continue

            # Check for invalid codes
            invalid = [code for code in course_codes if code not in code_to_course]
            if invalid:
                print(f"Error: Invalid course codes: {', '.join(invalid)}. Please try again.")
                course_codes = None
                continue

            if len(course_codes) == 0:
                print("Error: No course codes provided. Please try again.")
                course_codes = None
                continue

            if len(course_codes) > 7:
                print("Error: Cannot select more than 7 courses. Please try again.")
                course_codes = None
                continue

            # All codes are valid
            self.selected_courses = [code_to_course[code] for code in course_codes]
            print("\nSelected Courses:")
            for course in self.selected_courses:
                print(f"- {course.name} (Code: {course.course_code})")
            print()

            break

    def get_selected_courses(self) -> list[Course]:
        """
        Return the selected courses.
        """
        return self.selected_courses
