import sys
import os
import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from src.services.schedule_api import ScheduleAPI
from src.controllers.MainConroller import MainController

if __name__ == "__main__":
    #  Base directory 
    basedir = os.path.dirname(os.path.realpath(__file__))

    # Set Windows AppUserModelID (for taskbar icon) 
    if os.name == 'nt':
        myappid = 'com.biu.scheduleking' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # Create the QApplication
    app = QApplication(sys.argv)

    # Platform-specific icon selection
    if sys.platform == "win32":
        icon_file = "favicon.ico"
    elif sys.platform == "darwin":
        icon_file = "icon.png"  # Optional: only if you create one
    else:
        icon_file = "icon.png"   # Optional fallback

    icon_path = os.path.join(basedir, "src/assets", icon_file)
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        print(f"Icon not found at: {icon_path}")

    # Load and apply the stylesheet 
    style_path = os.path.join(basedir, "src/styles/style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Stylesheet not found at: {style_path}")

    # Initialize core logic
    api = ScheduleAPI()
    controller = MainController(api, maximize_on_start=True, fullscreen_on_start=False)
    controller.start_application()

    #  Run the Qt event loop
    sys.exit(app.exec_())
