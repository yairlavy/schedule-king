from .time_slot import TimeSlot

class LectureGroup:
    """
    A class to represent a group of lectures, tirguls, and maabadas for a course.
    """

    def __init__(self, course_name: str, course_code: str, instructor: str,
                 lecture: TimeSlot, tirguls: TimeSlot, maabadas: TimeSlot):
        """
        Initialize a LectureGroup instance.

        Args:
            course_name (str): The name of the course.
            course_code (str): The code of the course.
            instructor (str): The name of the instructor.
            lecture (TimeSlot): The time slot for the lecture.
            tirguls (TimeSlot): The time slot for the tirguls.
            maabadas (TimeSlot): The time slot for the maabadas.
        """
        self._course_name = course_name
        self._course_code = course_code
        self._instructor = instructor
        self._lecture = lecture
        self._tirguls = tirguls
        self._maabadas = maabadas    

    @property
    def course_name(self):
        """
        Get the name of the course.

        Returns:
            str: The course name.
        """
        return self._course_name

    @property
    def course_code(self):
        """
        Get the code of the course.

        Returns:
            str: The course code.
        """
        return self._course_code

    @property
    def instructor(self):
        """
        Get the name of the instructor.

        Returns:
            str: The instructor's name.
        """
        return self._instructor

    @property
    def lecture(self):
        """
        Get the time slot for the lecture.

        Returns:
            TimeSlot: The lecture time slot.
        """
        return self._lecture    

    @property
    def tirguls(self):
        """
        Get the time slot for the tirguls.

        Returns:
            TimeSlot: The tutorial time slot.
        """
        return self._tirguls

    @property
    def maabadas(self):
        """
        Get the time slot for the maabadas.

        Returns:
            TimeSlot: The labs time slot.
        """
        return self._maabadas

    def __str__(self):
        """
        Return a string representation of the LectureGroup instance.

        Returns:
            str: A string containing course details and time slots.
        """
        return f"LectureGroup({self.course_code}, {self.course_name}, {self.instructor}, {self.lecture}, {self.tirguls}, {self.maabadas})"
