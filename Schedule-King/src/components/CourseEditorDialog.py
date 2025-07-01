from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel, QComboBox,
    QListWidget, QListWidgetItem, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush
from typing import List, Optional, Dict, Tuple
from src.models.course import Course
from src.models.time_slot import TimeSlot
from src.styles.ui_styles import green_button_style, red_button_style, blue_button_style
from collections import defaultdict
from src.components.course_time_slot_table import CourseTimeSlotTable
from src.components.create_time_slot_dialog import CreateTimeSlotDialog

class CourseEditorDialog(QDialog):
    # Signal emitted when a course is edited or created
    courseEdited = pyqtSignal(Course)

    def __init__(self, all_courses: List[Course], parent=None):
        '''Initialize the Course Editor Dialog.'''
        super().__init__(parent)
        # Initialize dialog properties
        self.setWindowTitle("Add / Edit Course")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Initialize internal state variables
        self.all_courses = all_courses # List of all courses available for editing
        self.current_course: Optional[Course] = None # Currently selected course, if any
        self.all_schedule_options: List[Dict[str, List[TimeSlot]]] = [] # List of all schedule options for the current course
        self.current_schedule_option_index: int = -1 # Index of the currently selected schedule option tab
        self.active_block_template: Optional[Tuple[str, str, str]] = None # Currently active time slot block template (room, building, type)
        self._init_ui() # Initialize the UI components
   
    def _init_ui(self):
        '''
        Constructs all UI elements and lays them out in a two-pane dialog:
          - Left pane: tabs containing CourseTimeSlotTable widgets for each schedule option
          - Right pane: course details form and block template list
        '''       
        main_layout = QHBoxLayout(self)

        # --- Left pane: Schedule Options ---
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("<b>Course Time Slots:</b>"))
        
        # Create a tab widget to hold multiple schedule options
        self.schedule_options_tab_widget = QTabWidget(self)
        self.schedule_options_tab_widget.setMinimumHeight(400)
        # Rebuild template list when the current tab changes
        self.schedule_options_tab_widget.currentChanged.connect(self.on_schedule_option_tab_changed)
        left_layout.addWidget(self.schedule_options_tab_widget)
        
        # Buttons to add schedule options
        schedule_option_buttons_layout = QHBoxLayout()
        self.add_schedule_option_button = QPushButton("Add Schedule Option")
        self.add_schedule_option_button.setStyleSheet(blue_button_style())
        self.add_schedule_option_button.clicked.connect(self.add_new_schedule_option)
        schedule_option_buttons_layout.addWidget(self.add_schedule_option_button)
        
        # Button to remove the current schedule option
        self.remove_schedule_option_button = QPushButton("Remove Current Option")
        self.remove_schedule_option_button.setStyleSheet(red_button_style())
        self.remove_schedule_option_button.clicked.connect(self.remove_current_schedule_option)
        schedule_option_buttons_layout.addWidget(self.remove_schedule_option_button)
        
        # finalize the left layout
        left_layout.addLayout(schedule_option_buttons_layout)
        main_layout.addLayout(left_layout, 2)
        
        # --- Right pane: Course Details and Block Templates ---
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)
       
        # Combo box (Dropdown) to select existing course or start new course
        course_selection_layout = QHBoxLayout()
        self.course_combo = QComboBox()
        self.course_combo.addItem("--- Select Course to Edit or Create New ---") # Placeholder for new course
        
        # Populate the Dropdown with existing courses
        for course in self.all_courses:
            # Limit course name to 50 characters, add '...' if exceeded
            display_name = course.name
            if len(display_name) > 40:
                display_name = display_name[:40] + '...'
            self.course_combo.addItem(f"{display_name} ({course.course_code})", userData=course)
        
        # Data of the selected course will be loaded when the selection changes
        self.course_combo.currentIndexChanged.connect(self.on_course_selected)
        course_selection_layout.addWidget(QLabel("Select Course:"))
        course_selection_layout.addWidget(self.course_combo)
        right_layout.addLayout(course_selection_layout)
        
        # Course details input fields
        right_layout.addWidget(QLabel("<b>Course Details:</b>"))
        
        # Input field for course name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Course Name (e.g.: Linear Algebra 1)")
        right_layout.addWidget(self.name_input)
        
        # Input field for course code
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Course Code (e.g.: 83014)")
        right_layout.addWidget(self.code_input)
        
        # Input field for instructor name
        self.instructor_input = QLineEdit()
        self.instructor_input.setPlaceholderText("Instructor Name")
        right_layout.addWidget(self.instructor_input)
        
        right_layout.addSpacing(20) # Add some vertical space
        
        # Button to add a new time slot block
        self.add_new_slot_block_button = QPushButton("Add Time Slot Block")
        self.add_new_slot_block_button.setStyleSheet(blue_button_style())
        self.add_new_slot_block_button.clicked.connect(self.open_new_time_slot_block_dialog)
        right_layout.addWidget(self.add_new_slot_block_button)
        
        # List widget to display available time slot blocks
        right_layout.addWidget(QLabel("<b>Available Time Slot Blocks (Select to Fill):</b>"))
        self.available_block_templates_list_widget = QListWidget()
        self.available_block_templates_list_widget.setMinimumHeight(150)
        self.available_block_templates_list_widget.itemClicked.connect(self.on_block_selected)
        right_layout.addWidget(self.available_block_templates_list_widget)
        
        # Button to remove selected time slot block
        self.remove_block_template_button = QPushButton("Remove Selected Template Block")
        self.remove_block_template_button.setStyleSheet(red_button_style())
        self.remove_block_template_button.clicked.connect(self.remove_selected_block)
        right_layout.addWidget(self.remove_block_template_button)
        
        right_layout.addStretch(1) # Add stretch to push buttons to the bottom
        button_layout = QHBoxLayout()
        
        # Button to save the course
        self.save_button = QPushButton("Save Course")
        self.save_button.setStyleSheet(green_button_style())
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.save_button)
        
        # Button to cancel and close the dialog
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet(red_button_style())
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # finalize the right layout 
        right_layout.addLayout(button_layout)
        main_layout.addLayout(right_layout, 1)
        
        # finalize the dialog layout
        self.setLayout(main_layout)
        self.setMinimumSize(1200, 700)
        self.clear_all_fields()

    def clear_all_fields(self):
        '''        
        Clears all input fields, removes existing tabs, and adds one empty schedule option.
        Called when creating a new course or resetting the form.
        '''
        # Clear text inputs
        self.name_input.clear()
        self.code_input.clear()
        self.instructor_input.clear()
        
        self.schedule_options_tab_widget.clear() # Remove all schedule option tabs

        # Reset internal schedule data
        self.all_schedule_options.clear()
        self.current_schedule_option_index = -1
        
        self.available_block_templates_list_widget.clear() # Clear templates list
        
        # Reset course tracking
        self.current_course = None
        self.course_combo.setCurrentIndex(0)
        self.active_block_template = None

        self.add_new_schedule_option()

    def on_course_selected(self, index: int):
        ''' when a course is selected from the dropdown, this method loads its data into the form.'''
        # If index is 0, it means "Create New Course" was selected
        if index == 0:
            self.clear_all_fields()
            return
        
        # Otherwise, load the selected course's data into the form fields
        selected_course: Course = self.course_combo.currentData()
        if selected_course:
            # populate the input fields
            self.current_course = selected_course
            self.name_input.setText(selected_course.name)
            self.code_input.setText(selected_course.course_code)
            self.instructor_input.setText(selected_course.instructor)
            
            # Clear existing schedule options and populate with the selected course's data
            self.schedule_options_tab_widget.clear()
            self.all_schedule_options.clear()
            self.current_schedule_option_index = -1
            
            # Determine the maximum number of options available
            max_options = max(len(selected_course.lectures), len(selected_course.tirguls), len(selected_course.maabadas))
            
            # If no options exist, add an empty option
            if max_options == 0:
                self.add_new_schedule_option()
            
            # Otherwise, populate the schedule options with existing data
            else:
                # Create one tab per existing option
                for i in range(max_options):
                    schedule_option_data = {
                        "lecture": selected_course.lectures[i] if i < len(selected_course.lectures) else [],
                        "tirgul": selected_course.tirguls[i] if i < len(selected_course.tirguls) else [],
                        "maabada": selected_course.maabadas[i] if i < len(selected_course.maabadas) else []
                    }

                    # Merge contiguous slots in each list
                    self.merge_time_slots(schedule_option_data)
                    self.all_schedule_options.append(schedule_option_data)
                    
                    # Create a new CourseTimeSlotTable for this option
                    table_widget = CourseTimeSlotTable(parent=self.schedule_options_tab_widget)
                    table_widget.cellAction.connect(self.handle_table_cell_action)
                    self.schedule_options_tab_widget.addTab(table_widget, f"Option {i + 1}")
                    table_widget.populate_with_course_slots(schedule_option_data["lecture"], schedule_option_data["tirgul"], schedule_option_data["maabada"])
                
                # Set the current index to the first option
                self.schedule_options_tab_widget.setCurrentIndex(0)
                self.current_schedule_option_index = 0
            
            # Populate the available block templates list widget
            self.populate_available_block_list()
            self.active_block_template = None
            self.available_block_templates_list_widget.clearSelection()

    def restore_active_block_selection(self):
        '''
        Helper function 
        Finds and re-selects the active block template in the list widget if it exists.
        '''
        if self.active_block_template is not None:
            for i in range(self.available_block_templates_list_widget.count()):
                item = self.available_block_templates_list_widget.item(i)
                if item.data(Qt.UserRole) == self.active_block_template:
                    self.available_block_templates_list_widget.setCurrentItem(item)
                    break

    def on_schedule_option_tab_changed(self, index: int):
        ''' Handles the event when the user switches between schedule option tabs.'''
        # Get the currently new selected tab index
        self.current_schedule_option_index = index
        self.populate_available_block_list()

        # Pass the active block template down into the newly selected table
        widget = self.schedule_options_tab_widget.currentWidget()
        if widget and self.active_block_template:
            self.restore_active_block_selection()
            widget.set_active_time_slot_block(self.active_block_template)

    def add_new_schedule_option(self: bool = False):
        '''
        Add a new empty schedule option.
        '''
        # Create a new empty schedule option with empty lists for each type
        new_option_data = {"lecture": [], "tirgul": [], "maabada": []}
        # append it to the list of all schedule options
        self.all_schedule_options.append(new_option_data)
        # Create a new CourseTimeSlotTable for this option
        new_table_widget = CourseTimeSlotTable(parent=self.schedule_options_tab_widget)
        new_table_widget.cellAction.connect(self.handle_table_cell_action)
        # Add the new table widget to the tab widget
        tab_name = f"Option {len(self.all_schedule_options)}"
        self.schedule_options_tab_widget.addTab(new_table_widget, tab_name)
        self.schedule_options_tab_widget.setCurrentIndex(len(self.all_schedule_options) - 1)
        
        # Rebuild the block list and restore the active block selection
        self.populate_available_block_list()
        self.restore_active_block_selection()

    def remove_current_schedule_option(self):
        ''' 
        Remove the currently selected schedule option tab.
        If there is only one option left, show an error message instead.
        '''
        # Check if there is at more then one schedule option, if not, show an error message
        if self.current_schedule_option_index == -1 or len(self.all_schedule_options) == 1:
            QMessageBox.warning(self, "Error", "Cannot remove the last schedule option.")
            return
        
        # Confirm with the user before removing the option
        option_title = self.schedule_options_tab_widget.tabText(self.current_schedule_option_index) 
        reply = QMessageBox.question(
            self, "Remove Schedule Option",
            f"Are you sure you want to remove '{option_title}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Remove the selected option from the list and the tab widget
            self.all_schedule_options.pop(self.current_schedule_option_index)
            self.schedule_options_tab_widget.removeTab(self.current_schedule_option_index)
            
            # Adjust index and refresh the current tab by setting it to the last available option
            self.current_schedule_option_index = min(self.current_schedule_option_index, len(self.all_schedule_options) - 1)
            if self.current_schedule_option_index != -1:
                self.schedule_options_tab_widget.setCurrentIndex(self.current_schedule_option_index)
            
            # Reset active block template and refresh UI
            self.active_block_template = None
            self.refresh_all_schedule_tables()
            self.populate_available_block_list()
            QMessageBox.information(self, "Removal Completed", "Schedule option removed successfully.")

    def populate_available_block_list(self):
        ''' Populate the list of available time slot block templates based on the current schedule options.'''
        # create a unique set of templates and load the exisitng block list 
        unique_templates = set()
        for i in range(self.available_block_templates_list_widget.count()):
            tpl = self.available_block_templates_list_widget.item(i).data(Qt.UserRole)
            unique_templates.add(tpl)

        # Clear the exisitng block list            
        self.available_block_templates_list_widget.clear()
        
        # Collect unique templates from all schedule options (For loading exisiting course blocks)
        for option_data in self.all_schedule_options:
            for slot_type, slots_list in option_data.items():
                for slot in slots_list:
                    unique_templates.add((slot.room, slot.building, slot_type))
        
        # Add each template as a widget item in the list
        for room, building, slot_type in sorted(unique_templates):
            item = QListWidgetItem(f"Room: {room} | Building: {building} ({slot_type})")
            item.setData(Qt.UserRole, (room, building, slot_type))
            
            # Set the background color based on the slot type (Right now it dont work)
            color = CourseTimeSlotTable.COLOR_MAP.get(slot_type, QColor(200, 200, 200, 150))
            item.setBackground(QBrush(color))
            
            self.available_block_templates_list_widget.addItem(item)

    def open_new_time_slot_block_dialog(self):
        '''
        Opens `CreateTimeSlotDialog` to let the user define a new block template.
        If accepted, adds to the template list (unless it's already present).
        '''
        # Create and show the dialog for creating a new time slot block
        dialog = CreateTimeSlotDialog(self)
        # If the dialog is accepted, get the time slot data
        if dialog.exec_() == QDialog.Accepted:
            # Get the time slot data from the dialog
            template_data = dialog.get_time_slot_data()
            
            # If the user provided valid data, check if it already exists
            if template_data:
                room, building, slot_type = template_data
                new_template = (room, building, slot_type)
                for i in range(self.available_block_templates_list_widget.count()):
                    item = self.available_block_templates_list_widget.item(i)
                    
                    # if the template already exists, select it and show a message
                    if item.data(Qt.UserRole) == new_template:
                        self.available_block_templates_list_widget.setCurrentItem(item)
                        self.on_block_selected(item)
                        QMessageBox.information(self, "Template Exists", "This block template already exists.")
                        return
                
                # If the template is new, add it to the list widget and select it
                item = QListWidgetItem(f"Room: {room} | Building: {building} ({slot_type})")
                item.setData(Qt.UserRole, new_template)
                
                # Set the background color based on the slot type (Right now it dont work)
                color = CourseTimeSlotTable.COLOR_MAP.get(slot_type, QColor(200, 200, 200, 150))
                item.setBackground(QBrush(color))
                
                self.available_block_templates_list_widget.addItem(item)
                self.available_block_templates_list_widget.setCurrentItem(item)
                self.on_block_selected(item)
                #QMessageBox.information(self, "Template Block Created", "New time slot block added.")

    def remove_selected_block(self):
        ''' Remove the currently selected time slot block template from the list and all schedule options.'''
        # Check if an item is selected, if not, show a warning message
        selected_item = self.available_block_templates_list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Error", "Please select a template block to remove.")
            return
        
        # Confirm with the user before removing the selected block
        block_title = selected_item.text()
        reply = QMessageBox.question(self, "Remove Template Block",
                                     f"Are you sure you want to remove '{block_title}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        # If the user confirms, remove the block from all schedule options and the list widget
        if reply == QMessageBox.Yes:
            room, building, slot_type = selected_item.data(Qt.UserRole)
            # Remove the block from all schedule options
            for option_data in self.all_schedule_options:
                option_data[slot_type] = [s for s in option_data[slot_type]
                                          if not (s.room == room and s.building == building)]
            # Remove from UI list
            self.available_block_templates_list_widget.takeItem(self.available_block_templates_list_widget.row(selected_item))
            # If it was actively selected, clear it
            if self.active_block_template == (room, building, slot_type):
                self.active_block_template = None
                self.schedule_options_tab_widget.currentWidget().set_active_time_slot_block(None)
            self.refresh_all_schedule_tables()
            self.populate_available_block_list()
            QMessageBox.information(self, "Removal Completed", "Template block removed successfully.")

    def on_block_selected(self, item: QListWidgetItem):
        ''' Handles the selection of a time slot block template from the list.'''
        self.active_block_template = item.data(Qt.UserRole)
        # clear existing selection in the list widget and set the active time slot block in the current table widget
        widget = self.schedule_options_tab_widget.currentWidget()
        if widget:
            widget.set_active_time_slot_block(self.active_block_template)
            widget.clearSelection()

    def handle_table_cell_action(self, row: int, col: int, action_mode: str, slot_type: Optional[str] = None):
        ''' 
        Handles actions on the course time slot table cells.
        - `row` and `col` specify the cell coordinates.
        - `action_mode` can be 'remove' or 'add'.
          • 'remove': deletes the time slot from both UI and internal model
            • 'add': creates a new TimeSlot and updates model & UI
        - `slot_type` is used when adding a new slot to specify its type.
        '''

        # If no schedule option is selected, do nothing
        if self.current_schedule_option_index == -1:
            return
        
        # Get the current table widget and the data for the current schedule option
        current_table: CourseTimeSlotTable = self.schedule_options_tab_widget.currentWidget()
        current_option_data = self.all_schedule_options[self.current_schedule_option_index]
        
        # If the action mode is 'remove', remove the time slot at the specified coordinates
        if action_mode == 'remove':
            slot_data = current_table.remove_course_time_slot_at_coords(row, col)
            # If a valid slot was found, remove it from the current option data
            if slot_data:
                slot_obj, slot_type = slot_data
                # Remove the slot object from the current option data
                if slot_obj in current_option_data[slot_type]:
                    current_option_data[slot_type].remove(slot_obj)
                # Merge any remaining contiguous slots to ensure no gaps
                self.merge_time_slots(current_option_data)
                self.refresh_all_schedule_tables()
        
        # If the action mode is 'add', create a new time slot at the specified coordinates
        # Using the active block template if available
        elif action_mode == 'add' and self.active_block_template:
            # If current table has no slot data at the specified coordinates,
            # create a new TimeSlot using the active block template
            if not current_table.get_slot_data_at_coords(row, col):
                room, building, slot_type = self.active_block_template
                new_slot = current_table.convert_cell_coords_to_timeslot(row, col, room, building)
                # If a new slot was created and the slot type is valid, add it to the current option data
                if new_slot and slot_type:
                    current_option_data[slot_type].append(new_slot)
                    # Merge any contiguous slots
                    self.merge_time_slots(current_option_data)
                    self.refresh_all_schedule_tables()

        current_table.clearSelection()

    def merge_time_slots(self, option_data: Dict[str, List[TimeSlot]]):
        """
        Replaces each slot list with a merged version where consecutive hours of the same
        room/building are combined into one TimeSlot.
        """
        # Iterate over each slot type in the option data and merge consecutive time slots
        for slot_type in option_data.keys():
            option_data[slot_type] = self.merge_consecutive_time_slots_list(option_data[slot_type])

    def merge_consecutive_time_slots_list(self, slots: List[TimeSlot]) -> List[TimeSlot]:
        ''' Merges consecutive time slots that have the same day, room, and building.'''
        # If no slots are provided, return an empty list
        if not slots: return []
        
        # Sort the slots by day, room, building
        grouped_slots = defaultdict(list)
        for slot in slots:
            grouped_slots[(slot.day, slot.room, slot.building)].append(slot)
        
        # Merge consecutive slots for each group
        merged_results = []
        # for each group of slots, sort them by start time and merge consecutive slots
        for (day, room, building), daily_slots in grouped_slots.items():
            # Sort the slots for the day by start time
            daily_slots.sort(key=lambda s: s.start_time)
            # Initialize the current merged slot as the first in the sorted list
            current_merged_slot = daily_slots[0]
            # Iterate through the sorted slots and merge them if they are consecutive
            # If the next slot starts exactly when the current one ends, merge them
            for next_slot in daily_slots[1:]:
                if next_slot.start_time == current_merged_slot.end_time:
                    # Create a new merged slot with the same day, room, and building and extend the end time
                    current_merged_slot = TimeSlot(
                        current_merged_slot.day,
                        current_merged_slot.start_time.strftime("%H:%M"),
                        next_slot.end_time.strftime("%H:%M"),
                        current_merged_slot.room,
                        current_merged_slot.building
                    )
                # Otherwise, if they are not consecutive, add the current merged slot to results
                else:
                    merged_results.append(current_merged_slot)
                    current_merged_slot = next_slot
            merged_results.append(current_merged_slot)
        return merged_results

    def refresh_all_schedule_tables(self):
        ''' Refreshes all schedule option tables with the current data.'''
        # Iterate over all schedule options and update their corresponding table widgets
        for i, option_data in enumerate(self.all_schedule_options):
            table_widget = self.schedule_options_tab_widget.widget(i)
            if table_widget and isinstance(table_widget, CourseTimeSlotTable):
                table_widget.populate_with_course_slots(
                    option_data["lecture"],
                    option_data["tirgul"],
                    option_data["maabada"]
                )

    def accept(self):
        ''' 
        When the user clicks "Save Course", this method validates inputs,
        assembles final Course data, and closes the dialog.
        '''
        # Get the course details from the input fields
        course_name = self.name_input.text().strip()
        course_code = self.code_input.text().strip()
        instructor = self.instructor_input.text().strip()
        
        # If any of the required fields are empty, show a warning
        if not course_name or not course_code or not instructor:
            QMessageBox.warning(self, "Input Error", "Please fill in all course details.")
            return
        
        # Filter out schedule options where all lists are empty
        valid_schedule_options = [
            option for option in self.all_schedule_options
            if option["lecture"] or option["tirgul"] or option["maabada"]
        ]
        
        # Assemble final data, preserving the structure of each option
        final_lectures_data = []
        final_tirguls_data = []
        final_maabadas_data = []
        
        # For each valid schedule option, append its time slot lists.
        # This maintains the alignment between lectures, tirguls, and maabadas for each option.
        for option in valid_schedule_options:
            final_lectures_data.append(option["lecture"])
            final_tirguls_data.append(option["tirgul"])
            final_maabadas_data.append(option["maabada"])
        
        # If a current course exists, update its data
        if self.current_course:
            self.current_course._name = course_name
            self.current_course._course_code = course_code
            self.current_course._instructor = instructor
            self.current_course._lectures = final_lectures_data
            self.current_course._tirguls = final_tirguls_data
            self.current_course._maabadas = final_maabadas_data
        
        # Otherwise, create a new Course object
        else:
            self.current_course = Course(
                course_name=course_name,
                course_code=course_code,
                instructor=instructor,
                lectures=final_lectures_data,
                tirguls=final_tirguls_data,
                maabadas=final_maabadas_data
            )
        
        self.courseEdited.emit(self.current_course)
        super().accept()