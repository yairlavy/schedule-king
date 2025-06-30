# Schedule King

A modern, user-friendly application for building student study schedules. Schedule King enables students to select courses, generate all possible conflict-free schedules, and export them in various formats. The application features a polished PyQt5 interface and supports both local and online course data sources.

---

## Features

- **Intuitive Course Selection**: Load course data from a local file or fetch from the ChoiceFreak global database.
- **Automatic Schedule Generation**: Instantly generate all possible conflict-free schedules based on your selected courses and constraints.
- **Conflict Checking**: Ensures no time or room conflicts exist in generated schedules.
- **Advanced Constraints**: Specify forbidden and preferred time slots to tailor your schedule.
- **Schedule Ranking**: Sort and rank schedules by custom metrics (e.g., compactness, free days, etc.).
- **Export Options**: Export schedules in text, Excel, or calendar formats.
- **Modern UI**: Built with PyQt5, featuring a responsive, modular, and visually appealing interface.

---

## Requirements

- **Python**: Version 3.8 or higher
  - Download Python from [python.org](https://www.python.org/downloads/)
  - Ensure "Add Python to PATH" is checked during installation
  - Verify installation:
    ```bash
    python --version
    ```
- **Dependencies**: Listed in `requirements.txt` (see Installation)

---

## Project Structure

```
Schedule-King/
├── src/
│   ├── assets/           # Static assets (icons, images)
│   ├── components/       # Reusable UI components
│   ├── controllers/      # Application controllers (logic)
│   ├── interfaces/       # Interface definitions
│   ├── models/           # Core data models
│   ├── services/         # Business logic, scheduling, export, APIs
│   ├── styles/           # UI stylesheets (QSS, style helpers)
│   └── views/            # Main UI windows (course selection, schedule view)
├── tests/                # Unit and integration tests
├── main.py               # Application entry point
├── requirements.txt      # Production dependencies
└── dev-requirements.txt  # Development dependencies
```

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Schedule-King
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Application

1. **Start the Application:**
   ```bash
   python main.py
   ```
2. **Using the Application:**
   - The course selection window appears on launch.
   - Click **"Select File"** to load a local course data file, or choose **"ChoiceFreak"** to fetch from the global database.
   - Select your desired courses (multiple selection supported).
   - Optionally, set forbidden/preferred time slots for advanced scheduling.
   - Click **"Generate Schedules"** to create all possible conflict-free combinations.
   - Use navigation controls to browse schedule options.
   - Rank schedules by your preferred criteria.
   - Export your preferred schedule(s) as text, Excel, or calendar files.

---

## Running Tests

To ensure everything is working correctly, run the tests using `pytest`:

```bash
python -m pytest
```

Or use the custom test runner:

```bash
cd tests
python SuperTester.py
```

---

## Usage Overview

### 1. Load Course Data
- Click **"Select File"** to load a `.txt` file (see format below), or use **ChoiceFreak** for online data.
- Example input files are available in `tests/test_files`.

### 2. Select Courses
- Check the boxes next to the courses you want to include.
- The app automatically checks for conflicts between selected courses.

### 3. Set Constraints (Optional)
- Add forbidden or preferred time slots to further customize your schedule.

### 4. Generate Schedules
- Click **"Generate Schedules"** to create all possible conflict-free combinations.
- A progress bar shows generation status.
- Once complete, the schedule view window appears.

### 5. View, Rank, and Export Schedules
- Browse schedules using navigation controls.
- Rank schedules by metrics (e.g., compactness, free days).
- Export schedules as `.txt`, `.xlsx`, or calendar files (Google/iCal).
- For large numbers of schedules, only the last 100 are exported to Excel for performance.

---

## Input/Output Formats

### Input: Course Data File (`.txt`)
- Each course is separated by `$$$$`
- Each course block contains:
  - Course Name
  - Course Code
  - Instructor Name
  - Schedule Details (one or more lines)
- **Schedule Details Format:**
  ```
  <Session Type> <Day>,<Start Time>,<End Time>,<Room Number>,<Building Number>
  ```
  - **Session Type**: `L` (Lecture), `T` (Tutorial), `M` (Meeting)
  - **Day**: `S,1` (Sunday), `S,2` (Monday), ..., `S,5` (Thursday)
  - **Time**: 24-hour format (e.g., `09:00`)

#### Example Input File:
```
$$$$
Linear Algebra
10101
Dr. Emmy Noether
L S,1,09:00,11:00,1001,10
T S,2,13:00,14:00,1002,30
T S,4,12:00,13:00,1002,32
$$$$
Introduction to Programming
10102
Prof. Dennis Ritchie
L S,2,08:00,10:00,2001,11
T S,2,10:00,11:00,2002,35
T S,3,11:00,12:00,2002,36
M S,1,14:00,15:00,2005,46
$$$$
```

### Output
- **Text file (`.txt`)**: Human-readable, formatted schedule details.
- **Excel file (`.xlsx`)**: Styled tables, one sheet per schedule.
- **Calendar export**: Google Calendar/iCal integration (from schedule view window).

---

## Advanced Features

- **ChoiceFreak Integration**: Fetch course data from the ChoiceFreak global database.
- **Forbidden/Preferred Slots**: Fine-tune your schedule by blocking or preferring specific times.
- **Schedule Ranking**: Sort schedules by custom metrics (e.g., compactness, free days).
- **Export to Calendar**: Export schedules directly to Google Calendar or iCal.
- **Modern, Modular UI**: Built with reusable components for a seamless experience.

---
