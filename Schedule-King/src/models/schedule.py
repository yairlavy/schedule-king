from dataclasses import dataclass
from typing import List
from collections import defaultdict
from datetime import datetime
from src.models.lecture_group import LectureGroup
from src.models.preferred_schedule_matrix import PreferredScheduleMatrix, CellPreference

# Mapping day numbers to names
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
    Represents a schedule and its calculated metrics.
    """
    lecture_groups: List[LectureGroup]
    active_days: int = 0
    gap_count: int = 0
    total_gap_time: int = 0
    avg_start_time: float = 0.0
    avg_end_time: float = 0.0
    preference_score: int = 0  # Score based on preferred time slots

    def __str__(self):
        course_codes = [lg.course_code for lg in self.lecture_groups]
        return f"Schedule({', '.join(course_codes)})"

    def extract_by_day(self):
        day_map = defaultdict(list)
        for lg in self.lecture_groups:
            for slot in lg.lecture:
                day_map[slot.day].append(("Lecture", lg.course_name, lg.course_code, slot))
            if lg.tirguls:
                for slot in lg.tirguls:
                    day_map[slot.day].append(("Tirgul", lg.course_name, lg.course_code, slot))
            if lg.maabadas:
                for slot in lg.maabadas:
                    day_map[slot.day].append(("Maabada", lg.course_name, lg.course_code, slot))
        return day_map

    def compute_preference_score(self, preferred_matrix: PreferredScheduleMatrix) -> None:
        """
        Computes preference alignment score:
        +3 for preferred slot
        -1 for forbidden slot
        +1 for neutral slots if day used without any preferred/forbidden marking
        """
        score = 0
        used_slots_per_day = [[] for _ in range(7)]  # Sunday = 0, Saturday = 6

        for lg in self.lecture_groups:
            for group in [lg.lecture, lg.tirguls, lg.maabadas]:
                if not group:
                    continue
                slots = group if isinstance(group, list) else [group]
                for s in slots:
                    day_index = int(s.day) - 1
                    slot_index = s.start_time.hour - 8  # Assuming 08:00 is the first slot

                    if 0 <= day_index < 7 and 0 <= slot_index < 12:
                        used_slots_per_day[day_index].append(slot_index)
                        cell = preferred_matrix.get_slot(day_index, slot_index)

                        if cell == CellPreference.PREFERRED:
                            score += 3
                        elif cell == CellPreference.FORBIDDEN:
                            score -= 0

        # Add +1 per day if used only in EMPTY (neutral) slots
        for day_index in range(7):
            if not used_slots_per_day[day_index]:
                continue
            if all(preferred_matrix.get_slot(day_index, slot) == CellPreference.EMPTY
                   for slot in used_slots_per_day[day_index]):
                score += 1

        self.preference_score = score

    def generate_metrics(self):
        """
        Computes all schedule metrics: days, gaps, total gap time, average start/end times.
        """
        daily_slots = defaultdict(list)
        for lg in self.lecture_groups:
            if lg.lecture:
                for slot in lg.lecture:
                    day = DAY_NAMES.get(slot.day, slot.day)
                    daily_slots[day].append(slot)
            if lg.tirguls:
                for slot in lg.tirguls:
                    day = DAY_NAMES.get(slot.day, slot.day)
                    daily_slots[day].append(slot)
            if lg.maabadas:
                for slot in lg.maabadas:
                    day = DAY_NAMES.get(slot.day, slot.day)
                    daily_slots[day].append(slot)

        self.active_days = len(daily_slots)
        self.gap_count = 0
        self.total_gap_time = 0
        daily_start_times = []
        daily_end_times = []

        for day, slots in daily_slots.items():
            if not slots:
                continue

            sorted_slots = sorted(slots, key=lambda s: s.start_time)
            start_minutes = [s.start_time.hour * 60 + s.start_time.minute for s in sorted_slots]
            end_minutes = [s.end_time.hour * 60 + s.end_time.minute for s in sorted_slots]

            daily_start_times.append(self.minutes_to_time_format(start_minutes[0]))
            daily_end_times.append(self.minutes_to_time_format(end_minutes[-1]))

            for i in range(len(start_minutes) - 1):
                gap = start_minutes[i + 1] - end_minutes[i]
                if gap > 30 and end_minutes[i] > start_minutes[0] and start_minutes[i + 1] < end_minutes[-1]:
                    self.gap_count += 1
                    self.total_gap_time += gap / 60.0  # in hours

        self.avg_start_time = (
            sum(daily_start_times) / len(daily_start_times) if daily_start_times else 0
        )
        self.avg_end_time = (
            sum(daily_end_times) / len(daily_end_times) if daily_end_times else 0
        )

        self.metric_tuple = (
            int(self.active_days),
            int(self.gap_count),
            int(self.total_gap_time * 2),  # Convert to half-hours
            self.time_format_to_minutes(int(self.avg_start_time)),
            self.time_format_to_minutes(int(self.avg_end_time)),
            int(self.preference_score),
        )

    @staticmethod
    def time_to_minutes(t):
        return t.hour * 60 + t.minute

    @staticmethod
    def time_format_to_minutes(time_format: int) -> int:
        hours = time_format // 100
        minutes = time_format % 100
        return hours * 60 + minutes

    @staticmethod
    def minutes_to_time_format(minutes: int) -> int:
        hours = minutes // 60
        mins = minutes % 60
        return hours * 100 + mins
