import sys
import os
from PyQt6.QtWidgets import QApplication, QDialog

# Ensure current directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Infrastructure.database.connection import DatabaseConnection
from Infrastructure.database.schema import init_db
from Infrastructure.repositories.user_repository import UserRepository
from Infrastructure.repositories.taxpayer_repository import TaxpayerRepository
from Infrastructure.repositories.declaration_repository import DeclarationRepository
from Infrastructure.repositories.audit_repository import AuditRepository

from Kernel.services.auth_service import AuthService
from Kernel.services.taxpayer_service import TaxpayerService
from Kernel.services.declaration_service import DeclarationService
from Kernel.services.dashboard_service import DashboardService

from GUI.stylesheet import get_dark_stylesheet
from GUI.login_window import LoginWindow
from GUI.dashboard_window import DashboardWindow

def main():
    # 1. Initialize SQLite Database
    db_name = "taxes.db"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, db_name)
    
    DatabaseConnection.initialize(db_path)
    
    try:
        init_db()
    except Exception as e:
        print(f"CRITICAL: Failed to initialize SQLite database: {e}", file=sys.stderr)
        sys.exit(1)

    # 2. Instantiate Repositories (Infrastructure)
    user_repo = UserRepository()
    taxpayer_repo = TaxpayerRepository()
    declaration_repo = DeclarationRepository()
    audit_repo = AuditRepository()

    # 3. Instantiate Services (Kernel Business Logic)
    auth_service = AuthService(user_repo, audit_repo)
    taxpayer_service = TaxpayerService(taxpayer_repo, audit_repo)
    declaration_service = DeclarationService(declaration_repo, taxpayer_repo, audit_repo)
    dashboard_service = DashboardService(taxpayer_repo, declaration_repo, audit_repo)

    # 4. Start PyQt Application
    app = QApplication(sys.argv)
    
    # Apply Slate Dark QSS stylesheet
    app.setStyleSheet(get_dark_stylesheet())

    # 5. Routing Event Loop (Handles Login / Logout session transitions)
    while True:
        # Show Login Screen
        login = LoginWindow(auth_service)
        if login.exec() != QDialog.DialogCode.Accepted:
            # User canceled login or closed login dialog
            break
            
        current_user = auth_service.get_current_user()
        if not current_user:
            break
            
        # Initialize and show main dashboard window
        dashboard_window = DashboardWindow(
            auth_service, 
            taxpayer_service, 
            declaration_service, 
            dashboard_service
        )
        dashboard_window.show()
        
        # Execute PyQt main loop. Blocks until dashboard_window is closed.
        app.exec()
        
        # If the user closed the window and session is cleared, they logged out.
        # Loop back to show Login Window. If they closed the window without logging out, exit.
        if not auth_service.is_authenticated():
            continue
        else:
            break

    sys.exit(0)

if __name__ == "__main__":
    main()
