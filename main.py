import sys
from PyQt6.QtWidgets import QApplication, QWidget

from Infrastructure.migrations.schema import DatabaseInitializer

# Services
from Kernel.services.auth_service import AuthService
from Kernel.services.dashboard_service import DashboardService
from Kernel.services.declaration_service import DeclarationService
from Kernel.services.audit_service import AuditService
from Kernel.services.taxpayer_service import TaxpayerService

# Repositories
from Infrastructure.repositories.user_repository import UserRepository
from Infrastructure.repositories.taxpayer_repository import TaxpayerRepository
from Infrastructure.repositories.declaration_repository import DeclarationRepository

# UI
from GUI.windows.login_window import LoginWindow
from GUI.windows.dashboard_window import DashboardWindow
from GUI.pages.taxpayer_page import TaxpayerPage
from GUI.pages.declaration_page import DeclarationPage

from Infrastructure.database.connection import DatabaseConnection
from Infrastructure.repositories.audit_repository import AuditRepository
from Infrastructure.migrations.schema import DatabaseInitializer

def main():
    print("🚀 Starting application...")

    app = QApplication(sys.argv)
     # =========================
    # DATABASE INITIALIZATION
    # =========================
    db_init = DatabaseInitializer()
    db_init.initialize()
    print("✅ Database initialized")
    # ----------------------------
    # Database
    # ----------------------------
    db = DatabaseConnection()

    # ----------------------------
    # Repositories
    # ----------------------------
    user_repo = UserRepository(db)
    taxpayer_repo = TaxpayerRepository(db)
    declaration_repo = DeclarationRepository(db)
    audit_repo = AuditRepository(db)


    print("✅ Repositories created")

    # ==================================================
    # Services (BUSINESS LAYER)
    # ==================================================
    
    audit_service = AuditService(audit_repo)
    auth_service = AuthService(
        user_repo,
        audit_service
    )
    taxpayer_service = TaxpayerService(taxpayer_repo, audit_service)

    taxpayer_service = TaxpayerService(
    taxpayer_repo,
    audit_service
    )

    declaration_service = DeclarationService(
        declaration_repo,
        taxpayer_repo,
        audit_service
    )

    dashboard_service = DashboardService(
    taxpayer_service,
    declaration_service,
    audit_service
)

    print("✅ Services created")

    # ==================================================
    # UI state
    # ==================================================
    dashboard = None
    login_window = None

    # ==================================================
    # Login callback
    # ==================================================
    def on_login_success(user):
        if user is None:
            print("❌ Login failed (wrong credentials)")
            return
        nonlocal dashboard, login_window

        print(f"✅ Login successful: {user.username}")

        dashboard = DashboardWindow(
            auth_service=auth_service,
            dashboard_service=dashboard_service,
            taxpayer_page=TaxpayerPage(taxpayer_service),
            declaration_page = DeclarationPage(
                declaration_service=declaration_service,
                taxpayer_service=taxpayer_service,
                auth_service=auth_service,
            ),
            on_logout=on_logout
        )

        dashboard.show()
        login_window.hide()

    def on_logout():
        nonlocal dashboard, login_window
        dashboard.close()
        login_window.show()

    # ==================================================
    # Login window
    # ==================================================
    login_window = LoginWindow(
        auth_service=auth_service,
        on_login_success=on_login_success
    )

    login_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()