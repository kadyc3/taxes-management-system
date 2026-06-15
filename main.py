import sys
from PyQt6.QtWidgets import QApplication

from Infrastructure.database import initialize_database
from Infrastructure.repositories.user_repository import UserRepository
from Kernel.services.auth_service import AuthService
from GUI.windows.login_window import LoginWindow
from GUI.windows.dashboard_window import DashboardWindow


def main():
    # 1. Initialize database (creates tables if not exist)
    initialize_database()

    # 2. Wire up dependencies
    user_repo    = UserRepository()
    auth_service = AuthService(user_repo)

    # 3. Start Qt application
    app = QApplication(sys.argv)

    # 4. Define what happens after successful login
    def on_login_success(user):
        dashboard = DashboardWindow(user)
        dashboard.show()
        login_window.close()

    # 5. Show login window
    login_window = LoginWindow(auth_service, on_login_success)
    login_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()