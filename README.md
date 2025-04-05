# Software-for-building-a-student-study-schedule
This project is a Python-based application designed to help students create and manage their study schedules effectively. By taking input such as available time slots, subjects, and priorities, the software automatically generates a personalized study plan. The goal is to optimize study time and improve productivity, making it easier for students to stay organized and focused.

## Project Structure

```
/Software-for-building-a-student-study-schedule
├── src/                # Source code for the application
├── data/               # Sample data and datasets
├── docs/               # Documentation and resources
├── tests/              # Unit and integration tests
├── README.md           # Project README file
└── requirements.txt    # Python dependencies
```

## Running Instructions

1. **Clone the Repository**  
```bash
    git clone https://github.com/your-username/Software-for-building-a-student-study-schedule.git
    cd Software-for-building-a-student-study-schedule
```

2. **Install Dependencies**  
    Make sure you have Python installed. Then, install the required dependencies:
```bash
    pip install -r requirements.txt
 ```

3. **Run the Application**  
    Execute the main script to start the application:
```bash
    python src/main.py
```

4. **Run Tests**  
    To ensure everything is working correctly, run the tests:
```bash
    python -m pytest
```

## Features

- **Automatic Schedule Generation**: The application generates a study schedule based on input data such as available time slots, subjects, and priorities.
- **Validation**: Ensures that users select between 1 and 7 courses to generate a valid schedule.
- **Error Handling**: Provides warnings and error messages for invalid inputs, such as incorrect course codes.

### Input
The application takes the following inputs:
1. **Course Database File**: A text file containing course details (e.g., course name, course code, and other metadata).
2. **User Selection**: Users can select courses interactively or provide a list of course codes as input.

Example of a course database file:
```bash
Course Name: Mathematics, Code: MATH101
Course Name: Physics, Code: PHYS102
Course Name: Chemistry, Code: CHEM103
```

### Output
The application generates a formatted study schedule based on the selected courses. The output is saved to a specified file and may look like this:
```bsh
Schedule for Selected Courses:
1. Mathematics - Monday 10:00 AM to 12:00 PM
2. Physics - Wednesday 2:00 PM to 4:00 PM
3. Chemistry - Friday 9:00 AM to 11:00 AM
```

The output file can be found in the specified output path, such as:
```bash
C:\Desktop\Schedules\output.txt
```