import os
import requests
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QEventLoop, QTimer
from PyQt5.QtWebEngineWidgets import QWebEnginePage

# Custom QWebEnginePage to suppress JavaScript console messages
class SilentWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        pass  # Do nothing – suppress console logs

class ChoiceFreakSessionManager:
    COOKIE_FILE = "cookie.txt"  # File to store the cookie
    LOGIN_URL = "https://choicefreak.appspot.com/_ah/conflogin?continue=https://choicefreak.appspot.com/biu/"

    def __init__(self):
        self._cookie = None  # Lazy-loaded cookie

    @property
    def cookie(self):
        """Returns the cookie string, loading it if necessary."""
        return self._cookie

    def get_cookie(self):
        # Return cached cookie if available
        if self._cookie is not None:
            return self._cookie
        # Check for internet connectivity
        try:
            res = requests.get("https://www.google.com")
            if res.status_code != 200:
                return None
        except:
            return None
        # Load or login to get cookie if not already loaded
        if self._cookie is None:
            self._cookie = self.load_or_login()
        return self._cookie

    def load_or_login(self):
        # Try to load cookie from file and test it
        if os.path.exists(self.COOKIE_FILE):
            with open(self.COOKIE_FILE, "r") as f:
                cookie = f.read().strip()
                if self.test_cookie(cookie):
                    return cookie
        # If not valid, perform browser login
        return self.browser_login()

    def test_cookie(self, cookie_str):
        # Test if the cookie is valid by making a request
        try:
            res = requests.get(
                "https://choicefreak.appspot.com/biu/movies/?period=4&ids=01010",
                headers={"Cookie": cookie_str},
            )
            res.raise_for_status()
            res.json()  # Check if the response is valid JSON
            return True
        except (requests.RequestException, ValueError):
            return False
    
    def browser_login(self):
        # Create QApplication if not already running
        app = QApplication.instance()
        created_app = False
        if app is None:
            app = QApplication([])
            created_app = True

        # Set up the browser view and profile
        view = QWebEngineView()
        view.setPage(SilentWebEnginePage(view))
        profile = QWebEngineProfile.defaultProfile()
        
        # Optionally clear cookies and cache (commented out)
        # profile.cookieStore().deleteAllCookies()
        # profile.clearHttpCache()
        cookie_store = profile.cookieStore()

        cookie_data = {}

        # Callback for when a cookie is added
        def on_cookie_added(cookie):
            name = bytes(cookie.name()).decode()
            value = bytes(cookie.value()).decode()
            if name in ["selper", "SACSID"]:
                cookie_data[name] = value
                # If both cookies are found, exit the event loop
                if "selper" in cookie_data and "SACSID" in cookie_data:
                    loop.quit()

        cookie_store.cookieAdded.connect(on_cookie_added)
        from PyQt5.QtCore import QUrl
        view.setUrl(QUrl(self.LOGIN_URL))
        view.show()

        # Start event loop, with a timeout of 2 minutes
        loop = QEventLoop()
        QTimer.singleShot(120000, loop.quit)
        loop.exec_()

        # Clean up the view
        view.close()
        view.deleteLater()

        # Quit the app if we created it
        if created_app:
            app.quit()

        # If both cookies are found, save and return them
        if "selper" in cookie_data and "SACSID" in cookie_data:
            cookie_str = f"selper={cookie_data['selper']}; SACSID={cookie_data['SACSID']}"
            with open(self.COOKIE_FILE, "w") as f:
                f.write(cookie_str)
            return cookie_str
        else:
            raise Exception("Login failed or timed out")

    def cookie_dict(self, cookie_str):
        # Convert cookie string to dictionary
        return dict(pair.strip().split("=", 1) for pair in cookie_str.split(";"))
