import os
import pytest
from src.services.excel_parser import ExcelParser
from src.models.course import Course
from src.models.time_slot import TimeSlot
from datetime import time

# ---------------- Fixtures ----------------

@pytest.fixture
def test_files_dir():
    # Go up one directory from the current file's directory (test_services)
    # then join with 'excel_tests_files'
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'excel_tests_files')

@pytest.fixture
def simple_courses_path(test_files_dir):
    return os.path.join(test_files_dir, 'simple_courses.xlsx')

@pytest.fixture
def five_courses_path(test_files_dir):
    return os.path.join(test_files_dir, '5courses.xlsx')

@pytest.fixture
def seven_courses_path(test_files_dir):
    return os.path.join(test_files_dir, '7courses.xlsx')

@pytest.fixture
def engineering_path(test_files_dir):
    return os.path.join(test_files_dir, 'EngineeringV2.xlsx')

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
    
    # Verify basic structure
    assert isinstance(courses, list)
    assert all(isinstance(course, Course) for course in courses)
    
    # Find and verify a specific course
    discrete_math = next((c for c in courses if c.course_code == '80001'), None)
    assert discrete_math is not None
    assert discrete_math.name == 'מתמטיקה בדידה'
    assert discrete_math.instructor == 'מר יוסי גולד'

# EXCELPARSER_FUNC_003
def test_course_counts(five_courses_path, seven_courses_path):
    """Test course count validation"""
    # Test 5 courses file
    parser = ExcelParser(five_courses_path)
    courses = parser.parse()
    assert len(courses) == 4
    
    # Test 7 courses file
    parser = ExcelParser(seven_courses_path)
    courses = parser.parse()
    assert len(courses) == 8 

# EXCELPARSER_VALID_001
def test_course_data_validation(simple_courses_path):
    """Test course data format and content validation"""
    parser = ExcelParser(simple_courses_path)
    courses = parser.parse()
    
    for course in courses:
        # Course code validation
        assert course.course_code.isdigit() and len(course.course_code) == 5
        
        # Course name validation
        assert course.name and any('\u0590' <= char <= '\u05FF' for char in course.name)
        
        # Instructor validation
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
            # Time format validation
            assert isinstance(time_slot.start_time, time)
            assert isinstance(time_slot.end_time, time)
            assert 0 <= time_slot.start_time.hour <= 23
            assert 0 <= time_slot.end_time.hour <= 23
            assert 0 <= time_slot.start_time.minute <= 59
            assert 0 <= time_slot.end_time.minute <= 59
            
            # Time consistency
            assert time_slot.end_time > time_slot.start_time
            duration = (time_slot.end_time.hour - time_slot.start_time.hour) + \
                      (time_slot.end_time.minute - time_slot.start_time.minute) / 60
            assert 1 <= duration <= 4
            
            # Building and room validation
            assert time_slot.building
            assert time_slot.room and time_slot.room.replace('-', '').isalnum()
            
            # Day validation
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
        
        # Check meeting distribution
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