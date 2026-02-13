import io
import json
import re
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import List, Tuple

from openpyxl import Workbook

from .models import EmployeeRow, SIFRequest

DEC3 = Decimal("0.001")
DEC2 = Decimal("0.01")

REQUIRED_COLS = [
    "Employee ID Type",
    "Employee ID",
    "Reference Number",
    "Employee Name",
    "Employee BIC Code",
    "Employee Account",
    "Salary Frequency",
    "Number Of Working days",
    "Net Salary",
    "Basic Salary",
    "Extra Hours",
    "Extra Income",
    "Deductions",
    "Social Security Deductions",
    "Notes / Comments",
]


def q3(value) -> str:
    if value in (None, ""):
        return "0.000"
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        decimal_value = Decimal("0")
    d = decimal_value.quantize(DEC3, rounding=ROUND_HALF_UP)
    return f"{d:.3f}"


def q2(value) -> str:
    if value in (None, ""):
        return "0.00"
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        decimal_value = Decimal("0")
    d = decimal_value.quantize(DEC2, rounding=ROUND_HALF_UP)
    return f"{d:.2f}"


def safe_text(value, max_len: int) -> str:
    text = "" if value is None else str(value)
    text = text.strip()
    if len(text) > max_len:
        return text[:max_len]
    return text


def default_filename(employer_cr: str, payer_bank_short: str, processing_date: date, seq: int) -> str:
    ymd = processing_date.strftime("%Y%m%d")
    clean_employer = re.sub(r"[^0-9A-Za-z]+", "", employer_cr.strip())
    clean_bank = re.sub(r"[^0-9A-Za-z]+", "", payer_bank_short.strip())
    return f"SIF_{clean_employer}_{clean_bank}_{ymd}_{seq:03d}.xlsx"


def normalize_employee(employee: EmployeeRow) -> EmployeeRow:
    id_type = safe_text(employee.employee_id_type, 1).upper()
    if id_type not in ("C", "P"):
        id_type = "C"

    salary_frequency = safe_text(employee.salary_frequency, 1).upper()
    if salary_frequency not in ("M", "B"):
        salary_frequency = "M"

    working_days = safe_text(employee.number_of_working_days, 3)
    if not str(working_days).isdigit():
        working_days = "0"

    basic_salary = q3(employee.basic_salary)
    extra_income = q3(employee.extra_income)
    deductions = q3(employee.deductions)
    social_security_deductions = q3(employee.social_security_deductions)
    net_salary_decimal = (
        Decimal(basic_salary)
        + Decimal(extra_income)
        - Decimal(deductions)
        - Decimal(social_security_deductions)
    )
    net_salary = f"{net_salary_decimal.quantize(DEC3, rounding=ROUND_HALF_UP):.3f}"
    notes = safe_text(employee.notes_comments, 300)
    if Decimal(net_salary) == Decimal("0.000") and notes == "":
        notes = "Net salary is 0"

    return EmployeeRow(
        employee_id_type=id_type,
        employee_id=safe_text(employee.employee_id, 17),
        reference_number=safe_text(employee.reference_number, 64),
        employee_name=safe_text(employee.employee_name, 70),
        employee_bic_code=safe_text(employee.employee_bic_code, 11).upper(),
        employee_account=safe_text(employee.employee_account, 30),
        salary_frequency=salary_frequency,
        number_of_working_days=working_days,
        net_salary=net_salary,
        basic_salary=basic_salary,
        extra_hours=q2(employee.extra_hours),
        extra_income=extra_income,
        deductions=deductions,
        social_security_deductions=social_security_deductions,
        notes_comments=notes,
    )


def build_sif_rows(request: SIFRequest) -> Tuple[List[List[str]], List[EmployeeRow], str, str, int]:
    employer_cr = safe_text(request.employer_cr, 32)
    payer_cr = safe_text(request.payer_cr, 32)
    payer_bank_short = safe_text(request.payer_bank_short, 16)
    payer_account = safe_text(request.payer_account, 64)
    payment_type = safe_text(request.payment_type, 32)

    normalized = [normalize_employee(row) for row in request.employees]

    total_salaries = sum(Decimal(str(row.net_salary)) for row in normalized)
    total_salaries_str = f"{total_salaries.quantize(DEC3, rounding=ROUND_HALF_UP):.3f}"
    number_of_records = len(normalized)

    row0 = [
        "Employer CR-NO",
        "Payer CR-NO",
        "Payer Bank Short Name",
        "Payer Account Number",
        "Salary Year",
        "Salary Month",
        "Total Salaries",
        "Number Of Records",
        "Payment Type",
        "",
        "",
        "",
        "",
        "",
        "",
    ]

    row1 = [
        employer_cr,
        payer_cr,
        payer_bank_short,
        payer_account,
        str(request.salary_year),
        f"{request.salary_month:02d}",
        total_salaries_str,
        str(number_of_records),
        payment_type,
        "",
        "",
        "",
        "",
        "",
        "",
    ]

    row2 = REQUIRED_COLS[:]

    employee_rows = []
    for row in normalized:
        employee_rows.append(
            [
                row.employee_id_type,
                row.employee_id,
                row.reference_number,
                row.employee_name,
                row.employee_bic_code,
                row.employee_account,
                row.salary_frequency,
                row.number_of_working_days,
                str(row.net_salary),
                str(row.basic_salary),
                str(row.extra_hours),
                str(row.extra_income),
                str(row.deductions),
                str(row.social_security_deductions),
                row.notes_comments,
            ]
        )

    rows = [row0, row1, row2] + employee_rows
    filename = default_filename(
        employer_cr=employer_cr,
        payer_bank_short=payer_bank_short,
        processing_date=request.processing_date,
        seq=request.seq,
    )

    return rows, normalized, filename, total_salaries_str, number_of_records


def build_xlsx_bytes(rows: List[List[str]], sheet_name: str) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = safe_text(sheet_name, 31) or "Sheet1"

    for row in rows:
        ws.append(row)

    bio = io.BytesIO()
    wb.save(bio)
    return bio.getvalue()


def load_banks(data_path: Path) -> list:
    content = data_path.read_text(encoding="utf-8")
    data = json.loads(content)
    return sorted(data, key=lambda item: item["bank_name"].lower())
