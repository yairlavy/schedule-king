from src.services.schedule_api import ScheduleAPI
from src.views.course_window import CourseWindow
from src.views.schedule_window import ScheduleWindow

if __name__ == "__main__":
    # Define the default source file path for input data
    DEFAULT_SOURCE = r"C:\Users\orlib\Documents\Barilan\simester 4\kugler\schedule-king\Schedule-King\tests\test_files\7courses.txt"
    
    # Define the default destination file path for output data
    DEFAULT_DESTINATION = r"C:\Users\orlib\Documents\Barilan\simester 4\kugler\schedule-king\Schedule-King\tests\test_files\OrOut.txt"
    
    # Create the ScheduleAPI instance
    api = ScheduleAPI(DEFAULT_SOURCE, DEFAULT_DESTINATION)

    # Create the CourseWindow and load/display courses
    course_window = CourseWindow(api)
    course_window.load_courses()
    course_window.handle_selection()  # user selects courses

    # Create the ScheduleWindow with api AND output path
    schedule_window = ScheduleWindow(api, DEFAULT_DESTINATION)
    schedule_window.generate_schedules(course_window.get_selected_courses())
    schedule_window.display_schedules()
