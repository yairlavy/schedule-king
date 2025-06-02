from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QComboBox, QPushButton, QLabel,
    QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from src.models.Preference import Preference, Metric
import os

class RankingControls(QWidget):
    """
    A widget that provides controls for ranking schedules by different metrics.
    Allows users to select a metric and sort order (ascending/descending).
    """
    preference_changed = pyqtSignal(object)  # Emits Preference object

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_styles()
        self.current_preference = None

    def setup_ui(self):
        """Initialize the UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Add label
        self.label = QLabel("Sort by:")
        self.label.setObjectName("ranking_label")
        layout.addWidget(self.label)

        # Create metric selector
        self.metric_selector = QComboBox()
        self.metric_selector.setObjectName("metric_selector")
        self.metric_selector.setMinimumWidth(150)
        
        # Add metrics to selector
        for metric in Metric:
            self.metric_selector.addItem(metric.name.replace('_', ' ').title(), metric)
        
        # Add "Insertion Order" option
        self.metric_selector.addItem("Insertion Order", None)
        layout.addWidget(self.metric_selector)

        # Create sort order button
        self.sort_order_button = QPushButton()
        self.sort_order_button.setObjectName("sort_order_button")
        self.sort_order_button.setFixedSize(32, 32)
        self.sort_order_button.setCheckable(True)
        self.update_sort_order_icon()
        layout.addWidget(self.sort_order_button)

        # Add stretch to push controls to the left
        layout.addStretch()

        self.setLayout(layout)

        # Connect signals
        self.metric_selector.currentIndexChanged.connect(self.on_preference_changed)
        self.sort_order_button.toggled.connect(self.on_preference_changed)

    def load_styles(self):
        style_path = os.path.join(os.path.dirname(__file__), '../assets/styles/ranking_controls.qss')
        try:
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Error loading ranking controls styles: {e}")

    def update_sort_order_icon(self):
        """Update the sort order button icon"""
        icon_name = "sort_desc" if self.sort_order_button.isChecked() else "sort_asc"
        icon_path = os.path.join(os.path.dirname(__file__), f'../assets/icons/{icon_name}.png')
        if os.path.exists(icon_path):
            self.sort_order_button.setIcon(QIcon(icon_path))

    def on_preference_changed(self):
        """Handle metric selection change"""
        metric = self.metric_selector.currentData()
        ascending = not self.sort_order_button.isChecked()
        self.update_sort_order_icon()
        self.preference_changed.emit((metric, ascending))

    def set_preference(self, metric, ascending):
        """Set the current preference"""
        self.current_preference = Preference(metric, ascending)
        if metric is None:
            self.metric_selector.setCurrentText("Insertion Order")
            self.sort_order_button.setChecked(True)
        else:
            self.metric_selector.setCurrentText(metric.name.replace('_', ' ').title())
            self.sort_order_button.setChecked(not ascending)
            self.update_sort_order_icon() 