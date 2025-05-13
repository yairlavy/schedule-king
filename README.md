# Schedule King

A modern, user-friendly application for building student study schedules. Schedule King allows students to select courses, generate conflict-free schedules, and export them in various formats.

## Features

- **Course Selection**: Load course data from a text file and select courses via a modern UI.
- **Schedule Generation**: Automatically generates all possible conflict-free schedules based on selected courses.
- **Conflict Checking**: Ensures no time or room conflicts exist in the generated schedules.
- **Export Options**: Export schedules in both text and Excel formats.
- **Modern UI**: Built with PyQt5, featuring a responsive and intuitive interface.

## Project Structure

```
Schedule-King/
├── src/
│   ├── assets/           # Static assets (icons, images)
│   ├── components/       # Reusable UI components
│   ├── controllers/      # Application controllers
│   ├── data/             # Data handling (parsers, formatters)
│   ├── interfaces/       # Interface definitions
│   ├── models/           # Core data models
│   ├── services/         # Business logic and utilities
│   ├── styles/           # UI stylesheets
│   └── views/            # UI views
├── tests/                # Test files
├── main.py               # Application entry point
├── requirements.txt      # Production dependencies
└── dev-requirements.txt  # Development dependencies
```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Schedule-King
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. For development, install additional dependencies:
   ```bash
   pip install -r dev-requirements.txt
   ```

## Run Tests
To ensure everything is working correctly, you can run the tests using `pytest`:

```bash
python -m pytest
```

Alternatively, you can use the custom test runner `SuperTester.py`:

```bash
cd tests
python SuperTester.py
```


## Usage

1. **Run the Application**:
   ```bash
   python main.py
   ```

2. **Load Course Data**:
   - Use the UI to select a course file (text format).
 
 **Explanation of the Course Format**:
1. **Course Name**: The name of the course (e.g., "Calculus 1").
2. **Course Code**: A unique identifier for the course (e.g., "00001").
3. **Instructor Name**: The name of the instructor teaching the course (e.g., "Prof. O. Some").
4. **Schedule Details**: A list of sessions for the course, where each session is defined as:
  ```
  <Session Type> <Day> <Start Time>,<End Time>,<Room Number>,<Building Number>
  ```
  - **Session Type**: The type of session (e.g., "L" for Lecture, "T" for Tirgul, etc.).
  - **Day**: The day of the week (e.g., "1" for Sunday, "2" for Monday, etc.).
  - **Start Time**: The starting time of the session in 24-hour format (e.g., "16:00").
  - **End Time**: The ending time of the session in 24-hour format (e.g., "17:00").
  - **Room Number**: The room where the session is held (e.g., "1100").
  - **Building Number**: The building where the session is held (e.g., "22").

#### Example Input:
```bash
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
$$$$
Calculus 1 (eng)
83112
Dr. Erez Scheiner
L S,1,14:00,16:00,1401,4 S,2,14:00,16:00,1401,4
T S,1,16:00,18:00,1104,42
T S,2,16:00,18:00,605,14
$$$$
```

3. **Select Courses**:
   - Choose courses from the loaded list.
   - The application will generate all possible conflict-free schedules.

4. **View and Export Schedules**:
   - Navigate through generated schedules using the UI.
   - Export schedules in text or Excel format.

## Input/Output Formats

- **Input**: Text file (`.txt`) with course blocks separated by "$$$$".
- **Output**: 
  - Text file (`.txt`) with formatted schedule details.
  - Excel file (`.xlsx`) with styled schedule tables.

## Development
- **Code Style**: The project uses black for formatting and flake8 for linting.

