from src.services.schedule_api import ScheduleAPI  # Import the ScheduleAPI class from the schedule_api module

if __name__ == "__main__":
    # Define the default source file path for input data
    DEFAULT_SOURCE = r"C:\Users\orlib\Documents\Barilan\simester 4\kugler\schedule-king\Schedule-King\tests\test_files\7courses.txt"
    
    # Define the default destination file path for output data
    DEFAULT_DESTINATION = r"C:\Users\orlib\Documents\Barilan\simester 4\kugler\schedule-king\Schedule-King\tests\test_files\OrOut.txt"
    
    # Create an instance of ScheduleAPI with the default source and destination paths
    api = ScheduleAPI(DEFAULT_SOURCE, DEFAULT_DESTINATION)
    
    # Call the process method to execute the main functionality of the API
    api.process()