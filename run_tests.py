import os
import unittest
from datetime import datetime
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
from Kernel.exceptions.app_exceptions import ValidationError, PermissionDeniedError, AuthenticationError

class TestTaxesManagementSystem(unittest.TestCase):
    db_path = "test_taxes.db"

    @classmethod
    def setUpClass(cls):
        # Point connection to test database
        if os.path.exists(cls.db_path):
            try:
                os.remove(cls.db_path)
            except OSError:
                pass
        DatabaseConnection.initialize(cls.db_path)
        init_db()

    @classmethod
    def tearDownClass(cls):
        # Clean up test database
        if os.path.exists(cls.db_path):
            try:
                os.remove(cls.db_path)
            except OSError:
                pass

    def setUp(self):
        # Re-initialize Repositories and Services
        self.user_repo = UserRepository()
        self.taxpayer_repo = TaxpayerRepository()
        self.declaration_repo = DeclarationRepository()
        self.audit_repo = AuditRepository()

        self.auth_service = AuthService(self.user_repo, self.audit_repo)
        self.taxpayer_service = TaxpayerService(self.taxpayer_repo, self.audit_repo)
        self.declaration_service = DeclarationService(self.declaration_repo, self.taxpayer_repo, self.audit_repo)
        self.dashboard_service = DashboardService(self.taxpayer_repo, self.declaration_repo, self.audit_repo)

    def test_01_authentication_flow(self):
        # Seed users are checked
        # 1. Successful Admin Login
        admin = self.auth_service.login("admin", "admin123")
        self.assertEqual(admin.username, "admin")
        self.assertEqual(admin.role.value, "admin")
        self.assertTrue(self.auth_service.is_authenticated())

        # 2. Failed Login (invalid pass)
        with self.assertRaises(AuthenticationError):
            self.auth_service.login("admin", "wrongpassword")

        # 3. Failed Login (invalid user)
        with self.assertRaises(AuthenticationError):
            self.auth_service.login("unknown_user", "password")

        # 4. Logout
        self.auth_service.logout()
        self.assertFalse(self.auth_service.is_authenticated())

    def test_02_taxpayer_crud(self):
        admin = self.auth_service.login("admin", "admin123")
        
        # 1. Create Taxpayer
        taxpayer = self.taxpayer_service.create_taxpayer(
            nin="NIN-100200300",
            full_name="John Doe Corp",
            taxpayer_type="Company",
            status="Active",
            email="johndoe@example.com",
            phone="+123456789",
            address="123 Financial Way",
            current_user=admin
        )
        self.assertIsNotNone(taxpayer.id)
        self.assertEqual(taxpayer.nin, "NIN-100200300")
        self.assertEqual(taxpayer.taxpayer_type.value, "Company")

        # 2. Duplicate NIN check
        with self.assertRaises(ValidationError):
            self.taxpayer_service.create_taxpayer(
                nin="NIN-100200300",
                full_name="Other Name",
                taxpayer_type="Individual",
                status="Active",
                email="other@example.com",
                phone="000",
                address="Addr",
                current_user=admin
            )

        # 3. Email Validation
        with self.assertRaises(ValidationError):
            self.taxpayer_service.create_taxpayer(
                nin="NIN-999999",
                full_name="Bad Email Guy",
                taxpayer_type="Individual",
                status="Active",
                email="bad_email_format",
                phone="000",
                address="Addr",
                current_user=admin
            )

        # 4. Read / Search
        taxpayers = self.taxpayer_service.search_taxpayers(query="John")
        self.assertEqual(len(taxpayers), 1)
        self.assertEqual(taxpayers[0].full_name, "John Doe Corp")

        # 5. Role restrictions (read-only user cannot write)
        readonly_user = self.auth_service.login("user", "user123")
        with self.assertRaises(PermissionDeniedError):
            self.taxpayer_service.create_taxpayer(
                nin="NIN-222", full_name="User", taxpayer_type="Individual", status="Active",
                email="u@u.com", phone="123", address="Addr", current_user=readonly_user
            )

    def test_03_declaration_crud_and_calculation(self):
        admin = self.auth_service.login("admin", "admin123")
        
        # Get the seeded taxpayer
        taxpayers = self.taxpayer_service.search_taxpayers(query="John")
        self.assertTrue(len(taxpayers) > 0)
        taxpayer_id = taxpayers[0].id

        # 1. Create Declaration
        declaration = self.declaration_service.create_declaration(
            taxpayer_id=taxpayer_id,
            reference_number="DEC-2026-001",
            declaration_type="TVA",
            fiscal_year=2026,
            period="Q1",
            gross_amount=10000.0,
            deductions=2000.0,
            penalties=500.0,
            current_user=admin
        )
        self.assertIsNotNone(declaration.id)
        # Verify calculation: 10000.0 - 2000.0 + 500.0 = 8500.0
        self.assertEqual(declaration.total_due, 8500.0)
        self.assertEqual(declaration.status.value, "Draft")

        # 2. Validation constraints: Deductions > Gross
        with self.assertRaises(ValidationError):
            self.declaration_service.create_declaration(
                taxpayer_id=taxpayer_id, reference_number="DEC-2026-BAD", declaration_type="TVA",
                fiscal_year=2026, period="Q1", gross_amount=1000.0, deductions=2000.0, penalties=0.0,
                current_user=admin
            )

        # 3. Validation flow: Submit
        submitted_dec = self.declaration_service.submit_declaration(declaration.id, admin)
        self.assertEqual(submitted_dec.status.value, "Submitted")

        # 4. Validation flow: Validate (Admin only)
        editor = self.auth_service.login("editor", "editor123")
        with self.assertRaises(PermissionDeniedError):
            self.declaration_service.validate_declaration(declaration.id, editor)

        self.auth_service.login("admin", "admin123")
        validated_dec = self.declaration_service.validate_declaration(declaration.id, admin)
        self.assertEqual(validated_dec.status.value, "Validated")

        # 5. Lock test: Validated declarations cannot be edited
        with self.assertRaises(ValidationError):
            self.declaration_service.update_declaration(
                declaration_id=declaration.id, taxpayer_id=taxpayer_id, reference_number="DEC-2026-001",
                declaration_type="TVA", fiscal_year=2026, period="Q1", gross_amount=9000.0,
                deductions=1000.0, penalties=0.0, current_user=admin
            )

    def test_04_dashboard_telemetry(self):
        admin = self.auth_service.login("admin", "admin123")
        kpis = self.dashboard_service.get_kpis()
        
        # We created 1 active taxpayer (on top of 4 seeded ones), and 1 validated declaration (on top of 3 seeded validated ones)
        self.assertEqual(kpis["taxpayers"]["total"], 5)
        self.assertEqual(kpis["declarations"]["validated"], 4)
        # Total revenue = 8500 (created) + 105000 (seeded) + 131500 (seeded) + 77000 (seeded) = 322000.0
        self.assertEqual(kpis["total_revenue"], 322000.0)

        # Activities check
        activities = self.dashboard_service.get_recent_activity(5)
        self.assertTrue(len(activities) > 0)
        # Most recent activity should be related to database seeding, login or CRUD operations
        self.assertEqual(activities[0].username, "admin")

    def test_05_exports(self):
        admin = self.auth_service.login("admin", "admin123")
        decs = self.declaration_service.search_declarations()
        
        excel_path = "test_export.xlsx"
        csv_path = "test_export.csv"

        if os.path.exists(excel_path):
            os.remove(excel_path)
        if os.path.exists(csv_path):
            os.remove(csv_path)

        self.declaration_service.export_to_excel(decs, excel_path)
        self.declaration_service.export_to_csv(decs, csv_path)

        self.assertTrue(os.path.exists(excel_path))
        self.assertTrue(os.path.exists(csv_path))

        os.remove(excel_path)
        os.remove(csv_path)

if __name__ == '__main__':
    unittest.main()
