from typing import List
from src.interfaces.formatter_interface import IFormatter
from src.models.schedule import Schedule, DAY_NAMES
import os
import pandas as pd
from datetime import datetime, timedelta


class ExcelFormatter(IFormatter):
    """Exports schedules to a styled Excel workbook."""

    def __init__(self, path: str, start: str = "08:00", end: str = "20:00", interval: int = 30):
        self.path = path
        self.start_time = start
        self.end_time = end
        self.interval = interval

    def format(self, schedules: List[Schedule]):
        if not schedules:
            raise ValueError("No schedules available to format.")
        self._export_all(schedules)

    def _export_all(self, schedules: List[Schedule]):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with pd.ExcelWriter(self.path, engine="xlsxwriter") as writer:
            workbook = writer.book
            for idx, schedule in enumerate(schedules, start=1):
                sheet_name = f"Schedule {idx}"
                df = self._build_dataframe(schedule)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                worksheet = writer.sheets[sheet_name]
                self._apply_styles(workbook, worksheet, df)

    def _build_dataframe(self, schedule: Schedule) -> pd.DataFrame:
        # Generate time slots
        slots = self._time_slots(self.start_time, self.end_time, self.interval)
        # Prepare empty grid
        days = list(DAY_NAMES.values())
        grid = [["" for _ in days] for _ in slots]

        # Fill in events
        day_map = schedule.extract_by_day()
        for day_num, events in day_map.items():
            day_idx = list(DAY_NAMES.keys()).index(day_num)
            for kind, name, code, slot in events:
                start_i = self._find_index(slot.start_time, slots)
                end_i = self._find_index(slot.end_time, slots)
                text = f"{name} ({code})\n[{kind}]"
                for row in range(start_i, end_i):
                    grid[row][day_idx] = text

        # Build DataFrame with header
        times = [t.strftime("%H:%M") for t in slots]
        df = pd.DataFrame(grid, columns=days)
        df.insert(0, "Time", times)
        return df

    def _time_slots(self, start: str, end: str, minutes: int) -> List[datetime.time]:
        start_dt = datetime.strptime(start, "%H:%M")
        end_dt = datetime.strptime(end, "%H:%M")
        delta = timedelta(minutes=minutes)
        slots = []
        while start_dt < end_dt:
            slots.append(start_dt.time())
            start_dt += delta
        return slots

    def _find_index(self, target: datetime.time, slots: List[datetime.time]) -> int:
        for i, t in enumerate(slots):
            if target <= t:
                return i
        return len(slots)

    def _apply_styles(self, workbook, worksheet, df: pd.DataFrame):
        # Formats
        header_fmt = workbook.add_format({"bold": True, "align": "center", "bg_color": "#DCE6F1", "border": 1})
        time_fmt = workbook.add_format({"align": "center", "border": 1})
        cell_fmt = workbook.add_format({"text_wrap": True, "valign": "top", "border": 1})

        # Set column widths
        worksheet.set_column(0, 0, 12, time_fmt)
        for col in range(1, len(df.columns)):
            worksheet.set_column(col, col, 25, cell_fmt)

        # Style headers
        for col, header in enumerate(df.columns):
            worksheet.write(0, col, header, header_fmt)

        # Freeze panes below header
        worksheet.freeze_panes(1, 1)
