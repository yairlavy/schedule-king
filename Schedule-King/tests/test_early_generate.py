# test_all_strategy.py

import pytest
from unittest.mock import MagicMock
from src.core.all_strategy import AllStrategy
from src.data.models.schedule import Schedule
from src.data.models.course import Course
from src.data.models.lecture_group import LectureGroup
from src.core.conflict_checker import ConflictChecker

@pytest.mark.describe("AllStrategy.generate")
class TestAllStrategyGenerate:

    @pytest.fixture
    def mock_conflict_checker(self):
        return MagicMock(spec=ConflictChecker)

    @pytest.fixture
    def sample_courses(self):
        # Create sample courses with mock data
        course1 = Course(
            name="Course 1",
            course_code="C1",
            instructor="Instructor 1",
            lectures=["L1"],
            tirguls=["T1"],
            maabadas=["M1"]
        )
        course2 = Course(
            name="Course 2",
            course_code="C2",
            instructor="Instructor 2",
            lectures=["L2"],
            tirguls=["T2"],
            maabadas=["M2"]
        )
        return [course1, course2]

    @pytest.mark.happy_path
    def test_generate_valid_schedules(self, sample_courses, mock_conflict_checker):
        """
        Test that generate returns valid schedules when there are no conflicts.
        """
        # Mock the conflict checker to always return False (no conflict)
        mock_conflict_checker.check_time_conflict.return_value = False
        mock_conflict_checker.check_room_conflict.return_value = False

        strategy = AllStrategy(selected=sample_courses, checker=mock_conflict_checker)
        schedules = strategy.generate()

        # Assert that schedules are generated and are instances of Schedule
        assert len(schedules) > 0
        assert all(isinstance(schedule, Schedule) for schedule in schedules)

    @pytest.mark.happy_path
    def test_generate_no_schedules_due_to_conflicts(self, sample_courses, mock_conflict_checker):
        """
        Test that generate returns no schedules when all combinations have conflicts.
        """
        # Mock the conflict checker to always return True (conflict exists)
        mock_conflict_checker.check_time_conflict.return_value = True
        mock_conflict_checker.check_room_conflict.return_value = True

        strategy = AllStrategy(selected=sample_courses, checker=mock_conflict_checker)
        schedules = strategy.generate()

        # Assert that no schedules are generated
        assert len(schedules) == 0

    @pytest.mark.edge_case
    def test_generate_with_max_courses(self, mock_conflict_checker):
        """
        Test that generate handles the maximum number of courses (7) without error.
        """
        # Create 7 sample courses
        courses = [
            Course(
                name=f"Course {i}",
                course_code=f"C{i}",
                instructor=f"Instructor {i}",
                lectures=[f"L{i}"],
                tirguls=[f"T{i}"],
                maabadas=[f"M{i}"]
            ) for i in range(7)
        ]

        # Mock the conflict checker to always return False (no conflict)
        mock_conflict_checker.check_time_conflict.return_value = False
        mock_conflict_checker.check_room_conflict.return_value = False

        strategy = AllStrategy(selected=courses, checker=mock_conflict_checker)
        schedules = strategy.generate()

        # Assert that schedules are generated
        assert len(schedules) > 0

    @pytest.mark.edge_case
    def test_generate_with_more_than_max_courses(self, mock_conflict_checker):
        """
        Test that initializing AllStrategy with more than 7 courses raises a ValueError.
        """
        # Create 8 sample courses
        courses = [
            Course(
                name=f"Course {i}",
                course_code=f"C{i}",
                instructor=f"Instructor {i}",
                lectures=[f"L{i}"],
                tirguls=[f"T{i}"],
                maabadas=[f"M{i}"]
            ) for i in range(8)
        ]

        with pytest.raises(ValueError, match="Cannot select more than 7 courses."):
            AllStrategy(selected=courses, checker=mock_conflict_checker)

    @pytest.mark.edge_case
    def test_generate_with_no_courses(self, mock_conflict_checker):
        """
        Test that generate returns an empty list when no courses are selected.
        """
        strategy = AllStrategy(selected=[], checker=mock_conflict_checker)
        schedules = strategy.generate()

        # Assert that no schedules are generated
        assert len(schedules) == 0