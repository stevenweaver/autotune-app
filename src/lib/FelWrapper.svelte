<script>
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { FelVisualization } from 'hyphy-scope';

  export let data;

  let mounted = false;
  let error = null;

  // Validate expected HyPhy FEL data structure
  $: isValidData = data && data.MLE && data.MLE.content && data.input;

  onMount(() => {
    mounted = true;
  });
</script>

<div class="fel-wrapper">
  {#if mounted && isValidData}
    <FelVisualization {data} />
  {:else if mounted && data && !isValidData}
    <div class="p-4 bg-amber-50 border border-amber-200 rounded">
      <p class="text-amber-700 font-medium">Data Format Warning</p>
      <p class="text-amber-600 text-sm mt-1">
        The data format is not recognized as valid HyPhy FEL output. Expected properties: MLE.content, input.
      </p>
    </div>
  {:else if error}
    <div class="p-4 bg-red-50 border border-red-200 rounded">
      <p class="text-red-700">Error loading FEL visualization: {error}</p>
    </div>
  {:else}
    <div class="p-8 bg-gray-50 rounded-lg text-center">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
      <p class="text-gray-600">Loading FEL visualization...</p>
    </div>
  {/if}
</div>

<style>
  .fel-wrapper {
    min-height: 400px;
    width: 100%;
  }
</style>