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
    python main.py
```

4. **Run Tests**  
To ensure everything is working correctly, you can run the tests using `pytest`:

```bash
python -m pytest
```

Alternatively, you can use the custom test runner `SuperTester.py`:

```bash
cd tests
python SuperTester.py
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
```bash
1. Calculus 1 (Code: 00001)
2. Software Project (Code: 83533)
3. Calculus 1 (eng) (Code: 83112)

Enter course codes (space-separated): 00001 83533 83112

Selected Courses:
- Calculus 1
- Software Project
- Calculus 1 (eng)
```

The output file can be found in the specified output path, such as:
```bash
C:\Desktop\Schedules\output.txt
```
and should look like this : 
````bash
------------------------------------------------------
Schedule 1:
Sunday:
  [Lecture] Calculus 1 (eng) (83112)
    14:00 - 16:00 |  Room 1401, Building 4
  [Tirgul] Calculus 1 (eng) (83112)
    16:00 - 18:00 |  Room 1104, Building 42

Monday:
  [Maabada] Calculus 1 (eng) (83112)
    14:00 - 16:00 |  Room 1300, Building 3
  [Lecture] Calculus 1 (00001)
    16:00 - 17:00 |  Room 1100, Building 22
  [Tirgul] Calculus 1 (00001)
    18:00 - 19:00 |  Room 1100, Building 22

Tuesday:
  [Maabada] Software Project (83533)
    14:00 - 16:00 |  Room 1300, Building 3

Thursday:
  [Lecture] Software Project (83533)
    10:00 - 16:00 |  Room 605, Building 061
  [Maabada] Calculus 1 (00001)
    14:00 - 16:00 |  Room 1300, Building 3
  [Tirgul] Software Project (83533)
    16:00 - 17:00 |  Room 605, Building 061
------------------------------------------------------
Schedule 2:
Sunday:
  [Lecture] Calculus 1 (eng) (83112)
    14:00 - 16:00 |  Room 1401, Building 4

Monday:
  [Maabada] Calculus 1 (eng) (83112)
    14:00 - 16:00 |  Room 1300, Building 3
  [Lecture] Calculus 1 (00001)
    16:00 - 17:00 |  Room 1100, Building 22
  [Tirgul] Calculus 1 (eng) (83112)
    17:00 - 18:00 |  Room 605, Building 14
  [Tirgul] Calculus 1 (00001)
    18:00 - 19:00 |  Room 1100, Building 22

Tuesday:
  [Maabada] Software Project (83533)
    14:00 - 16:00 |  Room 1300, Building 3

Thursday:
  [Lecture] Software Project (83533)
    10:00 - 14:00 |  Room 605, Building 061
  [Maabada] Calculus 1 (00001)
    14:00 - 16:00 |  Room 1300, Building 3
  [Tirgul] Software Project (83533)
    16:00 - 17:00 |  Room 605, Building 061
------------------------------------------------------
````
