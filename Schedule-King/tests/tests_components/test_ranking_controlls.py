import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.components.ranking_controls import RankingControls
from src.models.Preference import Preference, Metric

@pytest.fixture(autouse=True)
def app():
    """Create a QApplication instance for testing"""
    return QApplication.instance() or QApplication([])

@pytest.fixture
def controls(app):
    """Create a RankingControls instance for testing"""
    controls = RankingControls()
    controls.show()  # Show the widget to ensure proper initialization
    yield controls
    controls.deleteLater()

def test_initial_setup(controls):
    """Test initial UI setup and default values"""
    # Check if metric selector has all options
    assert controls.metric_selector.count() == len(Metric) + 1  # +1 for "Random Order"
    assert controls.metric_selector.currentText() == "Random Order"
    assert controls.metric_selector.currentData() is None

    # Check sort order button
    assert controls.sort_order_button.isChecked() is False  # Initially unchecked for ascending
    assert controls.sort_order_button.isCheckable() is True

    # Check current preference
    assert controls.current_preference is None

def test_metric_selection(controls):
    """Test selecting different metrics"""
    # Select a specific metric
    controls.metric_selector.setCurrentText("Active Days")
    assert controls.metric_selector.currentData() == Metric.ACTIVE_DAYS
    assert controls.current_preference.metric == Metric.ACTIVE_DAYS

    # Select another metric
    controls.metric_selector.setCurrentText("Gap Count")
    assert controls.metric_selector.currentData() == Metric.GAP_COUNT
    assert controls.current_preference.metric == Metric.GAP_COUNT

    # Select Random Order
    controls.metric_selector.setCurrentText("Random Order")
    assert controls.metric_selector.currentData() is None
    assert controls.current_preference.metric is None

def test_sort_order_toggle(controls):
    """Test toggling sort order"""
    # Initial state (ascending)
    assert controls.sort_order_button.isChecked() is False
    assert controls.current_preference is None

    # Select a metric to enable sort order
    controls.metric_selector.setCurrentText("Active Days")
    assert controls.current_preference.ascending is True

    # Toggle to descending
    controls.sort_order_button.setChecked(True)
    assert controls.current_preference.ascending is False

    # Toggle back to ascending
    controls.sort_order_button.setChecked(False)
    assert controls.current_preference.ascending is True

def test_preference_changed_signal(controls, qtbot):
    """Test that preference_changed signal is emitted correctly"""
    with qtbot.waitSignal(controls.preference_changed, timeout=1000) as blocker:
        # Select a metric
        controls.metric_selector.setCurrentText("Active Days")
        metric, ascending = blocker.args
        assert metric == Metric.ACTIVE_DAYS
        assert ascending is True

    with qtbot.waitSignal(controls.preference_changed, timeout=1000) as blocker:
        # Toggle sort order
        controls.sort_order_button.setChecked(True)
        metric, ascending = blocker.args
        assert metric == Metric.ACTIVE_DAYS
        assert ascending is False

def test_set_preference(controls):
    """Test setting preference programmatically"""
    # Set preference with metric
    controls.set_preference(Metric.ACTIVE_DAYS, True)
    assert controls.metric_selector.currentData() == Metric.ACTIVE_DAYS
    assert controls.sort_order_button.isChecked() is False
    assert controls.current_preference.metric == Metric.ACTIVE_DAYS
    assert controls.current_preference.ascending is True

    # Set preference to random order
    controls.set_preference(None, False)
    assert controls.metric_selector.currentData() is None
    assert controls.sort_order_button.isChecked() is True
    assert controls.current_preference.metric is None
    assert controls.current_preference.ascending is False
