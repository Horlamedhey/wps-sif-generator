<script>
  import '../app.css';
  import { onMount } from 'svelte';

  import EmployerPayerSection from '$lib/components/wps/EmployerPayerSection.svelte';
  import EmployeesTable from '$lib/components/wps/EmployeesTable.svelte';
  import GeneratePanel from '$lib/components/wps/GeneratePanel.svelte';
  import { translations } from '$lib/i18n/translations';
  import { withCalculatedNetSalary } from '$lib/wps/employee';

  const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
  const showSeedButton = import.meta.env.DEV && !import.meta.env.PROD;

  let banks = [];
  let loadingBanks = true;
  let banksError = '';

  function toLocalIsoDate(value = new Date()) {
    const year = value.getFullYear();
    const month = String(value.getMonth() + 1).padStart(2, '0');
    const day = String(value.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  const now = new Date();
  let form = {
    employerCr: '',
    payerCr: '',
    sameAsEmployer: true,
    payerAccount: '',
    payerBankShort: 'BMCT',
    salaryYear: now.getFullYear(),
    salaryMonth: now.getMonth() + 1,
    paymentType: 'Salary',
    processingDate: toLocalIsoDate(now),
    seq: 1,
    sheetName: 'Sheet1'
  };

  let employees = [];

  let status = '';
  let error = '';
  let previewInfo = null;
  let generating = false;
  let seededEmployeeDraft = null;
  let seedEmployeeRequestId = 0;
  let seedEmployeeSerial = 0;
  let theme = 'light';
  let language = 'en';
  let systemThemeMedia = null;
  let removeThemeListener = () => {};

  $: t = translations[language] || translations.en;

  $: if (form.sameAsEmployer && form.payerCr !== form.employerCr) {
    form = { ...form, payerCr: form.employerCr };
  }

  $: if (banks.length > 0 && !banks.some((bank) => bank.short_name === form.payerBankShort)) {
    const bmct = banks.find((bank) => bank.short_name === 'BMCT');
    form = { ...form, payerBankShort: bmct ? bmct.short_name : banks[0].short_name };
  }

  function apiUrl(path) {
    return `${API_BASE}${path}`;
  }

  async function loadBanks() {
    loadingBanks = true;
    banksError = '';
    try {
      const response = await fetch(apiUrl('/api/banks'));
      if (!response.ok) {
        throw new Error(`Banks API failed (${response.status})`);
      }
      const data = await response.json();
      banks = data.banks ?? [];
    } catch (e) {
      banksError = e instanceof Error ? e.message : 'Failed to load banks.';
    } finally {
      loadingBanks = false;
    }
  }

  function detectSystemTheme() {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
      return 'light';
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(nextTheme) {
    if (typeof document === 'undefined') {
      return;
    }
    const root = document.documentElement;
    root.classList.remove('theme-light', 'theme-dark');
    root.classList.add(nextTheme === 'dark' ? 'theme-dark' : 'theme-light');
    root.dataset.theme = nextTheme;
  }

  function applyLanguage(nextLanguage) {
    if (typeof document === 'undefined') {
      return;
    }
    const root = document.documentElement;
    root.lang = nextLanguage;
    root.dir = nextLanguage === 'ar' ? 'rtl' : 'ltr';
  }

  function toggleTheme() {
    theme = theme === 'dark' ? 'light' : 'dark';
    safeStorageSet('wps-theme', theme);
    applyTheme(theme);
  }

  function toggleLanguage() {
    language = language === 'ar' ? 'en' : 'ar';
    safeStorageSet('wps-language', language);
    applyLanguage(language);
  }

  function safeStorageGet(key) {
    if (typeof window === 'undefined') {
      return null;
    }
    try {
      return window.localStorage.getItem(key);
    } catch {
      return null;
    }
  }

  function safeStorageSet(key, value) {
    if (typeof window === 'undefined') {
      return;
    }
    try {
      window.localStorage.setItem(key, value);
    } catch {
      // localStorage can be unavailable in some privacy modes
    }
  }

  function seedDevData() {
    const todayIso = toLocalIsoDate(new Date());
    const targetBank = banks.find((bank) => bank.short_name === 'BMCT') || banks[0];
    const serial = ++seedEmployeeSerial;
    const serial4 = String(serial).padStart(4, '0');
    const serial3 = String(serial).padStart(3, '0');

    form = {
      employerCr: '11111111',
      payerCr: '1111111',
      sameAsEmployer: false,
      payerAccount: '0432111111110009',
      payerBankShort: 'BMCT',
      salaryYear: 2026,
      salaryMonth: 2,
      paymentType: 'Salary',
      processingDate: todayIso,
      seq: 1,
      sheetName: 'Sheet1'
    };

    seededEmployeeDraft = {
      employee_id_type: 'C',
      employee_id: `9999888877776${serial4}`,
      reference_number: `REF-${serial3}`,
      employee_name: `TEST EMPLOYEE ${serial}`,
      employee_bic_code: targetBank?.bic || 'BMUSOMRX',
      employee_account: `032111111111${serial4}`,
      salary_frequency: 'M',
      number_of_working_days: '30',
      net_salary: '19.5',
      basic_salary: '20',
      extra_hours: '0',
      extra_income: '2',
      deductions: '1',
      social_security_deductions: '1.5',
      notes_comments: ''
    };
    seedEmployeeRequestId += 1;
  }

  function buildPayload() {
    const normalizedEmployees = employees.map((employee) => withCalculatedNetSalary(employee));
    return {
      employer_cr: form.employerCr,
      payer_cr: form.payerCr,
      payer_bank_short: form.payerBankShort,
      payer_account: form.payerAccount,
      salary_year: Number(form.salaryYear),
      salary_month: Number(form.salaryMonth),
      payment_type: form.paymentType,
      processing_date: form.processingDate,
      seq: Number(form.seq),
      sheet_name: form.sheetName,
      employees: normalizedEmployees
    };
  }

  function isBlank(value) {
    return value === null || value === undefined || String(value).trim() === '';
  }

  function isValidNumber(value) {
    if (isBlank(value)) return false;
    return !Number.isNaN(Number(value));
  }

  function validateEmployeeRowsBeforeGenerate() {
    const rowIssues = [];
    const normalizedEmployees = employees.map((employee) => withCalculatedNetSalary(employee));

    if (normalizedEmployees.length === 0) {
      rowIssues.push('Add at least one employee row.');
      return rowIssues;
    }

    normalizedEmployees.forEach((employee, index) => {
      const missing = [];
      if (!['C', 'P'].includes((employee.employee_id_type || '').toUpperCase())) missing.push('Employee ID Type (C/P)');
      if (isBlank(employee.employee_id)) missing.push('Employee ID');
      if (isBlank(employee.employee_name)) missing.push('Employee Name');
      if (isBlank(employee.employee_bic_code)) missing.push('Employee Bank Identification Code');
      if (isBlank(employee.employee_account)) missing.push('Employee Account Number');
      if (!['M', 'B'].includes((employee.salary_frequency || '').toUpperCase())) missing.push('Salary Frequency (M/B)');
      if (!isValidNumber(employee.number_of_working_days)) missing.push('Number of Working Days');
      if (!isValidNumber(employee.basic_salary)) missing.push('Basic Salary');

      const netSalary = isValidNumber(employee.net_salary) ? Number(employee.net_salary) : null;
      if (netSalary === 0 && isBlank(employee.notes_comments)) {
        missing.push('Notes / Comments required when Net Salary is 0');
      }

      if (missing.length > 0) {
        rowIssues.push(`Row ${index + 1}: ${missing.join(', ')}`);
      }
    });

    return rowIssues;
  }

  function validateBeforeGenerate() {
    const topMissing = [];
    if (isBlank(form.employerCr)) topMissing.push('Employer CR-NO');
    if (isBlank(form.payerCr)) topMissing.push('Payer CR-NO');
    if (isBlank(form.payerAccount)) topMissing.push('Payer Account Number');
    if (isBlank(form.payerBankShort)) topMissing.push('Employer Bank');
    if (!isValidNumber(form.salaryYear) || Number(form.salaryYear) < 2000 || Number(form.salaryYear) > 2100) {
      topMissing.push('Salary Year (valid 2000-2100)');
    }
    if (!isValidNumber(form.salaryMonth) || Number(form.salaryMonth) < 1 || Number(form.salaryMonth) > 12) {
      topMissing.push('Salary Month (1-12)');
    }
    if (isBlank(form.paymentType)) topMissing.push('Payment Type');
    if (isBlank(form.processingDate)) topMissing.push('Processing Date');
    if (!isValidNumber(form.seq) || Number(form.seq) < 1) topMissing.push('File sequence number');

    const messageParts = [];
    if (topMissing.length > 0) {
      messageParts.push(`Please complete required Employer/Payer fields:\n- ${topMissing.join('\n- ')}`);
    }

    const employeeRowIssues = validateEmployeeRowsBeforeGenerate();
    if (employeeRowIssues.length > 0) {
      const preview = employeeRowIssues.slice(0, 6);
      const more = employeeRowIssues.length - preview.length;
      const suffix = more > 0 ? `\n- ...and ${more} more row(s)` : '';
      messageParts.push(`Please complete required Employee fields:\n- ${preview.join('\n- ')}${suffix}`);
    }

    if (messageParts.length > 0) {
      const message = messageParts.join('\n\n');
      error = message;
      if (typeof window !== 'undefined') {
        window.alert(message);
      }
      return false;
    }

    return true;
  }

  async function generateFile() {
    generating = true;
    status = '';
    error = '';
    previewInfo = null;

    try {
      if (!validateBeforeGenerate()) {
        return;
      }

      const payload = buildPayload();

      const previewRes = await fetch(apiUrl('/api/sif/preview'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!previewRes.ok) {
        const body = await previewRes.text();
        throw new Error(body || `Preview failed (${previewRes.status})`);
      }

      previewInfo = await previewRes.json();

      const generateRes = await fetch(apiUrl('/api/sif/generate'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!generateRes.ok) {
        const body = await generateRes.text();
        throw new Error(body || `Generation failed (${generateRes.status})`);
      }

      const blob = await generateRes.blob();
      const headerName = generateRes.headers.get('x-generated-filename') || previewInfo.filename;
      const objectUrl = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = objectUrl;
      anchor.download = headerName || 'SIF.xlsx';
      anchor.click();
      URL.revokeObjectURL(objectUrl);

      status = `Generated ${headerName}`;
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to generate file.';
    } finally {
      generating = false;
    }
  }

  onMount(() => {
    const localNow = new Date();
    form = {
      ...form,
      salaryYear: localNow.getFullYear(),
      salaryMonth: localNow.getMonth() + 1,
      processingDate: toLocalIsoDate(localNow)
    };

    loadBanks();

    if (typeof window !== 'undefined') {
      try {
        const savedTheme = safeStorageGet('wps-theme');
        theme = savedTheme === 'dark' || savedTheme === 'light' ? savedTheme : detectSystemTheme();
        applyTheme(theme);

        if (!savedTheme && typeof window.matchMedia === 'function') {
          systemThemeMedia = window.matchMedia('(prefers-color-scheme: dark)');
          const listener = (event) => {
            if (!safeStorageGet('wps-theme')) {
              theme = event.matches ? 'dark' : 'light';
              applyTheme(theme);
            }
          };
          if (typeof systemThemeMedia.addEventListener === 'function') {
            systemThemeMedia.addEventListener('change', listener);
            removeThemeListener = () => systemThemeMedia.removeEventListener('change', listener);
          } else {
            systemThemeMedia.addListener(listener);
            removeThemeListener = () => systemThemeMedia.removeListener(listener);
          }
        }

        const savedLanguage = safeStorageGet('wps-language');
        const detectedLanguage = window.navigator.language?.toLowerCase().startsWith('ar') ? 'ar' : 'en';
        language = savedLanguage === 'ar' || savedLanguage === 'en' ? savedLanguage : detectedLanguage;
        applyLanguage(language);
      } catch {
        theme = detectSystemTheme();
        language = 'en';
        applyTheme(theme);
        applyLanguage(language);
      }
    } else {
      applyTheme('light');
      applyLanguage('en');
    }

    return () => {
      removeThemeListener();
    };
  });
</script>

<svelte:head>
  <title>{t.appTitle}</title>
</svelte:head>

<main class="mx-auto max-w-[1920px] px-4 pb-10 pt-6 md:px-6">
  <div class="mb-3 flex items-center justify-between gap-3 flex-wrap">
    <h1 class="text-4xl font-extrabold tracking-tight text-[#dbe5f6] md:text-5xl">{t.appTitle}</h1>
    <div class="flex items-center gap-2">
      <button
        class="h-9 rounded-md border border-[#2d3b57] bg-[#172239] px-3 text-sm font-medium text-[#dbe5f6] hover:bg-[#1f2f4a]"
        onclick={toggleTheme}
        type="button"
      >
        {t.themeToggle}
      </button>
      <button
        class="h-9 rounded-md border border-[#2d3b57] bg-[#172239] px-3 text-sm font-medium text-[#dbe5f6] hover:bg-[#1f2f4a]"
        onclick={toggleLanguage}
        type="button"
      >
        {t.languageToggle}
      </button>
    </div>
    {#if showSeedButton}
      <button
        class="h-9 rounded-md border border-[#2d3b57] bg-[#172239] px-3 text-sm font-medium text-[#dbe5f6] hover:bg-[#1f2f4a]"
        onclick={seedDevData}
        type="button"
      >
        Seed Demo Data
      </button>
    {/if}
  </div>

  <EmployerPayerSection
    {banks}
    {loadingBanks}
    {banksError}
    bind:form
    labels={t.labels}
    sectionTitle={t.sections.employerPayer}
  />

  <EmployeesTable
    bind:employees
    {form}
    {banks}
    {loadingBanks}
    {banksError}
    {seededEmployeeDraft}
    {seedEmployeeRequestId}
    labels={t.labels}
    sectionTitles={t.sections}
    tipText={t.tip}
    buttonLabels={t.buttons}
  />

  <GeneratePanel
    {generating}
    {generateFile}
    bind:sheetName={form.sheetName}
    {status}
    {error}
    {previewInfo}
    labels={t.labels}
    buttonLabels={t.buttons}
  />
</main>
