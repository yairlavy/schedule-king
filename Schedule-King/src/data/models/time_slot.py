from datetime import datetime, time  

# This class represents a time slot for a class or event.
# It includes the day of the week, start and end times, room number, and building name.
# It also includes methods for checking conflicts with other time slots and validating the data.

class TimeSlot:
    # Constructor to initialize a TimeSlot object with day, start time, end time, room, and building.
    def __init__(self, day: str, start_time: str, end_time: str, room: str, building: str):
        self._day = day
        self._start_time = datetime.strptime(start_time, "%H:%M").time()
        self._end_time = datetime.strptime(end_time, "%H:%M").time()
        self._room = room
        self._building = building
        
    # Method to check if this time slot conflicts with another time slot.
    def conflicts_with(self, other):
        return (self.day == other.day and self.start_time < other.end_time and self.end_time > other.start_time)
        
    # Method to return a string representation of the time slot.
    def __str__(self):
        return f"S,{self.day},{self.start_time},{self.end_time},{self.room},{self.building}"
    
    # Method to calculate the duration of the time slot in minutes.
    def duration(self):
        start_dt = datetime.combine(datetime.min, self.start_time)
        end_dt = datetime.combine(datetime.min, self.end_time)
        return (end_dt - start_dt).seconds // 60
    
    # Method to validate the attributes of the time slot.
    def validate(self):
        if not self.day in ["1", "2", "3", "4", "5", "6"]:
            raise ValueError("Invalid day")
        if not isinstance(self.start_time, time) or not isinstance(self.end_time, time):
            raise ValueError("Invalid time format")
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")
        if not isinstance(self.room, str) or not isinstance(self.building, str):
            raise ValueError("Invalid room or building format")
        if len(self.room) == 0 or len(self.building) == 0:
            raise ValueError("Room and building cannot be empty")
        if not self.room.isalnum() or not self.building.isalnum():
            raise ValueError("Room and building must be alphanumeric")
        
    # Property to get the day of the time slot.
    @property
    def day(self):
        return self._day

    # Property to get the start time of the time slot.
    @property
    def start_time(self):
        return self._start_time

    # Property to get the end time of the time slot.
    @property
    def end_time(self):
        return self._end_time

    # Property to get the room of the time slot.
    @property
    def room(self):
        return self._room

    # Property to get the building of the time slot.
    @property
    def building(self):
        return self._building