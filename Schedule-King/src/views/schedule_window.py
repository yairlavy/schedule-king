from src.services.text_formatter import TextFormatter

class ScheduleWindow:
    def __init__(self, schedule_api, output_path: str):
        """
        Window for displaying and exporting schedules.
        """
        self.schedule_api = schedule_api
        self.generated_schedules = []
        self.formatter = TextFormatter(output_path)  # Create a TextFormatter instance

    def generate_schedules(self, selected_courses: list) -> None:
        """
        Generate schedules based on the selected courses.
        """
        self.generated_schedules = self.schedule_api.process(selected_courses)
        print(f"Generated {len(self.generated_schedules)} schedules.")

        if self.generated_schedules:
            self.formatter.format(self.generated_schedules)
            print(f"Schedules exported successfully to {self.formatter.path}.")

    def display_schedules(self) -> None:
        """
        Display the generated schedules using the TextFormatter formatting.
        """
        if not self.generated_schedules:
            print("No schedules to display.")
            return

        # Use TextFormatter to format all schedules nicely as text
        formatted_text = self.formatter.formatText(self.generated_schedules)
        print("\nFormatted Schedules:\n")
        print(formatted_text)
