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
    
    This class is flexible and supports both single TimeSlot and list formats.
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

    def _extract_slots_from_session(self, session_group):
        """
        Helper method to extract TimeSlot objects from a session.
        Handles both single TimeSlot objects and lists of TimeSlots.
        
        Args:
            session_group: Either a TimeSlot, list of TimeSlots, or None
            
        Returns:
            list: List of TimeSlot objects
        """
        if not session_group:
            return []
        
        # If it's a list, return it as is
        if isinstance(session_group, list):
            return session_group
        
        # If it's a single TimeSlot, wrap it in a list
        return [session_group]

    def _get_all_slots_from_lecture_group(self, lg):
        """
        Extract all TimeSlot objects from a LectureGroup.
        This function adapts to the actual structure used in all_strategy.py
        
        Args:
            lg: LectureGroup object
            
        Returns:
            list: List of TimeSlot objects
        """
        all_slots = []
        
        # Based on all_strategy.py, the LectureGroup is created with:
        # lecture=lecture (which comes from course.lectures - a list)
        # tirguls=tirgul (which comes from course.tirguls - a list) 
        # maabadas=maabada (which comes from course.maabadas - a list)
        
        # So lg.lecture, lg.tirguls, lg.maabadas are actually lists of TimeSlot
        
        # Extract from lecture (expecting a list)
        if lg.lecture:
            if isinstance(lg.lecture, list):
                all_slots.extend(lg.lecture)
            else:
                # Fallback: if it's a single TimeSlot, add it
                all_slots.append(lg.lecture)
        
        # Extract from tirguls (expecting a list)
        if lg.tirguls:
            if isinstance(lg.tirguls, list):
                all_slots.extend(lg.tirguls)
            else:
                # Fallback: if it's a single TimeSlot, add it
                all_slots.append(lg.tirguls)
        
        # Extract from maabadas (expecting a list)
        if lg.maabadas:
            if isinstance(lg.maabadas, list):
                all_slots.extend(lg.maabadas)
            else:
                # Fallback: if it's a single TimeSlot, add it
                all_slots.append(lg.maabadas)
        
        return all_slots

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
        
        # Track which preferred slots are actually used (avoid double counting)
        filled_preferred_positions = set()
        
        for lg in schedule.lecture_groups:
            # Extract all TimeSlot objects from this LectureGroup
            all_slots = self._get_all_slots_from_lecture_group(lg)
            
            # Process each slot and check if it covers any preferred time slots
            for slot in all_slots:
                try:
                    day_index = int(slot.day) - 1
                    
                    # Calculate the range of hour slots this TimeSlot covers
                    start_hour = slot.start_time.hour
                    end_hour = slot.end_time.hour
                    
                    # If the slot crosses into the next hour (e.g., 10:30-11:30), include both hours
                    if slot.end_time.minute > 0:
                        end_hour += 1
                    
                    # Mark all hour slots that this TimeSlot covers
                    for hour in range(start_hour, end_hour):
                        slot_index = hour - FIRST_HOUR
                        
                        if 0 <= day_index < DAYS and 0 <= slot_index < SLOTS_PER_DAY:
                            # Check if this hour slot is preferred
                            if self.matrix[day_index][slot_index] == CellPreference.PREFERRED:
                                # Add position to set (automatically handles duplicates)
                                filled_preferred_positions.add((day_index, slot_index))
                except (AttributeError, IndexError):
                    # Handle cases where slot.day or slot.start_time is not properly defined
                    continue
        
        # Count unique preferred slots that are filled
        filled_preferred_slots = len(filled_preferred_positions)
        
        # Calculate percentage and ensure it's between 1-100
        percentage = int((filled_preferred_slots / total_preferred_slots) * 100)
        return max(1, min(100, percentage))