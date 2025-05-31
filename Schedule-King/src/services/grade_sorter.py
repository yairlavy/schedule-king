

class GradeSorter:
    def __init__(self, upper_bound: float = 100):
        """
        Initializes the GradeSorter with upper and lower bounds for grades.
        :param upper_bound: The maximum grade value (default is 100).
        """
        self.upper_bound = upper_bound
        self.buckets = [[] for _ in range(int(upper_bound + 1))]  # Create buckets for each grade from 0 to upper_bound-1
        self.size = [0] * (int(upper_bound + 1))  # Initialize size for each bucket
        self.total_items = 0  # Total number of items added
    
    def insert(self, item, grade: int):
        """
        Inserts an item into the appropriate bucket based on its grade.
        :param item: The item to insert (e.g., a course or student).
        :param grade: The grade associated with the item.
        """
        if not (0 <= grade <= self.upper_bound):
            raise ValueError(f"Grade {grade} is out of bounds (0 to {self.upper_bound})")
        
        self.buckets[grade].append(item)
        self.size[grade] += 1
        self.total_items += 1
    
    def insert_chunk(self, items_grades: list):
        """
        Inserts a chunk of items with their associated grades.
        :param items_grades: A list of tuples (item, grade).
        """
        for item, grade in items_grades:
            self.insert(item, grade)
    
    def get_kth_item(self, k: int):
        """
        Retrieves the k-th item in the sorted order.
        :param k: The index of the item to retrieve (0-based).
        :return: The k-th item in sorted order.
        """
        if k < 0 or k >= self.total_items:
            raise IndexError(f"k={k} is out of bounds for total items {self.total_items}")
        
        count = 0
        for grade, bucket in enumerate(self.buckets):
            if count + self.size[grade] > k:
                return bucket[k - count]
            count += self.size[grade]
