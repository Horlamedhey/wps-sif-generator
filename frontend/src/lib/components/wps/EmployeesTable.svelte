<script>
  import { Card } from '$lib/components/ui/card';
  import { Input } from '$lib/components/ui/input';
  import { Button } from '$lib/components/ui/button';
  import { employeeHeaders, employeeFieldKeys } from '$lib/wps/employee';

  export let employees = [];
  export let addRow = () => {};
  export let removeRow = () => {};

  const cellInputClass =
    'h-9 rounded-none border-0 bg-transparent px-2 text-[13px] text-[#dbe5f6] focus-visible:ring-0 focus-visible:border-0';
  const thClass =
    'border border-[#1f2b40] bg-[#0f1727] px-2 py-2 text-left text-[11px] font-semibold text-[#aebcce] whitespace-nowrap';
  const tdClass = 'border border-[#1f2b40]';

  function updateEmployeeField(rowIndex, field, value) {
    const next = [...employees];
    next[rowIndex] = { ...next[rowIndex], [field]: value };
    employees = next;
  }
</script>

<h2 class="mt-5 text-3xl font-bold tracking-tight text-[#dbe5f6] md:text-4xl">Employees</h2>
<p class="mb-2 text-xs text-[#96a5bf]">
  Tip: Paste rows from Excel. Amounts are normalized to 3 decimals. Extra Hours to 2 decimals.
</p>

<Card class="overflow-hidden rounded-[10px] border border-[#243247] bg-[linear-gradient(180deg,rgba(17,24,39,0.98),rgba(9,16,30,0.96))] p-0 shadow-none gap-0">
  <div class="overflow-x-auto">
    <table class="min-w-[1550px] w-full border-collapse">
      <thead>
        <tr>
          {#each employeeHeaders as header}
            <th class={thClass}>{header}</th>
          {/each}
          <th class={thClass}></th>
        </tr>
      </thead>
      <tbody>
        {#each employees as employee, idx (idx)}
          <tr>
            {#each employeeFieldKeys as field}
              <td class={tdClass}>
                <Input
                  class={cellInputClass}
                  oninput={(event) => updateEmployeeField(idx, field, event.currentTarget.value)}
                  value={employee[field]}
                />
              </td>
            {/each}
            <td class="border border-[#1f2b40] px-2 py-1 text-center">
              <Button
                class="h-8 w-8 rounded-md border border-[#5a2a3a] bg-[#2b1822] px-0 text-[#f4a9bd] hover:bg-[#3a1f2d]"
                on:click={() => removeRow(idx)}
                type="button"
                variant="outline"
              >
                -
              </Button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  <div class="border-t border-[#1f2b40] p-3">
    <Button
      class="h-9 rounded-md border border-[#2d3b57] bg-[#172239] text-[#dbe5f6] hover:bg-[#1f2f4a]"
      on:click={addRow}
      type="button"
      variant="outline"
    >
      Add Row
    </Button>
  </div>
</Card>
