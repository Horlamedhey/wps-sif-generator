<script>
  import '../app.css';
  import { onMount } from 'svelte';

  const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

  function createEmployee() {
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

  let banks = [];
  let loadingBanks = true;
  let banksError = '';

  let employerCr = '';
  let payerCr = '';
  let sameAsEmployer = true;
  let payerAccount = '';
  let payerBankShort = 'BMCT';

  const now = new Date();
  let salaryYear = now.getFullYear();
  let salaryMonth = now.getMonth() + 1;
  let paymentType = 'Salary';
  let processingDate = now.toISOString().slice(0, 10);
  let seq = 1;
  let sheetName = 'Sheet1';

  let employees = [createEmployee()];

  let status = '';
  let error = '';
  let previewInfo = null;
  let generating = false;

  $: if (sameAsEmployer) {
    payerCr = employerCr;
  }

  $: if (banks.length > 0 && !banks.some((bank) => bank.short_name === payerBankShort)) {
    const bmct = banks.find((bank) => bank.short_name === 'BMCT');
    payerBankShort = bmct ? bmct.short_name : banks[0].short_name;
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
      employer_cr: employerCr,
      payer_cr: payerCr,
      payer_bank_short: payerBankShort,
      payer_account: payerAccount,
      salary_year: Number(salaryYear),
      salary_month: Number(salaryMonth),
      payment_type: paymentType,
      processing_date: processingDate,
      seq: Number(seq),
      sheet_name: sheetName,
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

<main class="page">
  <h1>Oman WPS (SIF) Excel Generator</h1>

  <section class="panel">
    <details open>
      <summary>Employer / Payer Details</summary>
      <div class="grid3">
        <div class="col">
          <label>
            Employer CR-NO
            <input bind:value={employerCr} type="text" />
          </label>

          <div class="payer-row">
            <label class="checkline">
              <input bind:checked={sameAsEmployer} type="checkbox" />
              Same as Employer CR-NO
            </label>

            <label>
              Payer CR-NO
              <input bind:value={payerCr} disabled={sameAsEmployer} type="text" />
            </label>
          </div>

          <label>
            Payer Account Number
            <input bind:value={payerAccount} type="text" />
          </label>
        </div>

        <div class="col">
          <label>
            Employer Bank
            <select bind:value={payerBankShort}>
              {#if loadingBanks}
                <option>Loading banks...</option>
              {:else if banksError}
                <option>Failed to load banks</option>
              {:else}
                {#each banks as bank}
                  <option value={bank.short_name}>{bank.bank_name}</option>
                {/each}
              {/if}
            </select>
          </label>

          <label>
            Salary Year (YYYY)
            <input bind:value={salaryYear} min="2000" max="2100" step="1" type="number" />
          </label>

          <label>
            Salary Month (MM)
            <input bind:value={salaryMonth} min="1" max="12" step="1" type="number" />
          </label>
        </div>

        <div class="col">
          <label>
            Payment Type
            <input bind:value={paymentType} type="text" />
          </label>

          <label>
            Processing date (used for file name)
            <input bind:value={processingDate} type="date" />
          </label>

          <label>
            File sequence number
            <input bind:value={seq} min="1" max="999" step="1" type="number" />
          </label>
        </div>
      </div>
    </details>
  </section>

  <h2>Employees</h2>
  <p class="tip">Tip: Paste rows from Excel. Amounts are normalized to 3 decimals. Extra Hours to 2 decimals.</p>

  <section class="panel table-wrap">
    <table>
      <thead>
        <tr>
          <th>Employee ID Type</th>
          <th>Employee ID</th>
          <th>Reference Number</th>
          <th>Employee Name</th>
          <th>Employee BIC Code</th>
          <th>Employee Account</th>
          <th>Salary Frequency</th>
          <th>Number Of Working days</th>
          <th>Net Salary</th>
          <th>Basic Salary</th>
          <th>Extra Hours</th>
          <th>Extra Income</th>
          <th>Deductions</th>
          <th>Social Security Deductions</th>
          <th>Notes / Comments</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {#each employees as employee, idx (idx)}
          <tr>
            <td><input bind:value={employee.employee_id_type} /></td>
            <td><input bind:value={employee.employee_id} /></td>
            <td><input bind:value={employee.reference_number} /></td>
            <td><input bind:value={employee.employee_name} /></td>
            <td><input bind:value={employee.employee_bic_code} /></td>
            <td><input bind:value={employee.employee_account} /></td>
            <td><input bind:value={employee.salary_frequency} /></td>
            <td><input bind:value={employee.number_of_working_days} /></td>
            <td><input bind:value={employee.net_salary} /></td>
            <td><input bind:value={employee.basic_salary} /></td>
            <td><input bind:value={employee.extra_hours} /></td>
            <td><input bind:value={employee.extra_income} /></td>
            <td><input bind:value={employee.deductions} /></td>
            <td><input bind:value={employee.social_security_deductions} /></td>
            <td><input bind:value={employee.notes_comments} /></td>
            <td>
              <button class="danger" on:click={() => removeRow(idx)} type="button">-</button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
    <div class="table-actions">
      <button on:click={addRow} type="button">Add Row</button>
    </div>
  </section>

  <section class="footer-row">
    <button class="primary" disabled={generating} on:click={generateFile} type="button">
      {generating ? 'Generating...' : 'Generate .xlsx'}
    </button>

    <label class="sheet-input">
      Sheet name
      <input bind:value={sheetName} type="text" />
    </label>
  </section>

  {#if status}
    <p class="status ok">{status}</p>
  {/if}

  {#if error}
    <p class="status err">{error}</p>
  {/if}

  {#if previewInfo}
    <p class="status muted">
      Preview: {previewInfo.number_of_records} records, total {previewInfo.total_salaries}, file {previewInfo.filename}
    </p>
  {/if}
</main>

<style>
  .page {
    max-width: 1600px;
    margin: 24px auto;
    padding: 0 24px 40px;
  }

  h1 {
    font-size: 44px;
    margin: 0 0 14px;
    font-weight: 800;
    letter-spacing: 0.2px;
  }

  h2 {
    margin: 16px 0 8px;
    font-size: 34px;
  }

  .tip {
    color: var(--text-muted);
    margin: 0 0 10px;
    font-size: 13px;
  }

  .panel {
    background: linear-gradient(180deg, rgba(17, 24, 39, 0.98), rgba(9, 16, 30, 0.96));
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 10px;
  }

  details summary {
    cursor: pointer;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 12px;
  }

  .grid3 {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
  }

  .col {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  label {
    font-size: 12px;
    color: var(--text-muted);
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  input,
  select {
    background: #1b2436;
    border: 1px solid #2a3853;
    color: var(--text);
    border-radius: 8px;
    height: 38px;
    padding: 8px 10px;
  }

  .checkline {
    flex-direction: row;
    align-items: center;
    gap: 8px;
  }

  .checkline input {
    height: 15px;
    width: 15px;
  }

  .table-wrap {
    overflow-x: auto;
    padding: 0;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    min-width: 1500px;
  }

  th,
  td {
    border: 1px solid #1f2b40;
    padding: 0;
  }

  th {
    background: #0f1727;
    color: #aebcce;
    font-size: 12px;
    font-weight: 600;
    text-align: left;
    padding: 9px 8px;
    white-space: nowrap;
  }

  td input {
    border: 0;
    border-radius: 0;
    width: 100%;
    height: 36px;
    background: transparent;
  }

  td input:focus {
    outline: 1px solid var(--accent);
    outline-offset: -1px;
  }

  .table-actions {
    padding: 10px;
    border-top: 1px solid #1f2b40;
  }

  .footer-row {
    margin-top: 16px;
    display: grid;
    grid-template-columns: auto minmax(240px, 420px);
    gap: 16px;
    align-items: end;
  }

  .primary,
  .danger,
  .table-actions button {
    border: 1px solid #2d3b57;
    border-radius: 8px;
    background: #172239;
    color: var(--text);
    height: 40px;
    padding: 0 14px;
    cursor: pointer;
  }

  .primary {
    min-width: 170px;
    font-weight: 700;
    background: linear-gradient(180deg, #2756a3, #1b3f7a);
    border-color: #2f5cab;
  }

  .primary:disabled {
    opacity: 0.6;
    cursor: wait;
  }

  .danger {
    height: 32px;
    width: 32px;
    background: #2b1822;
    border-color: #5a2a3a;
    color: #f4a9bd;
  }

  .sheet-input {
    align-self: stretch;
  }

  .status {
    margin: 10px 0 0;
    font-size: 14px;
  }

  .status.ok {
    color: #7fd9a7;
  }

  .status.err {
    color: #ff9ba9;
    white-space: pre-wrap;
  }

  .status.muted {
    color: var(--text-muted);
  }

  @media (max-width: 1100px) {
    .grid3 {
      grid-template-columns: 1fr;
    }

    .footer-row {
      grid-template-columns: 1fr;
    }

    h1 {
      font-size: 32px;
    }

    h2 {
      font-size: 26px;
    }
  }
</style>
