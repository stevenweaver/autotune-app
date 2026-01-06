<script>
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import * as Plot from '@observablehq/plot';
  import RenderPlot from '../../../Plot.svelte';
  import SvelteTable from 'svelte-table';
  import Tooltip from '$lib/Tooltip.svelte';
  import { selectedGenotype, selectedThreshold, genotypes, thresholds } from '$lib/hcvStore.js';
  import {
    getRegionClassification,
    getClassificationDisplay,
    OPTIMAL_REGIONS,
    POOR_REGIONS
  } from '$lib/regionClassification.js';

  import diversityData from '../../../data/hcv/autotune/diversity_analysis.json';

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
    // Filter data for current selection, excluding invalid regions
    // Enrich with region classification
    currentData = diversityData.individual_results
      .filter(
        d => d.genotype === $selectedGenotype &&
            d.consensus === $selectedThreshold &&
            d.region &&
            d.region !== "0" &&
            d.region.trim() !== "" &&
            d.region !== "null"
      )
      .map(d => {
        const classification = getRegionClassification(d.region);
        const classDisplay = getClassificationDisplay(classification);
        return {
          ...d,
          classification,
          classDisplay
        };
      });
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
          fill: d => d.nucleotide_diversity > summaryStats.diversity_statistics.mean_nucleotide_diversity ? "#f97316" : "#3b82f6",
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
          fill: d => d.tajima_d > 2 || d.tajima_d < -2 ? "#ea580c" : d.tajima_d > 0 ? "#3b82f6" : "#94a3b8",
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
      // Filter out invalid regions including "0", empty strings, or null
      if (d.distance_statistics && d.region && d.region !== "0" && d.region.trim() !== "") {
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
        // Error bar vertical lines showing standard deviation
        Plot.ruleX(histogramData, {
          x: "region",
          y1: d => Math.max(0, d.mean_distance - d.std_distance),
          y2: d => d.mean_distance + d.std_distance,
          stroke: "black",
          strokeWidth: 1.5
        }),
        // Error bar top caps
        Plot.tickY(histogramData, {
          x: "region",
          y: d => d.mean_distance + d.std_distance,
          stroke: "black",
          strokeWidth: 1.5
        }),
        // Error bar bottom caps
        Plot.tickY(histogramData, {
          x: "region",
          y: d => Math.max(0, d.mean_distance - d.std_distance),
          stroke: "black",
          strokeWidth: 1.5
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
    if (value > 2) return "Strong balancing selection";
    if (value < -2) return "Strong purifying selection or expansion";
    if (value > 0) return "Possible balancing selection";
    if (value < 0) return "Possible purifying selection or expansion";
    return "Neutral evolution";
  }
  
  // Use shared genotypes and thresholds from store
  
  onMount(() => {
    updateVisualizations();
  });
</script>

<div class="container px-5">
  <div class="grid grid-cols-1 items-center my-5">
    <div class="col-start-1 col-span-2">
      <h1 class="text-5xl">HCV Genomic Diversity Analysis</h1>
      <p>Analysis of nucleotide diversity, segregating sites, Tajima's D, TN93 distances, and GC content across different HCV gene regions. This analysis helps understand evolutionary patterns and selective pressures in different genomic regions.</p>

      <!-- Global Selection Controls (persist across all HCV pages) -->
      <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center bg-indigo-50 border border-indigo-200 p-4 rounded-lg mt-4">
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
        <a href="/hcv/comparison" class="px-3 py-1.5 sm:px-4 sm:py-2 text-sm sm:text-base bg-teal-600 text-white rounded-md hover:bg-teal-700 transition-colors">
          Genotype Comparison
        </a>
        <a href="/hcv/fel" class="px-3 py-1.5 sm:px-4 sm:py-2 text-sm sm:text-base bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors">
          FEL Analysis
        </a>
        <a href="/hcv/meme" class="px-3 py-1.5 sm:px-4 sm:py-2 text-sm sm:text-base bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors">
          MEME Analysis
        </a>
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
              <div class="text-sm text-gray-600">Mean Nucleotide Diversity<Tooltip text="Average pairwise differences per nucleotide site (π). Higher values indicate more genetic variation within the population." /></div>
              <div class="text-2xl font-bold">{summaryStats.diversity_statistics.mean_nucleotide_diversity.toFixed(4)}</div>
            </div>
            <div class="bg-gray-50 p-3 rounded">
              <div class="text-sm text-gray-600">Mean Segregating Sites<Tooltip text="Number of polymorphic positions in the alignment. Higher values indicate more variable sites." /></div>
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
          <h2 class="text-2xl font-semibold mb-4">Nucleotide Diversity (π) by Region<Tooltip text="Pi (π) measures the average number of nucleotide differences per site between sequences. Higher values indicate greater genetic diversity." /></h2>
          <RenderPlot options={$nucleotideDiversityOptions} />
          <p class="text-sm text-gray-600 mt-2">
            Nucleotide diversity (π) measures the average number of nucleotide differences per site between sequences.
            Higher values indicate greater genetic diversity. Red dashed line shows the mean across all regions.
          </p>
          <div class="flex gap-4 mt-2 text-sm">
            <span class="flex items-center gap-1"><span class="inline-block w-4 h-4 rounded" style="background-color: #f97316;"></span> Above mean diversity</span>
            <span class="flex items-center gap-1"><span class="inline-block w-4 h-4 rounded" style="background-color: #3b82f6;"></span> At or below mean diversity</span>
          </div>
        </div>
        
        <!-- Tajima's D Plot -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Tajima's D Statistics<Tooltip text="Statistical test for neutrality. Negative values suggest purifying selection or population expansion; positive values suggest balancing selection. Values outside ±2 are typically significant." /></h2>
          <RenderPlot options={$tajimaDOptions} />
          <p class="text-sm text-gray-600 mt-2">
            Tajima's D tests for neutrality. Values &gt; 0 suggest balancing selection, values &lt; 0 suggest purifying selection or population expansion.
            Orange dashed lines mark significance thresholds (±2).
          </p>
          <div class="flex gap-4 mt-2 text-sm flex-wrap">
            <span class="flex items-center gap-1"><span class="inline-block w-4 h-4 rounded" style="background-color: #3b82f6;"></span> Positive (D &gt; 0): possible balancing selection</span>
            <span class="flex items-center gap-1"><span class="inline-block w-4 h-4 rounded" style="background-color: #94a3b8;"></span> Negative (-2 &lt; D ≤ 0): weak/no selection</span>
            <span class="flex items-center gap-1"><span class="inline-block w-4 h-4 rounded" style="background-color: #ea580c;"></span> Significant (|D| &gt; 2): strong selection signal</span>
          </div>
        </div>
        
        <!-- TN93 Distance Plot -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">TN93 Distance Statistics<Tooltip text="Tamura-Nei 93 genetic distance accounts for different transition/transversion rates and base frequencies. Used as the distance metric for HIV-TRACE clustering." /></h2>
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
        
        <!-- Region Classification Reference -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Region Classification Reference<Tooltip text="Based on manuscript findings, regions are classified by their suitability for epidemiological clustering analysis." /></h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-green-50 p-3 rounded-lg border border-green-200">
              <h3 class="font-medium text-green-700 mb-2">Optimal Regions (Recommended)</h3>
              <p class="text-sm text-green-600 mb-2">Higher diversity, balanced cluster sizes (R1/R2 ratios 2.0-2.7)</p>
              <div class="flex flex-wrap gap-2">
                {#each OPTIMAL_REGIONS as region}
                  <span class="px-2 py-1 bg-green-100 text-green-700 rounded text-sm font-mono uppercase">{region}</span>
                {/each}
              </div>
            </div>
            <div class="bg-orange-50 p-3 rounded-lg border border-orange-200">
              <h3 class="font-medium text-orange-700 mb-2">Conserved Regions (Limited)</h3>
              <p class="text-sm text-orange-600 mb-2">Lower diversity, dominant cluster problem (R1/R2 ratios 13.7-19.8)</p>
              <div class="flex flex-wrap gap-2">
                {#each POOR_REGIONS as region}
                  <span class="px-2 py-1 bg-orange-100 text-orange-700 rounded text-sm font-mono uppercase">{region}</span>
                {/each}
              </div>
            </div>
          </div>
        </div>

        <!-- Detailed Data Table -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Detailed Diversity Metrics</h2>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase">Region</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase">Type</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase">Sequences</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase">Length</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase">Nuc. Diversity</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase">Seg. Sites</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase">Tajima's D</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase">GC %</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase">Mean TN93</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                {#each currentData as row}
                  <tr class="hover:bg-gray-50">
                    <td class="px-3 py-2 text-sm font-medium text-gray-700">{row.region?.toUpperCase() || 'N/A'}</td>
                    <td class="px-3 py-2 text-sm">
                      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium {row.classDisplay?.bgColor} {row.classDisplay?.color} border {row.classDisplay?.borderColor}">
                        {row.classDisplay?.label}
                      </span>
                    </td>
                    <td class="px-3 py-2 text-sm text-gray-700">{row.sequence_count || 'N/A'}</td>
                    <td class="px-3 py-2 text-sm text-gray-700">{row.sequence_length || 'N/A'}</td>
                    <td class="px-3 py-2 text-sm text-gray-700 font-mono">{typeof row.nucleotide_diversity === 'number' ? row.nucleotide_diversity.toFixed(5) : 'N/A'}</td>
                    <td class="px-3 py-2 text-sm text-gray-700">{row.segregating_sites || 'N/A'}</td>
                    <td class="px-3 py-2 text-sm text-gray-700 font-mono">{typeof row.tajima_d === 'number' ? row.tajima_d.toFixed(3) : 'N/A'}</td>
                    <td class="px-3 py-2 text-sm text-gray-700">{typeof row.mean_gc_content === 'number' ? row.mean_gc_content.toFixed(2) : 'N/A'}</td>
                    <td class="px-3 py-2 text-sm text-gray-700 font-mono">{row.distance_statistics?.mean_distance ? row.distance_statistics.mean_distance.toFixed(5) : 'N/A'}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {:else}
        <div class="bg-amber-50 border border-amber-200 p-6 rounded-lg mt-6 text-center">
          <p class="text-amber-700 font-medium text-lg">No Diversity Data Available</p>
          <p class="text-amber-600 text-sm mt-2">
            No genomic diversity results found for genotype <strong>{$selectedGenotype}</strong> at threshold <strong>{$selectedThreshold}</strong>.
          </p>
          <p class="text-amber-500 text-sm mt-1">
            Try selecting a different genotype or consensus threshold combination.
          </p>
        </div>
      {/if}
    </div>
  </div>
</div>