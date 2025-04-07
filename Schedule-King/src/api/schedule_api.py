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
        # Ensure the user selects between 1 and 7 valid courses
        selected_courses = []
        while True:
            print("Please select between 1 and 7 valid courses.")
            # Reset selected_courses at the start of each iteration
            selected_courses = [] 
            seen_codes = set()
            # Create a mapping of course codes to Course objects for quick lookup
            code_to_course = {course.course_code: course for course in courses}
            # Interactive mode: Prompt user for course codes if not provided
            self.display_courses(courses)
            raw_input = input("Enter course codes (space-separated): ")
            course_codes = raw_input.strip().split()
            # Validate the course codes and add the corresponding courses to the selection
            for raw_code in course_codes:
                code = raw_code.strip()
                if code in seen_codes:
                    print(f"Warning: Duplicate course code '{code}' found. Skipping.")
                    continue
                course = code_to_course.get(code)
                if course:
                    selected_courses.append(course)
                    seen_codes.add(code)
                else:
                    # Warn the user if a course code is invalid
                    print(f"Warning: Course code '{code}' not found. Skipping.")
            # Check if no valid courses were selected
            if not selected_courses:
                print("Error: No valid courses selected.")
                continue
            # Enforce a maximum limit of 7 courses
            if len(selected_courses) > 7:
                print("Error: Cannot select more than 7 courses.")
                continue
            break

        return selected_courses

    def process(self, course_codes: list[str] = None) -> str:
        """
        Main entry point: Parses input, selects courses, generates schedules, and returns formatted output.

        :param course_codes: Optional list of course codes to bypass manual selection
        :return: Formatted schedule string
        """
        # Parse the input file to retrieve available courses
        courses = self.file_handler.parse()
        # Get the user's course selection (interactive or non-interactive)
        selected_courses = self.get_course_selection(courses, course_codes)
        # Display the selected courses
        print("\nSelected Courses:")
        for course in selected_courses:
            print(f"- {course.name}")
        # Generate schedules using the Scheduler and AllStrategy
        scheduler = Scheduler(selected_courses, AllStrategy(selected_courses))
        schedules = scheduler.generate()
        # Format the generated schedules and return the result
        return self.file_handler.format(schedules)