from src.api.schedule_api import ScheduleAPI

if __name__ == "__main__":
    DEFAULT_SOURCE = r"C:\Users\kfird\Desktop\schedule-king\Schedule-King\tests\test_files\input_test_api.txt"
    DEFAULT_DESTINATION = r"C:\Users\kfird\Desktop\schedule-king\Schedule-King\tests\test_files\expected_test_api_output.txt"
    api = ScheduleAPI(DEFAULT_SOURCE, DEFAULT_DESTINATION)
    api.process()