# test_all_strategy.py

import pytest
from src.core.all_strategy import AllStrategy
from src.core.conflict_checker import ConflictChecker
from src.data.models.course import Course

# Mock classes for testing
class MockCourse(Course):
    pass

class MockConflictChecker(ConflictChecker):
    pass

@pytest.mark.describe("AllStrategy __init__ method")
class TestAllStrategyInit:
    
    @pytest.mark.happy_path
    def test_init_with_valid_courses(self):
        """Test initializing AllStrategy with a valid list of courses."""
        courses = [MockCourse() for _ in range(3)]
        checker = MockConflictChecker()
        strategy = AllStrategy(selected=courses, checker=checker)
        assert strategy._selected == courses
        assert strategy._checker == checker

    @pytest.mark.happy_path
    def test_init_with_maximum_courses(self):
        """Test initializing AllStrategy with exactly 7 courses."""
        courses = [MockCourse() for _ in range(7)]
        checker = MockConflictChecker()
        strategy = AllStrategy(selected=courses, checker=checker)
        assert strategy._selected == courses
        assert strategy._checker == checker

    @pytest.mark.edge_case
    def test_init_with_no_courses(self):
        """Test initializing AllStrategy with an empty list of courses."""
        courses = []
        checker = MockConflictChecker()
        strategy = AllStrategy(selected=courses, checker=checker)
        assert strategy._selected == courses
        assert strategy._checker == checker

    @pytest.mark.edge_case
    def test_init_with_more_than_maximum_courses(self):
        """Test initializing AllStrategy with more than 7 courses raises ValueError."""
        courses = [MockCourse() for _ in range(8)]
        checker = MockConflictChecker()
        with pytest.raises(ValueError, match="Cannot select more than 7 courses."):
            AllStrategy(selected=courses, checker=checker)

    @pytest.mark.edge_case
    def test_init_with_none_checker(self):
        """Test initializing AllStrategy with None as the conflict checker."""
        courses = [MockCourse() for _ in range(3)]
        with pytest.raises(TypeError):
            AllStrategy(selected=courses, checker=None)