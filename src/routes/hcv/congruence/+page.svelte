<script>
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import * as Plot from '@observablehq/plot';
  import RenderPlot from '../../../Plot.svelte';
  import SvelteTable from 'svelte-table';
  
  import congruenceData from '../../../data/hcv/autotune/network_congruence_analysis.json';
  import treeComparisonData from '../../../data/hcv/autotune/tree_comparison_analysis.json';
  
  let selectedGenotype = writable('1a');
  let selectedThreshold = writable('0.2');
  let isLoading = writable(false);
  
  let alphaPlotOptions = writable({});
  let networkStatsPlotOptions = writable({});
  let pairwiseHeatmapOptions = writable({});
  let rfHeatmapOptions = writable({});
  
  let currentData = {};
  let pairwiseData = [];
  let networkStatsData = [];
  let rfData = [];
  
  $: combinationKey = `${$selectedGenotype}_${$selectedThreshold}`;
  $: if (congruenceData[combinationKey]) {
    currentData = congruenceData[combinationKey];
    updateVisualizations();
  }
  
  function updateVisualizations() {
    if (!currentData.krippendorff_alpha_pairwise) {
      console.log("No krippendorff_alpha_pairwise data found in currentData:", currentData);
      return;
    }
    
    // Prepare pairwise data for heatmap, excluding ns5a-ns5b-ns3
    pairwiseData = Object.entries(currentData.krippendorff_alpha_pairwise)
      .filter(([comparison]) => !comparison.includes('ns5a-ns5b-ns3'))
      .map(([comparison, alpha]) => {
        const [region1, region2] = comparison.split('_vs_');
        return {
          region1,
          region2,
          alpha: parseFloat(alpha),
          comparison
        };
      });
    
    console.log("Generated pairwiseData:", pairwiseData.length, "entries");
    console.log("Sample pairwise entries:", pairwiseData.slice(0, 3));
    
    // Prepare network statistics data, excluding ns5a-ns5b-ns3
    networkStatsData = Object.entries(currentData.network_statistics || {})
      .filter(([region]) => region !== 'ns5a-ns5b-ns3')
      .map(([region, stats]) => ({
        region,
        total_sequences: stats.total_sequences_analyzed,
        networked_sequences: stats.networked_sequences,
        singleton_sequences: stats.singleton_sequences,
        network_proportion: stats.network_proportion,
        total_clusters: stats.total_clusters,
        edges: stats.edges
      }));
    
    generateAlphaPlot();
    generateNetworkStatsPlot();
    generatePairwiseHeatmap();
    generateRFHeatmap();
  }
  
  function generateAlphaPlot() {
    const regions = [...new Set([
      ...pairwiseData.map(d => d.region1),
      ...pairwiseData.map(d => d.region2)
    ])];
    
    // Calculate average alpha for each region
    const regionAlphas = regions.map(region => {
      const regionComparisons = pairwiseData.filter(
        d => d.region1 === region || d.region2 === region
      );
      const avgAlpha = regionComparisons.reduce((sum, d) => sum + d.alpha, 0) / regionComparisons.length;
      
      return {
        region,
        average_alpha: avgAlpha,
        comparison_count: regionComparisons.length
      };
    });
    
    alphaPlotOptions.set({
      grid: true,
      width: 800,
      height: 400,
      marginBottom: 100,
      marginLeft: 80,
      x: {
        tickRotate: -45,
        label: "Gene Region"
      },
      y: {
        label: "Average Krippendorff's Alpha",
        domain: [0, 1]
      },
      marks: [
        Plot.frame(),
        Plot.barY(regionAlphas, {
          x: "region",
          y: "average_alpha",
          fill: "average_alpha",
          title: d => `${d.region}\nAvg Alpha: ${d.average_alpha.toFixed(3)}\nComparisons: ${d.comparison_count}`
        }),
        Plot.ruleY([0.8], { stroke: "orange", strokeDasharray: "2,2" }),
        Plot.ruleY([0.9], { stroke: "green", strokeDasharray: "2,2" })
      ],
      color: {
        legend: true,
        scheme: "viridis",
        domain: [0.75, 1.0],
        label: "Average Alpha"
      }
    });
  }
  
  function generateNetworkStatsPlot() {
    networkStatsPlotOptions.set({
      grid: true,
      width: 800,
      height: 400,
      marginBottom: 100,
      marginLeft: 80,
      x: {
        tickRotate: -45,
        label: "Gene Region"
      },
      y: {
        label: "Network Proportion"
      },
      marks: [
        Plot.frame(),
        Plot.barY(networkStatsData, {
          x: "region",
          y: "network_proportion",
          fill: "#3b82f6",
          title: d => `${d.region}\nTotal: ${d.total_sequences}\nNetworked: ${d.networked_sequences}\nSingletons: ${d.singleton_sequences}\nClusters: ${d.total_clusters}`
        })
      ]
    });
  }
  
  function generatePairwiseHeatmap() {
    // Create a simpler heatmap using all pairwise data directly
    if (!pairwiseData || pairwiseData.length === 0) {
      console.log("No pairwise data available for heatmap");
      return;
    }
    
    console.log("Pairwise data for heatmap:", pairwiseData.slice(0, 5)); // Debug log
    
    // Get all unique regions and sort them consistently
    const regions = [...new Set([
      ...pairwiseData.map(d => d.region1),
      ...pairwiseData.map(d => d.region2)
    ])].sort();
    
    // Create triangular heatmap data - only show upper triangle
    const triangularData = [];
    
    try {
      regions.forEach((region1, i) => {
        regions.forEach((region2, j) => {
          if (i < j) { // Only show upper triangle (i < j)
            // Find the comparison in either direction
            const comparison = pairwiseData.find(
              d => (d.region1 === region1 && d.region2 === region2) ||
                   (d.region1 === region2 && d.region2 === region1)
            );
            
            if (comparison) {
              triangularData.push({
                region1,
                region2,
                alpha: comparison.alpha,
                comparison: `${region1}_vs_${region2}`
              });
            }
          }
        });
      });
    } catch (error) {
      console.error("Error creating triangular data:", error);
      return; // Exit early if there's an error
    }
    
    console.log("Sorted regions for axes:", regions);
    console.log("Triangular data length:", triangularData.length);
    
    pairwiseHeatmapOptions.set({
      width: 700,
      height: 700,
      marginLeft: 100,
      marginBottom: 100,
      marginTop: 50,
      marginRight: 50,
      x: {
        domain: regions,
        tickRotate: -45,
        label: "Region 2"
      },
      y: {
        domain: regions,
        tickRotate: 0,
        label: "Region 1"
      },
      marks: [
        Plot.frame(),
        Plot.cell(triangularData, {
          x: "region2",
          y: "region1",
          fill: "alpha",
          stroke: "#fff",
          strokeWidth: 0.5,
          title: d => `${d.region1} vs ${d.region2}\nAlpha: ${d.alpha.toFixed(3)}`
        })
      ],
      color: {
        legend: true,
        scheme: "viridis",
        domain: [0.75, 1.0],
        type: "linear",
        label: "Krippendorff's Alpha"
      }
    });
  }

  function generateRFHeatmap() {
    // Check if tree comparison data is loaded
    if (!treeComparisonData || !treeComparisonData.cross_region_comparisons) {
      console.log("Tree comparison data not loaded");
      rfData = [];
      return;
    }
    
    // Filter cross-region comparisons for the selected genotype and threshold
    const selectedThresholdValue = $selectedThreshold;
    
    // Filter comparisons for selected genotype and threshold
    const relevantComparisons = treeComparisonData.cross_region_comparisons.filter(
      comp => comp.genotype === $selectedGenotype &&
              comp.consensus === selectedThresholdValue
    );
    
    if (relevantComparisons.length === 0) {
      console.log("No Robinson-Foulds data found for genotype:", $selectedGenotype, "and threshold:", selectedThresholdValue);
      rfData = [];
      rfHeatmapOptions.set({});
      return;
    }
    
    // Create pairwise data for cross-region comparisons
    const rfPairwiseData = [];
    
    relevantComparisons.forEach(comp => {
      // Extract regions from the comparison
      const region1 = comp.tree1.region;
      const region2 = comp.tree2.region;
      
      rfPairwiseData.push({
        region1,
        region2,
        normalized_rf: comp.robinson_foulds.normalized_rf,
        rf_distance: comp.robinson_foulds.rf_distance,
        common_leaves: comp.robinson_foulds.common_leaves,
        comparison: `${region1}_vs_${region2}`
      });
    });
    
    console.log("RF pairwise data sample:", rfPairwiseData.slice(0, 5));
    
    // Get all unique regions
    const regions = [...new Set([
      ...rfPairwiseData.map(d => d.region1),
      ...rfPairwiseData.map(d => d.region2)
    ])].sort();
    
    console.log("Unique regions found:", regions);
    
    // Create triangular heatmap data - only show upper triangle
    const triangularRFData = [];
    
    regions.forEach((region1, i) => {
      regions.forEach((region2, j) => {
        if (i < j) { // Only show upper triangle
          // Find the comparison in either direction
          const comparison = rfPairwiseData.find(
            d => (d.region1 === region1 && d.region2 === region2) ||
                 (d.region1 === region2 && d.region2 === region1)
          );
          
          if (comparison) {
            triangularRFData.push({
              region1,
              region2,
              normalized_rf: comparison.normalized_rf,
              rf_distance: comparison.rf_distance,
              common_leaves: comparison.common_leaves,
              comparison: `${region1}_vs_${region2}`
            });
          }
        }
      });
    });
    
    rfData = triangularRFData;
    console.log("Triangular RF data generated:", triangularRFData.length, "comparisons");
    
    rfHeatmapOptions.set({
      width: 700,
      height: 700,
      marginLeft: 100,
      marginBottom: 100,
      marginTop: 50,
      marginRight: 50,
      x: {
        domain: regions,
        tickRotate: -45,
        label: "Region 2"
      },
      y: {
        domain: regions,
        tickRotate: 0,
        label: "Region 1"
      },
      marks: [
        Plot.frame(),
        Plot.cell(triangularRFData, {
          x: "region2",
          y: "region1",
          fill: "normalized_rf",
          stroke: "#fff",
          strokeWidth: 0.5,
          title: d => `${d.region1} vs ${d.region2}\nNormalized RF: ${d.normalized_rf.toFixed(3)}\nRF Distance: ${d.rf_distance}\nCommon leaves: ${d.common_leaves}`
        })
      ],
      color: {
        legend: true,
        scheme: "Viridis",
        reverse: false,
        domain: [0, 1],
        label: "Normalized Robinson-Foulds Distance"
      }
    });
  }
  
  // Get available genotypes and thresholds
  const availableCombinations = Object.keys(congruenceData)
    .filter(key => key !== '_summary')
    .map(key => {
      const [genotype, threshold] = key.split('_');
      return { genotype, threshold, key };
    });
  
  const genotypes = [...new Set(availableCombinations.map(c => c.genotype))];
  const thresholds = [...new Set(availableCombinations.map(c => c.threshold))];
  
  onMount(() => {
    updateVisualizations();
  });
</script>

<div class="container px-5">
  <div class="grid grid-cols-1 items-center my-5">
    <div class="col-start-1 col-span-2">
      <h1 class="text-5xl">HCV Network Congruence Analysis</h1>
      <p>Analysis of network agreement across different HCV gene regions using Krippendorff's Alpha reliability measurement. This helps understand how consistent clustering patterns are between different genomic regions.</p>
      
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
      
      <!-- Analysis Information -->
      {#if currentData.genotype_consensus}
        <div class="bg-blue-50 p-4 rounded-lg mb-6">
          <h3 class="text-lg font-semibold text-blue-700 mb-2">Analysis Parameters</h3>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span class="font-medium text-blue-600">Genotype:</span>
              <span class="ml-2">{$selectedGenotype}</span>
            </div>
            <div>
              <span class="font-medium text-blue-600">Consensus Threshold:</span>
              <span class="ml-2">{$selectedThreshold}</span>
            </div>
            <div>
              <span class="font-medium text-blue-600">Regions:</span>
              <span class="ml-2">{currentData.regions_analyzed?.length || 0}</span>
            </div>
          </div>
          <div class="mt-3 text-sm text-blue-600">
            <span class="font-medium">Global Krippendorff's Alpha:</span>
            <span class="ml-2 font-mono">{currentData.krippendorff_alpha_global?.toFixed(4) || 'N/A'}</span>
          </div>
          {#if currentData.autotune_thresholds && Object.keys(currentData.autotune_thresholds).length > 0}
            <div class="mt-4">
              <h4 class="text-sm font-medium text-blue-700 mb-2">AUTO-TUNE Thresholds Used:</h4>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                {#each Object.entries(currentData.autotune_thresholds) as [region, threshold]}
                  <div class="bg-blue-100 px-2 py-1 rounded">
                    <span class="font-medium">{region}:</span> 
                    <span class="font-mono">{threshold}</span>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        </div>
      {/if}
      
      <!-- Parameter Selection -->
      <div class="flex pt-4 space-x-6 items-center bg-gray-50 p-4 rounded-lg">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Select Genotype</label>
          <select bind:value={$selectedGenotype} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            {#each genotypes as genotype}
              <option value={genotype}>{genotype}</option>
            {/each}
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Select Consensus Threshold</label>
          <select bind:value={$selectedThreshold} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            {#each thresholds as threshold}
              <option value={threshold}>{threshold}</option>
            {/each}
          </select>
        </div>
      </div>
      
      {#if currentData.genotype_consensus}
        <!-- Summary Statistics -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Congruence Summary</h2>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div class="bg-gray-50 p-3 rounded">
              <div class="text-sm text-gray-600">Global Alpha</div>
              <div class="text-2xl font-bold">{currentData.krippendorff_alpha_global?.toFixed(3) || 'N/A'}</div>
            </div>
            <div class="bg-gray-50 p-3 rounded">
              <div class="text-sm text-gray-600">Mean Pairwise Alpha</div>
              <div class="text-2xl font-bold">{currentData.pairwise_summary?.mean_pairwise_alpha?.toFixed(3) || 'N/A'}</div>
            </div>
            <div class="bg-gray-50 p-3 rounded">
              <div class="text-sm text-gray-600">Regions Compared</div>
              <div class="text-2xl font-bold">{currentData.regions_analyzed?.length || 'N/A'}</div>
            </div>
          </div>
        </div>
        
        <!-- Alpha by Region Plot -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Average Krippendorff's Alpha by Region</h2>
          <RenderPlot options={$alphaPlotOptions} />
          <p class="text-sm text-gray-600 mt-2">
            Higher values indicate better agreement with other regions. 
            Blue colors indicate high agreement, yellow indicates moderate agreement, and red indicates low agreement.
            Dashed lines mark thresholds at 0.2 (moderate) and 0.5 (good).
          </p>
        </div>
        
        <!-- Network Statistics Plot -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Network Proportion by Region</h2>
          <RenderPlot options={$networkStatsPlotOptions} />
          <p class="text-sm text-gray-600 mt-2">
            Proportion of sequences that form networks (non-singletons) in each region.
          </p>
        </div>
        
        <!-- Pairwise Heatmap -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Pairwise Region Agreement Heatmap</h2>
          <RenderPlot options={$pairwiseHeatmapOptions} />
          <p class="text-sm text-gray-600 mt-2">
            Krippendorff's Alpha values for each pair of regions. Blue indicates high agreement, red indicates low agreement.
          </p>
        </div>
        
        <!-- Robinson-Foulds Tree Agreement Heatmap -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Robinson-Foulds Tree Agreement Heatmap</h2>
          {#if rfData.length > 0}
            <RenderPlot options={$rfHeatmapOptions} />
            <p class="text-sm text-gray-600 mt-2">
              Normalized Robinson-Foulds distance between phylogenetic trees from different genomic regions. Lower values (darker) indicate more similar tree topologies, while higher values (lighter) indicate more different tree structures. This helps identify which genomic regions produce similar phylogenetic relationships.
            </p>
          {:else}
            <div class="p-8 bg-gray-50 rounded-lg">
              <h3 class="text-lg font-semibold text-gray-700 mb-3">Limited Tree Comparison Data</h3>
              <p class="text-gray-600 mb-3">No cross-region tree comparison data available for genotype <strong>{$selectedGenotype}</strong> at threshold <strong>{$selectedThreshold}</strong>.</p>
              
              <div class="text-sm text-gray-600">
                <p class="font-medium mb-2">Data Coverage for Genotype 1a:</p>
                <ul class="list-disc list-inside space-y-1 mb-3">
                  <li><strong>Network Analysis:</strong> 15 regions available (core, e1, e2, ns2, ns3, ns4a, ns4b, ns5a, ns5b, p7, etc.)</li>
                  <li><strong>Tree Comparisons:</strong> Only 4-7 regions per threshold with cross-region phylogenetic comparisons</li>
                  <li><strong>At threshold 0.2:</strong> Only 4 regions (core-e2-ns5a-ns3, e1, ns4b, ns5a-ns3) have tree comparisons</li>
                </ul>
                
                <p class="text-gray-500">
                  The Robinson-Foulds analysis requires phylogenetic trees from multiple regions, but genotype 1a has limited sequence data 
                  or insufficient tree generation across all genomic regions. Try genotype <strong>3a</strong> or <strong>2b</strong> for more comprehensive coverage.
                </p>
              </div>
            </div>
          {/if}
        </div>
        
        <!-- Network Statistics Table -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Network Statistics by Region</h2>
          <SvelteTable 
            columns={[
              { key: 'region', title: 'Region', sortable: true, value: (row) => row.region || 'N/A', headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'total_sequences', title: 'Total Sequences', sortable: true, value: (row) => row.total_sequences || 'N/A', sortValue: (row) => row.total_sequences || 0, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'networked_sequences', title: 'Networked', sortable: true, value: (row) => row.networked_sequences || 'N/A', sortValue: (row) => row.networked_sequences || 0, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'singleton_sequences', title: 'Singletons', sortable: true, value: (row) => row.singleton_sequences || 'N/A', sortValue: (row) => row.singleton_sequences || 0, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'network_proportion', title: 'Network Proportion', sortable: true, value: (row) => typeof row.network_proportion === 'number' ? row.network_proportion.toFixed(3) : 'N/A', sortValue: (row) => row.network_proportion || 0, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'total_clusters', title: 'Clusters', sortable: true, value: (row) => row.total_clusters || 'N/A', sortValue: (row) => row.total_clusters || 0, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'edges', title: 'Edges', sortable: true, value: (row) => row.edges || 'N/A', sortValue: (row) => row.edges || 0, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' }
            ]}
            rows={networkStatsData}
            classNameTable={['min-w-full']}
            classNameThead={['bg-gray-50']}
            classNameTbody={['']}
            classNameRow={['hover:bg-gray-50']}
          />
        </div>
        
        <!-- Pairwise Comparisons Table -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Pairwise Alpha Values</h2>
          <SvelteTable 
            columns={[
              { key: 'comparison', title: 'Region Comparison', sortable: true, value: (row) => row.comparison?.replace('_vs_', ' vs ') || 'N/A', headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'alpha', title: "Krippendorff's Alpha", sortable: true, value: (row) => typeof row.alpha === 'number' ? row.alpha.toFixed(3) : 'N/A', sortValue: (row) => row.alpha || 0, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' }
            ]}
            rows={pairwiseData}
            classNameTable={['min-w-full']}
            classNameThead={['bg-gray-50']}
            classNameTbody={['']}
            classNameRow={['hover:bg-gray-50']}
          />
        </div>
      {:else}
        <div class="bg-yellow-50 border border-yellow-200 p-4 rounded-lg mt-6">
          <p class="text-yellow-700">No congruence data available for {$selectedGenotype} at threshold {$selectedThreshold}</p>
        </div>
      {/if}
    </div>
  </div>
</div>