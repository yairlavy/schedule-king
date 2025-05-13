import pytest
from src.services.file_handler import FileHandler
from src.models.course import Course
from src.models.time_slot import TimeSlot

# ——— RAW_DATA———
RAW_DATA = """
$$$$
Calculus 1
00001
Prof. O. Some
L S,2,16:00,17:00,1100,22 S,3,17:00,18:00,1100,42
T S,2,18:00,19:00,1100,22
T S,3,19:00,20:00,1100,42
$$$$
Software Project
83533
Dr. Terry Bell
L S,5,10:00,16:00,605,061
T S,5,16:00,17:00,605,061
""".strip()

# A dummy Schedule for TextFormatter testing
class DummySchedule:
    def __init__(self, day_map):
        self._dm = day_map
    def extract_by_day(self):
        return self._dm

# ——— FileHandler.parse Tests ———————————————————————————————————————
def test_filehandler_parse_txt(tmp_path):
    #Test parsing a .txt file 
    f = tmp_path / "in.txt"
    f.write_text(RAW_DATA, encoding="utf-8")

    courses = FileHandler.parse(str(f))
    assert isinstance(courses, list)
    assert all(isinstance(c, Course) for c in courses)

def test_filehandler_parse_missing_file(tmp_path):
    # Test parsing non-existing file to see if it raises FileNotFoundError
    missing = tmp_path / "nope.txt"
    with pytest.raises(FileNotFoundError):
        FileHandler.parse(str(missing))

def test_filehandler_parse_unsupported_ext(tmp_path):
    # Test parsing unsupported file extension to see if it raises ValueError
    f = tmp_path / "data.csv"
    f.write_text("someting", encoding="utf-8")
    with pytest.raises(ValueError) as exc:
        FileHandler.parse(str(f))
    assert "No parser registered for extension '.csv'" in str(exc.value)

# ——— FileHandler.format Tests ————————————————————————————————————————
def test_filehandler_format_creates_file(tmp_path):
    # Test if FileHandler.format creates the output file
    out_path = tmp_path / "out" / "s.txt"
    
    # Dummy schedule list with one schedule 
    slot = TimeSlot("1", "08:00", "09:00", "11", "12")
    Schedule = DummySchedule({"1":[("Lecture","Math","41",slot)]})

    FileHandler.format([Schedule], str(out_path))

    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert "Lecture" in content
    assert "Schedule 1" in content

def test_filehandler_format_nested_dirs(tmp_path):
    # Test if FileHandler.format creates nested directories for the output file when needed
    nested = tmp_path / "a" / "b" / "c" / "s.txt"
    slot = TimeSlot("1", "08:00", "09:00", "11", "12")
    Schedule = DummySchedule({"1":[("Lecture","Math","41",slot)]})

    FileHandler.format([Schedule], str(nested))
    assert nested.exists()

def test_filehandler_format_unsupported_ext(tmp_path):
    # Test if FileHandler.format raises ValueError for unsupported file extension
    dest = tmp_path / "o.csv"
    slot = TimeSlot("1", "08:00", "09:00", "11", "12")
    Schedule = DummySchedule({"1":[("Lecture","Math","41",slot)]})

    with pytest.raises(ValueError) as exc:
        FileHandler.format([Schedule], str(dest))
    assert "No formatter registered for extension '.csv'" in str(exc.value)