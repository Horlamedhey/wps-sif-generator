import re
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

import pandas as pd
import streamlit as st
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

# Bank Identification Codes from your bank guide (Section 8)  [oai_citation:2‡dfr-islamic-guide-english-wps.pdf](sediment://file_0000000007a0722fbd978cd25b70b470)
BANK_BIC = {
    "BANK DHOFAR": "BDOFOMRU",
    "Bank Muscat": "BMUSOMRX",
    "National Bank of Oman": "NBOMOMRX",
    "Oman Arab Bank": "OMABOMRU",
    "Bank Sohar": "BSHROMRU",
    "HSBC Bank Oman": "BBMEOMRX",
    "Ahli Bank": "AUBOOMRU",
    "Oman Development Bank": "ODBLOMRX",
    "Oman Housing Bank": "OHBLOMRX",
    "Bank Nizwa": "BNZWOMRX",
    "Dhofar Islamic Banking": "BDOFOMRUMIB",
    "Bank Muscat Meethaq": "BMUSOMRXISL",
    "NBO Muzn": "NBOMOMRXIBS",
    "Al Hilal Ahli Bank": "AUBOOMRUALH",
    "National Bank of Abu Dhabi": "NBADOMRX",
    "Qatar National Bank": "QNBAOMRX",
    "Standard Chartered Bank": "SCBLOMRX",
    "Bank of Beirut": "BABEOMRX",
    "Bank of Baroda": "BARBOMMX",
    "State Bank of India": "SBINOMRX",
    "Habib Bank Limited": "HABBOMRX",
    "AL IZZ ISLAMIC BANK": "IZZBOMRU",
    "Bank Sohar Islamic Window": "BSHROMRUISL",
    "Al Yusr Islamic Banking": "OMABOMRUYSR",
}

# --- Helpers ---
DEC3 = Decimal("0.001")
DEC2 = Decimal("0.01")

def q3(x) -> str:
    """Quantize to 3 decimals as string (WPS decimals are 9,3 for most money fields)."""
    if x is None or x == "":
        return "0.000"
    d = Decimal(str(x)).quantize(DEC3, rounding=ROUND_HALF_UP)
    return f"{d:.3f}"

def q2(x) -> str:
    """Quantize to 2 decimals as string (Extra hours in samples is 3,2)."""
    if x is None or x == "":
        return "0.00"
    d = Decimal(str(x)).quantize(DEC2, rounding=ROUND_HALF_UP)
    return f"{d:.2f}"

def is_yyyymm_valid(year: int, month: int) -> bool:
    if year < 2000 or year > 2100:
        return False
    return 1 <= month <= 12

def safe_text(s: str, max_len: int) -> str:
    s = "" if s is None else str(s)
    s = s.strip()
    if len(s) > max_len:
        return s[:max_len]
    return s

def build_sif_dataframe(
    employer_cr: str,
    payer_cr: str,
    payer_bank_short: str,
    payer_account: str,
    salary_year: int,
    salary_month: int,
    payment_type: str,
    employees_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Returns a 2D dataframe that matches the sample layout:
    Row0 labels, Row1 values, Row2 labels, Row3+ employee values.
    """
    # Clean employer/payer values
    employer_cr = safe_text(employer_cr, 32)
    payer_cr = safe_text(payer_cr, 32)
    payer_bank_short = safe_text(payer_bank_short, 16)
    payer_account = safe_text(payer_account, 64)
    payment_type = safe_text(payment_type, 32)

    # Ensure required employee columns exist
    required_cols = [
        "Employee ID Type", "Employee ID", "Reference Number", "Employee Name",
        "Employee BIC Code", "Employee Account", "Salary Frequency", "Number Of Working days",
        "Net Salary", "Basic Salary", "Extra Hours", "Extra Income", "Deductions",
        "Social Security Deductions", "Notes / Comments"
    ]
    for c in required_cols:
        if c not in employees_df.columns:
            employees_df[c] = ""

    # Normalize/validate employee rows
    normalized_rows = []
    for _, r in employees_df.iterrows():
        id_type = safe_text(r["Employee ID Type"], 1).upper()
        if id_type not in ("C", "P"):
            id_type = "C"  # default

        emp_id = safe_text(r["Employee ID"], 17)
        ref = safe_text(r["Reference Number"], 64)
        name = safe_text(r["Employee Name"], 70)
        bic = safe_text(r["Employee BIC Code"], 11).upper()
        acct = safe_text(r["Employee Account"], 30)
        freq = safe_text(r["Salary Frequency"], 1).upper()
        if freq not in ("M", "B"):
            freq = "M"
        work_days = safe_text(r["Number Of Working days"], 3)
        if not str(work_days).isdigit():
            work_days = "0"

        net = q3(r["Net Salary"])
        basic = q3(r["Basic Salary"])
        ex_hours = q2(r["Extra Hours"])
        ex_income = q3(r["Extra Income"])
        ded = q3(r["Deductions"])
        ssd = q3(r["Social Security Deductions"])
        notes = safe_text(r["Notes / Comments"], 300)

        # Notes mandatory if net salary is 0 (per guide)  [oai_citation:3‡dfr-islamic-guide-english-wps.pdf](sediment://file_0000000007a0722fbd978cd25b70b470)
        if Decimal(net) == Decimal("0.000") and notes == "":
            notes = "Net salary is 0"

        normalized_rows.append([
            id_type, emp_id, ref, name, bic, acct, freq, work_days,
            net, basic, ex_hours, ex_income, ded, ssd, notes
        ])

    emp_values_df = pd.DataFrame(normalized_rows, columns=required_cols)

    # Compute totals
    total_salaries = sum(Decimal(v) for v in emp_values_df["Net Salary"].tolist())
    total_salaries_str = f"{total_salaries.quantize(DEC3, rounding=ROUND_HALF_UP):.3f}"
    num_records = len(emp_values_df)

    # Compose the 4+ rows, 15 columns exactly
    row0 = [
        "Employer CR-NO", "Payer CR-NO", "Payer Bank Short Name", "Payer Account Number",
        "Salary Year", "Salary Month", "Total Salaries", "Number Of Records", "Payment Type",
        "", "", "", "", "", ""
    ]
    row1 = [
        employer_cr, payer_cr, payer_bank_short, payer_account,
        salary_year, f"{salary_month:02d}", total_salaries_str, num_records, payment_type,
        "", "", "", "", "", ""
    ]
    row2 = required_cols[:]  # employee headers
    # Employee rows should align to 15 columns
    data_rows = emp_values_df.values.tolist()

    all_rows = [row0, row1, row2] + data_rows
    return pd.DataFrame(all_rows)

def write_xlsx(df2d: pd.DataFrame, out_path: str, sheet_name: str = "Sheet1"):
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    for r in dataframe_to_rows(df2d, index=False, header=False):
        ws.append(r)

    # Bank note: only one sheet  [oai_citation:4‡dfr-islamic-guide-english-wps.pdf](sediment://file_0000000007a0722fbd978cd25b70b470)
    wb.save(out_path)

def default_filename(employer_cr: str, payer_bank_short: str, processing_date: datetime, seq: int) -> str:
    ymd = processing_date.strftime("%Y%m%d")
    employer_cr = re.sub(r"[^0-9A-Za-z]+", "", employer_cr.strip())
    payer_bank_short = re.sub(r"[^0-9A-Za-z]+", "", payer_bank_short.strip())
    return f"SIF_{employer_cr}_{payer_bank_short}_{ymd}_{seq:03d}.xlsx"


# --- UI ---
st.set_page_config(page_title="Oman WPS SIF Generator", layout="wide")
st.title("Oman WPS (SIF) Excel Generator")

with st.expander("Employer / Payer Details", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        employer_cr = st.text_input("Employer CR-NO", value="")
        payer_cr = st.text_input("Payer CR-NO", value="")
        payer_account = st.text_input("Payer Account Number", value="")
    with c2:
        payer_bank_short = st.text_input("Payer Bank Short Name (e.g. BMCT, SBI)", value="BMCT")
        salary_year = st.number_input("Salary Year (YYYY)", min_value=2000, max_value=2100, value=datetime.now().year, step=1)
        salary_month = st.number_input("Salary Month (MM)", min_value=1, max_value=12, value=datetime.now().month, step=1)
    with c3:
        payment_type = st.text_input("Payment Type (e.g. Salary / Monthly Salary)", value="Salary")
        processing_date = st.date_input("Processing date (used for file name)", value=datetime.now().date())
        seq = st.number_input("File sequence number", min_value=1, max_value=999, value=1, step=1)

    if not is_yyyymm_valid(int(salary_year), int(salary_month)):
        st.error("Invalid Salary Year/Month.")

st.subheader("Employees")
st.caption("Tip: Paste rows from Excel. Amounts will be normalized to 3 decimals. Extra Hours to 2 decimals.")

# Default blank table (one row)
default_emp = pd.DataFrame([{
    "Employee ID Type": "C",
    "Employee ID": "",
    "Reference Number": "",
    "Employee Name": "",
    "Employee BIC Code": "BMUSOMRX",
    "Employee Account": "",
    "Salary Frequency": "M",
    "Number Of Working days": "30",
    "Net Salary": "0",
    "Basic Salary": "0",
    "Extra Hours": "0",
    "Extra Income": "0",
    "Deductions": "0",
    "Social Security Deductions": "0",
    "Notes / Comments": "",
}])

employees_df = st.data_editor(
    default_emp,
    num_rows="dynamic",
    width="stretch"
)

# Show quick bank code helper
with st.expander("Bank BIC Code Helper (from bank guide)"):
    st.write(pd.DataFrame([{"Bank": k, "BIC": v} for k, v in BANK_BIC.items()]))

# Generate
st.divider()

colA, colB = st.columns([2, 1])

with colA:
    generate = st.button("Generate .xlsx", type="primary")

with colB:
    sheet_name = st.text_input("Sheet name", value="Sheet1")

if generate:
    # basic required checks (lightweight; bank will validate on upload)  [oai_citation:5‡dfr-islamic-guide-english-wps.pdf](sediment://file_0000000007a0722fbd978cd25b70b470)
    if not employer_cr.strip() or not payer_cr.strip() or not payer_account.strip():
        st.error("Employer CR-NO, Payer CR-NO, and Payer Account Number are required.")
        st.stop()

    if sheet_name.strip() == "":
        sheet_name = "Sheet1"

    sif_df2d = build_sif_dataframe(
        employer_cr=employer_cr,
        payer_cr=payer_cr,
        payer_bank_short=payer_bank_short,
        payer_account=payer_account,
        salary_year=int(salary_year),
        salary_month=int(salary_month),
        payment_type=payment_type,
        employees_df=employees_df.copy()
    )

    filename = default_filename(
        employer_cr=employer_cr,
        payer_bank_short=payer_bank_short,
        processing_date=datetime.combine(processing_date, datetime.min.time()),
        seq=int(seq)
    )
    out_path = filename
    write_xlsx(sif_df2d, out_path=out_path, sheet_name=sheet_name)

    st.success(f"Generated: {filename}")
    st.dataframe(sif_df2d, width="stretch")

    with open(out_path, "rb") as f:
        st.download_button(
            label="Download generated file",
            data=f,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )