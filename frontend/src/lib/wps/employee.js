export const employeeColumns = [
  { key: 'employee_id_type', label: 'Employee ID Type' },
  { key: 'employee_id', label: 'Employee ID' },
  { key: 'reference_number', label: 'Reference Number' },
  { key: 'employee_name', label: 'Employee Name' },
  { key: 'employee_bic_code', label: 'Employee BIC Code' },
  { key: 'employee_account', label: 'Employee Account' },
  { key: 'salary_frequency', label: 'Salary Frequency' },
  { key: 'number_of_working_days', label: 'Number Of Working days' },
  { key: 'net_salary', label: 'Net Salary' },
  { key: 'basic_salary', label: 'Basic Salary' },
  { key: 'extra_hours', label: 'Extra Hours' },
  { key: 'extra_income', label: 'Extra Income' },
  { key: 'deductions', label: 'Deductions' },
  { key: 'social_security_deductions', label: 'Social Security Deductions' },
  { key: 'notes_comments', label: 'Notes / Comments' }
];

export const employeeHeaders = employeeColumns.map((column) => column.label);
export const employeeFieldKeys = employeeColumns.map((column) => column.key);

const ZERO = 0;

function toNumberOrZero(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : ZERO;
}

export function calculateNetSalary(employee) {
  const net =
    toNumberOrZero(employee.basic_salary) +
    toNumberOrZero(employee.extra_income) -
    toNumberOrZero(employee.deductions) -
    toNumberOrZero(employee.social_security_deductions);
  return net.toFixed(3);
}

export function withCalculatedNetSalary(employee) {
  return {
    ...employee,
    net_salary: calculateNetSalary(employee)
  };
}

export function createEmployee() {
  return {
    employee_id_type: 'C',
    employee_id: '',
    reference_number: '',
    employee_name: '',
    employee_bic_code: 'BMUSOMRX',
    employee_account: '',
    salary_frequency: 'M',
    number_of_working_days: '30',
    net_salary: '0',
    basic_salary: '0',
    extra_hours: '0',
    extra_income: '0',
    deductions: '0',
    social_security_deductions: '0',
    notes_comments: ''
  };
}
