# Schedule King

A modern, user-friendly application for building student study schedules. Schedule King allows students to select courses, generate conflict-free schedules, and export them in various formats.

## Features

- **Course Selection**: Load course data from a text file and select courses via a modern UI.
- **Schedule Generation**: Automatically generates all possible conflict-free schedules based on selected courses.
- **Conflict Checking**: Ensures no time or room conflicts exist in the generated schedules.
- **Export Options**: Export schedules in both text and Excel formats.
- **Modern UI**: Built with PyQt5, featuring a responsive and intuitive interface.

## Requirements

- **Python**: Version 3.8 or higher
  - Download Python from [python.org](https://www.python.org/downloads/)
  - Make sure to check "Add Python to PATH" during installation
  - Verify installation by opening a terminal/command prompt and typing:
    ```bash
    python --version
    ```

## Project Structure

```
Schedule-King/
├── src/
│   ├── assets/           # Static assets (icons images)
│   ├── components/       # Reusable UI components
│   ├── controllers/      # Application controllers
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

## Running the Application

1. **Start the Application**:
   ```bash
   python main.py
   ```

2. **Using the Application**:
   - When the application starts, you'll see the course selection window
   - Click "Select File" to choose your course data file
   - Select the courses you want to include in your schedule
   - Click "Generate Schedules" to create all possible conflict-free schedules
   - Use the navigation controls to browse through different schedule options
   - Export your preferred schedule using the "Export" button

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

1. **Load Course Data**:
   - Click the "Select File" button in the course selection window
   - Choose a text file containing your course data
   - The application will parse and display available courses

Note : the input file need to be in the write the right format you can use txt files in tests/test_files dir 

2. **Select Courses**:
   - Check the boxes next to the courses you want to include
   - You can select multiple courses
   - The application will automatically check for conflicts between selected courses

3. **Generate Schedules**:
   - Click "Generate Schedules" to create all possible conflict-free combinations
   - A progress bar will show the generation status
   - Once complete, you'll be taken to the schedule view window

4. **View and Navigate Schedules**:
   - Use the navigation controls to browse through different schedule options
   - The current schedule number and total number of schedules are displayed
   - The schedule is displayed in a table format showing:
     - Course name and code
     - Session type (Lecture/Tirgul)
     - Day and time
     - Room and building numbers

5. **Export Schedules**:
   - Click the "Export" button to save your schedule
   - Choose between text (.txt) or Excel (.xlsx) format
   - Select whether to export all schedules or just the current one
   - Choose the save location and filename
   - The exported file will maintain the same format as the input file

**Note**: If you have more than 100 schedules and choose to export to Excel, only the last 100 schedules will be exported for performance reasons.

## Input/Output Formats

- **Input**: Text file (`.txt`) with course blocks separated by "$$$$".
- **Output**: 
  - Text file (`.txt`) with formatted schedule details.
  - Excel file (`.xlsx`) with styled schedule tables.

## Input File Format

The input file should be a text file (`.txt`) with the following format:

1. Each course is separated by `$$$$`
2. Each course block contains:
   - Course Name
   - Course Code
   - Instructor Name
   - Schedule Details (one or more lines)

3. Schedule Details Format:
   ```
   <Session Type> <Day> <Start Time>,<End Time>,<Room Number>,<Building Number>
   ```
   Where:
   - **Session Type**: 
     - `L` for Lecture
     - `T` for Tutorial
     - `M` for Meeting
   - **Day**: 
     - `S,1` for Sunday
     - `S,2` for Monday
     - `S,3` for Tuesday
     - `S,4` for Wednesday
     - `S,5` for Thursday
   - **Time**: 24-hour format (e.g., "09:00")
   - **Room Number**: The room identifier
   - **Building Number**: The building identifier

### Example Input File:
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

You can find example input files in the `tests/test_files` directory.
