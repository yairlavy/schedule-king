from src.models.time_slot import TimeSlot

# Constants for matrix dimensions
DAYS = 7
SLOTS_PER_DAY = 12  # 8:00 to 20:00
FIRST_HOUR = 8

class MatrixConflictChecker:
    """
    Matrix-based conflict checker using a [day][hour-slot] boolean matrix.
    """

    def __init__(self):
        """
        # Initialize a 2D matrix to match the schedule.
        # The matrix is initialized to False, indicating all slots are free.
        """
        self.taken = [[False] * SLOTS_PER_DAY for _ in range(DAYS)]

    def can_place(self, slot: TimeSlot) -> bool:
        """
        # Check if a TimeSlot can be placed without conflict.
        """
        day_index = int(slot.day) - 1 # Convert day to 0-indexed
        start = slot.start_time.hour
        end = slot.end_time.hour
        
        # Check if the slot is within the valid range
        # and if the slot is not allready taken return True
        for hour in range(start, end):
            index = hour - FIRST_HOUR # 8:00 is index 0 so 8:00 - 8:00 = 0, 20:00 - 8:00 = 12
            if 0 <= index < SLOTS_PER_DAY and self.taken[day_index][index]: 
                return False
        return True

    def place(self, slot: TimeSlot):
        """
        # Mark a TimeSlot as taken.
        """
        day_index = int(slot.day) - 1
        start = slot.start_time.hour
        end = slot.end_time.hour

        # Mark the slot as taken in the matrix
        for hour in range(start, end):
            index = hour - FIRST_HOUR
            if 0 <= index < SLOTS_PER_DAY:
                self.taken[day_index][index] = True

    def remove(self, slot: TimeSlot):
        """
        # Unmark a TimeSlot as free from the matrix.
        """
        day_index = int(slot.day) - 1
        start = slot.start_time.hour
        end = slot.end_time.hour
       
        # Unmark the slot in the matrix
        for hour in range(start, end):
            index = hour - FIRST_HOUR
            if 0 <= index < SLOTS_PER_DAY:
                self.taken[day_index][index] = False