# Software-for-building-a-student-study-schedule

This project is a Python-based application designed to help students create and manage their study schedules effectively. By taking input such as available time slots, subjects, and priorities, the software automatically generates a personalized study plan. The goal is to optimize study time and improve productivity, making it easier for students to stay organized and focused.

## Project Structure

````bash
/Software-for-building-a-student-study-schedule
├── src/                # Source code for the application
├── src/core/           # Core algorithms for course scheduling
├── src/api/            # API for the schedule functionality
├── src/data/           # Data classes and utilities for handling course and schedule data
├── src/tests/          # Unit and integration tests
├── README.md           # Project README file
├── requirements.txt    # Python dependencies
└── main.py             # Entry point for the application
````

## Running Instructions

Before running the application, ensure you have Python installed on your system. You can download and install Python from the official website: [https://www.python.org/downloads/](https://www.python.org/downloads/).

Follow these steps to run the application:

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
### Example Input Format

The application expects input in the following format for each course:

```bash
  $$$$
  <Course Name>
  <Course Code>
  <Instructor Name>
  <Schedule Details>
  $$$$
```

#### Explanation of the Format:
1. **Course Name**: The name of the course (e.g., "Calculus 1").
2. **Course Code**: A unique identifier for the course (e.g., "00001").
3. **Instructor Name**: The name of the instructor teaching the course (e.g., "Prof. O. Some").
4. **Schedule Details**: A list of sessions for the course, where each session is defined as:
  ```
  <Session Type> <Day> <Start Time>,<End Time>,<Room Number>,<Building Number>
  ```
  - **Session Type**: The type of session (e.g., "L" for Lecture, "T" for Tirgul, etc.).
  - **Day**: The day of the week (e.g., "S" for Sunday, "M" for Monday, etc.).
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
Note in test folder there are test files to try it out!

2. **User Selection**: Users can select courses interactively or provide a list of course codes as input.
3. **File Paths**:  
  - **Course Database File Path**: Provide the full path to the text file containing course details (e.g., `C:\Users\User\Documents\Courses\course_database.txt`).  
  - **Output File Path**: Specify the desired path for the output file (e.g., `C:\Users\User\Documents\Schedules\output.txt`). If the output file does not exist, the application will create it automatically.


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
