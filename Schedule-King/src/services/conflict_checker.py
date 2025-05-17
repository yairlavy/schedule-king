
from itertools import combinations
from src.models.time_slot import TimeSlot
from src.models.lecture_group import LectureGroup

class ConflictChecker:
    """
    Check for time- and room-conflicts directly on LectureGroup objects.
    """

    def _time_overlaps(self, a: TimeSlot, b: TimeSlot) -> bool:
        """
        Check if two TimeSlot objects overlap in time on the same day.
        """
        if a.day != b.day:
            return False
        # Overlap exists unless one ends before the other starts
        return not (a.end_time <= b.start_time or b.end_time <= a.start_time)

    def check_time_conflict(self, a: TimeSlot, b: TimeSlot) -> bool:
        """
        Public method to check if two TimeSlot objects have a time conflict.
        """
        return self._time_overlaps(a, b)

    def check_room_conflict(self, a: TimeSlot, b: TimeSlot) -> bool:
        """
        Check if two TimeSlot objects are in the same room and overlap in time.
        """
        if a.building != b.building or a.room != b.room:
            return False
        return self._time_overlaps(a, b)

    def has_conflict_groups(self, groups: list[LectureGroup]) -> bool:
        """
        Check if there are any time or room conflicts among a list of LectureGroup objects.
        """
        # Flatten all non-None slots from each group (lecture, tirguls, maabadas)
        slots = [
            slot
            for g in groups
            for slot in (g.lecture, g.tirguls, g.maabadas)
            if slot is not None
        ]

        # Check all pairs for conflicts
        slots.sort(key=lambda s: (s.day, s.start_time))
        # Iterate through sorted slots and check for conflicts between consecutive slots
        for i in range(len(slots) - 1):
            a, b = slots[i], slots[i + 1]

            # Skip if slots are on different days (no possible conflict)
            if a.day != b.day:
                continue

            # Check for time or room conflict between the two slots
            if self.check_time_conflict(a, b) or self.check_room_conflict(a, b):
                return True  # Conflict found

        return False  # No conflicts found