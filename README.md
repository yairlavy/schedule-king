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

## Usage

1. **Run the Application**:
   ```bash
   python main.py
   ```

2. **Load Course Data**:
   - Use the UI to select a course file (text format).
   - The expected input format is a text file with course blocks separated by "$$$$". Each block should include:
     - Course name
     - Course code
     - Instructor name
     - Time slots for lectures (L), tutorials (T), and labs (M) in the format: `S,5,14:00,16:00,1300,1`

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

- **Testing**: Run tests using pytest:
  ```bash
  pytest
  ```

- **Code Style**: The project uses black for formatting and flake8 for linting.

