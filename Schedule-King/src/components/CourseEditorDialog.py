from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
    QListWidget, QListWidgetItem, QTimeEdit, QFrame, QFormLayout, QDialogButtonBox, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTime, QPoint
from PyQt5.QtGui import QColor, QBrush, QMouseEvent
from typing import List, Optional, Dict, Any, Tuple
from src.models.course import Course
from src.models.time_slot import TimeSlot
from src.styles.ui_styles import green_button_style, red_button_style, blue_button_style
from collections import defaultdict
from datetime import datetime, time, timedelta

# --- New Dialog for simple time slot block creation (only room, building, type) ---
class SimpleTimeSlotInputDialog(QDialog):
    """
    Dialog for creating a new time slot block template (room, building, type).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Time Slot Block")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # This dialog now returns a tuple (room, building, slot_type)
        self.slot_template_data: Optional[Tuple[str, str, str]] = None

        layout = QFormLayout()

        # Room and Building inputs
        self.room_input = QLineEdit()
        self.room_input.setPlaceholderText("Example: 101")
        layout.addRow("Room:", self.room_input)

        self.building_input = QLineEdit()
        self.building_input.setPlaceholderText("Example: Engineering")
        layout.addRow("Building:", self.building_input)

        # Type selection
        self.type_combo = QComboBox()
        self.type_combo.addItem("Lecture", userData="lecture")
        self.type_combo.addItem("Tirgul", userData="tirgul")
        self.type_combo.addItem("Maabada", userData="maabada")
        layout.addRow("Slot Type:", self.type_combo)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_slot_template_data(self) -> Optional[Tuple[str, str, str]]:
        """Returns (room, building, type_str) or None if cancelled/invalid."""
        return self.slot_template_data

    def accept(self):
        """
        Validate input and set slot_template_data if valid.
        """
        room = self.room_input.text().strip()
        building = self.building_input.text().strip()
        slot_type = self.type_combo.currentData()

        if not (room and building and slot_type):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        self.slot_template_data = (room, building, slot_type)
        super().accept()

# --- Course Time Slot Table ---
class CourseTimeSlotTable(QTableWidget):
    """
    A QTableWidget subclass to display and manage time slots for a course component.
    It supports multi-hour spans and colored cells based on slot type.
    Allows click-and-drag for filling/removing cells.
    """
    # Adjusted DAY_NAMES to 6 days to align with TimeSlot.validate
    DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    # Map day number string to column index
    DAY_TO_COL = {str(i+1): i for i in range(len(DAY_NAMES))}
    # Map hour (8-19) to row index
    HOUR_TO_ROW = {hour: hour - 8 for hour in range(8, 20)}
    ROW_TO_HOUR = {row: hour for hour, row in HOUR_TO_ROW.items()}

    # Color mapping for slot types
    COLOR_MAP = {
        "lecture": QColor(173, 216, 230, 178), # Light blue for lecture
        "tirgul": QColor(255, 218, 185, 178), # Light orange for tirgul
        "maabada": QColor(144, 238, 144, 178), # Light green for maabada
        "selected_add": QColor(255, 255, 0, 100) # Yellow for currently selected cells for addition
    }

    def __init__(self, editor_dialog_ref, parent=None): # Added editor_dialog_ref
        super().__init__(parent)
        self._editor_dialog_ref = editor_dialog_ref # Store the explicit reference

        self.setColumnCount(len(self.DAY_NAMES))
        self.setHorizontalHeaderLabels(self.DAY_NAMES)
        self.setRowCount(12) # For hours 8:00 to 19:00 (12 hours)
        self.setVerticalHeaderLabels([f"{hour}:00-{hour+1}:00" for hour in range(8, 20)])

        self.setSelectionMode(QTableWidget.ExtendedSelection) # Allow multiple cell selection
        self.setSelectionBehavior(QTableWidget.SelectItems) # Select individual cells
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(38)

        self.setShowGrid(True)
        self.setMinimumHeight(350)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Stores TimeSlot objects along with their type: {(row, col): (TimeSlot, type_str)}
        # This will hold the *start* of the TimeSlot, even if it spans multiple hours.
        self._displayed_slots_start_cells: Dict[Tuple[int, int], Tuple[TimeSlot, str]] = {}

        # Dragging state variables (from original v7)
        self._is_dragging = False
        self._drag_start_cell_coords: Optional[Tuple[int, int]] = None
        self._drag_mode: Optional[str] = None # 'add' or 'remove'
        self._active_block_template_for_drag: Optional[Tuple[str, str, str]] = None # (room, building, type_str)
        
        self.setMouseTracking(True) # Enable mouse tracking for drag events
        self.viewport().setMouseTracking(True) # Also for the viewport

        self.clear_all_slots()
        self.itemSelectionChanged.connect(self._update_selection_highlight) # Connect selection signal

    def get_slot_data_at_coords(self, row: int, col: int) -> Optional[Tuple[TimeSlot, str]]:
        """
        Finds the TimeSlot object and its type that occupies the given cell, considering spans.
        Returns a (TimeSlot, type_str) tuple or None if the cell is empty.
        """
        # Iterate through starting cells to find the slot that covers the clicked cell
        for (s_row, s_col), (slot_obj, s_type) in self._displayed_slots_start_cells.items():
            if s_col == col:  # Same column
                # Calculate the row span of the current slot
                span_rows = max(1, slot_obj.end_time.hour - slot_obj.start_time.hour)
                # Check if the given row falls within this slot's span
                if s_row <= row < (s_row + span_rows):
                    return (slot_obj, s_type)
        return None

    def set_active_block_template(self, template: Optional[Tuple[str, str, str]]):
        """Sets the currently active block template for drag-and-drop operations."""
        self._active_block_template_for_drag = template

    def _update_selection_highlight(self):
        """
        Highlights currently selected cells (yellow) and resets unselected cells.
        """
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if not item:
                    item = QTableWidgetItem("")
                    self.setItem(row, col, item)

                # Check if this cell is part of any active slot's span
                is_part_of_active_slot = False
                active_slot_type = None
                for (s_row, s_col), (slot_obj, slot_type) in self._displayed_slots_start_cells.items():
                    if s_col == col:
                        span_rows = max(1, slot_obj.end_time.hour - slot_obj.start_time.hour)
                        if s_row <= row < (s_row + span_rows):
                            is_part_of_active_slot = True
                            active_slot_type = slot_type
                            break

                if item.isSelected():
                    if not is_part_of_active_slot: # Only highlight if it's an empty cell
                        item.setBackground(QBrush(self.COLOR_MAP["selected_add"]))
                else:
                    # Reset background for unselected cells
                    if is_part_of_active_slot:
                        # If it's a displayed course slot, reset to its original color
                        item.setBackground(QBrush(self.COLOR_MAP.get(active_slot_type, QColor(200, 200, 200, 150))))
                    else:
                        # If it's an empty cell, reset to white
                        item.setBackground(QBrush(QColor(255, 255, 255)))

    def add_course_time_slot(self, time_slot: TimeSlot, slot_type: str) -> bool:
        """
        Adds a single TimeSlot to the table and displays it, handling multi-hour spans.
        Returns True if added successfully, False otherwise.
        """
        try:
            day_col = self.DAY_TO_COL.get(time_slot.day)
            start_hour = time_slot.start_time.hour
            start_row = self.HOUR_TO_ROW.get(start_hour)

            # Calculate span in terms of rows (hours) from TimeSlot's start and end hours
            span_rows = max(1, time_slot.end_time.hour - time_slot.start_time.hour)

            if day_col is None or start_row is None:
                print(f"Warning: Invalid time/day format for slot: {time_slot}")
                return False

            if span_rows <= 0:
                return False

            # Check for overlaps for all cells this new timeslot would cover
            for r_offset in range(span_rows):
                target_row = start_row + r_offset
                if not (0 <= target_row < self.rowCount()):
                    return False # Out of bounds

                # Check if this cell is part of an existing merged slot's span
                for (existing_s_row, existing_s_col), (existing_slot_obj, _) in self._displayed_slots_start_cells.items():
                    if existing_s_col == day_col: # same day
                        existing_span_rows = max(1, existing_slot_obj.end_time.hour - existing_slot_obj.start_time.hour)
                        # Check if 'target_row' falls within the span of 'existing_slot_obj'
                        if existing_s_row <= target_row < (existing_s_row + existing_span_rows):
                            print(f"Warning: Cell ({target_row}, {day_col}) overlaps with existing slot {existing_slot_obj.room} from {existing_slot_obj.start_time.strftime('%H:%M')}-{existing_slot_obj.end_time.strftime('%H:%M')}")
                            return False # Overlap detected

            # Store the TimeSlot object and its type in the _displayed_slots_start_cells for the *starting cell*
            key = (start_row, day_col)
            self._displayed_slots_start_cells[key] = (time_slot, slot_type)

            # Apply span and set item for the first cell
            item = QTableWidgetItem(f"{time_slot.room} | {time_slot.building}\n"
                                     f"({time_slot.start_time.strftime('%H:00')}-{time_slot.end_time.strftime('%H:00')})")
            item.setData(Qt.UserRole, (time_slot, slot_type)) # Store (TimeSlot, type) tuple
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(QBrush(self.COLOR_MAP.get(slot_type, QColor(200, 200, 200, 150))))
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable) # Make non-selectable (so click/drag handles removal)

            if span_rows > 1:
                self.setSpan(start_row, day_col, span_rows, 1)
            self.setItem(start_row, day_col, item)

            # For subsequent cells in the span, clear them but color them.
            # They don't get their own item in _displayed_slots_start_cells
            for r_offset in range(1, span_rows):
                spanned_row = start_row + r_offset
                spanned_item = QTableWidgetItem("")
                spanned_item.setBackground(QBrush(self.COLOR_MAP.get(slot_type, QColor(200, 200, 200, 150))))
                spanned_item.setFlags(spanned_item.flags() & ~Qt.ItemIsSelectable)
                self.setItem(spanned_row, day_col, spanned_item)
            return True

        except Exception as e:
            print(f"Error adding time slot: {e}")
            return False

    def remove_course_time_slot_at_coords(self, row: int, col: int) -> Optional[Tuple[TimeSlot, str]]:
        """
        Removes a specific time slot from the table based on row and column.
        Handles spans by finding the start of the span and clearing all covered cells.
        Returns the removed (TimeSlot, type_str) tuple if successful, else None.
        """
        # Find the actual TimeSlot object that occupies this cell, considering spans
        slot_data_to_remove: Optional[Tuple[TimeSlot, str]] = None
        start_row_of_slot: Optional[int] = None
        
        # Check if the clicked cell is a starting point of a slot
        clicked_key_candidate = (row, col)
        if clicked_key_candidate in self._displayed_slots_start_cells:
            slot_data_to_remove = self._displayed_slots_start_cells[clicked_key_candidate]
            start_row_of_slot = row
        else: # If not a starting point, it might be a spanned cell
            # Iterate through starting cells to find the slot that covers the clicked cell
            for (s_row, s_col), (slot_obj, s_type) in list(self._displayed_slots_start_cells.items()):
                if s_col == col: # Same column
                    current_slot_span = max(1, slot_obj.end_time.hour - slot_obj.start_time.hour)
                    if s_row <= row < (s_row + current_slot_span): # This slot spans the clicked cell
                        slot_data_to_remove = (slot_obj, s_type)
                        start_row_of_slot = s_row
                        break

        if slot_data_to_remove and start_row_of_slot is not None:
            removed_slot_obj, removed_slot_type = slot_data_to_remove
            
            # Remove the entry for the starting cell from our internal tracking
            del self._displayed_slots_start_cells[(start_row_of_slot, col)]

            span_rows = max(1, removed_slot_obj.end_time.hour - removed_slot_obj.start_time.hour)

            # Explicitly reset span only if it was greater than 1
            if span_rows > 1:
                self.setSpan(start_row_of_slot, col, 1, 1)

            # Clear all cells that were part of this slot's span
            for r_offset in range(span_rows):
                spanned_row = start_row_of_slot + r_offset
                item = self.item(spanned_row, col)
                if item: # If there's an item, clear its text, reset background, and make selectable
                    item.setText("")
                    item.setBackground(QBrush(QColor(255, 255, 255))) # Reset to white
                    item.setFlags(item.flags() | Qt.ItemIsSelectable) # Make selectable again
                else: # If no item, create a new one to set background and flags
                    new_item = QTableWidgetItem("")
                    new_item.setBackground(QBrush(QColor(255, 255, 255)))
                    new_item.setFlags(new_item.flags() | Qt.ItemIsSelectable)
                    self.setItem(spanned_row, col, new_item)

            return slot_data_to_remove
        return None

    def get_selected_cell_coordinates(self) -> List[Tuple[int, int]]:
        """Returns a list of (row, col) tuples for all currently selected cells."""
        return [(item.row(), item.column()) for item in self.selectedItems()]

    def get_all_time_slots_by_type(self) -> Dict[str, List[TimeSlot]]:
        """
        Returns a dictionary of lists of TimeSlot objects, categorized by type.
        { "lecture": [...], "tirgul": [...], "maabada": [...] }
        Only extracts slots from the starting cells in _displayed_slots_start_cells.
        """
        categorized_slots = defaultdict(list)
        for _, (slot, slot_type) in self._displayed_slots_start_cells.items():
            categorized_slots[slot_type].append(slot)
        return dict(categorized_slots)

    def clear_all_slots(self):
        """
        Clears all displayed time slots and internal tracking.
        Also resets all cell backgrounds and flags.
        """
        # 1. Explicitly remove all existing cell spans. This is the crucial fix.
        self.clearSpans()
        
        # 2. Clear the contents (text, data) of all items.
        self.clearContents()
        self._displayed_slots_start_cells.clear()
        
        # 3. Loop through every cell to ensure it's reset to a default, visible state.
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if not item:
                    item = QTableWidgetItem("")
                    self.setItem(row, col, item)
                
                # Reset background to white
                item.setBackground(QBrush(QColor(255, 255, 255)))
                
                # Reset flags to make the cell selectable and enabled, restoring the grid.
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                
    def populate_with_course_slots(self, lectures: List[TimeSlot], tirguls: List[TimeSlot], maabadas: List[TimeSlot]):
        """
        Populates the table with given lists of lectures, tirguls, and maabadas.
        """
        self.clear_all_slots() # Start fresh

        for slot in lectures:
            self.add_course_time_slot(slot, "lecture")
        for slot in tirguls:
            self.add_course_time_slot(slot, "tirgul")
        for slot in maabadas:
            self.add_course_time_slot(slot, "maabada")

    def _convert_coords_to_timeslot(self, row: int, col: int, room: str, building: str) -> Optional[TimeSlot]:
        """
        Converts table coordinates to a TimeSlot object, assuming 1-hour slots.
        """
        day_str = str(col + 1) # Convert column index back to day number string
        start_hour_default = self.ROW_TO_HOUR.get(row)
        
        if start_hour_default is None:
            print("Warning: Invalid start hour for selected cell.")
            return None
        
        start_time_str = f"{start_hour_default:02d}:00"
        end_time_str = f"{start_hour_default+1:02d}:00"

        try:
            return TimeSlot(
                day=day_str,
                start_time=start_time_str,
                end_time=end_time_str,
                room=room,
                building=building
            )
        except Exception as e:
            print(f"Error creating time slot from coords: {e}")
            return None

    # Mouse events for drag-and-drop (copied from v7, adjusted for v3's _displayed_slots)
    def mousePressEvent(self, event: QMouseEvent):
        """
        Handles mouse press for drag-and-drop add/remove of slots.
        """
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid():
                row, col = index.row(), index.column()
                
                # Determine if the clicked cell is part of an existing slot's span
                slot_data_at_click: Optional[Tuple[TimeSlot, str]] = None
                for (s_row, s_col), (slot_obj, slot_type) in self._displayed_slots_start_cells.items():
                    if s_col == col: # Same column
                        span_rows = max(1, slot_obj.end_time.hour - slot_obj.start_time.hour)
                        if s_row <= row < (s_row + span_rows):
                            slot_data_at_click = (slot_obj, slot_type)
                            break

                if slot_data_at_click: # Cell is already occupied by a slot
                    self._drag_mode = 'remove'
                    self._drag_start_cell_coords = (row, col) # Store original clicked cell for removal
                    # Trigger initial removal via _editor_dialog_ref
                    self._editor_dialog_ref._handle_table_cell_action(row, col, self._drag_mode, slot_data_at_click[1])
                elif self._active_block_template_for_drag: # Cell is empty and a template is active
                    self._drag_mode = 'add'
                    self._drag_start_cell_coords = (row, col)
                    # Trigger initial add via _editor_dialog_ref
                    self._editor_dialog_ref._handle_table_cell_action(row, col, self._drag_mode, self._active_block_template_for_drag[2])
                self._is_dragging = True
                self.clearSelection() # Clear selection to prevent yellow highlight interfering with drag

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Handles mouse move for drag-and-drop add/remove of slots.
        """
        super().mouseMoveEvent(event)
        if self._is_dragging and self._drag_mode:
            index = self.indexAt(event.pos())
            if index.isValid():
                row, col = index.row(), index.column()
                # Only act if cell has changed from previous drag position
                if (row, col) != self._drag_start_cell_coords:
                    # Determine the type hint ONLY for 'add' mode. For 'remove', the handler discovers the type.
                    # This prevents a crash if _active_block_template_for_drag is None or an invalid value during remove.
                    type_hint = None
                    if self._drag_mode == 'add' and self._active_block_template_for_drag:
                        type_hint = self._active_block_template_for_drag[2]

                    self._editor_dialog_ref._handle_table_cell_action(row, col, self._drag_mode, type_hint)
                    self._drag_start_cell_coords = (row, col) # Update last processed cell
                    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Handles mouse release for drag-and-drop add/remove of slots.
        """
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton and self._is_dragging:
            self._is_dragging = False
            self._drag_start_cell_coords = None
            self._drag_mode = None
            self.clearSelection() # Ensure selection is cleared after drag ends

# --- Main Course Editor Dialog ---
class CourseEditorDialog(QDialog):
    """
    Main dialog for adding/editing a course and its schedule options.
    """
    courseEdited = pyqtSignal(Course)

    def __init__(self, all_courses: List[Course], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add / Edit Course")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.all_courses = all_courses
        self._current_course: Optional[Course] = None

        # Data structure for managing multiple schedule options (pages)
        # Each item in the outer list is a dict for one schedule option:
        # { "lecture": [TimeSlot, ...], "tirgul": [TimeSlot, ...], "maabada": [TimeSlot, ...] }
        self._all_schedule_options: List[Dict[str, List[TimeSlot]]] = []
        self._current_schedule_option_index: int = -1 # Index of the currently displayed schedule option

        # Stores the currently selected "block template" from the right-side list
        self._active_block_template: Optional[Tuple[str, str, str]] = None # (room, building, type_str)

        self._init_ui()

    def _init_ui(self):
        """
        Initializes the dialog UI layout and widgets.
        """
        main_layout = QHBoxLayout(self)

        # === Left Side: Main Time Slot Tables (Tabbed) ===
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("<b>Course Time Slots:</b>"))

        self.schedule_options_tab_widget = QTabWidget(self) # Make QTabWidget a child of CourseEditorDialog
        self.schedule_options_tab_widget.setMinimumHeight(400)
        self.schedule_options_tab_widget.currentChanged.connect(self._on_schedule_option_tab_changed)
        left_layout.addWidget(self.schedule_options_tab_widget)

        # Buttons for managing schedule options (pages)
        schedule_option_buttons_layout = QHBoxLayout()
        self.add_schedule_option_button = QPushButton("Add Schedule Option")
        self.add_schedule_option_button.setStyleSheet(blue_button_style())
        self.add_schedule_option_button.clicked.connect(self._add_new_schedule_option)
        schedule_option_buttons_layout.addWidget(self.add_schedule_option_button)

        self.remove_schedule_option_button = QPushButton("Remove Current Option")
        self.remove_schedule_option_button.setStyleSheet(red_button_style())
        self.remove_schedule_option_button.clicked.connect(self._remove_current_schedule_option)
        schedule_option_buttons_layout.addWidget(self.remove_schedule_option_button)
        left_layout.addLayout(schedule_option_buttons_layout)

        main_layout.addLayout(left_layout, 2)

        # === Right Side: Course Details & Time Slot Controls ===
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)

        # Course Selection / New Course Section
        course_selection_layout = QHBoxLayout()
        self.course_combo = QComboBox()
        self.course_combo.addItem("--- Select Course to Edit or Create New ---")
        for course in self.all_courses:
            self.course_combo.addItem(f"{course.name} ({course.course_code})", userData=course)
        self.course_combo.currentIndexChanged.connect(self._on_course_selected)
        course_selection_layout.addWidget(QLabel("Select Course:"))
        course_selection_layout.addWidget(self.course_combo)
        right_layout.addLayout(course_selection_layout)

        # Course Details Inputs
        right_layout.addWidget(QLabel("<b>Course Details:</b>"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Course Name (e.g.: Linear Algebra 1)")
        right_layout.addWidget(self.name_input)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Course Code (e.g.: 83014)")
        right_layout.addWidget(self.code_input)

        self.instructor_input = QLineEdit()
        self.instructor_input.setPlaceholderText("Instructor Name")
        right_layout.addWidget(self.instructor_input)

        right_layout.addSpacing(20)

        # === New Time Slot Block Creation Button ===
        self.add_new_slot_block_button = QPushButton("Add Time Slot Block")
        self.add_new_slot_block_button.setStyleSheet(blue_button_style())
        self.add_new_slot_block_button.clicked.connect(self._open_new_time_slot_block_dialog)
        right_layout.addWidget(self.add_new_slot_block_button)

        # === Current Time Slot Blocks List (displaying templates) ===
        right_layout.addWidget(QLabel("<b>Available Time Slot Blocks (Select to Fill):</b>"))
        self.available_block_templates_list_widget = QListWidget() # Correct widget name
        self.available_block_templates_list_widget.setMinimumHeight(150)
        self.available_block_templates_list_widget.itemClicked.connect(self._on_block_template_selected)
        right_layout.addWidget(self.available_block_templates_list_widget)

        # Remove selected block template from list
        self.remove_block_template_button = QPushButton("Remove Selected Template Block")
        self.remove_block_template_button.setStyleSheet(red_button_style())
        self.remove_block_template_button.clicked.connect(self._remove_selected_block_template)
        right_layout.addWidget(self.remove_block_template_button)

        right_layout.addStretch(1) # Push content to the top

        # Save/Cancel Buttons (at the bottom of the right layout)
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Course")
        self.save_button.setStyleSheet(green_button_style())
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet(red_button_style())
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        right_layout.addLayout(button_layout)
        main_layout.addLayout(right_layout, 1) # Give less space to the right controls

        self.setLayout(main_layout)
        self.setMinimumSize(1200, 700) # Ensure enough space for the new layout

        # Initialize with empty fields for new course
        self._clear_fields()

    def _clear_fields(self):
        """
        Clears all input fields and resets the dialog state.
        """
        self.name_input.clear()
        self.code_input.clear()
        self.instructor_input.clear()

        # Clear all tabs and reset schedule options data
        self.schedule_options_tab_widget.clear()
        self._all_schedule_options.clear()
        self._current_schedule_option_index = -1

        self.available_block_templates_list_widget.clear()

        self._current_course = None
        self.course_combo.setCurrentIndex(0)
        self._active_block_template = None
        
        # If no schedule options, add a default one for a new course
        self._add_new_schedule_option(initial_load=True)

    def _on_course_selected(self, index: int):
        """
        Loads data for the selected course into the dialog fields and table.
        """
        if index == 0: # "--- Select Course to Edit or Create New ---"
            self._clear_fields()
        else:
            selected_course: Course = self.course_combo.currentData()
            if selected_course:
                self._current_course = selected_course
                self.name_input.setText(selected_course.name)
                self.code_input.setText(selected_course.course_code)
                self.instructor_input.setText(selected_course.instructor)
                
                # Clear existing tabs and schedule options data
                self.schedule_options_tab_widget.clear()
                self._all_schedule_options.clear()
                self._current_schedule_option_index = -1

                # Populate _all_schedule_options from the selected course's data
                # Assuming lectures, tirguls, maabadas are parallel lists of lists
                max_options = max(len(selected_course.lectures), len(selected_course.tirguls), len(selected_course.maabadas))

                if max_options == 0: # If no schedule options, add a default empty one
                    self._add_new_schedule_option(initial_load=True)
                else:
                    for i in range(max_options):
                        lectures_for_option = selected_course.lectures[i] if i < len(selected_course.lectures) else []
                        tirguls_for_option = selected_course.tirguls[i] if i < len(selected_course.tirguls) else []
                        maabadas_for_option = selected_course.maabadas[i] if i < len(selected_course.maabadas) else []
                        
                        schedule_option_data = {
                            "lecture": lectures_for_option,
                            "tirgul": tirguls_for_option,
                            "maabada": maabadas_for_option
                        }
                        # Merge slots within this option after loading
                        self._merge_time_slots_in_option(schedule_option_data)
                        self._all_schedule_options.append(schedule_option_data)
                        
                        # Create a new tab and populate its table
                        tab_name = f"Option {i + 1}"
                        # Pass 'self' (the CourseEditorDialog instance) as editor_dialog_ref
                        table_widget = CourseTimeSlotTable(editor_dialog_ref=self, parent=self.schedule_options_tab_widget)
                        self.schedule_options_tab_widget.addTab(table_widget, tab_name)
                        table_widget.populate_with_course_slots(
                            schedule_option_data["lecture"],
                            schedule_option_data["tirgul"],
                            schedule_option_data["maabada"]
                        )
                    self.schedule_options_tab_widget.setCurrentIndex(0) # Select the first tab
                    self._current_schedule_option_index = 0

                self._populate_available_block_templates_list_widget()
                self._active_block_template = None
                self.available_block_templates_list_widget.clearSelection() # Clear selection in block list
                # Set active template on the current table if any tab is selected
                if self._current_schedule_option_index != -1:
                    current_table = self.schedule_options_tab_widget.currentWidget()
                    if current_table:
                        current_table.set_active_block_template(None)

    def _on_schedule_option_tab_changed(self, index: int):
        """
        Updates the current schedule option index and repopulates block templates when a tab changes.
        """
        self._current_schedule_option_index = index
        self._populate_available_block_templates_list_widget() # Refresh block templates based on all slots
        
        # Pass the active block template to the newly selected table
        if self._active_block_template and self.schedule_options_tab_widget.currentWidget():
            self.schedule_options_tab_widget.currentWidget().set_active_block_template(self._active_block_template)

    def _add_new_schedule_option(self, initial_load: bool = False):
        """
        Adds a new empty schedule option (tab) to the QTabWidget.
        """
        new_option_data = {"lecture": [], "tirgul": [], "maabada": []}
        self._all_schedule_options.append(new_option_data)

        # Pass 'self' (the CourseEditorDialog instance) as editor_dialog_ref
        new_table_widget = CourseTimeSlotTable(editor_dialog_ref=self, parent=self.schedule_options_tab_widget)
        tab_name = f"Option {len(self._all_schedule_options)}"
        self.schedule_options_tab_widget.addTab(new_table_widget, tab_name)
        self.schedule_options_tab_widget.setCurrentIndex(len(self._all_schedule_options) - 1) # Select new tab

        if not initial_load:
            QMessageBox.information(self, "New Option", f"New schedule option '{tab_name}' added.")
            self._populate_available_block_templates_list_widget() # Refresh after adding

    def _remove_current_schedule_option(self):
        """
        Removes the currently selected schedule option (tab) from the QTabWidget.
        """
        if self._current_schedule_option_index == -1:
            QMessageBox.warning(self, "Error", "No schedule option selected.")
            return
        
        if len(self._all_schedule_options) == 1:
            QMessageBox.warning(self, "Error", "Cannot remove the last schedule option. A course must include at least one option.")
            return

        reply = QMessageBox.question(self, "Remove Schedule Option",
                                     f"Are you sure you want to remove the current schedule option ({self.schedule_options_tab_widget.tabText(self._current_schedule_option_index)})? This action is irreversible.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        self._all_schedule_options.pop(self._current_schedule_option_index)
        self.schedule_options_tab_widget.removeTab(self._current_schedule_option_index)
        
        # Adjust current index if the last tab was removed or if current index is out of bounds
        if self._current_schedule_option_index >= len(self._all_schedule_options):
            self._current_schedule_option_index = len(self._all_schedule_options) - 1
        
        if self._current_schedule_option_index != -1:
            self.schedule_options_tab_widget.setCurrentIndex(self._current_schedule_option_index)
        else: # No tabs left
            self._clear_fields() # Effectively reset to new course state with one empty tab
        
        self._populate_available_block_templates_list_widget() # Refresh after removing
        QMessageBox.information(self, "Removal Completed", "Schedule option removed successfully.")

    def _populate_available_block_templates_list_widget(self):
        """
        Populates the right-side list widget with all unique time slot block templates
        found across ALL current schedule options.
        """
        self.available_block_templates_list_widget.clear()

        unique_templates = set() # Use a set to avoid duplicates

        for option_data in self._all_schedule_options:
            for slot_type, slots_list in option_data.items():
                for slot in slots_list:
                    # Add (room, building, type) tuple to the set
                    unique_templates.add((slot.room, slot.building, slot_type))

        # Convert set back to list for sorting, or just iterate directly
        for room, building, slot_type in sorted(list(unique_templates)): # Sort for consistent order
            display_text = f"Room: {room} | Building: {building} ({slot_type})"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, (room, building, slot_type)) # Store (room, building, type_str) tuple
            
            # Set background color directly using QBrush
            color = CourseTimeSlotTable.COLOR_MAP.get(slot_type, QColor(200, 200, 200, 150))
            item.setBackground(QBrush(color))

            self.available_block_templates_list_widget.addItem(item)

    def _open_new_time_slot_block_dialog(self):
        """
        Opens a dialog to create a new TimeSlot block template.
        """
        dialog = SimpleTimeSlotInputDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # The dialog now returns a tuple: (room, building, slot_type)
            template_data = dialog.get_slot_template_data()
            if not template_data:
                return
                
            room, building, slot_type = template_data
            new_template = (room, building, slot_type)

            # Check if this template is already in the list widget to avoid duplicates
            is_duplicate = False
            for i in range(self.available_block_templates_list_widget.count()):
                item = self.available_block_templates_list_widget.item(i)
                if item.data(Qt.UserRole) == new_template:
                    is_duplicate = True
                    # If it's a duplicate, just select the existing one and activate it
                    self.available_block_templates_list_widget.setCurrentItem(item)
                    self._on_block_template_selected(item)
                    QMessageBox.information(self, "Template Exists", "This block template already exists.")
                    break
            
            # If it's a new, unique template, add it directly to the list widget.
            # This avoids adding a "dummy" TimeSlot to the actual schedule data.
            if not is_duplicate:
                display_text = f"Room: {room} | Building: {building} ({slot_type})"
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, new_template) # Store (room, building, type_str)
                
                # Set background color to match the slot type
                color = CourseTimeSlotTable.COLOR_MAP.get(slot_type, QColor(200, 200, 200, 150))
                item.setBackground(QBrush(color))
                
                self.available_block_templates_list_widget.addItem(item)
                
                # Automatically select and activate the new template so the user can use it immediately
                self.available_block_templates_list_widget.setCurrentItem(item)
                self._on_block_template_selected(item)
                
                QMessageBox.information(self, "Template Block Created", "New time slot block added to templates list and ready for use.")

    def _remove_selected_block_template(self):
        """
        Removes the selected time slot block template from the right-side list
        and also removes all associated TimeSlot instances from ALL schedule options.
        """
        selected_item = self.available_block_templates_list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Error", "Please select a template block to remove.")
            return

        reply = QMessageBox.question(self, "Remove Template Block",
                                     f"Are you sure you want to remove the template block '{selected_item.text()}'? This action will also remove all time slots in the table linked to this block from all options.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        template_room, template_building, template_type = selected_item.data(Qt.UserRole)

        # Iterate through all schedule options and remove matching slots
        for option_data in self._all_schedule_options:
            slots_to_keep = [
                slot for slot in option_data[template_type]
                if not (slot.room == template_room and slot.building == template_building)
            ]
            option_data[template_type] = slots_to_keep # Update the list in place

        # Remove the template item from the list widget
        self.available_block_templates_list_widget.takeItem(self.available_block_templates_list_widget.row(selected_item))
        
        # If the removed template was the active one, clear it
        if self._active_block_template == (template_room, template_building, template_type):
            self._active_block_template = None
            if self.schedule_options_tab_widget.currentWidget():
                self.schedule_options_tab_widget.currentWidget().set_active_block_template(None)

        # Repopulate all tables to reflect changes
        self._refresh_all_schedule_tables()
        self._populate_available_block_templates_list_widget() # Refresh list based on remaining actual slots

        QMessageBox.information(self, "Removal Completed", "Template block and all linked time slots removed successfully.")

    def _on_block_template_selected(self, item: QListWidgetItem):
        """
        Sets the active block template for filling the table when a template is selected from the list.
        """
        self._active_block_template = item.data(Qt.UserRole) # This is (room, building, type_str)
        if self.schedule_options_tab_widget.currentWidget():
            self.schedule_options_tab_widget.currentWidget().set_active_block_template(self._active_block_template)
            self.schedule_options_tab_widget.currentWidget().clearSelection() # Clear any previous table selection

    def _handle_table_cell_action(self, row: int, col: int, action_mode: str, slot_type_hint: Optional[str] = None):
        """
        Handles actions (add/remove) on a table cell by modifying the data model
        and then triggering a full refresh.
        """
        if self._current_schedule_option_index == -1:
            return

        current_table: CourseTimeSlotTable = self.schedule_options_tab_widget.currentWidget()
        current_option_data = self._all_schedule_options[self._current_schedule_option_index]

        if action_mode == 'remove':
            # Find the slot to remove
            slot_data = current_table.get_slot_data_at_coords(row, col)

            if slot_data:
                slot_obj, slot_type = slot_data

                if slot_obj in current_option_data[slot_type]:
                    current_option_data[slot_type].remove(slot_obj)

                    # Refresh view
                    self._merge_time_slots_in_option(current_option_data)
                    self._refresh_all_schedule_tables()
                    # Removed: self._populate_available_block_templates_list_widget()

        elif action_mode == 'add':
            if not current_table.get_slot_data_at_coords(row, col) and self._active_block_template:
                room, building, slot_type = self._active_block_template

                new_slot = current_table._convert_coords_to_timeslot(
                    row=row, col=col, room=room, building=building
                )

                if new_slot and slot_type_hint:
                    current_option_data[slot_type_hint].append(new_slot)
                    self._merge_time_slots_in_option(current_option_data)
                    self._refresh_all_schedule_tables()
                    # Removed: self._populate_available_block_templates_list_widget()

        current_table.clearSelection()

    def _merge_time_slots_in_option(self, option_data: Dict[str, List[TimeSlot]]):
        """
        Applies the merging logic to all types of time slots within a given schedule option.
        """
        for slot_type in option_data.keys():
            option_data[slot_type] = self._merge_consecutive_time_slots_list(option_data[slot_type])

    def _merge_consecutive_time_slots_list(self, slots: List[TimeSlot]) -> List[TimeSlot]:
        """
        Merges consecutive time slots of the same room and building on the same day.
        """
        if not slots:
            return []

        # Group by (day, room, building)
        grouped_slots = defaultdict(list)
        for slot in slots:
            # Ensure start_time and end_time are datetime.time objects for sorting key
            # and potentially for direct comparison if TimeSlot objects hold them as such.
            s_time_obj = slot.start_time if isinstance(slot.start_time, time) else datetime.strptime(slot.start_time, "%H:%M").time()
            e_time_obj = slot.end_time if isinstance(slot.end_time, time) else datetime.strptime(slot.end_time, "%H:%M").time()
            
            # Store TimeSlot objects as they are, but ensure they contain time objects if TimeSlot class handles it.
            # The issue indicates TimeSlot's start_time/end_time are already time objects.
            grouped_slots[(slot.day, slot.room, slot.building)].append(slot)

        merged_results = []
        for (day, room, building), daily_slots in grouped_slots.items():
            # Sort slots by their start time, assuming start_time is a datetime.time object
            daily_slots.sort(key=lambda s: s.start_time)

            if not daily_slots:
                continue

            current_merged_slot = daily_slots[0]
            
            for i in range(1, len(daily_slots)):
                next_slot = daily_slots[i]
                
                # Directly compare datetime.time objects
                # current_merged_slot.end_time is already a datetime.time object
                # next_slot.start_time is already a datetime.time object
                if next_slot.start_time == current_merged_slot.end_time:
                    # Merge: Extend the end time of the current_merged_slot
                    # Create a new TimeSlot object with the updated end time
                    current_merged_slot = TimeSlot(
                        current_merged_slot.day,
                        current_merged_slot.start_time.strftime("%H:%M"), # Format to string for constructor
                        next_slot.end_time.strftime("%H:%M"),             # Format to string for constructor
                        current_merged_slot.room,
                        current_merged_slot.building
                    )
                else:
                    # Not consecutive, add the current_merged_slot to results and start a new one
                    merged_results.append(current_merged_slot)
                    current_merged_slot = next_slot
            
            # Add the last (or only) merged slot to results
            merged_results.append(current_merged_slot)
        
        return merged_results

    def _refresh_all_schedule_tables(self):
        """
        Refreshes all CourseTimeSlotTable instances in the QTabWidget.
        """
        for i, option_data in enumerate(self._all_schedule_options):
            table_widget = self.schedule_options_tab_widget.widget(i)
            if table_widget and isinstance(table_widget, CourseTimeSlotTable):
                table_widget.populate_with_course_slots(
                    option_data["lecture"],
                    option_data["tirgul"],
                    option_data["maabada"]
                )

    def get_course_data(self) -> Optional[Course]:
        """
        Retrieves the Course object with its updated time slots from the dialog.
        This method is called after accept() to get the updated course.
        """
        return self._current_course

    def accept(self):
        """
        Validates input and emits the courseEdited signal.
        """
        course_name = self.name_input.text().strip()
        course_code = self.code_input.text().strip()
        instructor = self.instructor_input.text().strip()

        if not course_name or not course_code or not instructor:
            QMessageBox.warning(self, "Input Error", "Please fill in all course details (Name, Code, Instructor).")
            return

        if not self._all_schedule_options:
            QMessageBox.warning(self, "Input Error", "A course must include at least one schedule option.")
            return

        # Prepare lists of lists of TimeSlots for the Course model from _all_schedule_options
        final_lectures_data = [option["lecture"] for option in self._all_schedule_options]
        final_tirguls_data = [option["tirgul"] for option in self._all_schedule_options]
        final_maabadas_data = [option["maabada"] for option in self._all_schedule_options]

        if self._current_course:
            # Update existing course
            self._current_course._name = course_name
            self._current_course._course_code = course_code
            self._current_course._instructor = instructor
            self._current_course._lectures = final_lectures_data
            self._current_course._tirguls = final_tirguls_data
            self._current_course._maabadas = final_maabadas_data
        else:
            # Create new course
            self._current_course = Course(
                course_name=course_name,
                course_code=course_code,
                instructor=instructor,
                lectures=final_lectures_data,
                tirguls=final_tirguls_data,
                maabadas=final_maabadas_data
            )
        
        self.courseEdited.emit(self._current_course)
        super().accept()