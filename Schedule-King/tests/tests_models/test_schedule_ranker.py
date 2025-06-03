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

def create_time_slot(day: str, start_hour: int, start_minute: int, end_hour: int, end_minute: int, room: str = "101", building: str = "Main") -> TimeSlot:
    """
    Creates a TimeSlot object with the specified day, times, room, and building.
    """
    start_time = f"{start_hour:02d}:{start_minute:02d}"
    end_time = f"{end_hour:02d}:{end_minute:02d}"
    return TimeSlot(day, start_time, end_time, room, building)

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
    All time slots start and end only on the hour (minutes=0).
    """
    schedules = []
    
    # Schedule 1: Early start, early end, few gaps
    schedule1 = Schedule([
        create_lecture_group(
            "CS101", "Introduction to Programming", "Dr. Smith",
            "2", (8, 0), (9, 0),  # Monday lecture 8:00-9:00
            "2", (10, 0), (11, 0),  # Monday tirgul 10:00-11:00
            "3", (8, 0), (9, 0)  # Tuesday maabada 8:00-9:00
        ),
        create_lecture_group(
            "CS102", "Data Structures", "Dr. Johnson",
            "3", (10, 0), (11, 0),  # Tuesday lecture 10:00-11:00
            "4", (8, 0), (9, 0),  # Wednesday tirgul 8:00-9:00
            "5", (10, 0), (11, 0)  # Thursday maabada 10:00-11:00
        )
    ])
    schedule1.generate_metrics()
    schedules.append(schedule1)

    # Schedule 2: Late start, late end, many gaps
    schedule2 = Schedule([
        create_lecture_group(
            "CS201", "Advanced Programming", "Dr. Brown",
            "2", (10, 0), (11, 0),  # Monday lecture 10:00-11:00
            "3", (14, 0), (15, 0),  # Tuesday tirgul 14:00-15:00
            "4", (16, 0), (17, 0)  # Wednesday maabada 16:00-17:00
        ),
        create_lecture_group(
            "CS202", "Algorithms", "Dr. Wilson",
            "3", (12, 0), (13, 0),  # Tuesday lecture 12:00-13:00
            "4", (10, 0), (11, 0),  # Wednesday tirgul 10:00-11:00
            "5", (14, 0), (15, 0)  # Thursday maabada 14:00-15:00
        )
    ])
    schedule2.generate_metrics()
    schedules.append(schedule2)

    # Schedule 3: Middle of the day, moderate gaps
    schedule3 = Schedule([
        create_lecture_group(
            "CS301", "Database Systems", "Dr. Davis",
            "2", (9, 0), (10, 0),  # Monday lecture 9:00-10:00
            "3", (11, 0), (12, 0),  # Tuesday tirgul 11:00-12:00
            "4", (9, 0), (10, 0)  # Wednesday maabada 9:00-10:00
        ),
        create_lecture_group(
            "CS302", "Operating Systems", "Dr. Miller",
            "3", (11, 0), (12, 0),  # Tuesday lecture 11:00-12:00
            "4", (13, 0), (14, 0),  # Wednesday tirgul 13:00-14:00
            "5", (11, 0), (12, 0)  # Thursday maabada 11:00-12:00
        )
    ])
    schedule3.generate_metrics()
    schedules.append(schedule3)

    # Schedule 4: Very early schedule
    schedule4 = Schedule([
        create_lecture_group(
            "CS401", "Computer Networks", "Dr. Taylor",
            "2", (7, 0), (8, 0),  # Monday lecture 7:00-8:00
            "3", (7, 0), (8, 0),  # Tuesday tirgul 7:00-8:00
            "4", (7, 0), (8, 0)  # Wednesday maabada 7:00-8:00
        ),
        create_lecture_group(
            "CS402", "Software Engineering", "Dr. Anderson",
            "3", (9, 0), (10, 0),  # Tuesday lecture 9:00-10:00
            "4", (9, 0), (10, 0),  # Wednesday tirgul 9:00-10:00
            "5", (9, 0), (10, 0)  # Thursday maabada 9:00-10:00
        )
    ])
    schedule4.generate_metrics()
    schedules.append(schedule4)

    # Schedule 5: Very late schedule
    schedule5 = Schedule([
        create_lecture_group(
            "CS501", "Artificial Intelligence", "Dr. Thomas",
            "2", (11, 0), (12, 0),  # Monday lecture 11:00-12:00
            "3", (15, 0), (16, 0),  # Tuesday tirgul 15:00-16:00
            "4", (17, 0), (18, 0)  # Wednesday maabada 17:00-18:00
        ),
        create_lecture_group(
            "CS502", "Machine Learning", "Dr. Jackson",
            "3", (13, 0), (14, 0),  # Tuesday lecture 13:00-14:00
            "4", (11, 0), (12, 0),  # Wednesday tirgul 11:00-12:00
            "5", (15, 0), (16, 0)  # Thursday maabada 15:00-16:00
        )
    ])
    schedule5.generate_metrics()
    schedules.append(schedule5)

    # Schedule 6: Maximum active days (7 days)
    schedule6 = Schedule([
        create_lecture_group(
            "CS601", "Computer Graphics", "Dr. White",
            "1", (9, 0), (10, 0),  # Sunday lecture
            "2", (9, 0), (10, 0),  # Monday tirgul
            "3", (9, 0), (10, 0)  # Tuesday maabada
        ),
        create_lecture_group(
            "CS602", "Game Development", "Dr. Harris",
            "4", (9, 0), (10, 0),  # Wednesday lecture
            "5", (9, 0), (10, 0),  # Thursday tirgul
            "6", (9, 0), (10, 0)  # Friday maabada
        ),
        create_lecture_group(
            "CS603", "Virtual Reality", "Dr. Martin",
            "7", (9, 0), (10, 0),  # Saturday lecture
            "1", (11, 0), (12, 0),  # Sunday tirgul
            "2", (11, 0), (12, 0)  # Monday maabada
        )
    ])
    schedule6.generate_metrics()
    schedules.append(schedule6)

    # Schedule 7: Minimum active days (1 day)
    schedule7 = Schedule([
        create_lecture_group(
            "CS701", "Cloud Computing", "Dr. Thompson",
            "2", (9, 0), (10, 0),  # Monday lecture
            "2", (11, 0), (12, 0),  # Monday tirgul
            "2", (14, 0), (15, 0)  # Monday maabada
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
            "2", (9, 0), (10, 0),  # Monday lecture
            "3", (9, 0), (10, 0),  # Tuesday tirgul
            "4", (9, 0), (10, 0)  # Wednesday maabada
        ),
        create_lecture_group(
            "CS1002", "Mobile Development", "Dr. Lewis",
            "3", (11, 0), (12, 0),  # Tuesday lecture
            "4", (11, 0), (12, 0),  # Wednesday tirgul
            "5", (11, 0), (12, 0)  # Thursday maabada
        )
    ])
    schedule10.generate_metrics()
    schedules.append(schedule10)

    # Schedule 11: Schedule with 0 gaps
    schedule11 = Schedule([
        create_lecture_group(
            "CS1101", "Intro to AI", "Dr. Gates",
            "2", (9, 0), (10, 0),  # Monday lecture
            "2", (10, 0), (11, 0)  # Monday tirgul - no gap
        )
    ])
    schedule11.generate_metrics()
    schedules.append(schedule11)

    return schedules

def test_insert_single_schedule():
    """
    Tests the basic functionality of inserting a single schedule.
    Verifies that:
    1. The schedule is correctly stored
    2. The total count is 1
    3. The schedule can be retrieved by its index (0)
    """
    schedule = Schedule([
        create_lecture_group(
            "CS101", "Intro", "Dr. A",
            "2", (9, 0), (10, 0),
            "2", (11, 0), (12, 0)
        )
    ])
    schedule.generate_metrics()
    
    ranker = ScheduleRanker()
    ranker.insert_schedule(schedule)
    
    assert ranker.get_total_count() == 1
    retrieved_schedule = ranker.get_schedule_by_original_index(0)
    assert retrieved_schedule == schedule # Checks if the same object is retrieved

def test_insert_batch(sample_schedules):
    """
    Tests batch insertion of multiple schedules.
    Verifies that:
    1. All schedules are correctly stored
    2. The total count matches the input size
    3. Each schedule can be retrieved by its original index
    """
    ranker = ScheduleRanker()
    # Add print statements to inspect calculated metrics
    for i, schedule in enumerate(sample_schedules):
        print(f"Schedule {i+1} Metrics: Active Days={schedule.active_days}, Gap Count={schedule.gap_count}, Total Gap Time={schedule.total_gap_time}, Avg Start Time={schedule.avg_start_time}, Avg End Time={schedule.avg_end_time}")
    
    ranker.add_batch(sample_schedules)

    assert ranker.get_total_count() == len(sample_schedules)
    for i in range(len(sample_schedules)):
        assert ranker.get_schedule_by_original_index(i) == sample_schedules[i]

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
    - Ascending: Should start with minimum gaps (0) and end with maximum (based on calculation)
    - Descending: Should start with maximum gaps (based on calculation) and end with minimum (0)
    """
    ranker = ScheduleRanker()
    
    ranker.add_batch(sample_schedules)

    # Test ascending order
    ranker.set_preference(Preference(Metric.GAP_COUNT, ascending=True))
    ranked = list(ranker.iter_ranked_schedules())
    # Expected gap counts: 0 (S11), 1 (S?), 2 (S1, S3, S4, S5, S6, S7, S10), 3 (S9), 4 (S2, S8)
    assert ranked[0].gap_count == 0  # Schedule 11 has 0 gaps
    assert ranked[-1].gap_count == 4  # Schedules 2 and 8 have 4 gaps

    # Test descending order
    ranker.set_preference(Preference(Metric.GAP_COUNT, ascending=False))
    ranked = list(ranker.iter_ranked_schedules())
    assert ranked[0].gap_count == 4  # Schedules 2 and 8 have 4 gaps
    assert ranked[-1].gap_count == 0  # Schedule 11 has 0 gaps

def test_ranking_by_total_gap_time(sample_schedules):
    """
    Tests ranking schedules by total gap time.
    Verifies both ascending and descending order:
    - Ascending: Should start with minimum gap time (0) and end with maximum (based on calculation)
    - Descending: Should start with maximum gap time (based on calculation) and end with minimum (0)
    """
    ranker = ScheduleRanker()
    
    ranker.add_batch(sample_schedules)

    # Test ascending order
    ranker.set_preference(Preference(Metric.TOTAL_GAP_TIME, ascending=True))
    ranked = list(ranker.iter_ranked_schedules())
    # Expected total gap times (hours): 0.0 (S11), 2.5 (S3, S4, S7, S10, S6), 3.0 (S1), 4.0 (S5), 8.0 (S2, S8), 15.0 (S9)
    assert ranked[0].total_gap_time == pytest.approx(0.0)  # Schedule 11 has 0.0 total gap time
    assert ranked[-1].total_gap_time == pytest.approx(15.0)  # Schedule 9 has 15.0 total gap time

    # Test descending order
    ranker.set_preference(Preference(Metric.TOTAL_GAP_TIME, ascending=False))
    ranked = list(ranker.iter_ranked_schedules())
    assert ranked[0].total_gap_time == pytest.approx(15.0)  # Schedule 9 has 15.0 total gap time
    assert ranked[-1].total_gap_time == pytest.approx(0.0)  # Schedule 11 has 0.0 total gap time

def test_ranking_by_avg_start_time(sample_schedules):
    """
    Tests ranking schedules by average start time.
    Verifies both ascending and descending order:
    - Ascending: Should start with earliest time and end with latest time (based on calculation)
    - Descending: Should start with latest time and end with earliest time (based on calculation)
    """
    ranker = ScheduleRanker()
    
    ranker.add_batch(sample_schedules)

    # Test ascending order
    ranker.set_preference(Preference(Metric.AVG_START_TIME, ascending=True))
    ranked = list(ranker.iter_ranked_schedules())
    
    # Print actual values for debugging
    print("Actual avg start times (ascending):")
    for i, schedule in enumerate(ranked):
        print(f"  Schedule {i}: {schedule.avg_start_time}")
    
    # The actual earliest and latest start times based on correct calculation
    assert ranked[0].avg_start_time == pytest.approx(750.0)  # Schedule with earliest avg start time
    assert ranked[-1].avg_start_time == pytest.approx(1250.0)  # Schedule 5 has avg start time 1250.0

    # Test descending order
    ranker.set_preference(Preference(Metric.AVG_START_TIME, ascending=False))
    ranked = list(ranker.iter_ranked_schedules())
    assert ranked[0].avg_start_time == pytest.approx(1250.0)  # Schedule 5 has avg start time 1250.0
    assert ranked[-1].avg_start_time == pytest.approx(750.0)  # Schedule with earliest avg start time

def test_ranking_by_avg_end_time(sample_schedules):
    """
    Tests ranking schedules by average end time.
    Verifies both ascending and descending order:
    - Ascending: Should start with earliest time and end with latest time (based on calculation)
    - Descending: Should start with latest time and end with earliest time (based on calculation)
    """
    ranker = ScheduleRanker()
    
    ranker.add_batch(sample_schedules)

    # Test ascending order
    ranker.set_preference(Preference(Metric.AVG_END_TIME, ascending=True))
    ranked = list(ranker.iter_ranked_schedules())
    
    # Print actual values for debugging
    print("Actual avg end times (ascending):")
    for i, schedule in enumerate(ranked):
        print(f"  Schedule {i}: {schedule.avg_end_time}")
    
    # The actual earliest and latest end times based on correct calculation
    assert ranked[0].avg_end_time == pytest.approx(950.0)  # Schedule with earliest avg end time
    assert ranked[-1].avg_end_time == pytest.approx(1550.0)  # Schedule 5 has avg end time 1550.0

    # Test descending order
    ranker.set_preference(Preference(Metric.AVG_END_TIME, ascending=False))
    ranked = list(ranker.iter_ranked_schedules())
    assert ranked[0].avg_end_time == pytest.approx(1550.0)  # Schedule 5 has avg end time 1550.0
    assert ranked[-1].avg_end_time == pytest.approx(950.0)  # Schedule with earliest avg end time

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