<script>
  import { Button } from '$lib/components/ui/button';
  import { Alert, AlertDescription, AlertTitle } from '$lib/components/ui/alert';
  import { Separator } from '$lib/components/ui/separator';

  export let generating = false;
  export let generateFile = () => {};
  export let status = '';
  export let error = '';
  export let previewInfo = null;
  export let buttonLabels = {};

  let alerts = [];

  $: alerts = [
    status
      ? {
          key: 'status',
          title: 'Success',
          description: status,
          className: 'border-[#2e5743] bg-[#10291f] text-[#7fd9a7]'
        }
      : null,
    error
      ? {
          key: 'error',
          title: 'Error',
          description: error,
          className: 'border-[#5a2a3a] bg-[#2b1822] text-[#ff9ba9]',
          variant: 'destructive'
        }
      : null,
    previewInfo
      ? {
          key: 'preview',
          title: 'Preview',
          description: `${previewInfo.number_of_records} records, total ${previewInfo.total_salaries}, file ${previewInfo.filename}`,
          className: 'border-[#2a3853] bg-[#121a2a] text-[#9bb0cc]'
        }
      : null
  ].filter(Boolean);
</script>

<Separator class="my-4 bg-[#243247]" />

<section class="flex justify-center">
  <Button
    class="h-10 min-w-[320px] rounded-md border border-[#2f5cab] bg-[linear-gradient(180deg,#2756a3,#1b3f7a)] px-4 font-semibold text-white hover:brightness-110"
    disabled={generating}
    onclick={generateFile}
    type="button"
  >
    {generating ? buttonLabels.generating || 'Generating...' : buttonLabels.generate || 'Generate .xlsx'}
  </Button>
</section>

{#each alerts as alert (alert.key)}
  <Alert class={`mt-3 ${alert.className}`} variant={alert.variant}>
    <AlertTitle>{alert.title}</AlertTitle>
    <AlertDescription>{alert.description}</AlertDescription>
  </Alert>
{/each}
