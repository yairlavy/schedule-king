from src.api.schedule_api import ScheduleAPI
from src.data.parsers.text_parser import TextParser
from src.data.formatters.text_formatter import TextFormatter
from src.core.scheduler import Scheduler

if __name__ == "__main__":
    api = ScheduleAPI()
    api.process()