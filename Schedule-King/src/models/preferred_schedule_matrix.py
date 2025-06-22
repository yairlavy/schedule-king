from enum import Enum

# Constants
DAYS = 7                  # Number of days in the week (Sunday to Saturday)
SLOTS_PER_DAY = 12        # 12 time slots from 08:00 to 20:00
FIRST_HOUR = 8            # The first time slot starts at 08:00

class CellPreference(Enum):
    EMPTY = 0
    PREFERRED = 3
    FORBIDDEN = -1

class PreferredScheduleMatrix:
    """
    A matrix (7x12) storing user preferences for each time slot in the week.
    """
    def __init__(self):
        self.matrix = [
            [CellPreference.EMPTY for _ in range(SLOTS_PER_DAY)]
            for _ in range(DAYS)
        ]

    def add(self, slot):
        """
        Mark the given TimeSlot as preferred.
        :param slot: TimeSlot object
        """
        day_index = int(slot.day) - 1
        slot_index = slot.start_time.hour - FIRST_HOUR
        if 0 <= day_index < DAYS and 0 <= slot_index < SLOTS_PER_DAY:
            self.matrix[day_index][slot_index] = CellPreference.PREFERRED

    def set_slot(self, day_index: int, slot_index: int, preference: CellPreference):
        self.matrix[day_index][slot_index] = preference

    def get_slot(self, day_index: int, slot_index: int) -> CellPreference:
        return self.matrix[day_index][slot_index]

    def score_schedule(self, schedule) -> int:
        score = 0
        used_slots_per_day = [[] for _ in range(DAYS)]

        for lg in schedule.lecture_groups:
            for session_group in [lg.lecture, lg.tirguls, lg.maabadas]:
                if not session_group:
                    continue
                slots = session_group if isinstance(session_group, list) else [session_group]
                for s in slots:
                    day_index = int(s.day) - 1
                    slot_index = s.start_time.hour - FIRST_HOUR
                    if 0 <= day_index < DAYS and 0 <= slot_index < SLOTS_PER_DAY:
                        used_slots_per_day[day_index].append(slot_index)
                        if self.matrix[day_index][slot_index] == CellPreference.PREFERRED:
                            score += 3

        # Bonus for neutral day usage
        for day_index in range(DAYS):
            if used_slots_per_day[day_index]:
                if all(self.matrix[day_index][slot] == CellPreference.EMPTY for slot in used_slots_per_day[day_index]):
                    score += 1

        return score
