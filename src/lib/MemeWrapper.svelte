<script>
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { MemeVisualization } from 'hyphy-scope';
  
  export let data;
  
  let mounted = false;
  let error = null;
  
  onMount(() => {
    mounted = true;
  });
</script>

<div class="meme-wrapper">
  {#if mounted && data}
    <MemeVisualization {data} />
  {:else if error}
    <div class="p-4 bg-red-50 border border-red-200 rounded">
      <p class="text-red-700">Error loading MEME visualization: {error}</p>
    </div>
  {:else}
    <div class="p-8 bg-gray-50 rounded-lg text-center">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
      <p class="text-gray-600">Loading MEME visualization...</p>
    </div>
  {/if}
</div>

<style>
  .meme-wrapper {
    min-height: 400px;
    width: 100%;
  }
</style>