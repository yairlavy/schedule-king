# test_all_strategy.py

import pytest
from unittest.mock import Mock
from src.core.all_strategy import AllStrategy
from src.data.models.course import Course
from src.data.models.lecture_group import LectureGroup

@pytest.fixture
def mock_conflict_checker():
    return Mock()

@pytest.fixture
def sample_courses():
    return [Mock(spec=Course) for _ in range(3)]

@pytest.fixture
def sample_lecture_groups():
    # Create mock lecture groups with different attributes
    group1 = Mock(spec=LectureGroup)
    group2 = Mock(spec=LectureGroup)
    group3 = Mock(spec=LectureGroup)
    return [group1, group2, group3]

@pytest.mark.describe("_has_conflict method")
class TestHasConflict:

    @pytest.mark.happy_path
    def test_no_conflict(self, mock_conflict_checker, sample_courses, sample_lecture_groups):
        """
        Test that _has_conflict returns False when there are no conflicts.
        """
        # Setup mock to return False for any conflict check
        mock_conflict_checker.check_time_conflict.return_value = False
        mock_conflict_checker.check_room_conflict.return_value = False

        strategy = AllStrategy(sample_courses, mock_conflict_checker)
        assert not strategy._has_conflict(sample_lecture_groups)

    @pytest.mark.happy_path
    def test_time_conflict(self, mock_conflict_checker, sample_courses, sample_lecture_groups):
        """
        Test that _has_conflict returns True when there is a time conflict.
        """
        # Setup mock to return True for time conflict
        mock_conflict_checker.check_time_conflict.side_effect = lambda a, b: a == sample_lecture_groups[0].lecture and b == sample_lecture_groups[1].lecture

        strategy = AllStrategy(sample_courses, mock_conflict_checker)
        assert strategy._has_conflict(sample_lecture_groups)

    @pytest.mark.happy_path
    def test_room_conflict(self, mock_conflict_checker, sample_courses, sample_lecture_groups):
        """
        Test that _has_conflict returns True when there is a room conflict.
        """
        # Setup mock to return True for room conflict
        mock_conflict_checker.check_room_conflict.side_effect = lambda a, b: a == sample_lecture_groups[0].lecture and b == sample_lecture_groups[1].lecture

        strategy = AllStrategy(sample_courses, mock_conflict_checker)
        assert strategy._has_conflict(sample_lecture_groups)

    @pytest.mark.edge_case
    def test_empty_groups(self, mock_conflict_checker, sample_courses):
        """
        Test that _has_conflict returns False when the groups list is empty.
        """
        strategy = AllStrategy(sample_courses, mock_conflict_checker)
        assert not strategy._has_conflict([])

    @pytest.mark.edge_case
    def test_single_group(self, mock_conflict_checker, sample_courses, sample_lecture_groups):
        """
        Test that _has_conflict returns False when there is only one group.
        """
        strategy = AllStrategy(sample_courses, mock_conflict_checker)
        assert not strategy._has_conflict([sample_lecture_groups[0]])

    @pytest.mark.edge_case
    def test_maximum_courses(self, mock_conflict_checker):
        """
        Test that _has_conflict works with the maximum number of courses allowed.
        """
        max_courses = [Mock(spec=Course) for _ in range(7)]
        strategy = AllStrategy(max_courses, mock_conflict_checker)
        # Assuming no conflicts in this test
        mock_conflict_checker.check_time_conflict.return_value = False
        mock_conflict_checker.check_room_conflict.return_value = False
        assert not strategy._has_conflict([Mock(spec=LectureGroup) for _ in range(7)])