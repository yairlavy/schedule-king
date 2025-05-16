from itertools import combinations
from src.models.time_slot import TimeSlot
from src.models.lecture_group import LectureGroup

class ConflictChecker:
    """
    Check for time- and room-conflicts directly on LectureGroup objects.
    """

    def _time_overlaps(self, a: TimeSlot, b: TimeSlot) -> bool:
        if a.day != b.day:
            return False
        return not (a.end_time <= b.start_time or b.end_time <= a.start_time)

    def check_time_conflict(self, a: TimeSlot, b: TimeSlot) -> bool:
        return self._time_overlaps(a, b)

    def check_room_conflict(self, a: TimeSlot, b: TimeSlot) -> bool:
        if a.building != b.building or a.room != b.room:
            return False
        return self._time_overlaps(a, b)

    def find_conflicting_courses(self, courses: list[Course]) -> bool:
        """
        Check if there is any conflict among the course time slots.

        :param courses: List of Course objects
        :return: True if any conflicts exist, False otherwise
        """
        # Gather all time slots from all courses (lectures, tirguls, maabadas)
        all_slots: list[TimeSlot] = [
            slot for course in courses 
            for slot in course.lectures + course.tirguls + course.maabadas 
            if slot is not None
        ]
        # Pairwise check of conflicts
        for i in range(len(all_slots)):
            for j in range(i + 1, len(all_slots)):
                if (self.check_time_conflict(all_slots[i], all_slots[j]) or
                        self.check_room_conflict(all_slots[i], all_slots[j])):
                    return True

        return False
