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
            for lecture_slot in lg.lecture:
                day_map[lecture_slot.day].append(("Lecture", lg.course_name, lg.course_code, lecture_slot))
            # Add tirgul
            if lg.tirguls:
                for tirgul_slot in lg.tirguls:
                    day_map[tirgul_slot.day].append(("Tirgul", lg.course_name, lg.course_code, tirgul_slot))
            # Add maabada
            if lg.maabadas:
                for maabada_slot in lg.maabadas:
                    day_map[maabada_slot.day].append(("Maabada", lg.course_name, lg.course_code, maabada_slot))

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

        # Iterate through lecture groups and populate daily_slots
        for lg in self.lecture_groups:
            if lg.lecture:
                for lecture_slot in lg.lecture:
                    day = DAY_NAMES.get(lecture_slot.day, lecture_slot.day)
                    daily_slots[day].append(lecture_slot)
            if lg.tirguls:
                for tirgul_slot in lg.tirguls:
                    day = DAY_NAMES.get(tirgul_slot.day, tirgul_slot.day)
                    daily_slots[day].append(tirgul_slot)
            if lg.maabadas:
                for maabada_slot in lg.maabadas:
                    day = DAY_NAMES.get(maabada_slot.day, maabada_slot.day)
                    daily_slots[day].append(maabada_slot)

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
            end_minutes = [s.end_time.hour * 60 + s.end_time.minute for s in sorted_slots] 

            # Convert to time format (e.g., 700 for 7:00) for storage
            daily_start_times.append(self.minutes_to_time_format(start_minutes[0]))
            daily_end_times.append(self.minutes_to_time_format(end_minutes[-1]))
            
            # Count valid gaps between classes
            for i in range(len(start_minutes) - 1):
                gap = start_minutes[i + 1] - end_minutes[i]
                if gap > 30:# 30 minutes gap
                    # Check if the gap is valid (not at the start or end of the day)
                    if end_minutes[i] > start_minutes[0] and start_minutes[i + 1] < end_minutes[-1]:
                        self.gap_count += 1
                        self.total_gap_time += gap / 60.0  # convert to hours

        # Calculate averages only for days with lectures
        if daily_start_times:
            self.avg_start_time = sum(daily_start_times) / len(daily_start_times)
        else:
            self.avg_start_time = 0

        if daily_end_times:
            self.avg_end_time = sum(daily_end_times) / len(daily_end_times)
        else:
            self.avg_end_time = 0
        # Store metrics as a tuple for easy comparison or sorting
        # - active_days: number of days with lectures
        # - gap_count: number of gaps greater than 30 minutes
        # - total_gap_time: total gap time in half-hours (rounded down)
        # - avg_start_time: average start time in minutes since midnight
        # - avg_end_time: average end time in minutes since midnight
        self.metric_tuple = (
            int(self.active_days),
            int(self.gap_count),
            int(self.total_gap_time * 2),  # Convert hours to half-hours
            Schedule.time_format_to_minutes(int(self.avg_start_time)),  # e.g., 930 → 570
            Schedule.time_format_to_minutes(int(self.avg_end_time)),
        )