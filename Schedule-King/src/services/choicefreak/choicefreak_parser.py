import datetime
from datetime import timedelta
import json
from src.models.course import Course
from src.models.time_slot import TimeSlot
from src.services.choicefreak.choicefreak_api import ChoiceFreakApi
import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any

class ChoiceFreakParser():
    """
    Parses course data either from a local .json file or by fetching
    details for a given category name (first 10 courses).
    """

    # Mapping from Hebrew kind names to internal kind names
    _KIND_MAP = {
        "הרצאה": "lecture",
        "תרגיל": "tirgul",
        "תירגול": "tirgul",
        "מעבדה": "maabada",
    }

    def __init__(self, source: str, period: str = "2025-2"):
        """
        :param source: local .json file path or category name (str).
        :param period: semester code, e.g. "2025-2" (used if fetching by category)
        """
        self.source = source
        self.period = period

    def _heb_day(self, when: datetime) -> str:
        """
        Convert Python's isoweekday (Mon=1...Sun=7) to Hebrew day string (Sun="1"...Sat="7")
        """
        return str((when.isoweekday() % 7) + 1)

    def _show_to_timeslot(self, show: Dict[str, Any]) -> TimeSlot:
        """
        Convert a 'show' dictionary to a TimeSlot object.
        """
        when = datetime.fromisoformat(show["when"])
        start = when
        end = when + timedelta(minutes=show.get("duration", 0))
        return TimeSlot(
            day=self._heb_day(start),
            start_time=start.strftime("%H:%M"),
            end_time=end.strftime("%H:%M"),
            room=show["where"]["room"],
            building=show["where"]["building"],
        )

    def _course_from_dict(self, d: Dict[str, Any]) -> Course:
        """
        Convert a course dictionary to a Course object, including all its time slots.
        """
        # Collect unique instructor names from shows
        instructors = {
            s["details"]["who"]["name"]
            for s in d.get("shows", [])
            if s.get("details", {}).get("who")
        }
        instr_str = ", ".join(instructors)

        course = Course(
            course_name=d.get("title", ""),
            course_code=d.get("id", ""),
            instructor=instr_str,
        )

        # Add time slots to the course based on their kind
        for show in d.get("shows", []):
            ts = self._show_to_timeslot(show)
            kind = show.get("kind", "")
            target = self._KIND_MAP.get(kind, "lecture")

            if target == "lecture":
                course.add_lecture([ts])
            elif target == "tirgul":
                course.add_tirgul([ts])
            elif target == "maabada":
                course.add_maabada([ts])

        return course

    def _load_raw(self) -> List[Dict[str, Any]]:
        """
        Load raw course data from a JSON file or fetch from API by category.
        """
        # If source is a JSON file path, load it
        if self.source.lower().endswith('.json'):
            with open(self.source, 'r', encoding='utf-8') as f:
                return json.load(f)
        # Otherwise, treat source as a category name
        category = os.path.basename(self.source).replace(".category", "").strip()
        courses_by_cat = ChoiceFreakApi.get_courses_by_category()
        entries = courses_by_cat.get(category, [])
        # take first 10 course IDs
        ids = [c.get("id") for c in entries[:10]]
        # fetch details for these IDs
        return ChoiceFreakApi.get_courses_details(self.period, ids)

    def parse(self) -> List[Course]:
        """
        Parse the loaded raw data into a list of Course objects.
        """
        raw = self._load_raw()
        # If raw is a dict (single course), wrap into list
        if isinstance(raw, dict):
            raw = [raw]
        return [self._course_from_dict(d) for d in raw]

    def parse_by_ids(self, course_ids: List[str], university: str) -> List[Course]:
        """
        Fetch and parse courses by a list of course IDs.
        :param course_ids: List of course ID strings.
        :param university: University code (e.g., 'biu').
        :return: List of parsed Course objects.
        """
        raw = ChoiceFreakApi.get_courses_details(university, self.period, course_ids)
        if isinstance(raw, dict):
            raw = [raw]
        return [self._course_from_dict(d) for d in raw]