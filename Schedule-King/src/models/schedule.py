from .lecture_group import LectureGroup
from typing import List
from dataclasses import dataclass
from collections import defaultdict
from src.models.lecture_group import LectureGroup
from datetime import datetime
# Constants for day names
DAY_NAMES = {
    "1": "Sunday",
    "2": "Monday",
    "3": "Tuesday",
    "4": "Wednesday",
    "5": "Thursday",
    "6": "Friday",
    "7": "Saturday"
}
@dataclass
class Schedule:
    """
    Represents a schedule.
    """
    lecture_groups: List[LectureGroup]
    # Metrics
    active_days: int = 0
    gap_count: int = 0
    total_gap_time: int = 0
    avg_start_time: float = 0.0
    avg_end_time: float = 0.0

    def __str__(self):
        # Creating a list of course codes from each LectureGroup object and print them
        course_codes = [lecture_group.course_code for lecture_group in self.lecture_groups]
        return f"Schedule({', '.join(course_codes)})"
    

    def extract_by_day(self):
        day_map = defaultdict(list)

        for lg in self.lecture_groups:
            # Add lecture groups
            day_map[lg.lecture.day].append(("Lecture", lg.course_name, lg.course_code, lg.lecture))
            # Add tirgul
            if lg.tirguls:
                day_map[lg.tirguls.day].append(("Tirgul", lg.course_name, lg.course_code, lg.tirguls))
            # Add maabada
            if lg.maabadas:
                day_map[lg.maabadas.day].append(("Maabada", lg.course_name, lg.course_code, lg.maabadas))

        return day_map
    
    @staticmethod
    def time_to_minutes(t):
        return t.hour * 60 + t.minute

    def generate_metrics(self):
        """
        Computes and stores metrics: active_days, gap_count, total_gap_time, avg_start_time, avg_end_time
        """
        # Group lectures by day
        daily_slots = defaultdict(list)
        day_names = {
            "1": "Sunday",
            "2": "Monday",
            "3": "Tuesday",
            "4": "Wednesday",
            "5": "Thursday",
            "6": "Friday",
            "7": "Saturday"
        }

        # Iterate through lecture groups and populate daily_slots
        for lg in self.lecture_groups:
            if lg.lecture:
                day = day_names.get(lg.lecture.day, lg.lecture.day)
                daily_slots[day].append(lg.lecture)
            if lg.tirguls:
                day = day_names.get(lg.tirguls.day, lg.tirguls.day)
                daily_slots[day].append(lg.tirguls)
            if lg.maabadas:
                day = day_names.get(lg.maabadas.day, lg.maabadas.day)
                daily_slots[day].append(lg.maabadas)

        # Calculate metrics
        self.active_days = len(daily_slots)
        self.gap_count = 0
        self.total_gap_time = 0
        daily_start_times = []
        daily_end_times = []

        # Iterate through each day's slots to calculate metrics
        # Sort the slots by start time and calculate gaps
        for day, slots in daily_slots.items():

            # Sort the slots by day and then by start time
            sorted_slots = sorted(slots, key=lambda s: self.time_to_minutes(s.start_time))
            start_times = [self.time_to_minutes(s.start_time) for s in sorted_slots]
            end_times = [self.time_to_minutes(s.end_time) for s in sorted_slots]
            end_times = [self.time_to_minutes(s.end_time) for s in sorted_slots]

            if not start_times or not end_times:
                continue
            # Update active days
            daily_start_times.append(start_times[0])
            daily_end_times.append(end_times[-1])

            # Calculate gaps
            for i in range(len(sorted_slots) - 1):
                gap = start_times[i + 1] - end_times[i]
                if gap >= 30:
                    self.gap_count += 1
                    self.total_gap_time += gap

        self.avg_start_time = sum(daily_start_times) / len(daily_start_times) if daily_start_times else 0.0
        self.avg_end_time = sum(daily_end_times) / len(daily_end_times) if daily_end_times else 0.0