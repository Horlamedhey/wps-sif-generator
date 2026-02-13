from datetime import date
from typing import List, Union

from pydantic import BaseModel, Field

Numberish = Union[str, int, float]


class EmployeeRow(BaseModel):
    employee_id_type: str = "C"
    employee_id: str = ""
    reference_number: str = ""
    employee_name: str = ""
    employee_bic_code: str = "BMUSOMRX"
    employee_account: str = ""
    salary_frequency: str = "M"
    number_of_working_days: str = "30"
    net_salary: Numberish = "0"
    basic_salary: Numberish = "0"
    extra_hours: Numberish = "0"
    extra_income: Numberish = "0"
    deductions: Numberish = "0"
    social_security_deductions: Numberish = "0"
    notes_comments: str = ""


class SIFRequest(BaseModel):
    employer_cr: str
    payer_cr: str
    payer_bank_short: str
    payer_account: str
    salary_year: int = Field(ge=2000, le=2100)
    salary_month: int = Field(ge=1, le=12)
    payment_type: str = "Salary"
    processing_date: date
    seq: int = Field(default=1, ge=1, le=999)
    sheet_name: str = "Sheet1"
    employees: List[EmployeeRow]


class PreviewResponse(BaseModel):
    filename: str
    total_salaries: str
    number_of_records: int
    sheet_name: str
    row_count: int
    normalized_employees: List[EmployeeRow]
