export const employeeHeaders = [
  'Employee ID Type',
  'Employee ID',
  'Reference Number',
  'Employee Name',
  'Employee BIC Code',
  'Employee Account',
  'Salary Frequency',
  'Number Of Working days',
  'Net Salary',
  'Basic Salary',
  'Extra Hours',
  'Extra Income',
  'Deductions',
  'Social Security Deductions',
  'Notes / Comments'
];

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
