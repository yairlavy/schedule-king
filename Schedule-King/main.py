from src.services.schedule_api import ScheduleAPI
from src.views.course_window import CourseWindow
from src.views.schedule_window import ScheduleWindow

if __name__ == "__main__":
    api = ScheduleAPI()
    DEFAULT_SOURCE = ""
    DEFAULT_DESTINATION = ""
    # Create the CourseWindow and load/display courses
    course_window = CourseWindow(api)
    course_window.load_courses()
    course_window.handle_selection()  # user selects courses

    # Create the ScheduleWindow with api AND output path
    schedule_window = ScheduleWindow(api, DEFAULT_DESTINATION)
    schedule_window.generate_schedules(course_window.get_selected_courses())
    schedule_window.display_schedules()
