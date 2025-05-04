# main.py

import sys
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication

from src.services.schedule_api import ScheduleAPI
from src.controllers.MainConroller import MainController 

if __name__ == "__main__":
    # Load environment variables
    load_dotenv(dotenv_path=".env.local")

    DEFAULT_SOURCE = os.getenv("DEFAULT_SOURCE")

    if not DEFAULT_SOURCE:
        print("Error: DEFAULT_SOURCE not set in .env.local")
        exit(1)

    # Create the QApplication
    app = QApplication(sys.argv)

    # Load and apply the stylesheet
    with open("src/styles/style.qss", "r") as f:
        app.setStyleSheet(f.read())

    # Create the ScheduleAPI instance
    api = ScheduleAPI(DEFAULT_SOURCE)

    # Create and start the MainController
    controller = MainController(api)
    controller.start_application()

    # Run the event loop
    sys.exit(app.exec_())
