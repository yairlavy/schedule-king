
import pytest
from datetime import time
from collections import namedtuple
from src.models.schedule import Schedule
from src.models.lecture_group import LectureGroup   


Lecture = namedtuple("Lecture", ["day", "start_time"])

class MockLectureGroup:
    def __init__(self, lecture=None, tirguls=None, maabadas=None):
        self.lecture = lecture
        self.tirguls = tirguls
        self.maabadas = maabadas

def tf(hour, minute=0):
    return hour * 100 + minute

@pytest.fixture
def empty_schedule():
    return Schedule(lecture_groups=[])

@pytest.fixture
def single_day_schedule():
    lg1 = MockLectureGroup(lecture=Lecture(day="2", start_time=time(9, 0)))
    lg2 = MockLectureGroup(tirguls=Lecture(day="2", start_time=time(10, 0)))
    lg3 = MockLectureGroup(maabadas=Lecture(day="2", start_time=time(11, 0)))
    return Schedule(lecture_groups=[lg1, lg2, lg3])

@pytest.fixture
def multi_day_schedule_with_gaps():
    lg1 = MockLectureGroup(lecture=Lecture(day="2", start_time=time(9, 0)))
    lg2 = MockLectureGroup(tirguls=Lecture(day="2", start_time=time(11, 0)))
    lg3 = MockLectureGroup(lecture=Lecture(day="4", start_time=time(8, 0)))
    lg4 = MockLectureGroup(tirguls=Lecture(day="4", start_time=time(9, 0)))
    lg5 = MockLectureGroup(maabadas=Lecture(day="4", start_time=time(13, 0)))
    return Schedule(lecture_groups=[lg1, lg2, lg3, lg4, lg5])

@pytest.fixture
def schedule_with_minimal_gap():
    lg1 = MockLectureGroup(lecture=Lecture(day="3", start_time=time(9, 0)))
    lg2 = MockLectureGroup(tirguls=Lecture(day="3", start_time=time(10, 30)))
    return Schedule(lecture_groups=[lg1, lg2])

@pytest.fixture
def schedule_with_varied_days_and_empty_groups():
    lg1 = MockLectureGroup()
    lg2 = MockLectureGroup(lecture=Lecture(day="1", start_time=time(8, 0)))
    lg3 = MockLectureGroup(tirguls=Lecture(day="5", start_time=time(14, 0)))
    return Schedule(lecture_groups=[lg1, lg2, lg3])

class TestScheduleGenerateMetrics:

    def test_empty_schedule_metrics(self, empty_schedule):
        empty_schedule.generate_metrics()
        assert empty_schedule.active_days == 0
        assert empty_schedule.gap_count == 0
        assert empty_schedule.total_gap_time == 0
        assert empty_schedule.avg_start_time == 0
        assert empty_schedule.avg_end_time == 0

    def test_single_day_no_gaps(self, single_day_schedule):
        single_day_schedule.generate_metrics()
        assert single_day_schedule.active_days == 1
        assert single_day_schedule.gap_count == 0
        assert single_day_schedule.total_gap_time == 0
        assert single_day_schedule.avg_start_time == tf(9)
        assert single_day_schedule.avg_end_time == tf(12)

    def test_multi_day_with_gaps(self, multi_day_schedule_with_gaps):
        multi_day_schedule_with_gaps.generate_metrics()
        assert multi_day_schedule_with_gaps.active_days == 2
        assert multi_day_schedule_with_gaps.gap_count == 2
        assert multi_day_schedule_with_gaps.total_gap_time == pytest.approx(4.0)

    def test_gap_exactly_30_minutes_not_counted(self, schedule_with_minimal_gap):
        schedule_with_minimal_gap.generate_metrics()
        assert schedule_with_minimal_gap.gap_count == 0
        assert schedule_with_minimal_gap.total_gap_time == 0
        assert schedule_with_minimal_gap.avg_start_time == tf(9)
        assert schedule_with_minimal_gap.avg_end_time == tf(11, 30)

    def test_varied_days_and_empty_lecture_groups(self, schedule_with_varied_days_and_empty_groups):
        # This schedule has lectures on two days, with one day having an empty lecture group
        # and the other day having a lecture and a tirgul.
        schedule_with_varied_days_and_empty_groups.generate_metrics()
        assert schedule_with_varied_days_and_empty_groups.active_days == 2
        assert schedule_with_varied_days_and_empty_groups.gap_count == 0
        assert schedule_with_varied_days_and_empty_groups.total_gap_time == 0
        assert schedule_with_varied_days_and_empty_groups.avg_start_time == pytest.approx((tf(8) + tf(14)) / 2)
        assert schedule_with_varied_days_and_empty_groups.avg_end_time == pytest.approx((tf(9) + tf(15)) / 2)

    def test_lectures_on_all_days(self):
        # This schedule has lectures on all days of the week, with no gaps.

        lgs = [MockLectureGroup(lecture=Lecture(day=str(i), start_time=time(7 + i, 0))) for i in range(1, 8)]
        schedule = Schedule(lecture_groups=lgs)
        schedule.generate_metrics()
        assert schedule.active_days == 7
        assert schedule.gap_count == 0
        assert schedule.total_gap_time == 0
        expected_start = sum([tf(7 + i) for i in range(1, 8)]) / 7
        expected_end = sum([tf(8 + i) for i in range(1, 8)]) / 7
        assert schedule.avg_start_time == pytest.approx(expected_start)
        assert schedule.avg_end_time == pytest.approx(expected_end)

    def test_lectures_with_nonstandard_day_names(self):
        lg = MockLectureGroup(lecture=Lecture(day="X", start_time=time(10, 0)))
        schedule = Schedule(lecture_groups=[lg])
        schedule.generate_metrics()
        assert schedule.active_days == 1
        assert schedule.gap_count == 0
        assert schedule.total_gap_time == 0
        assert schedule.avg_start_time == tf(10)
        assert schedule.avg_end_time == tf(11)

    def test_lectures_with_overlapping_times(self):
        # This schedule has overlapping lecture times on the same day.
        # The first lecture starts at 9:00 and the second at 9:30.
        lg1 = MockLectureGroup(lecture=Lecture(day="2", start_time=time(9, 0)))
        lg2 = MockLectureGroup(tirguls=Lecture(day="2", start_time=time(9, 30)))
        schedule = Schedule(lecture_groups=[lg1, lg2])
        schedule.generate_metrics()
        assert schedule.gap_count == 0
        assert schedule.total_gap_time == 0
        assert schedule.avg_start_time == tf(9)
        assert schedule.avg_end_time == tf(10) + 30
