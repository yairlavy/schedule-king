# status_window.py
from PyQt5.QtWidgets import QMainWindow, QTableView, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QTimer, Qt
from src.models.job import JobTableModel
from src.controllers.job_controller import JobController

class StatusWindow(QMainWindow):
    def __init__(self, model: JobTableModel, controller: JobController):
        super().__init__()
        self.setWindowTitle("Background Jobs")
        self.resize(600, 400)

        self._model = model
        self._controller = controller

        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Add status label
        self._status_label = QLabel("Active Jobs: 0 | Queued Jobs: 0")
        self._status_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self._status_label)

        # Create and setup table
        table = QTableView()
        table.setModel(model)
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        layout.addWidget(table)

        self.setCentralWidget(central_widget)

        # Poll the multiprocessing queue every 50 ms
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._poll_queue)
        self._timer.start(50)
        
        # Force initial cleanup when window opens
        self._force_cleanup()

    def showEvent(self, event):
        """Force cleanup when window is shown"""
        super().showEvent(event)
        self._force_cleanup()

    def _force_cleanup(self):
        """Force cleanup of any zombie processes"""
        # Check all processes - if not alive, remove from controller
        for job_id, process in list(self._controller.processes.items()):
            if not process.is_alive():
                process.join(timeout=0.1)
                if job_id in self._controller.processes:
                    del self._controller.processes[job_id]
                    # Make sure to mark the job as finished
                    self._model.update_job(job_id, status="finished", progress=100)
        
        # Start any queued jobs if we have capacity
        self._controller._cleanup_finished_processes()
        
        # Update the status label
        self._update_status_label()

    def _update_status_label(self):
        """Update the status label with current job counts"""
        active_jobs = len(self._controller.processes)
        queued_jobs = self._controller.pending_jobs.qsize()
        self._status_label.setText(f"Active Jobs: {active_jobs} | Queued Jobs: {queued_jobs}")

    def _poll_queue(self):
        """Poll for updates from the job processes"""
        # Update status label first
        self._update_status_label()

        # Process queue messages
        q = self._controller.queue
        while not q.empty():
            try:
                job_id, status, progress = q.get_nowait()
                self._model.update_job(job_id, status=status, progress=progress)
                
                # Clean up finished processes
                p = self._controller.processes.get(job_id)
                if status == "finished" and p and not p.is_alive():
                    p.join()
                    if job_id in self._controller.processes:
                        del self._controller.processes[job_id]
                    self._controller._cleanup_finished_processes()
            except Exception:
                pass

        # Additional check for any non-alive processes
        for job_id, process in list(self._controller.processes.items()):
            if not process.is_alive():
                process.join(timeout=0.1)
                if job_id in self._controller.processes:
                    del self._controller.processes[job_id]
                    # Make sure to mark the job as finished
                    self._model.update_job(job_id, status="finished", progress=100)
                self._controller._cleanup_finished_processes()

        # Always try to start next job if we have capacity
        if len(self._controller.processes) < self._controller.max_concurrent_jobs:
            self._controller._cleanup_finished_processes()

        # Update status label again after all processing
        self._update_status_label()
