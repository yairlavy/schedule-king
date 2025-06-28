import os
import requests
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QEventLoop, QTimer

from PyQt5.QtWebEngineWidgets import QWebEnginePage

class SilentWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        pass  # Do nothing – suppress console logs

class ChoiceFreakSessionManager:
    COOKIE_FILE = "cookie.txt"
    LOGIN_URL = "https://choicefreak.appspot.com/_ah/conflogin?continue=https://choicefreak.appspot.com/biu/"

    def __init__(self):
        self._cookie = None  # Lazy-loaded

    @property
    def cookie(self):
        """Returns the cookie string, loading it if necessary."""
        return self._cookie

    def get_cookie(self):
        # if there is not internet return None
        if self._cookie is not None:
            return self._cookie
        try:
            res = requests.get("https://www.google.com")
            if res.status_code != 200:
                return None
        except:
            return None
        if self._cookie is None:
            self._cookie = self.load_or_login()
        return self._cookie

    def load_or_login(self):
        if os.path.exists(self.COOKIE_FILE):
            with open(self.COOKIE_FILE, "r") as f:
                cookie = f.read().strip()
                if self.test_cookie(cookie):
                    return cookie
        return self.browser_login()

    def test_cookie(self, cookie_str):
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
        app = QApplication.instance()
        created_app = False
        if app is None:
            app = QApplication([])
            created_app = True

        view = QWebEngineView()
        view.setPage(SilentWebEnginePage(view))
        profile = QWebEngineProfile.defaultProfile()
        
        # Clear persistent cookies
        # profile.cookieStore().deleteAllCookies()
        # # Clear cache
        # profile.clearHttpCache()
        cookie_store = profile.cookieStore()

        cookie_data = {}

        def on_cookie_added(cookie):
            name = bytes(cookie.name()).decode()
            value = bytes(cookie.value()).decode()
            if name in ["selper", "SACSID"]:
                cookie_data[name] = value
                if "selper" in cookie_data and "SACSID" in cookie_data:
                    loop.quit()

        cookie_store.cookieAdded.connect(on_cookie_added)
        from PyQt5.QtCore import QUrl
        view.setUrl(QUrl(self.LOGIN_URL))
        view.show()

        loop = QEventLoop()
        QTimer.singleShot(120000, loop.quit)
        loop.exec_()

        view.close()
        view.deleteLater()

        if created_app:
            app.quit()  # Only quit if we created it

        if "selper" in cookie_data and "SACSID" in cookie_data:
            cookie_str = f"selper={cookie_data['selper']}; SACSID={cookie_data['SACSID']}"
            with open(self.COOKIE_FILE, "w") as f:
                f.write(cookie_str)
            return cookie_str
        else:
            raise Exception("Login failed or timed out")

    def cookie_dict(self, cookie_str):
        return dict(pair.strip().split("=", 1) for pair in cookie_str.split(";"))
