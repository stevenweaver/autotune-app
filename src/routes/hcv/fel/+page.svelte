<script>
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import { browser } from '$app/environment';
  import FelWrapper from '../../../lib/FelWrapper.svelte';
  import { selectedGenotype, selectedThreshold, selectedRegion, genotypes, thresholds, regions } from '$lib/hcvStore.js';

  let felData = writable(null);
  let isLoading = writable(false);
  let error = writable(null);

  $: felFilePath = `/data/hcv/autotune/${$selectedGenotype}_${$selectedThreshold}_${$selectedRegion}.FEL.json`;

  async function loadFELData() {
    isLoading.set(true);
    error.set(null);
    
    try {
      const response = await fetch(felFilePath);
      if (!response.ok) {
        throw new Error(`Failed to load FEL data: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Check if the data contains error or valid FEL results
      if (data.error) {
        throw new Error(`FEL analysis error: ${data.error}`);
      }
      
      if (!data.MLE || !data.MLE.content) {
        throw new Error('Invalid FEL data format - missing MLE content');
      }
      
      felData.set(data);
      console.log('FEL data loaded successfully:', data);
      
    } catch (err) {
      console.error('Error loading FEL data:', err);
      error.set(err.message);
      felData.set(null);
    } finally {
      isLoading.set(false);
    }
  }

  // Load data when parameters change (only in browser)
  $: if (browser && $selectedGenotype && $selectedThreshold && $selectedRegion) {
    loadFELData();
  }

  onMount(() => {
    loadFELData();
  });
</script>

<div class="container px-5">
  <div class="grid grid-cols-1 items-center my-5">
    <div class="col-start-1 col-span-2">
      <h1 class="text-5xl">HCV FEL Analysis Results</h1>
      <p>Fixed Effects Likelihood (FEL) analysis results for detecting sites under selection in HCV sequences. FEL uses a site-by-site approach to identify positions evolving under positive or negative selection.</p>

      <!-- Global Selection Controls (persist across all HCV pages) -->
      <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center bg-indigo-50 border border-indigo-200 p-4 rounded-lg mt-4">
        <div>
          <label for="fel-genotype-select" class="block text-sm font-medium text-gray-700 mb-1">Select Genotype</label>
          <select id="fel-genotype-select" bind:value={$selectedGenotype} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            {#each genotypes as genotype}
              <option value={genotype}>{genotype}</option>
            {/each}
          </select>
        </div>

        <div>
          <label for="fel-threshold-select" class="block text-sm font-medium text-gray-700 mb-1">Select Consensus Threshold</label>
          <select id="fel-threshold-select" bind:value={$selectedThreshold} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            {#each thresholds as threshold}
              <option value={threshold}>{threshold}</option>
            {/each}
          </select>
        </div>

        <div>
          <label for="fel-region-select" class="block text-sm font-medium text-gray-700 mb-1">Select Region</label>
          <select id="fel-region-select" bind:value={$selectedRegion} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            {#each regions as region}
              <option value={region}>{region}</option>
            {/each}
          </select>
        </div>
      </div>

      <!-- Navigation Links -->
      <div class="flex flex-wrap gap-2 mt-4 mb-6">
        <a href="/hcv" class="px-3 py-1.5 sm:px-4 sm:py-2 text-sm sm:text-base bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors">
          Analysis Dashboard
        </a>
        <a href="/hcv/congruence" class="px-3 py-1.5 sm:px-4 sm:py-2 text-sm sm:text-base bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors">
          Congruence Analysis
        </a>
        <a href="/hcv/diversity" class="px-3 py-1.5 sm:px-4 sm:py-2 text-sm sm:text-base bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors">
          Diversity Analysis
        </a>
        <a href="/hcv/fel" class="px-3 py-1.5 sm:px-4 sm:py-2 text-sm sm:text-base bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors">
          FEL Analysis
        </a>
        <a href="/hcv/meme" class="px-3 py-1.5 sm:px-4 sm:py-2 text-sm sm:text-base bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors">
          MEME Analysis
        </a>
      </div>

      <!-- Loading/Error States -->
      {#if $isLoading}
        <div class="bg-blue-50 p-4 rounded-lg mt-6">
          <div class="flex items-center">
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-3"></div>
            <p class="text-blue-700">Loading FEL analysis results...</p>
          </div>
        </div>
      {/if}

      {#if $error}
        <div class="bg-red-50 border border-red-200 p-4 rounded-lg mt-6">
          <h3 class="text-lg font-semibold text-red-700 mb-2">Unable to Load FEL Analysis</h3>
          <p class="text-red-600 mb-3">{$error}</p>
          <div class="text-sm text-red-500">
            <p class="font-medium mb-1">Suggestions:</p>
            <ul class="list-disc list-inside space-y-1">
              <li>Check that the selected combination exists in the dataset</li>
              <li>Try a different region (e.g., ns5a, core, or whole)</li>
              <li>Some genotype/threshold combinations may have insufficient data</li>
              <li>Current selection: <strong>{$selectedGenotype}</strong> / <strong>{$selectedThreshold}</strong> / <strong>{$selectedRegion}</strong></li>
            </ul>
          </div>
        </div>
      {/if}

      <!-- FEL Results Visualization -->
      {#if $felData && !$isLoading && !$error}
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">
            FEL Results: {$selectedGenotype} - {$selectedRegion} (threshold: {$selectedThreshold})
          </h2>
          
          <!-- FEL Visualization Component -->
          <div class="fel-visualization">
            <FelWrapper data={$felData} />
          </div>
          
          <div class="mt-4 text-sm text-gray-600">
            <p class="mb-2"><strong>Analysis Summary:</strong></p>
            <ul class="list-disc list-inside space-y-1">
              <li><strong>Method:</strong> Fixed Effects Likelihood (FEL)</li>
              <li><strong>Purpose:</strong> Detect sites under positive or negative selection</li>
              <li><strong>Genotype:</strong> {$selectedGenotype}</li>
              <li><strong>Region:</strong> {$selectedRegion}</li>
              <li><strong>Consensus Threshold:</strong> {$selectedThreshold}</li>
            </ul>
          </div>
        </div>
      {/if}

      <!-- Information Panel -->
      <div class="bg-gray-50 p-4 rounded-lg mt-6">
        <h3 class="text-lg font-semibold text-gray-700 mb-3">About FEL Analysis</h3>
        <div class="text-sm text-gray-600">
          <p class="mb-3">
            Fixed Effects Likelihood (FEL) is a phylogenetic method for detecting sites under selection.
            It estimates synonymous (α) and nonsynonymous (β) substitution rates at each codon position.
          </p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div class="bg-white p-3 rounded border">
              <h4 class="font-medium text-gray-700 mb-2">Key Parameters</h4>
              <ul class="list-disc list-inside space-y-1 text-xs">
                <li><strong>α (alpha):</strong> Synonymous substitution rate</li>
                <li><strong>β (beta):</strong> Non-synonymous substitution rate</li>
                <li><strong>ω (omega):</strong> dN/dS ratio (β/α)</li>
                <li><strong>P-value:</strong> Statistical significance (typically &lt;0.05)</li>
              </ul>
            </div>
            <div class="bg-white p-3 rounded border">
              <h4 class="font-medium text-gray-700 mb-2">Interpretation Guide</h4>
              <ul class="list-disc list-inside space-y-1 text-xs">
                <li><strong>ω &gt; 1 (p&lt;0.05):</strong> Positive selection - adaptive evolution</li>
                <li><strong>ω &lt; 1 (p&lt;0.05):</strong> Negative selection - functional constraint</li>
                <li><strong>ω ≈ 1:</strong> Neutral evolution</li>
              </ul>
            </div>
          </div>
          <p class="text-xs text-gray-500">
            <strong>Reference:</strong> Kosakovsky Pond SL & Frost SDW (2005). Not so different after all: a comparison of methods for detecting amino acid sites under selection. Mol Biol Evol. 22(5):1208-22.
          </p>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .fel-visualization {
    min-height: 400px;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 1rem;
  }
</style>