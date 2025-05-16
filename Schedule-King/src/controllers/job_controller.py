# controller.py
import multiprocessing
from src.models.job import JobRecord, JobTableModel
from queue import Queue
from typing import Callable, Any, Tuple

class JobController:
    def __init__(self, model: JobTableModel):
        self.model = model
        self.queue = multiprocessing.Queue()
        self.next_id = 1
        self.processes = {}
        self.pending_jobs: Queue[Tuple[int, Callable, tuple, dict, str]] = Queue()  # Added job_id to the tuple
        self.max_concurrent_jobs = 1  # Only one active job at a time

    def start_task(self, worker_fn, *worker_args, name=None, **worker_kwargs):
        """
        worker_fn       – the function to run in a new Process
        *worker_args    – positional args to pass after (queue, job_id)
        name            – optional display name (defaults to worker_fn.__name__)
        **worker_kwargs – keyword args to pass to worker_fn
        """
        # Clean up finished processes
        self._cleanup_finished_processes()

        job_id = self.next_id
        self.next_id += 1

        # Register in model
        rec = JobRecord(job_id, name or worker_fn.__name__)
        self.model.add_job(rec)

        # If we have an active job, queue this one
        if len(self.processes) >= self.max_concurrent_jobs:
            self.pending_jobs.put((job_id, worker_fn, worker_args, worker_kwargs, name))
            self.model.update_job(job_id, status="queued")
            return job_id

        # Start the job immediately
        self._start_job(job_id, worker_fn, worker_args, worker_kwargs)
        return job_id

    def _start_job(self, job_id: int, worker_fn: Callable, worker_args: tuple, worker_kwargs: dict):
        """Start a new job process"""
        try:
            p = multiprocessing.Process(
                target=worker_fn,
                args=(self.queue, job_id) + worker_args,
                kwargs=worker_kwargs,
                daemon=True
            )
            p.start()
            self.processes[job_id] = p
            self.model.update_job(job_id, status="running", progress=0)
        except Exception as e:
            self.model.update_job(job_id, status="error", progress=0)

    def _cleanup_finished_processes(self):
        """Clean up finished processes and start next job in queue if available"""
        # First, check for any finished processes
        finished_jobs = []
        for job_id, process in list(self.processes.items()):
            if not process.is_alive():
                process.join(timeout=0.1)
                finished_jobs.append(job_id)
                
        # Update status for finished jobs
        for job_id in finished_jobs:
            if job_id in self.processes:
                del self.processes[job_id]
                # Make sure to mark the job as finished in the model
                self.model.update_job(job_id, status="finished", progress=100)

        # Check again to make sure all zombie processes are removed
        for job_id, process in list(self.processes.items()):
            if not process.is_alive():
                process.join(timeout=0.1)
                if job_id in self.processes:
                    del self.processes[job_id]
                    self.model.update_job(job_id, status="finished", progress=100)

        # If we have capacity and pending jobs, start the next one
        while len(self.processes) < self.max_concurrent_jobs and not self.pending_jobs.empty():
            try:
                # Get the next job from the queue
                job_id, worker_fn, worker_args, worker_kwargs, name = self.pending_jobs.get_nowait()
                # Start the job with the ORIGINAL job_id
                self._start_job(job_id, worker_fn, worker_args, worker_kwargs)
            except Exception:
                break

    def cleanup(self):
        """Clean up all processes"""
        for process in self.processes.values():
            if process.is_alive():
                process.terminate()
                process.join(timeout=1.0)
                if process.is_alive():
                    process.kill()
        self.processes.clear()
        # Clear pending jobs queue
        while not self.pending_jobs.empty():
            try:
                self.pending_jobs.get_nowait()
            except:
                pass
