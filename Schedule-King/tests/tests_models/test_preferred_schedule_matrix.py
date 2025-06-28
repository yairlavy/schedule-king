import pytest
from src.models.time_slot import TimeSlot
from src.models.lecture_group import LectureGroup
from src.models.schedule import Schedule
from src.models.preferred_schedule_matrix import PreferredScheduleMatrix


class TestPreferredScheduleMatrix:
    
    def test_no_preferred_slots_defined(self):
        """Test score when no preferred slots are defined - should return 1"""
        matrix = PreferredScheduleMatrix()
        
        lecture_slot = TimeSlot("1", "08:00", "09:00", "101", "Building A")
        tirgul_slot = TimeSlot("2", "10:00", "11:00", "102", "Building B")
        
        lecture_group = LectureGroup("Math", "MATH101", "Dr. Smith", 
                                   lecture_slot, tirgul_slot, None)
        schedule = Schedule([lecture_group])
        
        score = matrix.score_schedule(schedule)
        assert score == 1, "Should return 1 when no preferred slots are defined"
    
    def test_all_preferred_slots_filled(self):
        """Test 100% score when all preferred slots are filled"""
        matrix = PreferredScheduleMatrix()
        
        # Create 2 preferred slots
        lecture_slot = TimeSlot("1", "08:00", "09:00", "101", "Building A")
        tirgul_slot = TimeSlot("2", "10:00", "11:00", "201", "Building B")
        
        matrix.add_preferred(lecture_slot)
        matrix.add_preferred(tirgul_slot)
        
        lecture_group = LectureGroup("Math", "MATH101", "Dr. Smith", 
                                   lecture_slot, tirgul_slot, None)
        schedule = Schedule([lecture_group])
        
        score = matrix.score_schedule(schedule)
        assert score == 100, "Should return 100% when all preferred slots are filled"
    
    def test_half_preferred_slots_filled(self):
        """Test 50% score when half of preferred slots are filled"""
        matrix = PreferredScheduleMatrix()
        
        # Create 4 preferred slots but only use 2
        preferred1 = TimeSlot("1", "08:00", "09:00", "101", "Building A")
        preferred2 = TimeSlot("1", "09:00", "10:00", "102", "Building A")
        preferred3 = TimeSlot("2", "10:00", "11:00", "201", "Building B")
        preferred4 = TimeSlot("3", "14:00", "15:00", "301", "Building C")
        
        # Mark all 4 as preferred
        matrix.add_preferred(preferred1)
        matrix.add_preferred(preferred2)
        matrix.add_preferred(preferred3)
        matrix.add_preferred(preferred4)
        
        # Only use 2 preferred slots in schedule
        lecture_group = LectureGroup("Physics", "PHYS101", "Dr. Jones", 
                                   preferred1, preferred2, None)
        schedule = Schedule([lecture_group])
        
        score = matrix.score_schedule(schedule)
        assert score == 50, f"Should return 50% when half preferred slots are filled, got {score}"
    
    def test_preferred_and_neutral_slots_mixed(self):
        """Test score ignores neutral slots and only counts preferred"""
        matrix = PreferredScheduleMatrix()
        
        # Create 2 preferred slots
        preferred1 = TimeSlot("1", "08:00", "09:00", "101", "Building A")
        preferred2 = TimeSlot("2", "10:00", "11:00", "201", "Building B")
        
        matrix.add_preferred(preferred1)
        matrix.add_preferred(preferred2)
        
        # Schedule uses 1 preferred + 1 neutral slot
        neutral_slot = TimeSlot("4", "11:00", "12:00", "401", "Building D")
        
        lecture_group = LectureGroup("Chemistry", "CHEM101", "Dr. Brown", 
                                   preferred1, neutral_slot, None)
        schedule = Schedule([lecture_group])
        
        score = matrix.score_schedule(schedule)
        expected = 50  # 1 out of 2 preferred slots = 50%
        assert score == expected, f"Should ignore neutral slots, expected {expected}, got {score}"
    
    def test_no_preferred_slots_in_schedule(self):
        """Test score when schedule has no preferred slots (all neutral)"""
        matrix = PreferredScheduleMatrix()
        
        # Define preferred slots
        preferred1 = TimeSlot("1", "08:00", "09:00", "101", "Building A")
        preferred2 = TimeSlot("2", "10:00", "11:00", "201", "Building B")
        
        matrix.add_preferred(preferred1)
        matrix.add_preferred(preferred2)
        
        # Schedule with only neutral slots
        neutral1 = TimeSlot("3", "12:00", "13:00", "301", "Building C")
        neutral2 = TimeSlot("4", "14:00", "15:00", "401", "Building D")
        
        lecture_group = LectureGroup("Biology", "BIO101", "Dr. Green", 
                                   neutral1, neutral2, None)
        schedule = Schedule([lecture_group])
        
        score = matrix.score_schedule(schedule)
        assert score == 1, "Should return 1 when no preferred slots are filled"
    
    def test_single_preferred_slot(self):
        """Test edge case with only one preferred slot"""
        matrix = PreferredScheduleMatrix()
        
        preferred_slot = TimeSlot("1", "08:00", "09:00", "101", "Building A")
        neutral_slot = TimeSlot("2", "10:00", "11:00", "201", "Building B")
        
        matrix.add_preferred(preferred_slot)
        
        # Schedule that fills the preferred slot
        lecture_group = LectureGroup("Math", "MATH101", "Dr. Smith", 
                                   preferred_slot, neutral_slot, None)
        schedule = Schedule([lecture_group])
        
        score = matrix.score_schedule(schedule)
        assert score == 100, "Should return 100% when single preferred slot is filled"
        
        # Schedule that doesn't fill the preferred slot
        other_neutral = TimeSlot("3", "12:00", "13:00", "301", "Building C")
        lecture_group2 = LectureGroup("Physics", "PHYS101", "Dr. Jones", 
                                    neutral_slot, other_neutral, None)
        schedule2 = Schedule([lecture_group2])
        
        score2 = matrix.score_schedule(schedule2)
        assert score2 == 1, "Should return 1 when single preferred slot is not filled"
    
    def test_complex_multiple_lecture_groups(self):
        """Test with multiple lecture groups and mixed slot types"""
        matrix = PreferredScheduleMatrix()
        
        # Create 4 preferred slots
        pref1 = TimeSlot("1", "08:00", "09:00", "101", "Building A")
        pref2 = TimeSlot("1", "09:00", "10:00", "102", "Building A")
        pref3 = TimeSlot("2", "10:00", "11:00", "201", "Building B")
        pref4 = TimeSlot("3", "14:00", "15:00", "301", "Building C")
        
        matrix.add_preferred(pref1)
        matrix.add_preferred(pref2)
        matrix.add_preferred(pref3)
        matrix.add_preferred(pref4)
        
        # Create neutral slots
        neutral1 = TimeSlot("4", "11:00", "12:00", "401", "Building D")
        neutral2 = TimeSlot("5", "15:00", "16:00", "501", "Building E")
        
        # Course 1: uses 2 preferred slots
        lg1 = LectureGroup("Math", "MATH101", "Dr. Smith", pref1, pref2, None)
        
        # Course 2: uses 1 preferred + 1 neutral
        lg2 = LectureGroup("Physics", "PHYS101", "Dr. Jones", pref3, neutral1, None)
        
        # Course 3: uses only neutral slots
        lg3 = LectureGroup("Chemistry", "CHEM101", "Dr. Brown", neutral2, None, None)
        
        schedule = Schedule([lg1, lg2, lg3])
        
        score = matrix.score_schedule(schedule)
        expected = 75  # 3 out of 4 preferred slots = 75%
        assert score == expected, f"Expected {expected}% for complex schedule, got {score}%"
    
    @pytest.mark.parametrize("preferred_count,filled_count,expected_score", [
        (1, 1, 100),   # 1/1 = 100%
        (2, 1, 50),    # 1/2 = 50%
        (3, 1, 33),    # 1/3 = 33%
        (4, 1, 25),    # 1/4 = 25%
        (5, 2, 40),    # 2/5 = 40%
        (10, 0, 1),    # 0/10 = 0% but minimum is 1
    ])
    def test_percentage_calculations(self, preferred_count, filled_count, expected_score):
        """Test various percentage calculations"""
        matrix = PreferredScheduleMatrix()
        
        # Create preferred slots
        preferred_slots = []
        for i in range(preferred_count):
            day = (i % 5) + 1  # Cycle through days 1-5
            hour = 8 + (i % 10)  # Cycle through hours 8-17
            slot = TimeSlot(str(day), f"{hour:02d}:00", f"{hour+1:02d}:00", f"10{i}", "Building A")
            preferred_slots.append(slot)
            matrix.add_preferred(slot)
        
        # Create neutral slot for cases where we need tirgul/maabada
        neutral_slot = TimeSlot("6", "18:00", "19:00", "999", "Building Z")
        
        if filled_count > 0:
            # Use filled_count preferred slots + neutral for tirgul
            lecture_slot = preferred_slots[0]
            tirgul_slot = preferred_slots[1] if filled_count > 1 else neutral_slot
        else:
            # Use only neutral slots
            lecture_slot = neutral_slot
            tirgul_slot = neutral_slot
        
        lecture_group = LectureGroup("Test", "TEST101", "Dr. Test", 
                                   lecture_slot, tirgul_slot, None)
        schedule = Schedule([lecture_group])
        
        score = matrix.score_schedule(schedule)
        assert score == expected_score, f"Expected {expected_score}% for {filled_count}/{preferred_count}, got {score}%"
    
    def test_tirguls_and_maabadas_support(self):
        """Test that tirguls and maabadas are properly counted"""
        matrix = PreferredScheduleMatrix()
        
        # Create preferred slots
        lecture_pref = TimeSlot("1", "08:00", "09:00", "101", "Building A")
        tirgul_pref = TimeSlot("2", "10:00", "11:00", "201", "Building B")
        maabada_pref = TimeSlot("3", "12:00", "13:00", "301", "Building C")
        
        matrix.add_preferred(lecture_pref)
        matrix.add_preferred(tirgul_pref)
        matrix.add_preferred(maabada_pref)
        
        # Create schedule using all preferred slots
        lecture_group = LectureGroup("Advanced Math", "MATH301", "Dr. Expert",
                                   lecture_pref, tirgul_pref, maabada_pref)
        schedule = Schedule([lecture_group])
        
        score = matrix.score_schedule(schedule)
        assert score == 100, "Should return 100% when all lecture, tirgul, and maabada slots are preferred"


def test_integration_with_schedule_object():
    """Integration test to ensure it works with the actual Schedule class"""
    matrix = PreferredScheduleMatrix()
    
    # Set up preferred slots
    lecture_pref = TimeSlot("1", "08:00", "09:00", "101", "Building A")
    tirgul_neutral = TimeSlot("2", "10:00", "11:00", "201", "Building B")
    
    matrix.add_preferred(lecture_pref)
    
    # Create schedule
    lecture_group = LectureGroup("Math", "MATH101", "Dr. Smith", lecture_pref, tirgul_neutral, None)
    schedule = Schedule([lecture_group])
    
    # Test that compute_preference_score works
    score = schedule.compute_preference_score(matrix)
    assert score == 100, "Integration test failed - should be 100% with 1/1 preferred"
    
    # Test that the score can be stored
    schedule.preference_score = score
    assert schedule.preference_score == 100, "Score storage failed"