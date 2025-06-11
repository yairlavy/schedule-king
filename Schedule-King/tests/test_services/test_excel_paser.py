import os
import pytest
import time as time_module  # Rename to avoid conflict with datetime.time
from src.services.excel_parser import ExcelParser
from src.models.course import Course
from src.models.time_slot import TimeSlot
from datetime import time
from src.services.logger import Logger
import pandas as pd
import re

# ---------------- Fixtures ----------------

@pytest.fixture
def test_files_dir():
    # Returns the path to the directory containing test Excel files
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'excel_tests_files')

@pytest.fixture
def simple_courses_path(test_files_dir):
    # Path to a simple test Excel file with a few courses
    return os.path.join(test_files_dir, 'simple_courses.xlsx')

@pytest.fixture
def five_courses_path(test_files_dir):
    # Path to a test Excel file with 5 courses
    return os.path.join(test_files_dir, '5courses.xlsx')

@pytest.fixture
def seven_courses_path(test_files_dir):
    # Path to a test Excel file with 7 courses
    return os.path.join(test_files_dir, '7courses.xlsx')

@pytest.fixture
def engineering_path(test_files_dir):
    # Path to a test Excel file for engineering courses
    return os.path.join(test_files_dir, 'EngineeringV2.xlsx')

@pytest.fixture
def enhanced_100_path(test_files_dir):
    # Path to a test Excel file with 100+ courses for performance testing
    return os.path.join(test_files_dir, 'test_courses_enhanced_100.xlsx')

@pytest.fixture
def four_lec_six_tirg_path(test_files_dir):
    # Path to a test Excel file with 4 lectures and 6 tirgulim for a course
    return os.path.join(test_files_dir, 'test_courses_4lectures_6tirgulim.xlsx')

@pytest.fixture
def conflict_courses_path(test_files_dir):
    # Path to a test Excel file with room conflicts
    return os.path.join(test_files_dir, 'conflict_courses.xlsx')

# ---------------- Tests ----------------

# EXCELPARSER_FUNC_001
def test_file_not_found():
    """Test that FileNotFoundError is raised for non-existent file"""
    with pytest.raises(FileNotFoundError):
        ExcelParser("nonexistent_file.xlsx")

# EXCELPARSER_FUNC_002
def test_basic_parsing(simple_courses_path):
    """Test basic parsing functionality"""
    parser = ExcelParser(simple_courses_path)
    courses = parser.parse()
    
    # Verify the returned object is a list of Course instances
    assert isinstance(courses, list)
    assert all(isinstance(course, Course) for course in courses)
    
    # Find and verify a specific course's details
    # Find the course with code '80001' (Discrete Mathematics)
    discrete_math = next((c for c in courses if c.course_code == '80001'), None)
    # Ensure the course exists in the parsed results
    assert discrete_math is not None
    # Check that the course name matches the expected Hebrew name
    assert discrete_math.name == 'מתמטיקה בדידה'
    # Check that the instructor matches the expected value
    assert discrete_math.instructor == 'מר יוסי גולד'

# EXCELPARSER_FUNC_003
def test_course_counts(five_courses_path, seven_courses_path):
    """Test course count validation"""
    # Test 5 courses file (should parse 4 courses)
    parser = ExcelParser(five_courses_path)
    courses = parser.parse()
    assert len(courses) == 4
    
    # Test 7 courses file (should parse 8 courses)
    parser = ExcelParser(seven_courses_path)
    courses = parser.parse()
    assert len(courses) == 8 

# EXCELPARSER_VALID_001
def test_course_data_validation(simple_courses_path):
    """Test course data format and content validation"""
    parser = ExcelParser(simple_courses_path)
    courses = parser.parse()
    
    for course in courses:
        # Course code should be 5 digits
        assert course.course_code.isdigit() and len(course.course_code) == 5
        
        # Course name should contain Hebrew characters
        assert course.name and any('\u0590' <= char <= '\u05FF' for char in course.name)
        
        # Instructor should have a valid prefix
        assert course.instructor and any(
            course.instructor.startswith(prefix) 
            for prefix in ['ד"ר', 'פרופ', 'מר', 'גב']
        )

# EXCELPARSER_VALID_002
def test_time_slot_validation(simple_courses_path):
    """Test time slot format and consistency"""
    parser = ExcelParser(simple_courses_path)
    courses = parser.parse()
    
    for course in courses:
        # Flatten nested lists of time slots
        all_time_slots = []
        for slot in course.lectures + course.tirguls + course.maabadas:
            if isinstance(slot, list):
                all_time_slots.extend(slot)
            else:
                all_time_slots.append(slot)
        
        for time_slot in all_time_slots:
            # Time fields should be datetime.time objects and valid
            assert isinstance(time_slot.start_time, time)
            assert isinstance(time_slot.end_time, time)
            assert 0 <= time_slot.start_time.hour <= 23
            assert 0 <= time_slot.end_time.hour <= 23
            assert 0 <= time_slot.start_time.minute <= 59
            assert 0 <= time_slot.end_time.minute <= 59
            
            # End time should be after start time, duration between 1 and 4 hours
            assert time_slot.end_time > time_slot.start_time
            duration = (time_slot.end_time.hour - time_slot.start_time.hour) + \
                      (time_slot.end_time.minute - time_slot.start_time.minute) / 60
            assert 1 <= duration <= 4
            
            # Building and room should be non-empty and room should be alphanumeric (with optional '-')
            assert time_slot.building
            assert time_slot.room and time_slot.room.replace('-', '').isalnum()
            
            # Day should be between 1 and 7
            assert 1 <= int(time_slot.day) <= 7

# EXCELPARSER_VALID_003
def test_meeting_distribution(simple_courses_path):
    """Test meeting type distribution and scheduling"""
    parser = ExcelParser(simple_courses_path)
    courses = parser.parse()
    
    for course in courses:
        # Print course details for debugging
        print(f"\nCourse: {course.course_code} - {course.name}")
        print(f"Meetings: L={len(course.lectures)}, T={len(course.tirguls)}, M={len(course.maabadas)}")
        
        # Check that course has at least one meeting
        total_meetings = len(course.lectures) + len(course.tirguls) + len(course.maabadas)
        if total_meetings == 0:
            print(f"WARNING: Course {course.course_code} has no meetings!")
            continue
        
        # Check for overlapping days between lectures and tirguls
        if len(course.lectures) > 0 and len(course.tirguls) > 0:
            lecture_days = set()
            for ts in course.lectures:
                if isinstance(ts, list):
                    lecture_days.update(t.day for t in ts)
                else:
                    lecture_days.add(ts.day)
                    
            tirgul_days = set()
            for ts in course.tirguls:
                if isinstance(ts, list):
                    tirgul_days.update(t.day for t in ts)
                else:
                    tirgul_days.add(ts.day)
                    
            overlapping_days = lecture_days & tirgul_days
            if overlapping_days:
                print(f"WARNING: Course {course.course_code} has overlapping days: {overlapping_days}")
            assert not overlapping_days, f"Course {course.course_code} has overlapping lecture and tirgul days"

# EXCELPARSER_PERF_001
def test_parsing_performance(enhanced_100_path, four_lec_six_tirg_path):
    """Test parsing performance for large files"""
    # Test enhanced 100 courses file
    start_time = time_module.time()
    parser = ExcelParser(enhanced_100_path)
    courses = parser.parse()
    end_time = time_module.time()
    # Parsing should complete in under 5 seconds
    assert end_time - start_time < 5, f"Parsing took {end_time - start_time:.2f} seconds, expected under 5 seconds"
    assert len(courses) > 0, "Should parse at least one course"

    # Test 4 lectures 6 tirgulim file
    start_time = time_module.time()
    parser = ExcelParser(four_lec_six_tirg_path)
    courses = parser.parse()
    end_time = time_module.time()
    # Parsing should complete in under 5 seconds
    assert end_time - start_time < 5, f"Parsing took {end_time - start_time:.2f} seconds, expected under 5 seconds"
    assert len(courses) > 0, "Should parse at least one course"

# EXCELPARSER_VALID_004
def test_enhanced_100_validation(enhanced_100_path):
    """Test validation of enhanced 100 courses file"""
    parser = ExcelParser(enhanced_100_path)
    courses = parser.parse()
    
    # Basic structure validation
    assert isinstance(courses, list)
    assert all(isinstance(course, Course) for course in courses)
    
    # Course count validation
    assert len(courses) > 0, "Should parse at least one course"
    
    # Validate each course's code, name, and instructor
    for course in courses:
        assert course.course_code.isdigit() and len(course.course_code) == 5
        assert course.name and any('\u0590' <= char <= '\u05FF' for char in course.name)
        # Accept instructor names with or without prefix, but must contain Hebrew
        assert course.instructor and any(
            course.instructor.startswith(prefix) or 
            any('\u0590' <= char <= '\u05FF' for char in course.instructor)
            for prefix in ['ד"ר', 'פרופ', 'מר', 'גב']
        )
        

# EXCELPARSER_VALID_006
def test_room_conflict_detection(conflict_courses_path):
    """Test detection of room conflicts between courses"""
    parser = ExcelParser(conflict_courses_path)
    
    # Clear any existing room assignments
    parser.times_rooms = {}
    
    # Test Case 1: Basic Room Assignment
    ts1 = TimeSlot(day='1', start_time='10:00', end_time='12:00', room='101', building='A')
    assert parser.check_room_validity('101', 'A', ts1, 'C1') is True, "Should allow first room assignment"
    
    # Test Case 2: Same Room Different Day
    ts2 = TimeSlot(day='2', start_time='10:00', end_time='12:00', room='101', building='A')
    assert parser.check_room_validity('101', 'A', ts2, 'C2') is True, "Should allow same room on different day"
    
    # Test Case 3: Same Room Same Day Non-Overlapping
    ts3 = TimeSlot(day='1', start_time='13:00', end_time='15:00', room='101', building='A')
    assert parser.check_room_validity('101', 'A', ts3, 'C3') is True, "Should allow same room on same day if times don't overlap"
    
    # Test Case 4: Same Room Same Day Overlapping
    ts4 = TimeSlot(day='1', start_time='11:00', end_time='13:00', room='101', building='A')
    assert parser.check_room_validity('101', 'A', ts4, 'C4') is False, "Should detect conflict for overlapping times"
    
    # Test Case 5: Different Room Same Building
    ts5 = TimeSlot(day='1', start_time='10:00', end_time='12:00', room='102', building='A')
    assert parser.check_room_validity('102', 'A', ts5, 'C5') is True, "Should allow different room in same building"
    
    # Test Case 6: Same Room Different Building
    ts6 = TimeSlot(day='1', start_time='10:00', end_time='12:00', room='101', building='B')
    assert parser.check_room_validity('101', 'B', ts6, 'C6') is True, "Should allow same room number in different building"
    
    # Test Case 7: Edge Case - Exact Time Match
    ts7 = TimeSlot(day='1', start_time='10:00', end_time='12:00', room='101', building='A')
    assert parser.check_room_validity('101', 'A', ts7, 'C7') is False, "Should detect conflict for exact time match"
    
    # Test Case 8: Edge Case - Partial Overlap Start
    ts8 = TimeSlot(day='1', start_time='09:00', end_time='11:00', room='101', building='A')
    assert parser.check_room_validity('101', 'A', ts8, 'C8') is False, "Should detect conflict for partial overlap at start"
    
    # Test Case 9: Edge Case - Partial Overlap End
    ts9 = TimeSlot(day='1', start_time='11:00', end_time='14:00', room='101', building='A')
    assert parser.check_room_validity('101', 'A', ts9, 'C9') is False, "Should detect conflict for partial overlap at end"
    
    # Verify conflict logging
    assert "Conflict detected" in Logger.inner_conflict, "Should log conflict messages"
    
    # Print conflict log for debugging
    print("\nConflict Log:")
    print(Logger.inner_conflict)
    
    # Verify room assignments were tracked correctly
    assert len(parser.times_rooms) == 3, "Should track rooms in 3 different locations (A-101, A-102, B-101)"
    assert len(parser.times_rooms[('101', 'A')]) == 3, "Should have 3 time slots for room A-101"
    assert len(parser.times_rooms[('102', 'A')]) == 1, "Should have 1 time slot for room A-102"
    assert len(parser.times_rooms[('101', 'B')]) == 1, "Should have 1 time slot for room B-101"

# EXCELPARSER_VALID_007
def test_parse_row_validation(simple_courses_path):
    """Test validation of row parsing functionality"""
    parser = ExcelParser(simple_courses_path)
    
    # Test Case 1: Valid row with all fields
    valid_row = pd.Series({
        'קוד מלא': '80001-1',
        'שם': 'מתמטיקה בדידה',
        'סוג מפגש': 'הרצאה',
        'מועד': 'א\'10:00-12:00',
        'מרצים': 'ד"ר יוסי כהן',
        'חדר': 'הנדסה-1104-4',
        'תקופה': 'א'
    })
    result = parser._parse_row(0, valid_row)
    assert len(result) > 0, "Should parse valid row successfully"
    course_code, course_name, instructor, meeting_type, time_slots = result[0]
    assert course_code == '80001'
    assert course_name == 'מתמטיקה בדידה'
    assert instructor == 'ד"ר יוסי כהן'
    assert meeting_type == 'הרצאה'
    assert len(time_slots) == 1
    
    # Test Case 2: Invalid course code format
    invalid_code_row = valid_row.copy()
    invalid_code_row['קוד מלא'] = 'invalid'
    result = parser._parse_row(0, invalid_code_row)
    assert len(result) == 0, "Should reject invalid course code format"
    
    # Test Case 3: Invalid meeting type
    invalid_meeting_row = valid_row.copy()
    invalid_meeting_row['סוג מפגש'] = 'invalid'
    result = parser._parse_row(0, invalid_meeting_row)
    assert len(result) == 0, "Should reject invalid meeting type"
    
    # Test Case 4: Invalid semester
    invalid_semester_row = valid_row.copy()
    invalid_semester_row['תקופה'] = 'ב'
    result = parser._parse_row(0, invalid_semester_row)
    assert len(result) == 0, "Should reject non-first semester courses"
    
    # Test Case 5: Multiple time slots
    multi_time_row = valid_row.copy()
    multi_time_row['מועד'] = 'א\'10:00-12:00\nב\'14:00-16:00'
    result = parser._parse_row(0, multi_time_row)
    assert len(result) == 2, f"Should parse multiple time slots into separate entries, got {len(result)}"
    assert len(result[0][4]) == 1, f"First entry should have one time slot, got {len(result[0][4])}"
    assert len(result[1][4]) == 1, f"Second entry should have one time slot, got {len(result[1][4])}"

# EXCELPARSER_VALID_008
def test_room_building_parsing(simple_courses_path):
    """Test parsing of room and building information"""
    parser = ExcelParser(simple_courses_path)

    # Test Case 1: Standard format
    building, room = parser._parse_room_building(0, "הנדסה-1104-4")
    assert building == "הנדסה", f"Expected building 'הנדסה', got '{building}'"
    assert room == "1104-4", f"Expected room '1104-4', got '{room}'"

    # Test Case 2: Simple format
    building, room = parser._parse_room_building(0, "וואהל-11")
    assert building == "וואהל", f"Expected building 'וואהל', got '{building}'"
    assert room == "11", f"Expected room '11', got '{room}'"

    # Test Case 3: Space-separated format
    building, room = parser._parse_room_building(0, "בניין - חדר")
    assert building == "בניין", f"Expected building 'בניין', got '{building}'"
    assert room == "חדר", f"Expected room 'חדר', got '{room}'"

    # Test Case 4: Empty string
    building, room = parser._parse_room_building(0, "")
    assert building is None, f"Expected None for building, got '{building}'"
    assert room is None, f"Expected None for room, got '{room}'"

    # Test Case 5: Invalid format
    building, room = parser._parse_room_building(0, "invalid-format")
    assert building == "invalid", f"Expected building 'invalid', got '{building}'"
    assert room == "format", f"Expected room 'format', got '{room}'"

# EXCELPARSER_VALID_009
def test_four_lec_six_tirg_content(four_lec_six_tirg_path):
    """Test parsing of a course with 4 lectures and 6 tirgulim"""
    # Parse the Excel file with 4 lectures and 6 tirgulim for a single course
    parser = ExcelParser(four_lec_six_tirg_path)
    courses = parser.parse()

    # Find the target course with code 90000 (מודלים חישוביים 5)
    target_course = next((c for c in courses if c.course_code == "90000"), None)
    assert target_course is not None, "Target course with code 90000 not found"

    # Print all lectures for debugging
    print("\nAll lectures for course 90000:")
    for i, lecture in enumerate(target_course.lectures):
        if isinstance(lecture, list):
            for ts in lecture:
                print(f"Lecture {i}: day={ts.day}, start={ts.start_time.strftime('%H:%M')}, end={ts.end_time.strftime('%H:%M')}, room={ts.room}")
        else:
            print(f"Lecture {i}: day={lecture.day}, start={lecture.start_time.strftime('%H:%M')}, end={lecture.end_time.strftime('%H:%M')}, room={lecture.room}")

    # Expected course details
    expected_name = "מודלים חישוביים 5"
    assert target_course.name == expected_name, f"Expected name '{expected_name}', got '{target_course.name}'"

    # Verify the number of lectures and tirgulim
    assert len(target_course.lectures) == 4, f"Expected 4 lectures, got {len(target_course.lectures)}"
    assert len(target_course.tirguls) == 6, f"Expected 6 tirgulim, got {len(target_course.tirguls)}"

    # Define the expected meetings as per the Excel file, using day numbers as strings
    expected_meetings = [
        # Lectures
        {"type": "הרצאה", "day": "4", "start": "10:00", "end": "12:00"},
        {"type": "הרצאה", "day": "5", "start": "12:00", "end": "14:00"},
        {"type": "הרצאה", "day": "2", "start": "14:00", "end": "16:00"},
        {"type": "הרצאה", "day": "4", "start": "08:00", "end": "10:00"},

        # Tirgulim
        {"type": "תרגול", "day": "2", "start": "08:00", "end": "10:00"},
        {"type": "תרגול", "day": "5", "start": "08:00", "end": "10:00"},
        {"type": "תרגול", "day": "4", "start": "12:00", "end": "14:00"},
        {"type": "תרגול", "day": "1", "start": "10:00", "end": "12:00"},
        {"type": "תרגול", "day": "1", "start": "08:00", "end": "10:00"},
        {"type": "תרגול", "day": "5", "start": "10:00", "end": "12:00"},
    ]

    # Check that each expected meeting exists in the parsed meetings
    for expected in expected_meetings:
        # Find the appropriate list based on meeting type
        meetings = target_course.lectures if expected["type"] == "הרצאה" else target_course.tirguls
        # Find matching meeting
        match = None
        for meeting in meetings:
            if isinstance(meeting, list):
                for ts in meeting:
                    if (ts.day == expected["day"] and
                        ts.start_time.strftime("%H:%M") == expected["start"] and
                        ts.end_time.strftime("%H:%M") == expected["end"]):
                        match = ts
                        break
            else:
                if (meeting.day == expected["day"] and
                    meeting.start_time.strftime("%H:%M") == expected["start"] and
                    meeting.end_time.strftime("%H:%M") == expected["end"]):
                    match = meeting
                    break
        assert match is not None, f"Missing meeting: {expected}"
