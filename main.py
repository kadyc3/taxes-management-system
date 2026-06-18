import sys
from PyQt6.QtWidgets import QApplication, QWidget

from Kernel.services.auth_service import AuthService
from Kernel.services.dashboard_service import DashboardService
from Infrastructure.repositories.user_repository import UserRepository

from GUI.windows.login_window import LoginWindow
from GUI.windows.dashboard_window import DashboardWindow


def main():
    print("🚀 Starting application...")

    app = QApplication(sys.argv)
    print("✅ QApplication created")

    # ----------------------------
    # Core services
    # ----------------------------
    user_repo = UserRepository()
    print("✅ UserRepository created")

    auth_service = AuthService(user_repo)
    print("✅ AuthService created")

    dashboard = None
    login_window = None

    # ----------------------------
    # Login success callback
    # ----------------------------
    def on_login_success(user):
        nonlocal dashboard, login_window

        print(f"✅ Login successful: {user.username}")

        dashboard_service = DashboardService(user)

        # Temporary MVP pages (replace later with real ones)
        taxpayer_page = QWidget()
        declaration_page = QWidget()

        def on_logout():
            dashboard.close()
            login_window.show()

        dashboard = DashboardWindow(
            auth_service=auth_service,
            dashboard_service=dashboard_service,
            taxpayer_page=taxpayer_page,
            declaration_page=declaration_page,
            on_logout=on_logout
        )

        dashboard.show()
        login_window.hide()

    # ----------------------------
    # Login window
    # ----------------------------
    print("✅ Creating LoginWindow")

    login_window = LoginWindow(
        auth_service=auth_service,
        on_login_success=on_login_success
    )

    print("✅ Showing LoginWindow")
    login_window.show()

    print("✅ Entering Qt event loop")

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("❌ ERROR:")
        print(e)
        raise