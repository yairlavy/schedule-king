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
        """Convert time to minutes (e.g., 900 -> 540)"""
        return t.hour * 60 + t.minute

    @staticmethod
    def time_format_to_minutes(time_format: int) -> int:
        """Convert time format to minutes (e.g., 900 -> 540)"""
        hours = time_format // 100
        minutes = time_format % 100
        return hours * 60 + minutes

    @staticmethod
    def minutes_to_time_format(minutes: int) -> int:
        """Convert minutes to time format (e.g., 540 -> 900)"""
        hours = minutes // 60
        mins = minutes % 60
        return hours * 100 + mins

    def generate_metrics(self):
        """
        Computes and stores metrics: active_days, gap_count, total_gap_time, avg_start_time, avg_end_time
        Assumes each lecture takes exactly one hour
        Times are stored as integers: 700 for 7:00, 1300 for 13:00, etc.
        Only includes days with lectures in average calculations.
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
        for day, slots in daily_slots.items():
            if not slots:  # Skip days with no lectures
                continue
                
            # Sort the slots by start time
            sorted_slots = sorted(slots, key=lambda s: s.start_time)
            
            # Convert times to minutes for internal calculations
            start_minutes = [s.start_time.hour * 60 + s.start_time.minute for s in sorted_slots]
            end_minutes = [(s.start_time.hour + 1) * 60 + s.start_time.minute for s in sorted_slots]  # Each lecture takes 1 hour

            # Convert to time format (e.g., 700 for 7:00) for storage
            daily_start_times.append(self.minutes_to_time_format(start_minutes[0]))
            daily_end_times.append(self.minutes_to_time_format(end_minutes[-1]))

            # Calculate gaps in hours
            for i in range(len(sorted_slots) - 1):
                gap_minutes = start_minutes[i + 1] - end_minutes[i]
                if gap_minutes > 0:  # If there's any gap between lectures
                    self.gap_count += 1
                    self.total_gap_time += gap_minutes / 60  # Add gap in hours

        # Calculate averages only for days with lectures
        if daily_start_times:
            self.avg_start_time = sum(daily_start_times) / len(daily_start_times)
        else:
            self.avg_start_time = 0

        if daily_end_times:
            self.avg_end_time = sum(daily_end_times) / len(daily_end_times)
        else:
            self.avg_end_time = 0