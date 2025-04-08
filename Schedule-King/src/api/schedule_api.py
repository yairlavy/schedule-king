from src.data.file_handler import FileHandler
from src.core.scheduler import Scheduler
from src.core.all_strategy import AllStrategy
from src.data.models.course import Course

class ScheduleAPI:
    def __init__(self, file_path: str, output_path: str):
        """
        Initialize the ScheduleAPI with input/output file paths.
        """
        try:
            self.file_handler = FileHandler(file_path, output_path)
        except FileNotFoundError as e:
            print(f"Error: {e}. Please check the file path and try again.")
            exit(1)

    def display_courses(self, courses: list[Course]) -> None:
        """
        Prints available courses with their details.

        :param courses: List of Course objects to display
        """
        print("\nAvailable Courses:")
        for index, course in enumerate(courses, 1):
            # Display each course with its name and course code
            print(f"{index}. {course.name} (Code: {course.course_code})")
        print()

        
    def get_course_selection(self, courses: list[Course], course_codes: list[str] = None) -> list[Course]:
        """
        Selects courses based on user input or provided codes.

        :param courses: List of available Course objects
        :param course_codes: Optional list of course codes for non-interactive selection
        :return: Validated list of selected Course objects
        """
        code_to_course = {course.course_code: course for course in courses}
        print("Please select between 1 and 7 valid courses.")

        while True:

            # Interactive mode: Prompt user if course_codes not provided
            if course_codes is None:
                self.display_courses(courses)
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
            selected_courses = [code_to_course[code] for code in course_codes]

            print("\nSelected Courses:")
            for course in selected_courses:
                print(f"- {course.name} (Code: {course.course_code})")
            print()

            return selected_courses

    def process(self, course_codes: list[str] = None) -> str:
        """
        Main entry point: Parses input, selects courses, generates schedules, and returns formatted output.

        :param course_codes: Optional list of course codes to bypass manual selection
        :return: Formatted schedule string
        """
        # Parse the input file to retrieve available courses
        try:
            courses = self.file_handler.parse()
        except ValueError as e:
            print(f"Error: {e}. Please check the input file format.")
            return ""
        # Get the user's course selection (interactive or non-interactive)
        selected_courses = self.get_course_selection(courses, course_codes)
        # Generate schedules using the Scheduler and AllStrategy
        scheduler = Scheduler(selected_courses, AllStrategy(selected_courses))
        schedules = scheduler.generate()
        print(f"Generated {len(schedules)} schedules.")
        # Format the generated schedules and return the result
        return self.file_handler.format(schedules)