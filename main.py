import sys
from PyQt6.QtWidgets import QApplication

from Kernel.services.auth_service import AuthService
from Infrastructure.repositories.user_repository import UserRepository
from GUI.windows.login_window import LoginWindow
from GUI.windows.dashboard_window import DashboardWindow


def main():
    app = QApplication(sys.argv)

    user_repo = UserRepository()              # ✅ AJOUT
    auth_service = AuthService(user_repo)     # ✅ FIX ICI

    dashboard = None

    def on_login_success(user):
        nonlocal dashboard
        dashboard = DashboardWindow(user)
        dashboard.show()
        login_window.hide()

    global login_window
    login_window = LoginWindow(auth_service, on_login_success)
    login_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()