import pytest
from datetime import datetime, time
from src.models.schedule import Schedule
from src.models.schedule_ranker import ScheduleRanker
from src.models.Preference import Preference, Metric
from src.models.lecture_group import LectureGroup
from src.models.time_slot import TimeSlot

"""
This test suite verifies the functionality of the ScheduleRanker class.
The ScheduleRanker is responsible for:
1. Storing and managing multiple schedules
2. Ranking schedules based on different metrics (active days, gaps, times)
3. Supporting both ascending and descending order for each metric
4. Providing efficient batch operations and range queries
"""

def create_time_slot(day: str, start_hour: int, start_minute: int, end_hour: int, end_minute: int) -> TimeSlot:
    """
    Creates a TimeSlot object with the specified day and times.
    """
    start_time = time(start_hour, start_minute)
    end_time = time(end_hour, end_minute)
    return TimeSlot(day, start_time, end_time)

def create_lecture_group(
    course_code: str,
    course_name: str,
    instructor: str,
    lecture_day: str,
    lecture_start: tuple[int, int],
    lecture_end: tuple[int, int],
    tirgul_day: str = None,
    tirgul_start: tuple[int, int] = None,
    tirgul_end: tuple[int, int] = None,
    maabada_day: str = None,
    maabada_start: tuple[int, int] = None,
    maabada_end: tuple[int, int] = None
) -> LectureGroup:
    """
    Creates a LectureGroup with the specified course details and time slots.
    """
    lecture = create_time_slot(lecture_day, *lecture_start, *lecture_end)
    
    tirgul = None
    if tirgul_day and tirgul_start and tirgul_end:
        tirgul = create_time_slot(tirgul_day, *tirgul_start, *tirgul_end)
    
    maabada = None
    if maabada_day and maabada_start and maabada_end:
        maabada = create_time_slot(maabada_day, *maabada_start, *maabada_end)
    
    return LectureGroup(course_name, course_code, instructor, lecture, tirgul, maabada)

@pytest.fixture
def sample_schedules():
    """
    Creates a fixture with 10 diverse sample schedules for testing.
    Each schedule contains multiple lecture groups with different time slots
    to test various scenarios of active days, gaps, and times.
    """
    schedules = []
    
    # Schedule 1: Early start, early end, few gaps
    schedule1 = Schedule([
        create_lecture_group(
            "CS101", "Introduction to Programming", "Dr. Smith",
            "2", (8, 0), (10, 0),  # Monday lecture 8:00-10:00
            "2", (10, 30), (12, 30),  # Monday tirgul 10:30-12:30
            "3", (8, 0), (10, 0)  # Tuesday maabada 8:00-10:00
        ),
        create_lecture_group(
            "CS102", "Data Structures", "Dr. Johnson",
            "3", (10, 30), (12, 30),  # Tuesday lecture 10:30-12:30
            "4", (8, 0), (10, 0),  # Wednesday tirgul 8:00-10:00
            "5", (10, 30), (12, 30)  # Thursday maabada 10:30-12:30
        )
    ])
    schedule1.generate_metrics()
    schedules.append(schedule1)

    # Schedule 2: Late start, late end, many gaps
    schedule2 = Schedule([
        create_lecture_group(
            "CS201", "Advanced Programming", "Dr. Brown",
            "2", (10, 0), (12, 0),  # Monday lecture 10:00-12:00
            "3", (14, 0), (16, 0),  # Tuesday tirgul 14:00-16:00
            "4", (16, 0), (18, 0)  # Wednesday maabada 16:00-18:00
        ),
        create_lecture_group(
            "CS202", "Algorithms", "Dr. Wilson",
            "3", (12, 0), (14, 0),  # Tuesday lecture 12:00-14:00
            "4", (10, 0), (12, 0),  # Wednesday tirgul 10:00-12:00
            "5", (14, 0), (16, 0)  # Thursday maabada 14:00-16:00
        )
    ])
    schedule2.generate_metrics()
    schedules.append(schedule2)

    # Schedule 3: Middle of the day, moderate gaps
    schedule3 = Schedule([
        create_lecture_group(
            "CS301", "Database Systems", "Dr. Davis",
            "2", (9, 0), (11, 0),  # Monday lecture 9:00-11:00
            "3", (11, 30), (13, 30),  # Tuesday tirgul 11:30-13:30
            "4", (9, 0), (11, 0)  # Wednesday maabada 9:00-11:00
        ),
        create_lecture_group(
            "CS302", "Operating Systems", "Dr. Miller",
            "3", (11, 0), (13, 0),  # Tuesday lecture 11:00-13:00
            "4", (13, 30), (15, 30),  # Wednesday tirgul 13:30-15:30
            "5", (11, 0), (13, 0)  # Thursday maabada 11:00-13:00
        )
    ])
    schedule3.generate_metrics()
    schedules.append(schedule3)

    # Schedule 4: Very early schedule
    schedule4 = Schedule([
        create_lecture_group(
            "CS401", "Computer Networks", "Dr. Taylor",
            "2", (7, 0), (9, 0),  # Monday lecture 7:00-9:00
            "3", (7, 0), (9, 0),  # Tuesday tirgul 7:00-9:00
            "4", (7, 0), (9, 0)  # Wednesday maabada 7:00-9:00
        ),
        create_lecture_group(
            "CS402", "Software Engineering", "Dr. Anderson",
            "3", (9, 30), (11, 30),  # Tuesday lecture 9:30-11:30
            "4", (9, 30), (11, 30),  # Wednesday tirgul 9:30-11:30
            "5", (9, 30), (11, 30)  # Thursday maabada 9:30-11:30
        )
    ])
    schedule4.generate_metrics()
    schedules.append(schedule4)

    # Schedule 5: Very late schedule
    schedule5 = Schedule([
        create_lecture_group(
            "CS501", "Artificial Intelligence", "Dr. Thomas",
            "2", (11, 0), (13, 0),  # Monday lecture 11:00-13:00
            "3", (15, 0), (17, 0),  # Tuesday tirgul 15:00-17:00
            "4", (17, 0), (19, 0)  # Wednesday maabada 17:00-19:00
        ),
        create_lecture_group(
            "CS502", "Machine Learning", "Dr. Jackson",
            "3", (13, 0), (15, 0),  # Tuesday lecture 13:00-15:00
            "4", (11, 0), (13, 0),  # Wednesday tirgul 11:00-13:00
            "5", (15, 0), (17, 0)  # Thursday maabada 15:00-17:00
        )
    ])
    schedule5.generate_metrics()
    schedules.append(schedule5)

    # Schedule 6: Maximum active days (7 days)
    schedule6 = Schedule([
        create_lecture_group(
            "CS601", "Computer Graphics", "Dr. White",
            "1", (9, 0), (11, 0),  # Sunday lecture
            "2", (9, 0), (11, 0),  # Monday tirgul
            "3", (9, 0), (11, 0)  # Tuesday maabada
        ),
        create_lecture_group(
            "CS602", "Game Development", "Dr. Harris",
            "4", (9, 0), (11, 0),  # Wednesday lecture
            "5", (9, 0), (11, 0),  # Thursday tirgul
            "6", (9, 0), (11, 0)  # Friday maabada
        ),
        create_lecture_group(
            "CS603", "Virtual Reality", "Dr. Martin",
            "7", (9, 0), (11, 0),  # Saturday lecture
            "1", (11, 30), (13, 30),  # Sunday tirgul
            "2", (11, 30), (13, 30)  # Monday maabada
        )
    ])
    schedule6.generate_metrics()
    schedules.append(schedule6)

    # Schedule 7: Minimum active days (1 day)
    schedule7 = Schedule([
        create_lecture_group(
            "CS701", "Cloud Computing", "Dr. Thompson",
            "2", (9, 0), (11, 0),  # Monday lecture
            "2", (11, 30), (13, 30),  # Monday tirgul
            "2", (14, 0), (16, 0)  # Monday maabada
        )
    ])
    schedule7.generate_metrics()
    schedules.append(schedule7)

    # Schedule 8: Maximum gaps
    schedule8 = Schedule([
        create_lecture_group(
            "CS801", "Cybersecurity", "Dr. Garcia",
            "2", (8, 0), (9, 0),  # Monday lecture
            "2", (11, 0), (12, 0),  # Monday tirgul
            "2", (14, 0), (15, 0)  # Monday maabada
        ),
        create_lecture_group(
            "CS802", "Network Security", "Dr. Rodriguez",
            "3", (8, 0), (9, 0),  # Tuesday lecture
            "3", (11, 0), (12, 0),  # Tuesday tirgul
            "3", (14, 0), (15, 0)  # Tuesday maabada
        )
    ])
    schedule8.generate_metrics()
    schedules.append(schedule8)

    # Schedule 9: Maximum gap time
    schedule9 = Schedule([
        create_lecture_group(
            "CS901", "Big Data", "Dr. Martinez",
            "2", (8, 0), (9, 0),  # Monday lecture
            "2", (14, 0), (15, 0),  # Monday tirgul
            "3", (8, 0), (9, 0)  # Tuesday maabada
        ),
        create_lecture_group(
            "CS902", "Data Mining", "Dr. Robinson",
            "3", (14, 0), (15, 0),  # Tuesday lecture
            "4", (8, 0), (9, 0),  # Wednesday tirgul
            "4", (14, 0), (15, 0)  # Wednesday maabada
        )
    ])
    schedule9.generate_metrics()
    schedules.append(schedule9)

    # Schedule 10: Balanced schedule
    schedule10 = Schedule([
        create_lecture_group(
            "CS1001", "Web Development", "Dr. Clark",
            "2", (9, 0), (11, 0),  # Monday lecture
            "3", (9, 0), (11, 0),  # Tuesday tirgul
            "4", (9, 0), (11, 0)  # Wednesday maabada
        ),
        create_lecture_group(
            "CS1002", "Mobile Development", "Dr. Lewis",
            "3", (11, 30), (13, 30),  # Tuesday lecture
            "4", (11, 30), (13, 30),  # Wednesday tirgul
            "5", (11, 30), (13, 30)  # Thursday maabada
        )
    ])
    schedule10.generate_metrics()
    schedules.append(schedule10)

    return schedules

def test_insert_single_schedule():
    """
    Tests the basic functionality of inserting a single schedule.
    Verifies that:
    1. The schedule is correctly stored
    2. The total count is updated
    3. The schedule can be retrieved by its original index
    """
    ranker = ScheduleRanker()
    schedule = Schedule([
        create_lecture_group(
            "CS101", "Test Course", "Dr. Test",
            "2", (9, 0), (11, 0),  # Monday lecture
            "3", (9, 0), (11, 0),  # Tuesday tirgul
            "4", (9, 0), (11, 0)  # Wednesday maabada
        )
    ])
    schedule.generate_metrics()
    
    ranker.insert_schedule(schedule)
    assert ranker.get_total_count() == 1
    assert ranker.get_schedule_by_original_index(0) == schedule

def test_insert_batch(sample_schedules):
    """
    Tests batch insertion of multiple schedules.
    Verifies that:
    1. All schedules are correctly stored
    2. The total count matches the input size
    3. Each schedule can be retrieved by its original index
    """
    ranker = ScheduleRanker()
    ranker.add_batch(sample_schedules)
    assert ranker.get_total_count() == len(sample_schedules)
    
    # Verify all schedules were inserted correctly
    for i, schedule in enumerate(sample_schedules):
        assert ranker.get_schedule_by_original_index(i) == schedule

def test_ranking_by_active_days(sample_schedules):
    """
    Tests ranking schedules by number of active days.
    Verifies both ascending and descending order:
    - Ascending: Should start with minimum active days (1) and end with maximum (7)
    - Descending: Should start with maximum active days (7) and end with minimum (1)
    """
    ranker = ScheduleRanker()
    ranker.add_batch(sample_schedules)
    
    # Test ascending order
    ranker.set_preference(Preference(Metric.ACTIVE_DAYS, ascending=True))
    ranked = list(ranker.iter_ranked_schedules())
    assert ranked[0].active_days == 1  # Minimum active days
    assert ranked[-1].active_days == 7  # Maximum active days
    
    # Test descending order
    ranker.set_preference(Preference(Metric.ACTIVE_DAYS, ascending=False))
    ranked = list(ranker.iter_ranked_schedules())
    assert ranked[0].active_days == 7  # Maximum active days
    assert ranked[-1].active_days == 1  # Minimum active days

def test_ranking_by_gap_count(sample_schedules):
    """
    Tests ranking schedules by number of gaps.
    Verifies both ascending and descending order:
    - Ascending: Should start with minimum gaps (0) and end with maximum (8)
    - Descending: Should start with maximum gaps (8) and end with minimum (0)
    """
    ranker = ScheduleRanker()
    ranker.add_batch(sample_schedules)
    
    # Test ascending order
    ranker.set_preference(Preference(Metric.GAP_COUNT, ascending=True))
    ranked = list(ranker.iter_ranked_schedules())
    assert ranked[0].gap_count == 0  # Minimum gaps
    assert ranked[-1].gap_count == 8  # Maximum gaps
    
    # Test descending order
    ranker.set_preference(Preference(Metric.GAP_COUNT, ascending=False))
    ranked = list(ranker.iter_ranked_schedules())
    assert ranked[0].gap_count == 8  # Maximum gaps
    assert ranked[-1].gap_count == 0  # Minimum gaps

def test_ranking_by_total_gap_time(sample_schedules):
    """
    Tests ranking schedules by total gap time.
    Verifies both ascending and descending order:
    - Ascending: Should start with minimum gap time (0) and end with maximum (300)
    - Descending: Should start with maximum gap time (300) and end with minimum (0)
    """
    ranker = ScheduleRanker()
    ranker.add_batch(sample_schedules)
    
    # Test ascending order
    ranker.set_preference(Preference(Metric.TOTAL_GAP_TIME, ascending=True))
    ranked = list(ranker.iter_ranked_schedules())
    assert ranked[0].total_gap_time == 0  # Minimum gap time
    assert ranked[-1].total_gap_time == 300  # Maximum gap time
    
    # Test descending order
    ranker.set_preference(Preference(Metric.TOTAL_GAP_TIME, ascending=False))
    ranked = list(ranker.iter_ranked_schedules())
    assert ranked[0].total_gap_time == 300  # Maximum gap time
    assert ranked[-1].total_gap_time == 0  # Minimum gap time

def test_ranking_by_avg_start_time(sample_schedules):
    """
    Tests ranking schedules by average start time.
    Verifies both ascending and descending order:
    - Ascending: Should start with earliest time (700 = 7:00 AM) and end with latest (1100 = 11:00 AM)
    - Descending: Should start with latest time (1100 = 11:00 AM) and end with earliest (700 = 7:00 AM)
    """
    ranker = ScheduleRanker()
    ranker.add_batch(sample_schedules)
    
    # Test ascending order
    ranker.set_preference(Preference(Metric.AVG_START_TIME, ascending=True))
    ranked = list(ranker.iter_ranked_schedules())
    assert ranked[0].avg_start_time == 700  # Earliest start
    assert ranked[-1].avg_start_time == 1100  # Latest start
    
    # Test descending order
    ranker.set_preference(Preference(Metric.AVG_START_TIME, ascending=False))
    ranked = list(ranker.iter_ranked_schedules())
    assert ranked[0].avg_start_time == 1100  # Latest start
    assert ranked[-1].avg_start_time == 700  # Earliest start

def test_ranking_by_avg_end_time(sample_schedules):
    """
    Tests ranking schedules by average end time.
    Verifies both ascending and descending order:
    - Ascending: Should start with earliest time (1300 = 1:00 PM) and end with latest (1700 = 5:00 PM)
    - Descending: Should start with latest time (1700 = 5:00 PM) and end with earliest (1300 = 1:00 PM)
    """
    ranker = ScheduleRanker()
    ranker.add_batch(sample_schedules)
    
    # Test ascending order
    ranker.set_preference(Preference(Metric.AVG_END_TIME, ascending=True))
    ranked = list(ranker.iter_ranked_schedules())
    assert ranked[0].avg_end_time == 1300  # Earliest end
    assert ranked[-1].avg_end_time == 1700  # Latest end
    
    # Test descending order
    ranker.set_preference(Preference(Metric.AVG_END_TIME, ascending=False))
    ranked = list(ranker.iter_ranked_schedules())
    assert ranked[0].avg_end_time == 1700  # Latest end
    assert ranked[-1].avg_end_time == 1300  # Earliest end

def test_edge_cases():
    """
    Tests various edge cases and error conditions:
    1. Empty ranker behavior
    2. Invalid preference handling
    3. Out of bounds index handling
    4. Negative index handling
    """
    ranker = ScheduleRanker()
    
    # Test empty ranker
    assert ranker.get_total_count() == 0
    with pytest.raises(IndexError):
        ranker.get_ranked_schedule(0)
    
    # Test invalid preference
    with pytest.raises(ValueError):
        ranker.set_preference(Preference("INVALID_METRIC", True))
    
    # Test out of bounds index
    schedule = Schedule([
        create_lecture_group(
            "CS101", "Test Course", "Dr. Test",
            "2", (9, 0), (11, 0)  # Monday lecture only
        )
    ])
    schedule.generate_metrics()
    ranker.insert_schedule(schedule)
    with pytest.raises(IndexError):
        ranker.get_ranked_schedule(1)
    with pytest.raises(IndexError):
        ranker.get_ranked_schedule(-1)

def test_clear_functionality(sample_schedules):
    """
    Tests the clear functionality of the ranker.
    Verifies that:
    1. All schedules are removed
    2. The total count is reset to 0
    3. Attempting to access schedules after clearing raises an error
    """
    ranker = ScheduleRanker()
    ranker.add_batch(sample_schedules)
    assert ranker.get_total_count() == len(sample_schedules)
    
    ranker.clear()
    assert ranker.get_total_count() == 0
    with pytest.raises(IndexError):
        ranker.get_ranked_schedule(0)

def test_get_ranked_schedules_range(sample_schedules):
    """
    Tests retrieving ranges of ranked schedules.
    Verifies:
    1. Getting a specific range of schedules
    2. Getting all remaining schedules from a start point
    3. Error handling for invalid ranges
    """
    ranker = ScheduleRanker()
    ranker.add_batch(sample_schedules)
    
    # Test getting a range of schedules
    ranker.set_preference(Preference(Metric.ACTIVE_DAYS, ascending=True))
    schedules = ranker.get_ranked_schedules(start=2, count=3)
    assert len(schedules) == 3
    
    # Test getting all remaining schedules
    schedules = ranker.get_ranked_schedules(start=5)
    assert len(schedules) == len(sample_schedules) - 5
    
    # Test invalid range
    with pytest.raises(IndexError):
        ranker.get_ranked_schedules(start=len(sample_schedules))