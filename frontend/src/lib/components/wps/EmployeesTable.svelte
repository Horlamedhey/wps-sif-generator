<script>
  import { Card } from '$lib/components/ui/card';
  import { Input } from '$lib/components/ui/input';
  import { Button } from '$lib/components/ui/button';
  import { Label } from '$lib/components/ui/label';
  import * as Select from '$lib/components/ui/select';
  import OmrSymbol from '$lib/components/wps/OmrSymbol.svelte';
  import { employeeHeaders, employeeFieldKeys, createEmployee, withCalculatedNetSalary } from '$lib/wps/employee';

  export let form = {
    employerCr: '',
    payerCr: '',
    payerBankShort: '',
    payerAccount: '',
    salaryYear: '',
    salaryMonth: '',
    paymentType: ''
  };
  export let employees = [];
  export let banks = [];
  export let loadingBanks = false;
  export let banksError = '';
  export let seededEmployeeDraft = null;
  export let seedEmployeeRequestId = 0;
  export let labels = {};
  export let sectionTitles = {};
  export let buttonLabels = {};
  export let tipText =
    'Tip: Add a row through the form, then you can still edit directly in the table. Net Salary is auto-calculated as Basic Salary + Extra Income - Deductions - Social Security Deductions.';

  const previewMetaHeader = [
    'Employer CR-NO',
    'Payer CR-NO',
    'Payer Bank Short Name',
    'Payer Account Number',
    'Salary Year',
    'Salary Month',
    'Total Salaries',
    'Number Of Records',
    'Payment Type',
    '',
    '',
    '',
    '',
    '',
    ''
  ];

  const inputClass =
    'h-10 rounded-md border border-[#2a3853] bg-[#1b2436] text-[#dbe5f6] placeholder:text-[#7887a3] focus-visible:ring-2 focus-visible:ring-[#4a8cff]/50 focus-visible:border-[#4a8cff]';
  const currencyInputClass = `${inputClass} pl-12`;
  const selectTriggerClass = `${inputClass} w-full justify-between px-3 text-sm font-normal`;
  const selectContentClass = 'border border-[#2a3853] bg-[#0f1727] text-[#dbe5f6]';
  const selectItemClass = 'text-[#dbe5f6]';

  const cellInputClass =
    'h-9 rounded-none border-0 bg-transparent px-2 text-[13px] text-[#dbe5f6] focus-visible:ring-0 focus-visible:border-0';
  const cellSelectTriggerClass =
    'h-9 w-full rounded-none border-0 bg-transparent px-2 text-[13px] font-normal text-[#dbe5f6] shadow-none justify-between focus-visible:ring-0 focus-visible:border-0';
  const previewCellClass = 'border border-[#1f2b40] px-2 py-2 text-[12px] whitespace-nowrap';
  const decimalFieldScale = {
    basic_salary: 3,
    extra_hours: 2,
    extra_income: 3,
    deductions: 3,
    social_security_deductions: 3
  };

  let showAddForm = false;
  let addFormError = '';
  let draftEmployee = createEmployee();
  let selectedDraftBank = null;
  let lastSeedEmployeeRequestId = 0;

  let previewRows = [];

  $: if (banks.length > 0 && !banks.some((bank) => bank.bic === draftEmployee.employee_bic_code)) {
    draftEmployee = { ...draftEmployee, employee_bic_code: banks[0].bic };
  }
  $: selectedDraftBank = banks.find((bank) => bank.bic === draftEmployee.employee_bic_code) || null;
  $: if (seedEmployeeRequestId > lastSeedEmployeeRequestId && seededEmployeeDraft) {
    prepareDraft(seededEmployeeDraft);
    lastSeedEmployeeRequestId = seedEmployeeRequestId;
  }

  $: {
    const normalizedEmployees = employees.map((employee) =>
      normalizeEmployeeForPreview(withCalculatedNetSalary(employee))
    );
    const totalSalaries = normalizedEmployees
      .reduce((sum, row) => sum + Number(row.net_salary), 0)
      .toFixed(3);

    const metaRow = [
      safeText(form.employerCr, 32),
      safeText(form.payerCr, 32),
      safeText(form.payerBankShort, 16),
      safeText(form.payerAccount, 64),
      String(form.salaryYear ?? ''),
      isBlank(form.salaryMonth) ? '' : String(form.salaryMonth).padStart(2, '0'),
      totalSalaries,
      String(normalizedEmployees.length),
      safeText(form.paymentType, 32),
      '',
      '',
      '',
      '',
      '',
      ''
    ];

    previewRows = [
      previewMetaHeader,
      metaRow,
      employeeHeaders,
      ...normalizedEmployees.map((employee) => employeeFieldKeys.map((field) => employee[field]))
    ];
  }

  function openAddForm() {
    prepareDraft(createEmployee());
  }

  function prepareDraft(nextDraft) {
    showAddForm = true;
    addFormError = '';
    const mergedDraft = { ...createEmployee(), ...nextDraft };
    draftEmployee = withCalculatedNetSalary(sanitizeEmployeeEntry(applyBankFallback(mergedDraft)));
  }

  function applyBankFallback(employee) {
    if (banks.length === 0) {
      return employee;
    }

    if (banks.some((bank) => bank.bic === employee.employee_bic_code)) {
      return employee;
    }

    return { ...employee, employee_bic_code: banks[0].bic };
  }

  function cancelAddForm() {
    showAddForm = false;
    addFormError = '';
  }

  function updateDraftField(field, value) {
    const next = sanitizeEmployeeEntry({ ...draftEmployee, [field]: normalizeSelectValue(value) });
    draftEmployee = withCalculatedNetSalary(next);
  }

  function updateEmployeeField(rowIndex, field, value) {
    const next = [...employees];
    const current = next[rowIndex] || createEmployee();
    next[rowIndex] = withCalculatedNetSalary(
      sanitizeEmployeeEntry({ ...current, [field]: normalizeSelectValue(value) })
    );
    employees = next;
  }

  function handlePreviewCellInput(rowIndex, field, event) {
    if (isNetSalaryField(field)) {
      return;
    }
    updateEmployeeField(rowIndex, field, event.currentTarget.value);
  }

  function handlePreviewSelectChange(rowIndex, field, value) {
    const normalizedValue = normalizeSelectValue(value);
    if (!normalizedValue) {
      return;
    }
    updateEmployeeField(rowIndex, field, normalizedValue);
  }

  function normalizeSelectValue(value) {
    if (typeof value === 'string') {
      return value;
    }
    if (value && typeof value === 'object' && 'value' in value) {
      const extracted = value.value;
      return typeof extracted === 'string' ? extracted : String(extracted || '');
    }
    return '';
  }

  function isBlank(value) {
    return value === null || value === undefined || String(value).trim() === '';
  }

  function isValidNumber(value) {
    if (isBlank(value)) return false;
    return !Number.isNaN(Number(value));
  }

  function safeText(value, maxLen) {
    const text = value === null || value === undefined ? '' : String(value).trim();
    return text.length > maxLen ? text.slice(0, maxLen) : text;
  }

  function q(value, decimals) {
    if (isBlank(value) || Number.isNaN(Number(value))) {
      return decimals === 2 ? '0.00' : '0.000';
    }
    return Number(value).toFixed(decimals);
  }

  function normalizeEmployeeForPreview(employee) {
    const idType = ['C', 'P'].includes(safeText(employee.employee_id_type, 1).toUpperCase())
      ? safeText(employee.employee_id_type, 1).toUpperCase()
      : 'C';

    const salaryFrequency = ['M', 'B'].includes(safeText(employee.salary_frequency, 1).toUpperCase())
      ? safeText(employee.salary_frequency, 1).toUpperCase()
      : 'M';

    const workingDays = safeText(employee.number_of_working_days, 3);
    const normalizedWorkingDays = /^\d+$/.test(workingDays) ? workingDays : '0';

    const netSalary = q(employee.net_salary, 3);
    let notes = safeText(employee.notes_comments, 300);
    if (Number(netSalary) === 0 && notes === '') {
      notes = 'Net salary is 0';
    }

    return {
      employee_id_type: idType,
      employee_id: safeText(employee.employee_id, 17),
      reference_number: safeText(employee.reference_number, 64),
      employee_name: safeText(employee.employee_name, 70),
      employee_bic_code: safeText(employee.employee_bic_code, 11).toUpperCase(),
      employee_account: safeText(employee.employee_account, 30),
      salary_frequency: salaryFrequency,
      number_of_working_days: normalizedWorkingDays,
      net_salary: netSalary,
      basic_salary: q(employee.basic_salary, 3),
      extra_hours: q(employee.extra_hours, 2),
      extra_income: q(employee.extra_income, 3),
      deductions: q(employee.deductions, 3),
      social_security_deductions: q(employee.social_security_deductions, 3),
      notes_comments: notes
    };
  }

  function sanitizeDigits(value, maxLen) {
    const digits = String(value ?? '').replace(/\D/g, '');
    return typeof maxLen === 'number' ? digits.slice(0, maxLen) : digits;
  }

  function sanitizeLettersNoDigits(value, maxLen) {
    const text = String(value ?? '').replace(/\d/g, '');
    return typeof maxLen === 'number' ? text.slice(0, maxLen) : text;
  }

  function sanitizeAlphanumeric(value, maxLen) {
    const text = String(value ?? '').replace(/[^A-Za-z0-9]/g, '');
    return typeof maxLen === 'number' ? text.slice(0, maxLen) : text;
  }

  function sanitizeDecimal(value, scale) {
    const text = String(value ?? '');
    if (text === '') {
      return '';
    }

    let normalized = text.replace(/[^\d.]/g, '');
    if (normalized.startsWith('.')) {
      normalized = `0${normalized}`;
    }

    const dotIndex = normalized.indexOf('.');
    if (dotIndex === -1) {
      return normalized;
    }

    const integerPart = normalized.slice(0, dotIndex);
    const decimalPart = normalized.slice(dotIndex + 1).replace(/\./g, '').slice(0, scale);
    return `${integerPart}.${decimalPart}`;
  }

  function sanitizeEmployeeEntry(employee) {
    const idType = normalizeSelectValue(employee.employee_id_type) === 'P' ? 'P' : 'C';
    const salaryFrequency = normalizeSelectValue(employee.salary_frequency) === 'B' ? 'B' : 'M';

    return {
      ...employee,
      employee_id_type: idType,
      employee_id:
        idType === 'C'
          ? sanitizeDigits(employee.employee_id, 17)
          : sanitizeAlphanumeric(employee.employee_id, 17).toUpperCase(),
      reference_number: String(employee.reference_number ?? '').slice(0, 64),
      employee_name: sanitizeLettersNoDigits(employee.employee_name, 70),
      employee_bic_code: normalizeSelectValue(employee.employee_bic_code).toUpperCase().slice(0, 11),
      employee_account: sanitizeDigits(employee.employee_account, 30),
      salary_frequency: salaryFrequency,
      number_of_working_days: sanitizeDigits(employee.number_of_working_days, 3),
      basic_salary: sanitizeDecimal(employee.basic_salary, decimalFieldScale.basic_salary),
      extra_hours: sanitizeDecimal(employee.extra_hours, decimalFieldScale.extra_hours),
      extra_income: sanitizeDecimal(employee.extra_income, decimalFieldScale.extra_income),
      deductions: sanitizeDecimal(employee.deductions, decimalFieldScale.deductions),
      social_security_deductions: sanitizeDecimal(
        employee.social_security_deductions,
        decimalFieldScale.social_security_deductions
      ),
      notes_comments: String(employee.notes_comments ?? '').slice(0, 300)
    };
  }

  function validateDraftEmployee() {
    const missing = [];
    if (!['C', 'P'].includes(draftEmployee.employee_id_type)) missing.push('Employee ID Type');
    if (isBlank(draftEmployee.employee_id)) missing.push('Employee ID');
    if (isBlank(draftEmployee.employee_name)) missing.push('Employee Name');
    if (isBlank(draftEmployee.employee_bic_code)) missing.push('Employee Bank Identification Code');
    if (isBlank(draftEmployee.employee_account)) missing.push('Employee Account Number');
    if (!['M', 'B'].includes(draftEmployee.salary_frequency)) missing.push('Salary Frequency');
    if (isBlank(draftEmployee.number_of_working_days)) missing.push('Number of Working Days');
    if (!isValidNumber(draftEmployee.number_of_working_days)) missing.push('Number of Working Days must be numeric');
    if (isBlank(draftEmployee.basic_salary)) missing.push('Basic Salary');
    if (!isValidNumber(draftEmployee.basic_salary)) missing.push('Basic Salary must be numeric');

    const netSalary = isValidNumber(draftEmployee.net_salary) ? Number(draftEmployee.net_salary) : null;
    if (netSalary === 0 && isBlank(draftEmployee.notes_comments)) {
      missing.push('Notes / Comments is required when Net Salary is 0');
    }

    if (missing.length > 0) {
      addFormError = `Please fill required fields: ${missing.join(', ')}`;
      return false;
    }

    addFormError = '';
    return true;
  }

  function addDraftEmployee() {
    if (!validateDraftEmployee()) {
      return;
    }

    employees = [...employees, withCalculatedNetSalary({ ...draftEmployee })];
    showAddForm = false;
  }

  function isNetSalaryField(field) {
    return field === 'net_salary';
  }

  function isPreviewSelectField(field) {
    return field === 'employee_id_type' || field === 'employee_bic_code' || field === 'salary_frequency';
  }

  function getCellInputMode(field, rowIndex) {
    if (field === 'employee_id') {
      return getPreviewSelectValue(rowIndex, 'employee_id_type') === 'C' ? 'numeric' : 'text';
    }
    if (field === 'employee_account' || field === 'number_of_working_days') {
      return 'numeric';
    }
    if (field in decimalFieldScale) {
      return 'decimal';
    }
    return 'text';
  }

  function getCellMaxLength(field) {
    if (field === 'employee_id') return 17;
    if (field === 'reference_number') return 64;
    if (field === 'employee_name') return 70;
    if (field === 'employee_account') return 30;
    if (field === 'number_of_working_days') return 3;
    if (field === 'notes_comments') return 300;
    return undefined;
  }

  function getCellPattern(field, rowIndex) {
    if (field === 'employee_id') {
      return getPreviewSelectValue(rowIndex, 'employee_id_type') === 'C' ? '[0-9]*' : undefined;
    }
    if (field === 'employee_account' || field === 'number_of_working_days') {
      return '[0-9]*';
    }
    return undefined;
  }

  function getPreviewSelectValue(rowIndex, field) {
    const employee = employees[rowIndex] || createEmployee();
    const idType = normalizeSelectValue(employee.employee_id_type);
    const salaryFrequency = normalizeSelectValue(employee.salary_frequency);
    const employeeBicCode = normalizeSelectValue(employee.employee_bic_code).toUpperCase();
    if (field === 'employee_id_type') {
      return idType === 'P' ? 'P' : 'C';
    }
    if (field === 'salary_frequency') {
      return salaryFrequency === 'B' ? 'B' : 'M';
    }
    if (field === 'employee_bic_code') {
      return employeeBicCode;
    }
    return '';
  }

</script>

<h2 class="mt-5 text-3xl font-bold tracking-tight text-[#dbe5f6] md:text-4xl">{sectionTitles.employees || 'Employees'}</h2>
<p class="mb-2 text-sm font-medium text-[#96a5bf]">
  {tipText}
</p>

<div class="mb-3 flex justify-end">
  {#if !showAddForm}
    <Button
      class="h-9 rounded-md border border-[#2d3b57] bg-[#172239] text-[#dbe5f6] hover:bg-[#1f2f4a]"
      onclick={openAddForm}
      type="button"
      variant="outline"
    >
      {buttonLabels.addRow || 'Add Row'}
    </Button>
  {/if}
</div>

{#if showAddForm}
  <Card class="wps-panel mb-4 rounded-[10px] border border-[#243247] p-3 shadow-none gap-3">
    <h3 class="text-sm font-semibold text-[#dbe5f6]">{sectionTitles.newEmployee || 'New Employee'}</h3>

    <div class="grid grid-cols-1 gap-3 xl:grid-cols-3">
      <div class="space-y-3">
        <div class="space-y-1.5">
          <Label class="text-xs font-medium text-[#96a5bf]" for="new-employee-id-type">{labels.employeeIdType || 'Employee ID Type'}</Label>
          <Select.Root type="single" value={draftEmployee.employee_id_type} onValueChange={(value) => updateDraftField('employee_id_type', value || 'C')}>
            <Select.Trigger class={selectTriggerClass} id="new-employee-id-type">
              {draftEmployee.employee_id_type === 'P' ? 'Passport (P)' : 'Civil ID (C)'}
            </Select.Trigger>
            <Select.Content class={selectContentClass}>
              <Select.Item class={selectItemClass} label="Civil ID (C)" value="C">Civil ID (C)</Select.Item>
              <Select.Item class={selectItemClass} label="Passport (P)" value="P">Passport (P)</Select.Item>
            </Select.Content>
          </Select.Root>
        </div>

        <div class="space-y-1.5">
          <Label class="text-xs font-medium text-[#96a5bf]" for="new-employee-id">{labels.employeeId || 'Employee ID'}</Label>
          <Input
            id="new-employee-id"
            class={inputClass}
            inputmode={draftEmployee.employee_id_type === 'C' ? 'numeric' : 'text'}
            maxlength="17"
            oninput={(event) => updateDraftField('employee_id', event.currentTarget.value)}
            pattern={draftEmployee.employee_id_type === 'C' ? '[0-9]*' : undefined}
            type="text"
            value={draftEmployee.employee_id}
          />
        </div>

        <div class="space-y-1.5">
          <Label class="text-xs font-medium text-[#96a5bf]" for="new-reference-number">{labels.referenceNumber || 'Reference Number'}</Label>
          <Input
            id="new-reference-number"
            class={inputClass}
            maxlength="64"
            oninput={(event) => updateDraftField('reference_number', event.currentTarget.value)}
            type="text"
            value={draftEmployee.reference_number}
          />
        </div>

        <div class="space-y-1.5">
          <Label class="text-xs font-medium text-[#96a5bf]" for="new-employee-name">{labels.employeeName || 'Employee Name'}</Label>
          <Input
            id="new-employee-name"
            class={inputClass}
            inputmode="text"
            maxlength="70"
            oninput={(event) => updateDraftField('employee_name', event.currentTarget.value)}
            type="text"
            value={draftEmployee.employee_name}
          />
        </div>

        <div class="space-y-1.5">
          <Label class="text-xs font-medium text-[#96a5bf]" for="new-employee-bic">{labels.employeeBic || 'Employee Bank Identification Code'}</Label>
          {#if loadingBanks || banksError || banks.length === 0}
            <Input
              id="new-employee-bic"
              class={inputClass}
              disabled
              type="text"
              value={loadingBanks ? 'Loading banks...' : banksError || 'No bank codes available'}
            />
          {:else}
            <Select.Root type="single" value={draftEmployee.employee_bic_code} onValueChange={(value) => updateDraftField('employee_bic_code', value || draftEmployee.employee_bic_code)}>
              <Select.Trigger class={selectTriggerClass} id="new-employee-bic">
                {#if selectedDraftBank}
                  {selectedDraftBank.bic} - {selectedDraftBank.bank_name}
                {:else}
                  {draftEmployee.employee_bic_code}
                {/if}
              </Select.Trigger>
              <Select.Content class={selectContentClass}>
                {#each banks as bank}
                  <Select.Item class={selectItemClass} label={`${bank.bic} - ${bank.bank_name}`} value={bank.bic}>
                    {bank.bic} - {bank.bank_name}
                  </Select.Item>
                {/each}
              </Select.Content>
            </Select.Root>
          {/if}
        </div>
      </div>

      <div class="space-y-3">
        <div class="space-y-1.5">
          <Label class="text-xs font-medium text-[#96a5bf]" for="new-employee-account">{labels.employeeAccount || 'Employee Account Number'}</Label>
          <Input
            id="new-employee-account"
            class={inputClass}
            inputmode="numeric"
            maxlength="30"
            oninput={(event) => updateDraftField('employee_account', event.currentTarget.value)}
            pattern="[0-9]*"
            type="text"
            value={draftEmployee.employee_account}
          />
        </div>

        <div class="space-y-1.5">
          <Label class="text-xs font-medium text-[#96a5bf]" for="new-salary-frequency">{labels.salaryFrequency || 'Salary Frequency'}</Label>
          <Select.Root type="single" value={draftEmployee.salary_frequency} onValueChange={(value) => updateDraftField('salary_frequency', value || 'M')}>
            <Select.Trigger class={selectTriggerClass} id="new-salary-frequency">
              {draftEmployee.salary_frequency === 'B' ? 'Bi-weekly (B)' : 'Monthly (M)'}
            </Select.Trigger>
            <Select.Content class={selectContentClass}>
              <Select.Item class={selectItemClass} label="Monthly (M)" value="M">Monthly (M)</Select.Item>
              <Select.Item class={selectItemClass} label="Bi-weekly (B)" value="B">Bi-weekly (B)</Select.Item>
            </Select.Content>
          </Select.Root>
        </div>

        <div class="space-y-1.5">
          <Label class="text-xs font-medium text-[#96a5bf]" for="new-working-days">{labels.workingDays || 'Number of Working Days'}</Label>
          <Input
            id="new-working-days"
            class={inputClass}
            inputmode="numeric"
            maxlength="3"
            oninput={(event) => updateDraftField('number_of_working_days', event.currentTarget.value)}
            placeholder="0-999"
            pattern="[0-9]*"
            type="text"
            value={draftEmployee.number_of_working_days}
          />
        </div>

        <div class="space-y-1.5">
          <Label class="text-xs font-medium text-[#96a5bf]" for="new-net-salary">{labels.netSalaryAuto || 'Net Salary (Auto-calculated)'}</Label>
          <div class="relative">
            <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <OmrSymbol />
            </span>
            <Input
              id="new-net-salary"
              class={currencyInputClass}
              disabled
              type="text"
              value={draftEmployee.net_salary}
            />
          </div>
        </div>

        <div class="space-y-1.5">
          <Label class="text-xs font-medium text-[#96a5bf]" for="new-basic-salary">{labels.basicSalary || 'Basic Salary'}</Label>
          <div class="relative">
            <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <OmrSymbol />
            </span>
            <Input
              id="new-basic-salary"
              class={currencyInputClass}
              inputmode="decimal"
              oninput={(event) => updateDraftField('basic_salary', event.currentTarget.value)}
              type="text"
              value={draftEmployee.basic_salary}
            />
          </div>
        </div>
      </div>

      <div class="space-y-3">
        <div class="space-y-1.5">
          <Label class="text-xs font-medium text-[#96a5bf]" for="new-extra-hours">{labels.extraHours || 'Extra Hours'}</Label>
          <Input
            id="new-extra-hours"
            class={inputClass}
            inputmode="decimal"
            oninput={(event) => updateDraftField('extra_hours', event.currentTarget.value)}
            type="text"
            value={draftEmployee.extra_hours}
          />
        </div>

        <div class="space-y-1.5">
          <Label class="text-xs font-medium text-[#96a5bf]" for="new-extra-income">{labels.extraIncome || 'Extra Income'}</Label>
          <div class="relative">
            <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <OmrSymbol />
            </span>
            <Input
              id="new-extra-income"
              class={currencyInputClass}
              inputmode="decimal"
              oninput={(event) => updateDraftField('extra_income', event.currentTarget.value)}
              type="text"
              value={draftEmployee.extra_income}
            />
          </div>
        </div>

        <div class="space-y-1.5">
          <Label class="text-xs font-medium text-[#96a5bf]" for="new-deductions">{labels.deductions || 'Deductions'}</Label>
          <div class="relative">
            <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <OmrSymbol />
            </span>
            <Input
              id="new-deductions"
              class={currencyInputClass}
              inputmode="decimal"
              oninput={(event) => updateDraftField('deductions', event.currentTarget.value)}
              type="text"
              value={draftEmployee.deductions}
            />
          </div>
        </div>

        <div class="space-y-1.5">
          <Label class="text-xs font-medium text-[#96a5bf]" for="new-social-security">{labels.socialSecurityDeductions || 'Social Security Deductions'}</Label>
          <div class="relative">
            <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <OmrSymbol />
            </span>
            <Input
              id="new-social-security"
              class={currencyInputClass}
              inputmode="decimal"
              oninput={(event) => updateDraftField('social_security_deductions', event.currentTarget.value)}
              type="text"
              value={draftEmployee.social_security_deductions}
            />
          </div>
        </div>

        <div class="space-y-1.5">
          <Label class="text-xs font-medium text-[#96a5bf]" for="new-notes">{labels.notesComments || 'Notes / Comments'}</Label>
          <textarea
            id="new-notes"
            class={`${inputClass} min-h-[76px] p-3 leading-5`}
            maxlength="300"
            oninput={(event) => updateDraftField('notes_comments', event.currentTarget.value)}
            value={draftEmployee.notes_comments}
          ></textarea>
        </div>
      </div>
    </div>

    {#if addFormError}
      <p class="text-xs text-[#ff9ba9]">{addFormError}</p>
    {/if}

    <div class="flex justify-end gap-2">
      <Button
        class="h-9 rounded-md border border-[#2d3b57] bg-[#172239] text-[#dbe5f6] hover:bg-[#1f2f4a]"
        onclick={cancelAddForm}
        type="button"
        variant="outline"
      >
        {buttonLabels.cancel || 'Cancel'}
      </Button>
      <Button
        class="h-9 rounded-md border border-[#2f5cab] bg-[linear-gradient(180deg,#2756a3,#1b3f7a)] px-4 font-semibold text-white hover:brightness-110"
        onclick={addDraftEmployee}
        type="button"
      >
        {buttonLabels.add || 'Add'}
      </Button>
    </div>
  </Card>
{/if}

<h3 class="mt-4 mb-2 text-sm font-semibold text-[#dbe5f6]">{sectionTitles.preview || 'Full SIF Preview (Worksheet Layout)'}</h3>
<Card class="wps-panel overflow-hidden rounded-[10px] border border-[#243247] p-0 shadow-none gap-0">
  <div class="overflow-x-auto stylish-scrollbar">
    <table class="min-w-[1550px] w-full border-collapse">
      <tbody>
        {#each previewRows as row, rowIndex}
          <tr>
            {#each row as cell, colIndex}
              <td
                class={`${previewCellClass} ${rowIndex === 0 || rowIndex === 2 ? 'bg-[#0f1727] text-[#aebcce] font-semibold' : 'text-[#dbe5f6]'}`}
              >
                {#if rowIndex >= 3 && employeeFieldKeys[colIndex]}
                  {#if isNetSalaryField(employeeFieldKeys[colIndex])}
                    {cell ?? ''}
                  {:else if isPreviewSelectField(employeeFieldKeys[colIndex])}
                    {#if employeeFieldKeys[colIndex] === 'employee_bic_code' && (loadingBanks || banksError || banks.length === 0)}
                      {cell ?? ''}
                    {:else}
                      <Select.Root
                        type="single"
                        value={getPreviewSelectValue(rowIndex - 3, employeeFieldKeys[colIndex])}
                        onValueChange={(value) =>
                          handlePreviewSelectChange(rowIndex - 3, employeeFieldKeys[colIndex], value)}
                      >
                        <Select.Trigger class={cellSelectTriggerClass}>
                          {cell ?? ''}
                        </Select.Trigger>
                        <Select.Content class={selectContentClass}>
                          {#if employeeFieldKeys[colIndex] === 'employee_id_type'}
                            <Select.Item class={selectItemClass} label="C" value="C">C</Select.Item>
                            <Select.Item class={selectItemClass} label="P" value="P">P</Select.Item>
                          {:else if employeeFieldKeys[colIndex] === 'salary_frequency'}
                            <Select.Item class={selectItemClass} label="M" value="M">M</Select.Item>
                            <Select.Item class={selectItemClass} label="B" value="B">B</Select.Item>
                          {:else if employeeFieldKeys[colIndex] === 'employee_bic_code'}
                            {#each banks as bank}
                              <Select.Item class={selectItemClass} label={bank.bic} value={bank.bic}>
                                {bank.bic}
                              </Select.Item>
                            {/each}
                          {/if}
                        </Select.Content>
                      </Select.Root>
                    {/if}
                  {:else}
                    <Input
                      class={cellInputClass}
                      inputmode={getCellInputMode(employeeFieldKeys[colIndex], rowIndex - 3)}
                      maxlength={getCellMaxLength(employeeFieldKeys[colIndex])}
                      oninput={(event) => handlePreviewCellInput(rowIndex - 3, employeeFieldKeys[colIndex], event)}
                      pattern={getCellPattern(employeeFieldKeys[colIndex], rowIndex - 3)}
                      value={employees[rowIndex - 3]?.[employeeFieldKeys[colIndex]] ?? ''}
                    />
                  {/if}
                {:else}
                  {cell ?? ''}
                {/if}
              </td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</Card>
