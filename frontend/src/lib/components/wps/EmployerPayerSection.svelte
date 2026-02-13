<script>
  import { Calendar } from '$lib/components/ui/calendar';
  import { Card } from '$lib/components/ui/card';
  import { Checkbox } from '$lib/components/ui/checkbox';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import * as Popover from '$lib/components/ui/popover';
  import * as Select from '$lib/components/ui/select';
  import { getLocalTimeZone, parseDate, today } from '@internationalized/date';
  import { CalendarDays } from '@lucide/svelte';

  export let banks = [];
  export let loadingBanks = false;
  export let banksError = '';
  const currentYear = new Date().getFullYear();

  export let form = {
    employerCr: '',
    payerCr: '',
    sameAsEmployer: true,
    payerAccount: '',
    payerBankShort: 'BMCT',
    salaryYear: currentYear,
    salaryMonth: 1,
    paymentType: 'Salary',
    processingDate: '',
    seq: 1
  };

  const labelClass = 'text-xs font-medium text-[#96a5bf]';
  const inputClass =
    'h-10 rounded-md border border-[#2a3853] bg-[#1b2436] text-[#dbe5f6] placeholder:text-[#7887a3] focus-visible:ring-2 focus-visible:ring-[#4a8cff]/50 focus-visible:border-[#4a8cff]';
  const selectTriggerClass = `${inputClass} w-full justify-between px-3 text-sm font-normal`;
  const selectContentClass = 'border border-[#2a3853] bg-[#0f1727] text-[#dbe5f6]';
  const selectItemClass = 'text-[#dbe5f6]';
  const dateTriggerClass = `${inputClass} flex w-full items-center justify-between px-3 text-left text-sm font-normal`;

  const monthOptions = [
    { value: '1', label: '01 - January' },
    { value: '2', label: '02 - February' },
    { value: '3', label: '03 - March' },
    { value: '4', label: '04 - April' },
    { value: '5', label: '05 - May' },
    { value: '6', label: '06 - June' },
    { value: '7', label: '07 - July' },
    { value: '8', label: '08 - August' },
    { value: '9', label: '09 - September' },
    { value: '10', label: '10 - October' },
    { value: '11', label: '11 - November' },
    { value: '12', label: '12 - December' }
  ];

  let processingDateOpen = false;
  let processingDateValue;
  const minSelectableDate = today(getLocalTimeZone());
  const maxSelectableDate = minSelectableDate.add({ days: 7 });
  let selectedBankLabel = 'Select employer bank';
  let selectedMonthLabel = 'Select month';
  let selectedEmployerBank = null;

  $: processingDateValue = parseDateSafe(form.processingDate);
  $: selectedEmployerBank = banks.find((bank) => bank.short_name === form.payerBankShort) || null;
  $: selectedBankLabel = selectedEmployerBank
    ? `${selectedEmployerBank.short_name} - ${selectedEmployerBank.bank_name}`
    : 'Select employer bank';
  $: selectedMonthLabel =
    monthOptions.find((month) => month.value === String(form.salaryMonth))?.label || 'Select month';

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

  function digitsOnly(value) {
    return value.replace(/\D/g, '');
  }

  function lettersNoDigits(value) {
    return value.replace(/\d/g, '');
  }

  function limitedDigits(value, maxLen) {
    const digits = digitsOnly(value);
    return typeof maxLen === 'number' ? digits.slice(0, maxLen) : digits;
  }

  function parseDateSafe(value) {
    if (!value) {
      return undefined;
    }

    try {
      return parseDate(value);
    } catch {
      return undefined;
    }
  }

  function handleDigitInput(field, event, maxLen) {
    updateField(field, limitedDigits(event.currentTarget.value, maxLen));
  }

  function handlePaymentTypeInput(event) {
    updateField('paymentType', lettersNoDigits(event.currentTarget.value).slice(0, 32));
  }

  function handleSalaryYearInput(event) {
    const digits = limitedDigits(event.currentTarget.value, 4);
    updateField('salaryYear', digits === '' ? '' : Number(digits));
  }

  function handleSequenceInput(event) {
    const digits = limitedDigits(event.currentTarget.value, 3);
    updateField('seq', digits === '' ? '' : Number(digits));
  }

  function handleMonthChange(value) {
    if (value) {
      updateField('salaryMonth', Number(value));
    }
  }

  function handleBankChange(value) {
    if (value) {
      updateField('payerBankShort', value);
    }
  }

  function handleDateChange(value) {
    if (value) {
      updateField('processingDate', value.toString());
      processingDateOpen = false;
    }
  }

  function formatDateForDisplay(value) {
    if (!value) {
      return 'Select date';
    }
    const [year, month, day] = value.split('-');
    if (!year || !month || !day) {
      return value;
    }
    return `${day}/${month}/${year}`;
  }
</script>

<Card class="rounded-[10px] border border-[#243247] bg-[linear-gradient(180deg,rgba(17,24,39,0.98),rgba(9,16,30,0.96))] p-3 shadow-none gap-3">
  <h3 class="mb-3 text-sm font-semibold text-[#dbe5f6]">Employer / Payer Details</h3>

  <div class="grid grid-cols-1 gap-3 xl:grid-cols-3">
    <div class="space-y-3">
      <div class="space-y-1.5">
        <Label class={labelClass} for="employer-cr">Employer CR-NO</Label>
        <Input
          id="employer-cr"
          class={inputClass}
          inputmode="numeric"
          oninput={(event) => handleDigitInput('employerCr', event, 32)}
          pattern="[0-9]*"
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
            onCheckedChange={(checked) => updateField('sameAsEmployer', checked === true)}
          />
          <Label class="text-xs font-medium text-[#96a5bf]" for="same-employer">Same as Employer CR-NO</Label>
        </div>

        <div class="space-y-1.5">
          <Label class={labelClass} for="payer-cr">Payer CR-NO</Label>
          <Input
            id="payer-cr"
            class={inputClass}
            inputmode="numeric"
            oninput={(event) => handleDigitInput('payerCr', event, 32)}
            pattern="[0-9]*"
            readonly={form.sameAsEmployer}
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
          inputmode="numeric"
          maxlength="64"
          oninput={(event) => handleDigitInput('payerAccount', event, 64)}
          pattern="[0-9]*"
          type="text"
          value={form.payerAccount}
        />
      </div>
    </div>

    <div class="space-y-3">
      <div class="space-y-1.5">
        <Label class={labelClass} for="employer-bank">Employer Bank</Label>

        {#if loadingBanks || banksError || banks.length === 0}
          <Input
            id="employer-bank"
            class={inputClass}
            disabled
            type="text"
            value={loadingBanks ? 'Loading banks...' : banksError || 'No banks available'}
          />
        {:else}
          <Select.Root type="single" value={form.payerBankShort} onValueChange={handleBankChange}>
            <Select.Trigger class={selectTriggerClass} id="employer-bank">
              {selectedBankLabel}
            </Select.Trigger>
            <Select.Content class={selectContentClass}>
              {#each banks as bank}
                <Select.Item class={selectItemClass} label={`${bank.short_name} - ${bank.bank_name}`} value={bank.short_name}>
                  {bank.short_name} - {bank.bank_name}
                </Select.Item>
              {/each}
            </Select.Content>
          </Select.Root>
        {/if}
      </div>

      <div class="space-y-1.5">
        <Label class={labelClass} for="salary-year">Salary Year (YYYY)</Label>
        <Input
          id="salary-year"
          class={inputClass}
          inputmode="numeric"
          maxlength="4"
          oninput={handleSalaryYearInput}
          pattern="[0-9]*"
          type="text"
          value={form.salaryYear}
        />
      </div>

      <div class="space-y-1.5">
        <Label class={labelClass} for="salary-month">Salary Month (MM)</Label>
        <Select.Root type="single" value={String(form.salaryMonth)} onValueChange={handleMonthChange}>
          <Select.Trigger class={selectTriggerClass} id="salary-month">
            {selectedMonthLabel}
          </Select.Trigger>
          <Select.Content class={selectContentClass}>
            {#each monthOptions as month}
              <Select.Item class={selectItemClass} label={month.label} value={month.value}>
                {month.label}
              </Select.Item>
            {/each}
          </Select.Content>
        </Select.Root>
      </div>
    </div>

    <div class="space-y-3">
      <div class="space-y-1.5">
        <Label class={labelClass} for="payment-type">Payment Type</Label>
        <Input
          id="payment-type"
          class={inputClass}
          oninput={handlePaymentTypeInput}
          type="text"
          value={form.paymentType}
        />
      </div>

      <div class="space-y-1.5">
        <Label class={labelClass} for="processing-date">Processing date (used for file name)</Label>

        <Popover.Root bind:open={processingDateOpen}>
          <Popover.Trigger class={dateTriggerClass} id="processing-date">
            <span class="truncate">{formatDateForDisplay(form.processingDate)}</span>
            <CalendarDays class="size-4 text-[#96a5bf]" />
          </Popover.Trigger>
          <Popover.Content align="start" class="w-auto border border-[#2a3853] bg-[#0f1727] p-0">
            <Calendar
              type="single"
              value={processingDateValue}
              onValueChange={handleDateChange}
              captionLayout="dropdown"
              class="rounded-md border-0 bg-transparent p-3"
              minValue={minSelectableDate}
              maxValue={maxSelectableDate}
              initialFocus
            />
          </Popover.Content>
        </Popover.Root>
      </div>

      <div class="space-y-1.5">
        <Label class={labelClass} for="sequence">File sequence number</Label>
        <Input
          id="sequence"
          class={inputClass}
          inputmode="numeric"
          maxlength="3"
          oninput={handleSequenceInput}
          pattern="[0-9]*"
          type="text"
          value={form.seq}
        />
      </div>
    </div>
  </div>
</Card>
