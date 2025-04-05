from src.api.schedule_api import ScheduleAPI

if __name__ == "__main__":
    DEFAULT_SOURCE = r"C:\Users\User\Documents\Projects\Schedule-King\Software-for-building-a-student-study-schedule\Schedule-King\tests\test_files\V1.0CourseDB.txt"
    DEFAULT_DESTINATION = r"C:\Users\User\Documents\Projects\Schedule-King\Software-for-building-a-student-study-schedule\Schedule-King\tests\test_files\output.txt"
    api = ScheduleAPI(DEFAULT_SOURCE, DEFAULT_DESTINATION)
    api.process()