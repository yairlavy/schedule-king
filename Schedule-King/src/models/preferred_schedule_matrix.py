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
        
        Scoring system (assuming forbidden slots are handled by conflict checking):
        - +5 points for each preferred time slot used
        - +1 point for each neutral time slot used (basic bonus)
        - +2 bonus points for each "clean" day (all slots are neutral)
        - +3 bonus points for each "ideal" day (has at least one preferred slot)
        
        Args:
            schedule: Schedule object containing lecture_groups
            
        Returns:
            int: Preference score (higher is better)
        """
        score = 0
        used_slots_per_day = [[] for _ in range(DAYS)]
        
        # Collect all used time slots grouped by day
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
                        used_slots_per_day[day_index].append(slot_index)
                        
                        preference = self.matrix[day_index][slot_index]
                        
                        if preference == CellPreference.PREFERRED:
                            score += 5  # High bonus for preferred slots
                        else:  # EMPTY (forbidden slots won't reach here due to conflict checking)
                            score += 1  # Basic bonus for neutral slots
        
        # Day-level bonuses
        for day_index in range(DAYS):
            if used_slots_per_day[day_index]:  # Day has scheduled classes
                day_preferences = [
                    self.matrix[day_index][slot] 
                    for slot in used_slots_per_day[day_index]
                ]
                
                # Bonus for "clean" day - all slots are neutral
                if all(pref == CellPreference.EMPTY for pref in day_preferences):
                    score += 2  # Clean day bonus
                
                # Bonus for "ideal" day - has at least one preferred slot
                elif any(pref == CellPreference.PREFERRED for pref in day_preferences):
                    score += 3  # Ideal day bonus
        
        return score
