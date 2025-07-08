from PyQt5.QtCore import Qt, pyqtSignal
from src.models.time_slot import TimeSlot
from typing import List, Optional, Dict, Tuple, Any
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
from PyQt5.QtGui import QColor, QBrush, QMouseEvent

class CourseTimeSlotTable(QTableWidget):
    '''A table widget for displaying and managing course time slots.'''
    # Signal emitted when a cell action occurs (e.g., add/remove course slot)
    cellAction = pyqtSignal(int, int, str, str)  # row, col, action_mode ('add'/'remove'), slot_type (lecture/tirgul/maabada) 

    COLOR_MAP = {
        "lecture": QColor(173, 216, 230, 178), # Light blue for lectures
        "tirgul": QColor(255, 218, 185, 178), # light orange for tirguls
        "maabada": QColor(144, 238, 144, 178), # Light green for maabadas
    }
    default_cell_color = QColor(255, 255, 255) # White color for empty cells

    # Constants for day names, hour ranges, and mappings
    DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    HOUR_RANGE = range(8, 20)
    DAY_TO_COL = {str(i + 1): i for i in range(len(DAY_NAMES))}
    HOUR_TO_ROW = {hour: hour - 8 for hour in HOUR_RANGE}
    ROW_TO_HOUR = {row: hour for hour, row in HOUR_TO_ROW.items()}
    
    def __init__(self, parent=None):
        # Initialize the table grid with days as columns and hours as rows
        super().__init__(parent)
        self.setColumnCount(len(self.DAY_NAMES))
        self.setHorizontalHeaderLabels(self.DAY_NAMES)
        self.setRowCount(len(self.HOUR_RANGE))
        self.setVerticalHeaderLabels([f"{hour}:00-{hour+1}:00" for hour in self.HOUR_RANGE])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Set vertical header to fixed size
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(38)
        
        # Set minimum size and show grid lines
        self.setMinimumHeight(350)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setShowGrid(True)

        # Mouse tracking and selection settings
        # Allow mouse dragging and selection and disable editing
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.setSelectionMode(QTableWidget.ExtendedSelection)
        self.setSelectionBehavior(QTableWidget.SelectItems)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Initialize a dictionary to track displayed slots and their start cells
        self.displayed_slots_start_cells: Dict[Tuple[int, int], Tuple[TimeSlot, str]] = {}
        
        # Dragging state variables
        self.dragging = False
        self.action_mode = None  # 'add' or 'remove'
        self.drag_start_cell = None
        
        # Active time slot block for drag operations
        self.active_time_slot_block_for_drag: Optional[Tuple[str, str, str]] = None
        
        # clear all slots and connect selection change signal
        #self.clear_all_slots()

    def set_item_visual_state(self, row: int, col: int, color: QBrush, text: str = "", slot_data: Optional[Any] = None):
        """Helper method to set the visual state of a table item."""
        # Get the item at the specified row and column
        item = self.item(row, col)
        
        # If item does not exist, create a new one, and set its default flags
        if item is None:
            item = QTableWidgetItem()
            self.setItem(row, col, item)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled) # Set default flags when created
        
        # Set the item's text, background color, and alignment
        item.setText(text)
        item.setBackground(color)
        item.setTextAlignment(Qt.AlignCenter)
        
        # Set user data
        if slot_data is not None:
            item.setData(Qt.UserRole, slot_data)
        else:
            item.setData(Qt.UserRole, None) # Clear user data if not provided

    def get_slot_data_at_coords(self, row: int, col: int) -> Optional[Tuple[TimeSlot, str]]:
        """Retrieve the slot data at the specified table coordinates if it valid."""
        for (s_row, s_col), (slot, slot_type) in self.displayed_slots_start_cells.items():
            if s_col == col and s_row <= row < s_row + (slot.end_time.hour - slot.start_time.hour):
                return (slot, slot_type)
        return None

    def set_active_time_slot_block(self, time_slot: Optional[Tuple[str, str, str]]):
        """Set the active time slot block for drag operations."""
        self.active_time_slot_block_for_drag = time_slot

    def add_course_time_slot(self, time_slot: TimeSlot, slot_type: str) -> bool:
        """Add a course time slot to the table if it doesn't overlap with existing slots."""
        # Convert time slot to table coordinates
        col = self.DAY_TO_COL[time_slot.day]
        start_row = self.HOUR_TO_ROW[time_slot.start_time.hour]
        end_row = self.HOUR_TO_ROW[time_slot.end_time.hour - 1]  # -1 because end is exclusive
        span_rows = end_row - start_row + 1
        
        # Check for overlaps
        if any(self.get_slot_data_at_coords(r, col) for r in range(start_row, end_row + 1)):
            return False
            
        # Add to tracking dictionary
        key = (start_row, col)
        self.displayed_slots_start_cells[key] = (time_slot, slot_type)
        
        # Prepare slot display data, Set color and text
        slot_color = self.COLOR_MAP.get(slot_type, QColor(200, 200, 200, 150))
        slot_text = (f"{time_slot.room} | {time_slot.building}\n"
                    f"({time_slot.start_time.strftime('%H:%M')}-{time_slot.end_time.strftime('%H:%M')})")
        
        # Set main cell
        main_item = QTableWidgetItem(slot_text)
        main_item.setBackground(QBrush(slot_color))
        main_item.setTextAlignment(Qt.AlignCenter)
        main_item.setData(Qt.UserRole, (time_slot, slot_type))
        main_item.setFlags(Qt.ItemIsEnabled)  # Main cell not selectable
        self.setItem(start_row, col, main_item)
        
        # Set span and secondary cells if multi-hour
        if span_rows > 1:
            self.setSpan(start_row, col, span_rows, 1)
            for r in range(start_row + 1, end_row + 1):
                span_item = QTableWidgetItem()
                span_item.setBackground(QBrush(slot_color))
                span_item.setFlags(Qt.ItemIsEnabled)  # Span cells not selectable
                self.setItem(r, col, span_item)
                
        return True

    def remove_course_time_slot_at_coords(self, row: int, col: int) -> Optional[Tuple[TimeSlot, str]]:
        """Remove the slot covering (row, col), and reset its cells."""
        # Find the slot at (row, col). Bail if empty.
        slot_data = self.get_slot_data_at_coords(row, col)
        if not slot_data:
            return None
        slot_obj, slot_type = slot_data

        # Compute how many rows it spans
        span = slot_obj.end_time.hour - slot_obj.start_time.hour

        # Get the start cell of the block
        start_row, start_col = row, col

        # Remove from our tracking dict
        del self.displayed_slots_start_cells[(start_row, start_col)]

        # If it was a multi-row span, clear that span
        if span > 1:
            self.setSpan(start_row, start_col, 1, 1)

        # Reset each cell in the former block to white/selectable
        for r in range(start_row, start_row + span):
            item = self.item(r, start_col)
            if item:
                item.setText("")  # clear any text
                item.setData(Qt.UserRole, None)
                item.setBackground(QBrush(self.default_cell_color))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        return slot_data
    
    def clear_all_slots(self):
        """Clears all displayed slots, spans, and resets all cells to default state."""
        # Clear multi-row spans (block) slots
        self.clearSpans()
        # Reset all cells to default color and empty text by using set_item_visual_state 
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                 self.set_item_visual_state(row, col, QBrush(self.default_cell_color), "", 
                                            slot_data=None)
        self.displayed_slots_start_cells.clear()

    def populate_with_course_slots(self, lectures: List[TimeSlot], tirguls: List[TimeSlot], maabadas: List[TimeSlot]):
        '''Populate the table with course time slots for lectures, tirguls, and maabadas.'''
        self.clear_all_slots()
        for slot in lectures:
            self.add_course_time_slot(slot, "lecture")
        for slot in tirguls:
            self.add_course_time_slot(slot, "tirgul")
        for slot in maabadas:
            self.add_course_time_slot(slot, "maabada")

    def convert_cell_coords_to_timeslot(self, row: int, col: int, room: str, building: str) -> Optional[TimeSlot]:
        '''Convert table cell coordinates to a TimeSlot object based on the row and column indices.'''
        day_str = str(col + 1)
        start_hour = self.ROW_TO_HOUR.get(row)
        if start_hour is None:
            return None
        try:
            return TimeSlot(
                day=day_str,
                start_time=f"{start_hour:02d}:00", # Make 8 to "08:00", 19 to "19:00"
                end_time=f"{start_hour + 1:02d}:00",
                room=room,
                building=building
            )
        except Exception:
            return None

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events to update the drag state and emit cell actions."""
        super().mouseMoveEvent(event)
        # If not dragging, do nothing
        if self.dragging and self.action_mode:
            # Find which cell the mouse is currently over
            index = self.indexAt(event.pos())
            if index.isValid():
                row, col = index.row(), index.column()
                # If the mouse is over a different cell than where the drag started
                if (row, col) != self.drag_start_cell:
                    # Determine the slot_type: for 'add' mode use the active block's type, else empty
                    slot_type = (
                        self.active_time_slot_block_for_drag[2]
                        if self.action_mode == 'add' and self.active_time_slot_block_for_drag
                        else ""
                    )
                    # Inform listeners that the user is performing this action on (row, col)
                    self.cellAction.emit(row, col, self.action_mode, slot_type)
                    # Update start_cell so we don’t re-emit for this same cell
                    self.drag_start_cell = (row, col)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events for drag-and-drop functionality."""
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            # Find which cell the mouse is currently over
            index = self.indexAt(event.pos())
            if index.isValid():
                row, col = index.row(), index.column()
                # Store where the drag began
                self.drag_start_cell = (row, col)
                # Check if that cell already has a slot
                slot_data = self.get_slot_data_at_coords(row, col)
                
                # If occupied, switch into remove mode
                if slot_data:
                    self.action_mode = 'remove'
                    # Emit remove signal with the existing slot's type
                    self.cellAction.emit(row, col, self.action_mode, slot_data[1])
                
                # If empty and user has selected a block template, switch to add mode
                elif self.active_time_slot_block_for_drag:
                    self.action_mode = 'add'
                    # Emit add signal with the template's slot_type
                    self.cellAction.emit(row, col, self.action_mode, self.active_time_slot_block_for_drag[2])
                
                # Mark dragging as started and clear any built-in selection highlight
                self.dragging = True
                self.clearSelection()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events to finalize drag-and-drop actions."""
        super().mouseReleaseEvent(event)
        # Only act on left-button release if we were dragging
        if event.button() == Qt.LeftButton and self.dragging:
            # End the drag operation and reset the dragging state 
            self.dragging = False
            self.drag_start_cell = None
            self.action_mode = None
            self.clearSelection()