<script>
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import { browser } from '$app/environment';
  import MemeWrapper from '../../../lib/MemeWrapper.svelte';

  let selectedGenotype = writable('1a');
  let selectedThreshold = writable('0.2');
  let selectedRegion = writable('ns5a');
  let memeData = writable(null);
  let isLoading = writable(false);
  let error = writable(null);

  // Available options based on MEME files found
  const genotypes = ['1a', '1b', '2a', '2b', '3a', '4d'];
  const thresholds = ['0.01', '0.02', '0.05', '0.1', '0.2', '0.25'];
  const regions = ['core', 'e1', 'e2', 'ns2', 'ns3', 'ns4a', 'ns4b', 'ns5a', 'ns5b', 'p7', 'whole'];

  $: memeFilePath = `/src/data/hcv/autotune/${$selectedGenotype}_${$selectedThreshold}_${$selectedRegion}.MEME.json`;

  async function loadMEMEData() {
    isLoading.set(true);
    error.set(null);
    
    try {
      const response = await fetch(memeFilePath);
      if (!response.ok) {
        throw new Error(`Failed to load MEME data: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Check if the data contains error or valid MEME results
      if (data.error) {
        throw new Error(`MEME analysis error: ${data.error}`);
      }
      
      if (!data.MLE || !data.MLE.content) {
        throw new Error('Invalid MEME data format - missing MLE content');
      }
      
      memeData.set(data);
      console.log('MEME data loaded successfully:', data);
      
    } catch (err) {
      console.error('Error loading MEME data:', err);
      error.set(err.message);
      memeData.set(null);
    } finally {
      isLoading.set(false);
    }
  }

  // Load data when parameters change (only in browser)
  $: if (browser && $selectedGenotype && $selectedThreshold && $selectedRegion) {
    loadMEMEData();
  }

  onMount(() => {
    loadMEMEData();
  });
</script>

<div class="container px-5">
  <div class="grid grid-cols-1 items-center my-5">
    <div class="col-start-1 col-span-2">
      <h1 class="text-5xl">HCV MEME Analysis Results</h1>
      <p>Mixed Effects Model of Evolution (MEME) analysis results for detecting episodic diversifying selection in HCV sequences. MEME identifies individual sites that have experienced episodic positive selection across a portion of the phylogeny.</p>
      
      <!-- Navigation Links -->
      <div class="flex space-x-4 mt-4 mb-6">
        <a href="/hcv" class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors">
          Analysis Dashboard
        </a>
        <a href="/hcv/congruence" class="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors">
          Congruence Analysis
        </a>
        <a href="/hcv/diversity" class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors">
          Diversity Analysis
        </a>
        <a href="/hcv/fel" class="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors">
          FEL Analysis
        </a>
        <a href="/hcv/meme" class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors">
          MEME Analysis
        </a>
      </div>
      
      <!-- Parameter Selection -->
      <div class="flex pt-4 space-x-6 items-center bg-gray-50 p-4 rounded-lg">
        <div>
          <label for="meme-genotype-select" class="block text-sm font-medium text-gray-700 mb-1">Select Genotype</label>
          <select id="meme-genotype-select" bind:value={$selectedGenotype} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500 sm:text-sm">
            {#each genotypes as genotype}
              <option value={genotype}>{genotype}</option>
            {/each}
          </select>
        </div>

        <div>
          <label for="meme-threshold-select" class="block text-sm font-medium text-gray-700 mb-1">Select Consensus Threshold</label>
          <select id="meme-threshold-select" bind:value={$selectedThreshold} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500 sm:text-sm">
            {#each thresholds as threshold}
              <option value={threshold}>{threshold}</option>
            {/each}
          </select>
        </div>

        <div>
          <label for="meme-region-select" class="block text-sm font-medium text-gray-700 mb-1">Select Region</label>
          <select id="meme-region-select" bind:value={$selectedRegion} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500 sm:text-sm">
            {#each regions as region}
              <option value={region}>{region}</option>
            {/each}
          </select>
        </div>
      </div>

      <!-- Loading/Error States -->
      {#if $isLoading}
        <div class="bg-blue-50 p-4 rounded-lg mt-6">
          <div class="flex items-center">
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-3"></div>
            <p class="text-blue-700">Loading MEME analysis results...</p>
          </div>
        </div>
      {/if}

      {#if $error}
        <div class="bg-red-50 p-4 rounded-lg mt-6">
          <h3 class="text-lg font-semibold text-red-700 mb-2">Error Loading MEME Data</h3>
          <p class="text-red-600 mb-3">{$error}</p>
          <p class="text-sm text-red-500">
            This may occur if the MEME analysis failed for this combination or if the file doesn't exist. 
            Try selecting a different genotype, threshold, or region combination.
          </p>
        </div>
      {/if}

      <!-- MEME Results Visualization -->
      {#if $memeData && !$isLoading && !$error}
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">
            MEME Results: {$selectedGenotype} - {$selectedRegion} (threshold: {$selectedThreshold})
          </h2>
          
          <!-- MEME Visualization Component -->
          <div class="meme-visualization">
            <MemeWrapper data={$memeData} />
          </div>
          
          <div class="mt-4 text-sm text-gray-600">
            <p class="mb-2"><strong>Analysis Summary:</strong></p>
            <ul class="list-disc list-inside space-y-1">
              <li><strong>Method:</strong> Mixed Effects Model of Evolution (MEME)</li>
              <li><strong>Purpose:</strong> Detect episodic diversifying selection at individual sites</li>
              <li><strong>Genotype:</strong> {$selectedGenotype}</li>
              <li><strong>Region:</strong> {$selectedRegion}</li>
              <li><strong>Consensus Threshold:</strong> {$selectedThreshold}</li>
            </ul>
          </div>
        </div>
      {/if}

      <!-- Information Panel -->
      <div class="bg-gray-50 p-4 rounded-lg mt-6">
        <h3 class="text-lg font-semibold text-gray-700 mb-3">About MEME Analysis</h3>
        <div class="text-sm text-gray-600">
          <p class="mb-3">
            Mixed Effects Model of Evolution (MEME) identifies individual sites that have experienced episodic positive selection. 
            Unlike FEL, MEME can detect sites where positive selection occurred only in a subset of lineages.
          </p>
          <ul class="list-disc list-inside space-y-1">
            <li><strong>β+:</strong> Rate of nonsynonymous substitution under positive selection</li>
            <li><strong>β-:</strong> Rate of nonsynonymous substitution under negative/neutral selection</li>
            <li><strong>p-value:</strong> Statistical significance of episodic selection detection</li>
            <li><strong>Data Available:</strong> 960 MEME analysis files across different genotypes, thresholds, and regions</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .meme-visualization {
    min-height: 400px;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 1rem;
  }
</style>