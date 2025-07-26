<script>
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import * as Plot from '@observablehq/plot';
  import RenderPlot from '../../../Plot.svelte';
  import SvelteTable from 'svelte-table';
  
  import diversityData from '../../../data/hcv/autotune/diversity_analysis.json';
  
  let selectedGenotype = writable('1a');
  let selectedThreshold = writable('0.01');
  let isLoading = writable(false);
  
  let nucleotideDiversityOptions = writable({});
  let tajimaDOptions = writable({});
  let tn93DistanceOptions = writable({});
  let segregatingSitesOptions = writable({});
  let gcContentOptions = writable({});
  
  let currentData = [];
  let summaryStats = diversityData.summary;
  
  $: combinationKey = `${$selectedGenotype}_${$selectedThreshold}`;
  $: {
    // Filter data for current selection
    currentData = diversityData.individual_results.filter(
      d => d.genotype === $selectedGenotype && d.consensus === $selectedThreshold
    );
    updateVisualizations();
  }
  
  function updateVisualizations() {
    if (!currentData || currentData.length === 0) {
      console.log("No diversity data found for current selection");
      return;
    }
    
    generateNucleotideDiversityPlot();
    generateTajimaDPlot();
    generateTN93DistancePlot();
    generateSegregatingSitesPlot();
    generateGCContentPlot();
  }
  
  function generateNucleotideDiversityPlot() {
    nucleotideDiversityOptions.set({
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
        label: "Nucleotide Diversity (π)",
        domain: [0, Math.max(...currentData.map(d => d.nucleotide_diversity)) * 1.1]
      },
      marks: [
        Plot.frame(),
        Plot.barY(currentData, {
          x: "region",
          y: "nucleotide_diversity",
          fill: d => d.nucleotide_diversity > summaryStats.diversity_statistics.mean_nucleotide_diversity ? "#22c55e" : "#3b82f6",
          title: d => `${d.region}\nNucleotide Diversity: ${d.nucleotide_diversity.toFixed(5)}\nSequences: ${d.sequence_count}\nLength: ${d.sequence_length}`
        }),
        Plot.ruleY([summaryStats.diversity_statistics.mean_nucleotide_diversity], { 
          stroke: "red", 
          strokeDasharray: "2,2",
          title: `Mean: ${summaryStats.diversity_statistics.mean_nucleotide_diversity.toFixed(5)}`
        })
      ]
    });
  }
  
  function generateTajimaDPlot() {
    tajimaDOptions.set({
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
        label: "Tajima's D",
        domain: [
          Math.min(...currentData.map(d => d.tajima_d)) * 1.1,
          Math.max(...currentData.map(d => d.tajima_d)) * 1.1
        ]
      },
      marks: [
        Plot.frame(),
        Plot.barY(currentData, {
          x: "region",
          y: "tajima_d",
          fill: d => d.tajima_d > 0 ? "#22c55e" : d.tajima_d < -2 || d.tajima_d > 2 ? "#ef4444" : "#f59e0b",
          title: d => `${d.region}\nTajima's D: ${d.tajima_d.toFixed(3)}\nInterpretation: ${getTajimaDInterpretation(d.tajima_d)}`
        }),
        Plot.ruleY([0], { stroke: "black", strokeDasharray: "2,2" }),
        Plot.ruleY([-2], { stroke: "orange", strokeDasharray: "2,2", title: "Selection threshold" }),
        Plot.ruleY([2], { stroke: "orange", strokeDasharray: "2,2", title: "Balancing selection threshold" })
      ]
    });
  }
  
  function generateTN93DistancePlot() {
    // Create histogram data from distance statistics
    const histogramData = [];
    currentData.forEach(d => {
      if (d.distance_statistics) {
        histogramData.push({
          region: d.region,
          mean_distance: d.distance_statistics.mean_distance,
          median_distance: d.distance_statistics.median_distance,
          std_distance: d.distance_statistics.std_distance,
          max_distance: d.distance_statistics.max_distance
        });
      }
    });
    
    tn93DistanceOptions.set({
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
        label: "TN93 Distance",
        domain: [0, Math.max(...histogramData.map(d => d.max_distance)) * 1.1]
      },
      marks: [
        Plot.frame(),
        Plot.barY(histogramData, {
          x: "region",
          y: "mean_distance",
          fill: "#3b82f6",
          title: d => `${d.region}\nMean: ${d.mean_distance.toFixed(5)}\nMedian: ${d.median_distance.toFixed(5)}\nStd: ${d.std_distance.toFixed(5)}\nMax: ${d.max_distance.toFixed(5)}`
        }),
        // Add error bars showing standard deviation
        Plot.ruleY(histogramData, {
          x: "region",
          y1: d => Math.max(0, d.mean_distance - d.std_distance),
          y2: d => d.mean_distance + d.std_distance,
          stroke: "black",
          strokeWidth: 2
        })
      ]
    });
  }
  
  function generateSegregatingSitesPlot() {
    // Calculate mean segregating sites proportion for reference line
    const meanSegregatingProportion = currentData.reduce((sum, d) => sum + d.segregating_sites_proportion, 0) / currentData.length;
    
    segregatingSitesOptions.set({
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
        label: "Segregating Sites Proportion",
        domain: [0, Math.max(...currentData.map(d => d.segregating_sites_proportion)) * 1.1]
      },
      marks: [
        Plot.frame(),
        Plot.barY(currentData, {
          x: "region",
          y: "segregating_sites_proportion",
          fill: "#8b5cf6",
          title: d => `${d.region}\nSegregating Sites: ${d.segregating_sites} / ${d.sequence_length}\nProportion: ${(d.segregating_sites_proportion * 100).toFixed(1)}%\nLength-normalized comparison`
        }),
        Plot.ruleY([meanSegregatingProportion], { 
          stroke: "red", 
          strokeDasharray: "2,2",
          title: `Mean Proportion: ${(meanSegregatingProportion * 100).toFixed(1)}%`
        })
      ]
    });
  }
  
  function generateGCContentPlot() {
    gcContentOptions.set({
      grid: true,
      width: 800,
      height: 400,
      marginBottom: 120,
      marginLeft: 80,
      x: {
        tickRotate: -45,
        label: "Gene Region"
      },
      y: {
        label: "GC Content (%)",
        domain: [0, 100]
      },
      marks: [
        Plot.frame(),
        Plot.barY(currentData, {
          x: "region",
          y: "mean_gc_content",
          fill: "#10b981",
          title: d => `${d.region}\nGC Content: ${d.mean_gc_content.toFixed(2)}%\nSequences: ${d.sequence_count}`
        }),
        Plot.ruleY([50], { 
          stroke: "gray", 
          strokeDasharray: "3,3",
          strokeWidth: 2,
          title: "50% GC reference"
        })
      ]
    });
  }
  
  function getTajimaDInterpretation(value) {
    if (value > 2) return "Balancing selection";
    if (value < -2) return "Positive selection/population expansion";
    if (value > 0) return "Balancing selection (weak)";
    if (value < 0) return "Positive selection (weak)";
    return "Neutral evolution";
  }
  
  // Get available genotypes and thresholds
  const availableGenotypes = [...new Set(diversityData.individual_results.map(d => d.genotype))];
  const availableThresholds = [...new Set(diversityData.individual_results.map(d => d.consensus))];
  
  onMount(() => {
    updateVisualizations();
  });
</script>

<div class="container px-5">
  <div class="grid grid-cols-1 items-center my-5">
    <div class="col-start-1 col-span-2">
      <h1 class="text-5xl">HCV Genomic Diversity Analysis</h1>
      <p>Analysis of nucleotide diversity, segregating sites, Tajima's D, TN93 distances, and GC content across different HCV gene regions. This analysis helps understand evolutionary patterns and selective pressures in different genomic regions.</p>
      
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
      </div>
      
      <!-- Parameter Selection -->
      <div class="flex pt-4 space-x-6 items-center bg-gray-50 p-4 rounded-lg">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Select Genotype</label>
          <select bind:value={$selectedGenotype} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            {#each availableGenotypes as genotype}
              <option value={genotype}>{genotype}</option>
            {/each}
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Select Consensus Threshold</label>
          <select bind:value={$selectedThreshold} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            {#each availableThresholds as threshold}
              <option value={threshold}>{threshold}</option>
            {/each}
          </select>
        </div>
      </div>
      
      {#if currentData.length > 0}
        <!-- Summary Statistics -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Diversity Summary</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="bg-gray-50 p-3 rounded">
              <div class="text-sm text-gray-600">Regions Analyzed</div>
              <div class="text-2xl font-bold">{summaryStats.total_regions_analyzed}</div>
            </div>
            <div class="bg-gray-50 p-3 rounded">
              <div class="text-sm text-gray-600">Mean Nucleotide Diversity</div>
              <div class="text-2xl font-bold">{summaryStats.diversity_statistics.mean_nucleotide_diversity.toFixed(4)}</div>
            </div>
            <div class="bg-gray-50 p-3 rounded">
              <div class="text-sm text-gray-600">Mean Segregating Sites</div>
              <div class="text-2xl font-bold">{summaryStats.diversity_statistics.mean_segregating_sites.toFixed(0)}</div>
            </div>
            <div class="bg-gray-50 p-3 rounded">
              <div class="text-sm text-gray-600">Diversity Range</div>
              <div class="text-lg font-bold">{summaryStats.diversity_statistics.diversity_range.min.toFixed(3)} - {summaryStats.diversity_statistics.diversity_range.max.toFixed(3)}</div>
            </div>
          </div>
        </div>
        
        <!-- Nucleotide Diversity Plot -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Nucleotide Diversity by Region</h2>
          <RenderPlot options={$nucleotideDiversityOptions} />
          <p class="text-sm text-gray-600 mt-2">
            Nucleotide diversity (π) measures the average number of nucleotide differences per site between sequences. 
            Higher values indicate greater genetic diversity. Red line shows the mean across all regions.
          </p>
        </div>
        
        <!-- Tajima's D Plot -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Tajima's D Statistics</h2>
          <RenderPlot options={$tajimaDOptions} />
          <p class="text-sm text-gray-600 mt-2">
            Tajima's D tests for neutrality. Values &gt; 0 suggest balancing selection, values &lt; 0 suggest positive selection or population expansion.
            <span class="text-orange-500">Orange lines mark significance thresholds (±2)</span>.
          </p>
        </div>
        
        <!-- TN93 Distance Plot -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">TN93 Distance Statistics</h2>
          <RenderPlot options={$tn93DistanceOptions} />
          <p class="text-sm text-gray-600 mt-2">
            TN93 distances measure evolutionary divergence between sequences. Error bars show standard deviation.
            Higher mean distances indicate greater evolutionary divergence within the region.
          </p>
        </div>
        
        <!-- Segregating Sites Plot -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Segregating Sites by Region</h2>
          <RenderPlot options={$segregatingSitesOptions} />
          <p class="text-sm text-gray-600 mt-2">
            Segregating sites proportion shows the fraction of positions that vary, normalized by sequence length.
            This allows fair comparison across regions of different sizes. Red line shows the mean proportion.
          </p>
        </div>
        
        <!-- GC Content Plot -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">GC Content by Region</h2>
          <RenderPlot options={$gcContentOptions} />
          <p class="text-sm text-gray-600 mt-2">
            GC content varies across genomic regions and can affect secondary structure and function.
            Gray line shows 50% GC reference.
          </p>
        </div>
        
        <!-- Detailed Data Table -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Detailed Diversity Metrics</h2>
          <SvelteTable 
            columns={[
              { key: 'region', title: 'Region', sortable: true, value: (row) => row.region || 'N/A', headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'sequence_count', title: 'Sequences', sortable: true, value: (row) => row.sequence_count || 'N/A', headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'sequence_length', title: 'Length', sortable: true, value: (row) => row.sequence_length || 'N/A', headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'nucleotide_diversity', title: 'Nucleotide Diversity', sortable: true, value: (row) => typeof row.nucleotide_diversity === 'number' ? row.nucleotide_diversity.toFixed(5) : 'N/A', headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'segregating_sites', title: 'Segregating Sites', sortable: true, value: (row) => row.segregating_sites || 'N/A', headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'tajima_d', title: "Tajima's D", sortable: true, value: (row) => typeof row.tajima_d === 'number' ? row.tajima_d.toFixed(3) : 'N/A', headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'mean_gc_content', title: 'GC Content (%)', sortable: true, value: (row) => typeof row.mean_gc_content === 'number' ? row.mean_gc_content.toFixed(2) : 'N/A', headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'mean_distance', title: 'Mean TN93 Distance', sortable: true, value: (row) => row.distance_statistics?.mean_distance ? row.distance_statistics.mean_distance.toFixed(5) : 'N/A', headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' }
            ]}
            rows={currentData}
            classNameTable={['min-w-full']}
            classNameThead={['bg-gray-50']}
            classNameTbody={['']}
            classNameRow={['hover:bg-gray-50']}
          />
        </div>
      {:else}
        <div class="bg-yellow-50 border border-yellow-200 p-4 rounded-lg mt-6">
          <p class="text-yellow-700">No diversity data available for {$selectedGenotype} at threshold {$selectedThreshold}</p>
        </div>
      {/if}
    </div>
  </div>
</div>