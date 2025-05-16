from typing import List
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt


# models.py
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex

class JobRecord:
    def __init__(self, id, name):
        self.id       = id
        self.name     = name
        self.status   = "pending"
        self.progress = 0

    @property
    def display_status(self):
        """Get a user-friendly status display"""
        status_map = {
            "pending": "Pending",
            "queued": "Queued",
            "running": "Running",
            "finished": "Finished",
            "error": "Error"
        }
        return status_map.get(self.status, self.status)

class JobTableModel(QAbstractTableModel):
    def __init__(self, jobs=None):
        super().__init__()
        self.jobs = jobs or []

    def rowCount(self, parent=QModelIndex()):
        return len(self.jobs)

    def columnCount(self, parent=QModelIndex()):
        return 4  # ID, Name, Status, Progress

    def data(self, index, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        job = self.jobs[index.row()]
        return [job.id, job.name, job.display_status, f"{job.progress}%"][index.column()]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole or orientation != Qt.Horizontal:
            return None
        return ["ID", "Name", "Status", "Progress"][section]

    def add_job(self, job: JobRecord):
        self.beginInsertRows(QModelIndex(), len(self.jobs), len(self.jobs))
        self.jobs.append(job)
        self.endInsertRows()

    def update_job(self, job_id, *, status=None, progress=None):
        for row, job in enumerate(self.jobs):
            if job.id == job_id:
                if status is not None:
                    job.status = status
                if progress is not None:
                    job.progress = progress
                elif status == "finished":
                    job.progress = 100
                elif status == "error":
                    job.progress = 0
                elif status == "running" and job.progress == 0:
                    job.progress = 0
                elif status == "queued" and job.progress == 0:
                    job.progress = 0
                top = self.index(row, 0)
                bottom = self.index(row, self.columnCount() - 1)
                self.dataChanged.emit(top, bottom, [Qt.DisplayRole])
                break

    def get_job_status(self, job_id):
        """Get the current status of a job"""
        for job in self.jobs:
            if job.id == job_id:
                return job.status
        return None
