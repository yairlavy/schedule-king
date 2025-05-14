# main.py

import sys
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication

from src.services.schedule_api import ScheduleAPI
from src.controllers.MainConroller import MainController 

if __name__ == "__main__":
    # Create the QApplication
    app = QApplication(sys.argv)
    # Load and apply the stylesheet
    with open("src/styles/style.qss", "r") as f:
        app.setStyleSheet(f.read())
    # Create the ScheduleAPI instance
    api = ScheduleAPI()
    # Create and start the MainController
    controller = MainController(api)
    controller.start_application()
    # Run the event loop
    sys.exit(app.exec_())
