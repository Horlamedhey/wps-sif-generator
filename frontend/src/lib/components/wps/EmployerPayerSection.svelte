<script>
  import { Card } from '$lib/components/ui/card';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Checkbox } from '$lib/components/ui/checkbox';

  export let banks = [];
  export let loadingBanks = false;
  export let banksError = '';

  export let form = {
    employerCr: '',
    payerCr: '',
    sameAsEmployer: true,
    payerAccount: '',
    payerBankShort: 'BMCT',
    salaryYear: 2026,
    salaryMonth: 1,
    paymentType: 'Salary',
    processingDate: '',
    seq: 1
  };

  const labelClass = 'text-xs font-medium text-[#96a5bf]';
  const inputClass =
    'h-10 rounded-md border border-[#2a3853] bg-[#1b2436] text-[#dbe5f6] placeholder:text-[#7887a3] focus-visible:ring-2 focus-visible:ring-[#4a8cff]/50 focus-visible:border-[#4a8cff]';

  function updateField(field, value) {
    let next = { ...form, [field]: value };
    if (field === 'employerCr' && next.sameAsEmployer) {
      next = { ...next, payerCr: value };
    }
    if (field === 'sameAsEmployer' && value) {
      next = { ...next, payerCr: next.employerCr };
    }
    form = next;
  }
</script>

<Card class="rounded-[10px] border border-[#243247] bg-[linear-gradient(180deg,rgba(17,24,39,0.98),rgba(9,16,30,0.96))] p-3 shadow-none gap-3">
  <details open>
    <summary class="mb-3 cursor-pointer text-sm font-semibold text-[#dbe5f6]">Employer / Payer Details</summary>

    <div class="grid grid-cols-1 gap-3 xl:grid-cols-3">
      <div class="space-y-3">
        <div class="space-y-1.5">
          <Label class={labelClass} for="employer-cr">Employer CR-NO</Label>
          <Input
            id="employer-cr"
            class={inputClass}
            oninput={(event) => updateField('employerCr', event.currentTarget.value)}
            type="text"
            value={form.employerCr}
          />
        </div>

        <div class="space-y-2">
          <div class="flex items-center gap-2 rounded-md border border-[#2a3853] bg-[#151d2d] px-3 py-2">
            <Checkbox
              id="same-employer"
              class="border-[#2a3853] bg-[#101828] data-[state=checked]:border-[#4a8cff] data-[state=checked]:bg-[#2f5cab]"
              checked={form.sameAsEmployer}
              onCheckedChange={(checked) => updateField('sameAsEmployer', checked)}
            />
            <Label class="text-xs font-medium text-[#96a5bf]" for="same-employer">Same as Employer CR-NO</Label>
          </div>

          <div class="space-y-1.5">
            <Label class={labelClass} for="payer-cr">Payer CR-NO</Label>
            <Input
              id="payer-cr"
              class={inputClass}
              disabled={form.sameAsEmployer}
              oninput={(event) => updateField('payerCr', event.currentTarget.value)}
              type="text"
              value={form.payerCr}
            />
          </div>
        </div>

        <div class="space-y-1.5">
          <Label class={labelClass} for="payer-account">Payer Account Number</Label>
          <Input
            id="payer-account"
            class={inputClass}
            oninput={(event) => updateField('payerAccount', event.currentTarget.value)}
            type="text"
            value={form.payerAccount}
          />
        </div>
      </div>

      <div class="space-y-3">
        <div class="space-y-1.5">
          <Label class={labelClass} for="employer-bank">Employer Bank</Label>
          <select
            id="employer-bank"
            class={`${inputClass} w-full px-3 text-sm`}
            onchange={(event) => updateField('payerBankShort', event.currentTarget.value)}
            value={form.payerBankShort}
          >
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
        </div>

        <div class="space-y-1.5">
          <Label class={labelClass} for="salary-year">Salary Year (YYYY)</Label>
          <Input
            id="salary-year"
            class={inputClass}
            min="2000"
            max="2100"
            oninput={(event) => updateField('salaryYear', Number(event.currentTarget.value))}
            step="1"
            type="number"
            value={form.salaryYear}
          />
        </div>

        <div class="space-y-1.5">
          <Label class={labelClass} for="salary-month">Salary Month (MM)</Label>
          <Input
            id="salary-month"
            class={inputClass}
            min="1"
            max="12"
            oninput={(event) => updateField('salaryMonth', Number(event.currentTarget.value))}
            step="1"
            type="number"
            value={form.salaryMonth}
          />
        </div>
      </div>

      <div class="space-y-3">
        <div class="space-y-1.5">
          <Label class={labelClass} for="payment-type">Payment Type</Label>
          <Input
            id="payment-type"
            class={inputClass}
            oninput={(event) => updateField('paymentType', event.currentTarget.value)}
            type="text"
            value={form.paymentType}
          />
        </div>

        <div class="space-y-1.5">
          <Label class={labelClass} for="processing-date">Processing date (used for file name)</Label>
          <Input
            id="processing-date"
            class={inputClass}
            onchange={(event) => updateField('processingDate', event.currentTarget.value)}
            type="date"
            value={form.processingDate}
          />
        </div>

        <div class="space-y-1.5">
          <Label class={labelClass} for="sequence">File sequence number</Label>
          <Input
            id="sequence"
            class={inputClass}
            min="1"
            max="999"
            oninput={(event) => updateField('seq', Number(event.currentTarget.value))}
            step="1"
            type="number"
            value={form.seq}
          />
        </div>
      </div>
    </div>
  </details>
</Card>
