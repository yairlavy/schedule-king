from enum import Enum

# Constants
DAYS = 7                  # Number of days in the week (Sunday to Saturday)
SLOTS_PER_DAY = 12        # 12 time slots from 08:00 to 20:00
FIRST_HOUR = 8            # The first time slot starts at 08:00

class CellPreference(Enum):
    """
    Enum representing user preferences for time slots.
    Note: FORBIDDEN is handled at conflict checking level, not here.
    """
    EMPTY = 0      # Neutral time slot (no preference)
    PREFERRED = 1  # User prefers this time slot

class PreferredScheduleMatrix:
    """
    A matrix (7x12) storing user preferences for each time slot in the week.
    Only handles PREFERRED slots since FORBIDDEN slots are handled by conflict checking.
    """
    
    def __init__(self):
        """Initialize a 7x12 matrix with all slots set to EMPTY (neutral)."""
        self.matrix = [
            [CellPreference.EMPTY for _ in range(SLOTS_PER_DAY)]
            for _ in range(DAYS)
        ]

    def add_preferred(self, slot):
        """
        Mark the given TimeSlot as preferred.
        
        Args:
            slot: TimeSlot object with day and start_time attributes
        """
        day_index = int(slot.day) - 1  # Convert to 0-based index (Sunday=0)
        slot_index = slot.start_time.hour - FIRST_HOUR  # Convert to 0-based hour index
        
        if 0 <= day_index < DAYS and 0 <= slot_index < SLOTS_PER_DAY:
            self.matrix[day_index][slot_index] = CellPreference.PREFERRED

    def set_slot(self, day_index: int, slot_index: int, preference: CellPreference):
        """
        Set preference for a specific slot by indices.
        
        Args:
            day_index: Day index (0-6, Sunday=0)
            slot_index: Hour slot index (0-11, 8:00=0)
            preference: CellPreference enum value
        """
        if 0 <= day_index < DAYS and 0 <= slot_index < SLOTS_PER_DAY:
            self.matrix[day_index][slot_index] = preference

    def get_slot(self, day_index: int, slot_index: int) -> CellPreference:
        """
        Get preference for a specific slot by indices.
        
        Args:
            day_index: Day index (0-6, Sunday=0)
            slot_index: Hour slot index (0-11, 8:00=0)
            
        Returns:
            CellPreference enum value
        """
        if 0 <= day_index < DAYS and 0 <= slot_index < SLOTS_PER_DAY:
            return self.matrix[day_index][slot_index]
        return CellPreference.EMPTY

    def score_schedule(self, schedule) -> int:
        """
        Calculate preference score for a given schedule.
        
        PERCENTAGE-BASED SCORING SYSTEM:
        - Only looks at preferred time slots (ignores neutral/other slots)
        - Score = (filled_preferred_slots / total_preferred_slots) * 100
        - Range: 1-100 (1 if no preferred slots defined, up to 100 if all preferred slots are filled)
        
        Args:
            schedule: Schedule object containing lecture_groups
            
        Returns:
            int: Preference score 1-100 (higher is better)
        """
        # First, count total preferred slots in the matrix
        total_preferred_slots = 0
        for day_row in self.matrix:
            for cell in day_row:
                if cell == CellPreference.PREFERRED:
                    total_preferred_slots += 1
        
        # If no preferred slots are defined, return minimum score
        if total_preferred_slots == 0:
            return 1
        
        # Count how many preferred slots are actually used in the schedule
        filled_preferred_slots = 0
        
        for lg in schedule.lecture_groups:
            for session_group in [lg.lecture, lg.tirguls, lg.maabadas]:
                if not session_group:
                    continue
                
                # Handle both single slots and lists of slots
                slots = session_group if isinstance(session_group, list) else [session_group]
                
                for slot in slots:
                    day_index = int(slot.day) - 1
                    slot_index = slot.start_time.hour - FIRST_HOUR
                    
                    if 0 <= day_index < DAYS and 0 <= slot_index < SLOTS_PER_DAY:
                        # Check if this slot is preferred
                        if self.matrix[day_index][slot_index] == CellPreference.PREFERRED:
                            filled_preferred_slots += 1
        
        # Calculate percentage and ensure it's between 1-100
        percentage = int((filled_preferred_slots / total_preferred_slots) * 100)
        return max(1, min(100, percentage))

    def get_preference_breakdown(self, schedule):
        """
        Get detailed breakdown of preference allocation for display.
        
        Returns:
            dict: Contains preferred slots info and percentage breakdown
        """
        # Count total preferred slots in matrix
        total_preferred_slots = 0
        for day_row in self.matrix:
            for cell in day_row:
                if cell == CellPreference.PREFERRED:
                    total_preferred_slots += 1
        
        # Count filled preferred slots in schedule
        filled_preferred_slots = 0
        total_schedule_slots = 0
        slot_details = []
        
        for lg in schedule.lecture_groups:
            for session_group in [lg.lecture, lg.tirguls, lg.maabadas]:
                if not session_group:
                    continue
                
                slots = session_group if isinstance(session_group, list) else [session_group]
                
                for slot in slots:
                    day_index = int(slot.day) - 1
                    slot_index = slot.start_time.hour - FIRST_HOUR
                    
                    if 0 <= day_index < DAYS and 0 <= slot_index < SLOTS_PER_DAY:
                        total_schedule_slots += 1
                        is_preferred = self.matrix[day_index][slot_index] == CellPreference.PREFERRED
                        if is_preferred:
                            filled_preferred_slots += 1
                        
                        slot_details.append({
                            'day': slot.day,
                            'time': f"{slot.start_time}-{slot.end_time}",
                            'is_preferred': is_preferred,
                            'course': lg.course_name
                        })
        
        # Calculate percentage based only on preferred slots
        percentage = int((filled_preferred_slots / total_preferred_slots) * 100) if total_preferred_slots > 0 else 0
        
        return {
            'filled_preferred_slots': filled_preferred_slots,
            'total_preferred_slots': total_preferred_slots,
            'total_schedule_slots': total_schedule_slots,
            'percentage': percentage,
            'slot_details': slot_details,
            'display_text': f"{filled_preferred_slots}/{total_preferred_slots} preferred slots filled ({percentage}%)"
        }