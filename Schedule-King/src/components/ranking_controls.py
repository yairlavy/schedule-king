from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QComboBox, QPushButton, QLabel,
    QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QTransform
from src.models.Preference import Preference, Metric
import os

class RankingControls(QWidget):
    """
    A widget that provides controls for ranking schedules by different metrics.
    Allows users to select a metric and sort order (ascending/descending).
    """
    # Emits (metric: object, ascending: bool) when preference changes
    preference_changed = pyqtSignal(object, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_preference = None

    def setup_ui(self):
        """Initialize the UI components"""
        # Create a container widget with a frame for better visual appearance
        container = QWidget()
        container.setObjectName("ranking_container")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # Add label with icon
        self.label = QLabel("Sort by:")
        self.label.setObjectName("ranking_label")
        layout.addWidget(self.label)

        # Create metric selector with enhanced styling
        self.metric_selector = QComboBox()
        self.metric_selector.setObjectName("metric_selector")
        self.metric_selector.setMinimumWidth(180)
        self.metric_selector.setFixedHeight(32)
        
        # Add "Random Order" option (no metric selected)
        self.metric_selector.addItem("Random Order", None)
        # Add all available metrics to the selector
        for metric in Metric:
            self.metric_selector.addItem(metric.name.replace('_', ' ').title(), metric)
        # Set default selection to "Random Order"
        self.metric_selector.setCurrentIndex(0) 
        layout.addWidget(self.metric_selector)

        # Create sort order button (ascending/descending)
        self.sort_order_button = QPushButton()
        self.sort_order_button.setObjectName("sort_order_button")
        self.sort_order_button.setFixedSize(32, 32)
        self.sort_order_button.setCheckable(True)
        self.update_sort_order_icon()  # Set initial icon
        layout.addWidget(self.sort_order_button)

        # Add stretch to push controls to the left
        layout.addStretch()

        # Set the container as the main widget
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)

        # Connect signals for metric and sort order changes
        self.metric_selector.currentIndexChanged.connect(self.on_preference_changed)
        self.sort_order_button.toggled.connect(self.on_preference_changed)

    def update_sort_order_icon(self):
        """Update the sort order button icon based on current state"""
        # Use the down-arrow.png for both ascending and descending, flipping for ascending
        icon_path = os.path.join(os.path.dirname(__file__), '../assets/down-arrow.png')
        
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                if not self.sort_order_button.isChecked(): # Ascending
                    # Flip the pixmap vertically for ascending order
                    transform = QTransform().rotate(180)
                    pixmap = pixmap.transformed(transform)
                
                # Scale the pixmap down to a smaller size
                self.sort_order_button.setIcon(QIcon(pixmap.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
            else:
                # Fallback to text if image loading fails
                self.sort_order_button.setText("↓" if self.sort_order_button.isChecked() else "↑")
        else:
            # Fallback to text if file not found
            self.sort_order_button.setText("↓" if self.sort_order_button.isChecked() else "↑")

    def on_preference_changed(self):
        """Handle metric selection or sort order change"""
        metric = self.metric_selector.currentData()
        ascending = not self.sort_order_button.isChecked()
        self.update_sort_order_icon()
        # Emit metric and ascending as separate arguments
        self.preference_changed.emit(metric, ascending)

    def set_preference(self, metric, ascending):
        """Set the current preference and update UI accordingly"""
        self.current_preference = Preference(metric, ascending)
        if metric is None:
            # Select "Random Order" and set sort order to default
            self.metric_selector.setCurrentText("Insertion Order")
            self.sort_order_button.setChecked(True)
        else:
            # Select the given metric and set sort order
            self.metric_selector.setCurrentText(metric.name.replace('_', ' ').title())
            self.sort_order_button.setChecked(not ascending)
            self.update_sort_order_icon() 