from src.api.schedule_api import ScheduleAPI

if __name__ == "__main__":
    DEFAULT_SOURCE = r"C:\Users\orlib\Documents\Barilan\simester 4\kugler\schedule-king\Schedule-King\tests\test_files\V1.0CourseDB.txt"
    DEFAULT_DESTINATION = r"C:\Users\orlib\Documents\Barilan\simester 4\kugler\schedule-king\Schedule-King\tests\test_files\V1.0out.txt"
    api = ScheduleAPI(DEFAULT_SOURCE, DEFAULT_DESTINATION)
    api.process()