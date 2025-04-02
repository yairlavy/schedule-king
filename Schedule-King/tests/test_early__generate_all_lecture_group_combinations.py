# test_all_strategy.py

import pytest
from itertools import product
from src.core.all_strategy import AllStrategy
from src.data.models.course import Course
from src.data.models.lecture_group import LectureGroup
from src.core.conflict_checker import ConflictChecker

@pytest.fixture
def mock_conflict_checker():
    # Mock ConflictChecker for testing purposes
    return ConflictChecker()

@pytest.fixture
def sample_courses():
    # Create sample courses with lectures, tirguls, and maabadas
    return [
        Course(
            name="Course1",
            course_code="C1",
            instructor="Instructor1",
            lectures=["L1", "L2"],
            tirguls=["T1"],
            maabadas=["M1", "M2"]
        ),
        Course(
            name="Course2",
            course_code="C2",
            instructor="Instructor2",
            lectures=["L1"],
            tirguls=["T1", "T2"],
            maabadas=["M1"]
        )
    ]

@pytest.mark.describe("_generate_all_lecture_group_combinations")
class TestGenerateAllLectureGroupCombinations:

    @pytest.mark.happy_path
    def test_generate_combinations_happy_path(self, sample_courses, mock_conflict_checker):
        """
        Test that the method generates all possible combinations of lecture groups for given courses.
        """
        strategy = AllStrategy(selected=sample_courses, checker=mock_conflict_checker)
        combinations = strategy._generate_all_lecture_group_combinations(sample_courses)

        # Calculate expected number of combinations
        expected_combinations_count = 1
        for course in sample_courses:
            expected_combinations_count *= len(list(product(course.lectures, course.tirguls, course.maabadas)))

        assert len(combinations) == expected_combinations_count
        assert all(isinstance(combo, list) for combo in combinations)
        assert all(isinstance(group, LectureGroup) for combo in combinations for group in combo)

    @pytest.mark.edge_case
    def test_generate_combinations_empty_courses(self, mock_conflict_checker):
        """
        Test that the method returns an empty list when no courses are provided.
        """
        strategy = AllStrategy(selected=[], checker=mock_conflict_checker)
        combinations = strategy._generate_all_lecture_group_combinations([])

        assert combinations == []

    @pytest.mark.edge_case
    def test_generate_combinations_single_course_no_lectures(self, mock_conflict_checker):
        """
        Test that the method handles a course with no lectures, tirguls, or maabadas.
        """
        course_with_no_lectures = Course(
            name="Course3",
            course_code="C3",
            instructor="Instructor3",
            lectures=[],
            tirguls=[],
            maabadas=[]
        )
        strategy = AllStrategy(selected=[course_with_no_lectures], checker=mock_conflict_checker)
        combinations = strategy._generate_all_lecture_group_combinations([course_with_no_lectures])

        assert combinations == [[]]

    @pytest.mark.edge_case
    def test_generate_combinations_max_courses(self, mock_conflict_checker):
        """
        Test that the method handles the maximum number of courses allowed (7 courses).
        """
        courses = [Course(
            name=f"Course{i}",
            course_code=f"C{i}",
            instructor=f"Instructor{i}",
            lectures=["L1"],
            tirguls=["T1"],
            maabadas=["M1"]
        ) for i in range(7)]

        strategy = AllStrategy(selected=courses, checker=mock_conflict_checker)
        combinations = strategy._generate_all_lecture_group_combinations(courses)

        assert len(combinations) == 1  # Only one combination possible with single lecture, tirgul, and maabada per course

    @pytest.mark.edge_case
    def test_generate_combinations_more_than_max_courses(self, mock_conflict_checker):
        """
        Test that initializing AllStrategy with more than 7 courses raises a ValueError.
        """
        courses = [Course(
            name=f"Course{i}",
            course_code=f"C{i}",
            instructor=f"Instructor{i}",
            lectures=["L1"],
            tirguls=["T1"],
            maabadas=["M1"]
        ) for i in range(8)]

        with pytest.raises(ValueError, match="Cannot select more than 7 courses."):
            AllStrategy(selected=courses, checker=mock_conflict_checker)