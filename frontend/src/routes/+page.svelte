<script>
  import '../app.css';
  import { onMount } from 'svelte';

  import EmployerPayerSection from '$lib/components/wps/EmployerPayerSection.svelte';
  import EmployeesTable from '$lib/components/wps/EmployeesTable.svelte';
  import GeneratePanel from '$lib/components/wps/GeneratePanel.svelte';
  import { createEmployee } from '$lib/wps/employee';

  const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

  let banks = [];
  let loadingBanks = true;
  let banksError = '';

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
    processingDate: now.toISOString().slice(0, 10),
    seq: 1,
    sheetName: 'Sheet1'
  };

  let employees = [createEmployee()];

  let status = '';
  let error = '';
  let previewInfo = null;
  let generating = false;

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

  function addRow() {
    employees = [...employees, createEmployee()];
  }

  function removeRow(index) {
    if (employees.length === 1) {
      employees = [createEmployee()];
      return;
    }
    employees = employees.filter((_, idx) => idx !== index);
  }

  function buildPayload() {
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
      employees
    };
  }

  async function generateFile() {
    generating = true;
    status = '';
    error = '';
    previewInfo = null;

    try {
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

  onMount(loadBanks);
</script>

<svelte:head>
  <title>Oman WPS (SIF) Excel Generator</title>
</svelte:head>

<main class="mx-auto max-w-[1600px] px-4 pb-10 pt-6 md:px-6">
  <h1 class="mb-3 text-4xl font-extrabold tracking-tight text-[#dbe5f6] md:text-5xl">Oman WPS (SIF) Excel Generator</h1>

  <EmployerPayerSection
    {banks}
    {loadingBanks}
    {banksError}
    bind:form
  />

  <EmployeesTable bind:employees {addRow} {removeRow} />

  <GeneratePanel
    {generating}
    {generateFile}
    bind:sheetName={form.sheetName}
    {status}
    {error}
    {previewInfo}
  />
</main>
