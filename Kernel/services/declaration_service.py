import csv
from datetime import datetime
from typing import List, Optional, Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from ..models.declaration import Declaration, DeclarationStatus
from ..models.user import User, UserRole
from ..exceptions.app_exceptions import ValidationError, PermissionDeniedError, NotFoundError

class DeclarationService:
    def __init__(self, declaration_repo, taxpayer_repo, audit_repo):
        self.declaration_repo = declaration_repo
        self.taxpayer_repo = taxpayer_repo
        self.audit_repo = audit_repo

    def _verify_write_permission(self, user: Optional[User]):
        if not user:
            raise PermissionDeniedError("Authentication required.")
        if user.role not in (UserRole.ADMIN, UserRole.EDITOR):
            raise PermissionDeniedError("Only Administrators and Editors can modify declarations.")

    def _verify_admin_permission(self, user: Optional[User]):
        if not user:
            raise PermissionDeniedError("Authentication required.")
        if user.role != UserRole.ADMIN:
            raise PermissionDeniedError("Only Administrators can perform this action.")

    def _validate_declaration_data(
        self,
        taxpayer_id: int,
        ref_num: str,
        dec_type: str,
        fiscal_year: int,
        period: str,
        gross: float,
        deductions: float,
        penalties: float
    ):
        if not ref_num or not ref_num.strip():
            raise ValidationError("Reference number is required.")
        if not dec_type or not dec_type.strip():
            raise ValidationError("Declaration type is required.")
        if not period or not period.strip():
            raise ValidationError("Period is required.")
        if fiscal_year < 1900 or fiscal_year > 2100:
            raise ValidationError("Fiscal year must be between 1900 and 2100.")
        if gross < 0:
            raise ValidationError("Gross amount cannot be negative.")
        if deductions < 0:
            raise ValidationError("Deductions cannot be negative.")
        if penalties < 0:
            raise ValidationError("Penalties cannot be negative.")
        if deductions > gross:
            raise ValidationError("Deductions cannot exceed gross amount.")

        # Check taxpayer exists
        taxpayer = self.taxpayer_repo.get_by_id(taxpayer_id)
        if not taxpayer:
            raise ValidationError("Invalid taxpayer selected. Taxpayer does not exist.")

    def create_declaration(
        self,
        taxpayer_id: int,
        reference_number: str,
        declaration_type: str,
        fiscal_year: int,
        period: str,
        gross_amount: float,
        deductions: float,
        penalties: float,
        current_user: User,
        status: str = "Draft"
    ) -> Declaration:
        self._verify_write_permission(current_user)
        self._validate_declaration_data(
            taxpayer_id, reference_number, declaration_type, fiscal_year, period, gross_amount, deductions, penalties
        )

        # Check duplicate Reference Number
        existing = self.declaration_repo.get_by_reference_number(reference_number.strip())
        if existing:
            raise ValidationError(f"A declaration with reference number '{reference_number}' already exists.")

        total_due = gross_amount - deductions + penalties
        now_str = datetime.now().isoformat()

        data = {
            "taxpayer_id": taxpayer_id,
            "reference_number": reference_number.strip(),
            "declaration_type": declaration_type.strip(),
            "fiscal_year": fiscal_year,
            "period": period.strip(),
            "gross_amount": gross_amount,
            "deductions": deductions,
            "penalties": penalties,
            "total_due": total_due,
            "status": status,
            "filed_date": now_str,
            "rejection_reason": ""
        }

        new_id = self.declaration_repo.create(data)

        self.audit_repo.log(
            current_user.username,
            "create_declaration",
            "declaration",
            new_id,
            f"Created declaration {reference_number} for taxpayer ID {taxpayer_id} (Total due: {total_due:.2f})"
        )

        return self.get_declaration_by_id(new_id)

    def update_declaration(
        self,
        declaration_id: int,
        taxpayer_id: int,
        reference_number: str,
        declaration_type: str,
        fiscal_year: int,
        period: str,
        gross_amount: float,
        deductions: float,
        penalties: float,
        current_user: User
    ) -> Declaration:
        self._verify_write_permission(current_user)
        self._validate_declaration_data(
            taxpayer_id, reference_number, declaration_type, fiscal_year, period, gross_amount, deductions, penalties
        )

        existing = self.declaration_repo.get_by_id(declaration_id)
        if not existing:
            raise NotFoundError("Declaration not found.")

        # Block modifying validated/rejected declarations
        if existing["status"] == "Validated":
            raise ValidationError("Validated declarations are locked and cannot be edited.")

        # Check duplicate reference number if changed
        if existing["reference_number"].lower() != reference_number.strip().lower():
            dup = self.declaration_repo.get_by_reference_number(reference_number.strip())
            if dup:
                raise ValidationError(f"A declaration with reference number '{reference_number}' already exists.")

        total_due = gross_amount - deductions + penalties

        data = {
            "taxpayer_id": taxpayer_id,
            "reference_number": reference_number.strip(),
            "declaration_type": declaration_type.strip(),
            "fiscal_year": fiscal_year,
            "period": period.strip(),
            "gross_amount": gross_amount,
            "deductions": deductions,
            "penalties": penalties,
            "total_due": total_due,
            "status": existing["status"],  # retain current status
            "rejection_reason": existing.get("rejection_reason")
        }

        self.declaration_repo.update(declaration_id, data)

        self.audit_repo.log(
            current_user.username,
            "update_declaration",
            "declaration",
            declaration_id,
            f"Updated declaration {reference_number} (New total due: {total_due:.2f})"
        )

        return self.get_declaration_by_id(declaration_id)

    def delete_declaration(self, declaration_id: int, current_user: User) -> bool:
        self._verify_admin_permission(current_user)

        existing = self.declaration_repo.get_by_id(declaration_id)
        if not existing:
            raise NotFoundError("Declaration not found.")

        success = self.declaration_repo.delete(declaration_id)
        if success:
            self.audit_repo.log(
                current_user.username,
                "delete_declaration",
                "declaration",
                declaration_id,
                f"Deleted declaration {existing['reference_number']} (Taxpayer ID: {existing['taxpayer_id']})"
            )
        return success

    def submit_declaration(self, declaration_id: int, current_user: User) -> Declaration:
        self._verify_write_permission(current_user)
        
        existing = self.declaration_repo.get_by_id(declaration_id)
        if not existing:
            raise NotFoundError("Declaration not found.")

        if existing["status"] == "Validated":
            raise ValidationError("Declaration is already validated.")

        existing["status"] = "Submitted"
        existing["rejection_reason"] = ""
        self.declaration_repo.update(declaration_id, existing)

        self.audit_repo.log(
            current_user.username,
            "submit_declaration",
            "declaration",
            declaration_id,
            f"Submitted declaration {existing['reference_number']} for validation"
        )
        return self.get_declaration_by_id(declaration_id)

    def validate_declaration(self, declaration_id: int, current_user: User) -> Declaration:
        self._verify_admin_permission(current_user)

        existing = self.declaration_repo.get_by_id(declaration_id)
        if not existing:
            raise NotFoundError("Declaration not found.")

        existing["status"] = "Validated"
        existing["rejection_reason"] = ""
        self.declaration_repo.update(declaration_id, existing)

        self.audit_repo.log(
            current_user.username,
            "validate_declaration",
            "declaration",
            declaration_id,
            f"Validated declaration {existing['reference_number']}"
        )
        return self.get_declaration_by_id(declaration_id)

    def reject_declaration(self, declaration_id: int, reason: str, current_user: User) -> Declaration:
        self._verify_admin_permission(current_user)
        if not reason or not reason.strip():
            raise ValidationError("Rejection reason is required.")

        existing = self.declaration_repo.get_by_id(declaration_id)
        if not existing:
            raise NotFoundError("Declaration not found.")

        existing["status"] = "Rejected"
        existing["rejection_reason"] = reason.strip()
        self.declaration_repo.update(declaration_id, existing)

        self.audit_repo.log(
            current_user.username,
            "reject_declaration",
            "declaration",
            declaration_id,
            f"Rejected declaration {existing['reference_number']} (Reason: {reason.strip()})"
        )
        return self.get_declaration_by_id(declaration_id)

    def get_declaration_by_id(self, declaration_id: int) -> Declaration:
        row = self.declaration_repo.get_by_id(declaration_id)
        if not row:
            raise NotFoundError("Declaration not found.")
        return self._map_row_to_model(row)

    def search_declarations(self, query: str = "", status_filter: Optional[str] = None, taxpayer_id: Optional[int] = None) -> List[Declaration]:
        rows = self.declaration_repo.search(query, status_filter, taxpayer_id)
        return [self._map_row_to_model(row) for row in rows]

    def export_to_excel(self, declarations: List[Declaration], file_path: str):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Declarations"
        
        # Grid lines visible
        ws.views.sheetView[0].showGridLines = True

        # Styles
        title_font = Font(name="Segoe UI", size=14, bold=True, color="1F4E79")
        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        border_thin = Border(
            left=Side(style='thin', color='D9D9D9'),
            right=Side(style='thin', color='D9D9D9'),
            top=Side(style='thin', color='D9D9D9'),
            bottom=Side(style='thin', color='D9D9D9')
        )
        currency_fmt = "$#,##0.00"

        # Title
        ws.append(["Taxes Management System - Declarations Export"])
        ws.cell(1, 1).font = title_font
        ws.row_dimensions[1].height = 30
        ws.append([]) # spacer

        headers = [
            "Reference Number", "Taxpayer Name", "Type", "Fiscal Year", "Period",
            "Gross Amount", "Deductions", "Penalties", "Total Due", "Status",
            "Filed Date", "Rejection Reason"
        ]
        ws.append(headers)
        ws.row_dimensions[3].height = 24

        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=3, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for d in declarations:
            filed_str = d.filed_date.strftime("%Y-%m-%d %H:%M") if isinstance(d.filed_date, datetime) else str(d.filed_date)
            row_data = [
                d.reference_number,
                d.taxpayer_name or f"Taxpayer #{d.taxpayer_id}",
                d.declaration_type,
                d.fiscal_year,
                d.period,
                d.gross_amount,
                d.deductions,
                d.penalties,
                d.total_due,
                d.status.value,
                filed_str,
                d.rejection_reason or ""
            ]
            ws.append(row_data)

        # Format Cells
        start_row = 4
        end_row = len(declarations) + 3
        for r in range(start_row, end_row + 1):
            ws.row_dimensions[r].height = 18
            for c in range(1, len(headers) + 1):
                cell = ws.cell(row=r, column=c)
                cell.font = Font(name="Segoe UI", size=10)
                cell.border = border_thin
                
                # Alignments and Number Formats
                if c in (1, 4, 5, 10, 11): # Ref, Year, Period, Status, Date
                    cell.alignment = Alignment(horizontal="center")
                elif c in (6, 7, 8, 9): # Money columns
                    cell.alignment = Alignment(horizontal="right")
                    cell.number_format = currency_fmt
                else:
                    cell.alignment = Alignment(horizontal="left")

        # Auto-size columns
        for col in ws.columns:
            max_len = 0
            for cell in col:
                # Skip title row for size calculation
                if cell.row == 1:
                    continue
                
                val = cell.value
                if val is not None:
                    # Format float values nicely for string length estimate
                    if isinstance(val, float):
                        val_str = f"${val:,.2f}"
                    else:
                        val_str = str(val)
                    max_len = max(max_len, len(val_str))
            
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        wb.save(file_path)

    def export_to_csv(self, declarations: List[Declaration], file_path: str):
        with open(file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Reference Number", "Taxpayer Name", "Type", "Fiscal Year", "Period",
                "Gross Amount", "Deductions", "Penalties", "Total Due", "Status",
                "Filed Date", "Rejection Reason"
            ])
            for d in declarations:
                filed_str = d.filed_date.strftime("%Y-%m-%d %H:%M") if isinstance(d.filed_date, datetime) else str(d.filed_date)
                writer.writerow([
                    d.reference_number,
                    d.taxpayer_name or f"Taxpayer #{d.taxpayer_id}",
                    d.declaration_type,
                    d.fiscal_year,
                    d.period,
                    f"{d.gross_amount:.2f}",
                    f"{d.deductions:.2f}",
                    f"{d.penalties:.2f}",
                    f"{d.total_due:.2f}",
                    d.status.value,
                    filed_str,
                    d.rejection_reason or ""
                ])

    def _map_row_to_model(self, row: Dict[str, Any]) -> Declaration:
        try:
            filed_date = datetime.fromisoformat(row["filed_date"])
        except ValueError:
            filed_date = datetime.now()

        return Declaration(
            id=row["id"],
            taxpayer_id=row["taxpayer_id"],
            reference_number=row["reference_number"],
            declaration_type=row["declaration_type"],
            fiscal_year=row["fiscal_year"],
            period=row["period"],
            gross_amount=row["gross_amount"],
            deductions=row["deductions"],
            penalties=row["penalties"],
            total_due=row["total_due"],
            status=DeclarationStatus.from_str(row["status"]),
            filed_date=filed_date,
            rejection_reason=row.get("rejection_reason") or "",
            taxpayer_name=row.get("taxpayer_name")
        )
