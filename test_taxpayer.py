from Infrastructure.migrations.schema import DatabaseInitializer

DatabaseInitializer("taxes.db").initialize()

from Infrastructure.database.connection import DatabaseConnection
from Infrastructure.repositories.taxpayer_repository import TaxpayerRepository
from Infrastructure.repositories.audit_repository import AuditRepository

from Kernel.services.taxpayer_service import TaxpayerService
from Kernel.services.audit_service import AuditService

from Kernel.models.taxpayer import Taxpayer, TaxpayerType, TaxpayerStatus


def test_create_taxpayer():
    # ---------------- DB ----------------
    db = DatabaseConnection()

    # ---------------- Repos ----------------
    taxpayer_repo = TaxpayerRepository(db)
    audit_repo = AuditRepository(db)

    # ---------------- Services ----------------
    audit_service = AuditService(audit_repo)
    taxpayer_service = TaxpayerService(taxpayer_repo, audit_service)

    # ---------------- ACTION ----------------
    taxpayer = Taxpayer(
        id=None,
        tax_id="TEST001",
        name="Test User",
        taxpayer_type=TaxpayerType.PHYSICAL,
        status=TaxpayerStatus.ACTIVE,
        email="test@test.com",
        phone="123456",
        address="Tunis"
    )

    created = taxpayer_service.create(taxpayer)

    print("Created:", created)


if __name__ == "__main__":
    test_create_taxpayer()