<script>
  export let className = 'h-4 w-auto';
</script>

<img alt="" aria-hidden="true" class={`omr-symbol ${className}`} src="/omr-symbol.svg" />

<style>
  .omr-symbol {
    display: block;
    filter: none;
  }

  :global(html.theme-dark) .omr-symbol {
    filter: brightness(0) invert(1);
  }
</style>

