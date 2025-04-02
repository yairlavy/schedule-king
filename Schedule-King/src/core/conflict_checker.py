# src/core/conflict_checker.py

from src.data.models.time_slot import TimeSlot
from src.data.models.course import Course

class ConflictChecker:
    """
    Responsible for checking conflicts between time slots and courses.
    """

    def check_time_conflict(self, a: TimeSlot, b: TimeSlot) -> bool:
        """
        Check if two time slots conflict in time and day.

        :param a: First time slot
        :param b: Second time slot
        :return: True if they overlap in time on the same day, False otherwise
        """
        if a.day != b.day:
            return False
        
        return not (a.end_time <= b.start_time or b.end_time <= a.start_time)

    def check_room_conflict(self, a: TimeSlot, b: TimeSlot) -> bool:
        """
        Check if two time slots are in the same room at the same time.

        :param a: First time slot
        :param b: Second time slot
        :return: True if they overlap in time and are in the same room, False otherwise
        """
        if a.day != b.day:
            return False

        if a.building != b.building or a.room != b.room:
            return False

        return not (a.end_time <= b.start_time or b.end_time <= a.start_time)

    def find_conflicting_courses(self, courses: list[Course]) -> bool:
        """
        Check if there is any conflict among the course time slots.

        :param courses: List of Course objects
        :return: True if any conflicts exist, False otherwise
        """
        all_slots = []

        for course in courses:
            all_slots.extend(course.lectures)
            all_slots.extend(course.tirguls)
            all_slots.extend(course.maabadas)

        # Pairwise check of conflicts
        for i in range(len(all_slots)):
            for j in range(i + 1, len(all_slots)):
                if (self.check_time_conflict(all_slots[i], all_slots[j]) or
                        self.check_room_conflict(all_slots[i], all_slots[j])):
                    return True

        return False
