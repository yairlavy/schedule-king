import pytest
from datetime import datetime  
from src.data.models.time_slot import TimeSlot

def test_timeslot_init():
    #TIMESLOT_INIT_001
    #day, start time, end time, room, and building (strings)
    ts = TimeSlot("1", "09:00", "10:00", "101", "22")
    assert ts.day == "1"
    assert ts.start_time == datetime.strptime("09:00", "%H:%M").time()
    assert ts.end_time == datetime.strptime("10:00", "%H:%M").time()
    assert ts.room == "101"
    assert ts.building == "22"

@pytest.fixture
def time_slots():
    return {
        "slot1": TimeSlot("1", "09:00", "10:00", "101", "22"),
        "slot2": TimeSlot("1", "09:30", "10:30", "102", "22"),
        "slot3": TimeSlot("2", "9:00", "10:00", "103", "22"),
        "slot4": TimeSlot("2", "13:00", "15:30", "104", "42"),
    }

#TIMESLOT_COMP_001
def test_conflicts_with(time_slots):
    result1 = time_slots["slot1"].conflicts_with(time_slots["slot2"])
    result2 = time_slots["slot1"].conflicts_with(time_slots["slot3"])
    result3 = time_slots["slot1"].conflicts_with(time_slots["slot4"])
    
    print(f"\nslot1 conflict with slot2: {result1}")
    print(f"slot1 conflict with slot3: {result2}")
    print(f"slot1 conflict with slot4: {result3}")
    
    assert result1  # True because they overlap
    assert not result2  # False because they different days
    assert not result3  # False because they different days and times

#TIMESLOT_REPR_001
def test_str_representation(time_slots):
    expected = "S,1,09:00:00,10:00:00,101,22"
    assert str(time_slots["slot1"]) == expected

#TIMESLOT_FUNC_DUR_001
def test_duration_calculate(time_slots):
    assert time_slots["slot1"].duration() == 60
    assert time_slots["slot4"].duration() == 150

#TIMESLOT_NEG_INIT_001
#TIMESLOT_VALID_001
# Test cases for the validate method
def test_validate_invalid_day():
    ts = TimeSlot("7", "09:00", "10:00", "101", "22")
    with pytest.raises(ValueError, match="Invalid day"):
        ts.validate()

def test_validate_invalid_time_format():
    ts = TimeSlot("2", "9:00", "10:00", "101", "22")
    ts._start_time = "900"
    with pytest.raises(ValueError, match="Invalid time format"):
        ts.validate()

def test_validate_start_time_equals_end_time():
    ts = TimeSlot("1", "09:00", "09:00", "101", "22")
    with pytest.raises(ValueError, match="Start time must be before end time"):
        ts.validate()

def test_validate_start_time_after_end_time():
    ts = TimeSlot("1", "10:00", "09:00", "101", "22")
    with pytest.raises(ValueError, match="Start time must be before end time"):
        ts.validate()

def test_validate_building_not_string():
    ts = TimeSlot("1", "09:00", "10:00", "101", "22")
    ts._building = 22  # Set building to an integer instead of string
    with pytest.raises(ValueError, match="Invalid room or building format"):
        ts.validate()

def test_validate_room_not_string():
    ts = TimeSlot("1", "09:00", "10:00", "101", "22")
    ts._room = 22  # Set room to an integer instead of string
    with pytest.raises(ValueError, match="Invalid room or building format"):
        ts.validate()

def test_validate_empty_room():
    ts = TimeSlot("1", "09:00", "10:00", "", "22")
    with pytest.raises(ValueError, match="Room and building cannot be empty"):
        ts.validate()

def test_validate_empty_building():
    ts = TimeSlot("1", "09:00", "10:00", "101", "")
    with pytest.raises(ValueError, match="Room and building cannot be empty"):
        ts.validate()

def test_validate_non_alphanumeric_room():
    ts = TimeSlot("1", "09:00", "10:00", "101!", "22")
    with pytest.raises(ValueError, match="Room and building must be alphanumeric"):
        ts.validate()

def test_validate_non_alphanumeric_building():
    ts = TimeSlot("1", "09:00", "10:00", "101", "22#")
    with pytest.raises(ValueError, match="Room and building must be alphanumeric"):
        ts.validate()
