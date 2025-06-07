import os
import pytest
import time as time_module  # Rename to avoid conflict with datetime.time
from src.services.excel_parser import ExcelParser
from src.models.course import Course
from src.models.time_slot import TimeSlot
from datetime import time

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
    discrete_math = next((c for c in courses if c.course_code == '80001'), None)
    assert discrete_math is not None
    assert discrete_math.name == 'מתמטיקה בדידה'
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

# EXCELPARSER_VALID_005
def test_four_lec_six_tirg_validation(four_lec_six_tirg_path):
    """Test validation of 4 lectures 6 tirgulim file"""
    parser = ExcelParser(four_lec_six_tirg_path)
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
        
        # Validate that course has at least one meeting
        total_meetings = len(course.lectures) + len(course.tirguls) + len(course.maabadas)
        assert total_meetings > 0, f"Course {course.course_code} should have at least one meeting"
        
        # For this specific test file, all courses should have both lectures and tirguls
        assert len(course.lectures) > 0, f"Course {course.course_code} should have lectures"
        assert len(course.tirguls) > 0, f"Course {course.course_code} should have tirguls"
        
        # Verify that we have the expected number of meetings for known courses
        if course.course_code == '90000':
            assert len(course.lectures) == 4, "Course 90000 should have 4 lectures"
            assert len(course.tirguls) == 6, "Course 90000 should have 6 tirguls"
            # This course should have overlapping days
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
            assert overlapping_days, "Course 90000 should have overlapping lecture and tirgul days"
            
        elif course.course_code == '90001':
            assert len(course.lectures) > 0, "Course 90001 should have lectures"
            assert len(course.tirguls) > 0, "Course 90001 should have tirguls"
            # This course should have overlapping days
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
            assert overlapping_days, "Course 90001 should have overlapping lecture and tirgul days"
            
        elif course.course_code == '90002':
            assert len(course.lectures) > 0, "Course 90002 should have lectures"
            assert len(course.tirguls) > 0, "Course 90002 should have tirguls"
            # This course should NOT have overlapping days
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
            assert not overlapping_days, "Course 90002 should not have overlapping lecture and tirgul days"