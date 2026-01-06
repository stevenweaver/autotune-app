<script>
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';

  export let visible = false;
  export let networkUrl = null;
  export let meta = null; // { gene, genotype, threshold }
  export let onClose = () => {};

  let iframeRef;
  let isLoading = true;
  let hasError = false;
  let errorMessage = '';

  // Handle escape key to close
  function handleKeydown(event) {
    if (event.key === 'Escape' && visible) {
      onClose();
    }
  }

  // Build iframe URL with query parameters (this approach works!)
  $: iframeSrc = networkUrl && meta ?
    `/network-viewer.html?data=${encodeURIComponent(networkUrl)}&gene=${encodeURIComponent(meta.gene || '')}&genotype=${encodeURIComponent(meta.genotype || '')}&threshold=${encodeURIComponent(meta.threshold || '')}` :
    null;

  // Handle iframe load
  function onIframeLoad() {
    // Give hivtrace a moment to initialize
    setTimeout(() => {
      isLoading = false;
    }, 500);
  }

  // Handle iframe error
  function onIframeError() {
    hasError = true;
    errorMessage = 'Failed to load network viewer';
    isLoading = false;
  }

  // Listen for messages from iframe
  function handleMessage(event) {
    if (!browser) return;
    if (event.origin !== window.location.origin) return;

    if (event.data && event.data.type === 'NETWORK_READY') {
      isLoading = false;
    }
  }

  // Reset state when visibility changes
  $: if (visible) {
    isLoading = true;
    hasError = false;
    errorMessage = '';
  }

  onMount(() => {
    if (browser) {
      window.addEventListener('message', handleMessage);
      window.addEventListener('keydown', handleKeydown);
    }
  });

  onDestroy(() => {
    if (browser) {
      window.removeEventListener('message', handleMessage);
      window.removeEventListener('keydown', handleKeydown);
    }
  });
</script>

{#if visible}
  <!-- Modal overlay -->
  <div
    class="fixed inset-0 z-50 flex items-center justify-center"
    role="dialog"
    aria-modal="true"
    aria-labelledby="network-viewer-title"
  >
    <!-- Backdrop -->
    <div
      class="absolute inset-0 bg-black/60 backdrop-blur-sm"
      on:click={onClose}
      on:keydown={(e) => e.key === 'Enter' && onClose()}
      role="button"
      tabindex="0"
      aria-label="Close network viewer"
    ></div>

    <!-- Modal content -->
    <div class="relative w-[95vw] h-[90vh] max-w-7xl bg-white rounded-lg shadow-2xl overflow-hidden">
      <!-- Header -->
      <div class="absolute top-0 left-0 right-0 z-10 flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200">
        <h2 id="network-viewer-title" class="text-lg font-semibold text-gray-800">
          {#if meta}
            Network: {meta.gene?.toUpperCase() || 'Unknown'}
            <span class="text-sm font-normal text-gray-500">
              (Genotype {meta.genotype}, Threshold {meta.threshold})
            </span>
          {:else}
            Network Visualization
          {/if}
        </h2>
        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-500">Press ESC to close</span>
          <button
            on:click={onClose}
            class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Close"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Loading state -->
      {#if isLoading && !hasError}
        <div class="absolute inset-0 flex items-center justify-center bg-white z-20" style="top: 52px;">
          <div class="text-center">
            <div class="inline-block w-10 h-10 border-4 border-gray-200 border-t-indigo-600 rounded-full animate-spin"></div>
            <p class="mt-4 text-gray-600">Loading network visualization...</p>
          </div>
        </div>
      {/if}

      <!-- Error state -->
      {#if hasError}
        <div class="absolute inset-0 flex items-center justify-center bg-white z-20" style="top: 52px;">
          <div class="text-center max-w-md px-6">
            <div class="w-12 h-12 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
              <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-900 mb-2">Failed to Load Network</h3>
            <p class="text-gray-600 mb-4">{errorMessage}</p>
            <button
              on:click={onClose}
              class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      {/if}

      <!-- Iframe container -->
      <div class="w-full h-full pt-[52px]">
        {#if iframeSrc}
          <iframe
            bind:this={iframeRef}
            src={iframeSrc}
            title="Network Visualization"
            class="w-full h-full border-0"
            on:load={onIframeLoad}
            on:error={onIframeError}
          ></iframe>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  /* Ensure modal is above everything */
  :global(body:has(.fixed.inset-0.z-50)) {
    overflow: hidden;
  }
</style>
