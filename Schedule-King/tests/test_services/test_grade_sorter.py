import pytest
from src.services.grade_sorter import GradeSorter
def test_insert_and_get_kth_item():
    sorter = GradeSorter(upper_bound=10)
    sorter.insert("Alice", 7)
    sorter.insert("Bob", 3)
    sorter.insert("Charlie", 7)
    sorter.insert("David", 10)
    # Sorted order: Bob (3), Alice (7), Charlie (7), David (10)
    assert sorter.get_kth_item(0) == "Bob"
    assert sorter.get_kth_item(1) == "Alice"
    assert sorter.get_kth_item(2) == "Charlie"
    assert sorter.get_kth_item(3) == "David"

def test_insert_chunk_and_order():
    sorter = GradeSorter(upper_bound=5)
    items = [("A", 2), ("B", 5), ("C", 2), ("D", 0)]
    sorter.insert_chunk(items)
    # Sorted order: D (0), A (2), C (2), B (5)
    assert sorter.get_kth_item(0) == "D"
    assert sorter.get_kth_item(1) == "A"
    assert sorter.get_kth_item(2) == "C"
    assert sorter.get_kth_item(3) == "B"

def test_insert_invalid_grade_raises():
    sorter = GradeSorter(upper_bound=4)
    with pytest.raises(ValueError):
        sorter.insert("X", -1)
    with pytest.raises(ValueError):
        sorter.insert("Y", 5)

def test_get_kth_item_out_of_bounds():
    sorter = GradeSorter(upper_bound=2)
    sorter.insert("A", 1)
    with pytest.raises(IndexError):
        sorter.get_kth_item(-1)
    with pytest.raises(IndexError):
        sorter.get_kth_item(1)

def test_empty_sorter_raises_on_get():
    sorter = GradeSorter()
    with pytest.raises(IndexError):
        sorter.get_kth_item(0)
