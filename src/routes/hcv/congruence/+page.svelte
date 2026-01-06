<script>
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import * as Plot from '@observablehq/plot';
  import RenderPlot from '../../../Plot.svelte';
  import SvelteTable from 'svelte-table';
  import Tooltip from '$lib/Tooltip.svelte';
  import { selectedGenotype, selectedThreshold, genotypes, thresholds } from '$lib/hcvStore.js';

  import congruenceData from '../../../data/hcv/autotune/network_congruence_analysis.json';
  import treeComparisonData from '../../../data/hcv/autotune/tree_comparison_analysis.json';

  // ARI data - loaded dynamically from results folder
  let clusterComparisons = {};

  let isLoading = writable(false);

  let alphaPlotOptions = writable({});
  let networkStatsPlotOptions = writable({});
  let pairwiseHeatmapOptions = writable({});
  let rfHeatmapOptions = writable({});
  let ariHeatmapOptions = writable({});
  let clusterSizePlotOptions = writable({});

  let currentData = {};
  let pairwiseData = [];
  let networkStatsData = [];
  let rfData = [];
  let ariData = [];
  let clusterSizeData = [];
  let ariSummary = { mean: 0, min: 0, max: 0, excellent: 0, good: 0, moderate: 0, poor: 0, total: 0 };
  let rfSummary = { mean: 0, min: 0, max: 0, identical: 0, similar: 0, different: 0, total: 0 };
  
  $: combinationKey = `${$selectedGenotype}_${$selectedThreshold}`;
  $: if (congruenceData[combinationKey]) {
    currentData = congruenceData[combinationKey];
    updateVisualizations();
  }
  
  async function updateVisualizations() {
    if (!currentData.krippendorff_alpha_pairwise) {
      console.log("No krippendorff_alpha_pairwise data found in currentData:", currentData);
      return;
    }

    // Load cluster comparisons (ARI data) dynamically
    try {
      const response = await fetch('/results/cluster_comparisons.json');
      if (response.ok) {
        clusterComparisons = await response.json();
      }
    } catch (error) {
      console.warn('Could not load cluster comparisons:', error);
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
    
    // Helper function to load cluster sizes from HIVTrace files
    async function getClusterSizes(region) {
      try {
        const response = await fetch(`/results/${combinationKey}_${region}.hivtrace.json`);
        if (response.ok) {
          const hivtraceData = await response.json();
          const clusterSizes = hivtraceData['Cluster sizes'] || [];
          const sortedSizes = clusterSizes.sort((a, b) => b - a); // Sort descending
          return {
            largest: sortedSizes[0] || 0,
            secondLargest: sortedSizes[1] || 0,
            allSizes: sortedSizes,
            r1r2Ratio: sortedSizes[1] ? (sortedSizes[0] / sortedSizes[1]).toFixed(2) : 'N/A'
          };
        }
      } catch (error) {
        console.warn(`Could not load cluster sizes for ${region}:`, error);
      }
      return { largest: 0, secondLargest: 0, allSizes: [], r1r2Ratio: 'N/A' };
    }
    
    // Prepare network statistics data with cluster sizes, excluding ns5a-ns5b-ns3
    const networkStatsEntries = Object.entries(currentData.network_statistics || {})
      .filter(([region]) => region !== 'ns5a-ns5b-ns3');
    
    networkStatsData = await Promise.all(
      networkStatsEntries.map(async ([region, stats]) => {
        const clusterSizes = await getClusterSizes(region);
        return {
          region,
          total_sequences: stats.total_sequences_analyzed,
          networked_sequences: stats.networked_sequences,
          singleton_sequences: stats.singleton_sequences,
          network_proportion: stats.network_proportion,
          total_clusters: stats.total_clusters,
          edges: stats.edges,
          largest_cluster: clusterSizes.largest,
          second_largest_cluster: clusterSizes.secondLargest,
          r1r2_ratio: clusterSizes.r1r2Ratio,
          all_cluster_sizes: clusterSizes.allSizes
        };
      })
    );

    // Prepare cluster size distribution data
    clusterSizeData = networkStatsData.flatMap(region => {
      return region.all_cluster_sizes.map((size, index) => ({
        region: region.region,
        clusterIndex: index + 1,
        size: size,
        isLargest: index === 0,
        isDominant: region.largest_cluster > 0.5 * region.networked_sequences
      }));
    });

    generateAlphaPlot();
    generateNetworkStatsPlot();
    generatePairwiseHeatmap();
    generateARIHeatmap();
    generateRFHeatmap();
    generateClusterSizePlot();
  }

  function generateClusterSizePlot() {
    if (!networkStatsData || networkStatsData.length === 0) {
      return;
    }

    // Create a stacked bar chart showing cluster sizes per region
    const clusterData = [];
    networkStatsData.forEach(region => {
      if (region.all_cluster_sizes && region.all_cluster_sizes.length > 0) {
        // Take top 5 clusters for each region
        const topClusters = region.all_cluster_sizes.slice(0, 5);
        topClusters.forEach((size, idx) => {
          clusterData.push({
            region: region.region,
            clusterRank: `Cluster ${idx + 1}`,
            size: size,
            isLargest: idx === 0
          });
        });
      }
    });

    clusterSizePlotOptions.set({
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
        label: "Cluster Size (sequences)"
      },
      marks: [
        Plot.frame(),
        Plot.barY(clusterData, Plot.groupX(
          { y: "sum" },
          {
            x: "region",
            y: "size",
            fill: "clusterRank",
            title: d => `${d.region}\n${d.clusterRank}: ${d.size} sequences`
          }
        )),
        Plot.ruleY([0])
      ],
      color: {
        legend: true,
        scheme: "blues",
        domain: ["Cluster 1", "Cluster 2", "Cluster 3", "Cluster 4", "Cluster 5"],
        label: "Cluster Rank"
      }
    });
  }

  function generateARIHeatmap() {
    // Get ARI data from cluster comparisons
    const currentARI = clusterComparisons[combinationKey];
    if (!currentARI || !currentARI.cluster_consistency) {
      console.log("No ARI data available for", combinationKey);
      ariData = [];
      ariSummary = { mean: 0, min: 0, max: 0, excellent: 0, good: 0, moderate: 0, poor: 0, total: 0 };
      return;
    }

    // Prepare ARI pairwise data, excluding compound regions
    ariData = Object.entries(currentARI.cluster_consistency)
      .filter(([comparison]) => !comparison.includes('ns5a-ns5b-ns3') && !comparison.includes('whole'))
      .map(([comparison, ari]) => {
        const [region1, region2] = comparison.split('_vs_');
        return {
          region1,
          region2,
          ari: parseFloat(ari),
          comparison
        };
      });

    // Calculate ARI summary statistics
    const ariValues = ariData.map(d => d.ari);
    if (ariValues.length > 0) {
      ariSummary = {
        mean: ariValues.reduce((a, b) => a + b, 0) / ariValues.length,
        min: Math.min(...ariValues),
        max: Math.max(...ariValues),
        excellent: ariValues.filter(v => v >= 0.9).length,
        good: ariValues.filter(v => v >= 0.7 && v < 0.9).length,
        moderate: ariValues.filter(v => v >= 0.3 && v < 0.7).length,
        poor: ariValues.filter(v => v < 0.3).length,
        total: ariValues.length
      };
    }

    // Get all unique regions
    const regions = [...new Set([
      ...ariData.map(d => d.region1),
      ...ariData.map(d => d.region2)
    ])].sort();

    // Create triangular heatmap data
    const triangularARIData = [];
    regions.forEach((region1, i) => {
      regions.forEach((region2, j) => {
        if (i < j) {
          const comparison = ariData.find(
            d => (d.region1 === region1 && d.region2 === region2) ||
                 (d.region1 === region2 && d.region2 === region1)
          );
          if (comparison) {
            triangularARIData.push({
              region1,
              region2,
              ari: comparison.ari,
              comparison: `${region1}_vs_${region2}`
            });
          }
        }
      });
    });

    ariHeatmapOptions.set({
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
        Plot.cell(triangularARIData, {
          x: "region2",
          y: "region1",
          fill: "ari",
          stroke: "#fff",
          strokeWidth: 0.5,
          title: d => `${d.region1} vs ${d.region2}\nARI: ${d.ari.toFixed(3)}`
        })
      ],
      color: {
        legend: true,
        scheme: "RdYlGn",
        domain: [-0.1, 1.0],
        type: "linear",
        label: "Adjusted Rand Index"
      }
    });
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
        Plot.ruleY([0.8], { stroke: "#f97316", strokeDasharray: "2,2" }),
        Plot.ruleY([0.9], { stroke: "#2563eb", strokeDasharray: "2,2" })
      ],
      color: {
        legend: true,
        scheme: "viridis",
        domain: [0.0, 1.0],
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
        domain: [0.0, 1.0],
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

    // Calculate RF summary statistics
    const rfValues = triangularRFData.map(d => d.normalized_rf);
    if (rfValues.length > 0) {
      rfSummary = {
        mean: rfValues.reduce((a, b) => a + b, 0) / rfValues.length,
        min: Math.min(...rfValues),
        max: Math.max(...rfValues),
        identical: rfValues.filter(v => v < 0.1).length,
        similar: rfValues.filter(v => v >= 0.1 && v < 0.3).length,
        different: rfValues.filter(v => v >= 0.3).length,
        total: rfValues.length
      };
    }

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
  
  // Using shared genotypes and thresholds from store

  onMount(() => {
    updateVisualizations();
  });
</script>

<div class="container px-5">
  <div class="grid grid-cols-1 items-center my-5">
    <div class="col-start-1 col-span-2">
      <h1 class="text-5xl">HCV Network Congruence Analysis</h1>
      <p>Analysis of network agreement across different HCV gene regions using Krippendorff's Alpha reliability measurement. This helps understand how consistent clustering patterns are between different genomic regions.</p>

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
            <span class="font-medium">Global Krippendorff's Alpha:<Tooltip text="A reliability coefficient measuring agreement between clustering assignments across all regions. Values >0.8 indicate good agreement, >0.9 excellent agreement." /></span>
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

      {#if currentData.genotype_consensus}
        <!-- Summary Statistics -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Congruence Summary</h2>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div class="bg-gray-50 p-3 rounded">
              <div class="text-sm text-gray-600">Global Alpha<Tooltip text="Overall agreement across all regions. Values >0.8 = good, >0.9 = excellent." /></div>
              <div class="text-2xl font-bold">{currentData.krippendorff_alpha_global?.toFixed(4) || 'N/A'}</div>
            </div>
            <div class="bg-gray-50 p-3 rounded">
              <div class="text-sm text-gray-600">Mean Pairwise Alpha<Tooltip text="Average agreement between each pair of regions." /></div>
              <div class="text-2xl font-bold">{currentData.pairwise_summary?.mean_pairwise_alpha?.toFixed(4) || 'N/A'}</div>
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
            Purple/dark colors indicate lower agreement values (closer to 0), while green and yellow indicate higher agreement (closer to 1.0).
            Orange dashed line marks 0.8 (good agreement), blue dashed line marks 0.9 (excellent agreement).
          </p>
        </div>
        
        <!-- Network Statistics Plot with Enhanced Singleton Display -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Network Proportion by Region<Tooltip text="Shows the proportion of sequences that form transmission networks. Higher values indicate more sequences clustering together. The manuscript emphasizes E1 (81.7% networked, 38 singletons) and E2 (93.7% networked, 13 singletons)." /></h2>
          <RenderPlot options={$networkStatsPlotOptions} />

          <!-- Enhanced Singleton Summary -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
            {#each networkStatsData.sort((a, b) => b.singleton_sequences - a.singleton_sequences).slice(0, 4) as region}
              <div class="bg-gray-50 p-2 rounded text-sm">
                <div class="font-medium text-gray-700">{region.region.toUpperCase()}</div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Singletons:</span>
                  <span class="font-mono text-red-600">{region.singleton_sequences}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Networked:</span>
                  <span class="font-mono text-green-600">{(region.network_proportion * 100).toFixed(1)}%</span>
                </div>
              </div>
            {/each}
          </div>
          <p class="text-sm text-gray-600 mt-2">
            Proportion of sequences that form networks (non-singletons) in each region. Cards show regions with highest singleton counts.
          </p>
        </div>

        <!-- Cluster Size Distribution Plot -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Cluster Size Distribution<Tooltip text="Shows the size of clusters in each region. Conserved regions tend to have one dominant cluster (the 'dominant cluster problem'), while optimal regions have more balanced cluster sizes (R1/R2 ratios of 2.0-2.7)." /></h2>

          <!-- R1/R2 Ratio Summary -->
          <div class="grid grid-cols-2 md:grid-cols-5 gap-2 mb-4">
            {#each networkStatsData.filter(r => r.r1r2_ratio !== 'N/A').sort((a, b) => parseFloat(a.r1r2_ratio) - parseFloat(b.r1r2_ratio)).slice(0, 5) as region}
              <div class="bg-gray-50 p-2 rounded text-sm text-center">
                <div class="font-medium text-gray-700">{region.region.toUpperCase()}</div>
                <div class="text-lg font-mono {parseFloat(region.r1r2_ratio) <= 3 ? 'text-green-600' : parseFloat(region.r1r2_ratio) <= 10 ? 'text-yellow-600' : 'text-red-600'}">
                  {region.r1r2_ratio}
                </div>
                <div class="text-xs text-gray-500">R1/R2</div>
              </div>
            {/each}
          </div>

          <RenderPlot options={$clusterSizePlotOptions} />
          <p class="text-sm text-gray-600 mt-2">
            Stacked bar chart showing cluster sizes per region. Darker bars represent larger clusters. Regions with balanced cluster sizes (low R1/R2 ratios shown in green) are optimal for epidemiological analysis. High R1/R2 ratios (shown in red) indicate one dominant cluster.
          </p>

          <div class="mt-4 flex flex-wrap gap-4 text-xs text-gray-600">
            <div class="flex items-center gap-2">
              <span class="font-medium">R1/R2 Interpretation:</span>
            </div>
            <div class="flex items-center gap-1">
              <span class="inline-block w-3 h-3 rounded bg-green-500"></span>
              <span>≤3.0: Balanced clustering (optimal)</span>
            </div>
            <div class="flex items-center gap-1">
              <span class="inline-block w-3 h-3 rounded bg-yellow-500"></span>
              <span>3.1-10.0: Moderately unbalanced</span>
            </div>
            <div class="flex items-center gap-1">
              <span class="inline-block w-3 h-3 rounded bg-red-500"></span>
              <span>&gt;10.0: Dominant cluster problem</span>
            </div>
          </div>
        </div>
        
        <!-- Pairwise Heatmap -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Pairwise Region Agreement Heatmap (Krippendorff's Alpha)</h2>
          <RenderPlot options={$pairwiseHeatmapOptions} />
          <p class="text-sm text-gray-600 mt-2">
            Krippendorff's Alpha values for each pair of regions. Darker purple/blue indicates lower agreement, while green/yellow indicates higher agreement.
          </p>
        </div>

        <!-- ARI Heatmap Section -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Adjusted Rand Index (ARI) Heatmap<Tooltip text="ARI measures clustering consistency between regions. Values range from -0.1 to 1.0, where 1.0 indicates perfect agreement. The manuscript reports 69.1% of region pairs showed very poor agreement (ARI < 0.3) for genotype 1a." /></h2>

          {#if ariData.length > 0}
            <!-- ARI Summary Statistics -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div class="bg-gray-50 p-3 rounded">
                <div class="text-sm text-gray-600">Mean ARI</div>
                <div class="text-xl font-bold">{ariSummary.mean.toFixed(3)}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded">
                <div class="text-sm text-gray-600">Range</div>
                <div class="text-xl font-bold">{ariSummary.min.toFixed(2)} - {ariSummary.max.toFixed(2)}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded">
                <div class="text-sm text-gray-600">Total Comparisons</div>
                <div class="text-xl font-bold">{ariSummary.total}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded">
                <div class="text-sm text-gray-600">Poor Agreement (ARI &lt; 0.3)</div>
                <div class="text-xl font-bold text-red-600">
                  {ariSummary.poor} ({ariSummary.total > 0 ? ((ariSummary.poor / ariSummary.total) * 100).toFixed(1) : 0}%)
                </div>
              </div>
            </div>

            <!-- ARI Agreement Distribution -->
            <div class="flex flex-wrap gap-2 mb-4 text-sm">
              <span class="px-2 py-1 bg-green-100 text-green-700 rounded">
                Excellent (≥0.9): {ariSummary.excellent} ({ariSummary.total > 0 ? ((ariSummary.excellent / ariSummary.total) * 100).toFixed(1) : 0}%)
              </span>
              <span class="px-2 py-1 bg-blue-100 text-blue-700 rounded">
                Good (0.7-0.9): {ariSummary.good} ({ariSummary.total > 0 ? ((ariSummary.good / ariSummary.total) * 100).toFixed(1) : 0}%)
              </span>
              <span class="px-2 py-1 bg-yellow-100 text-yellow-700 rounded">
                Moderate (0.3-0.7): {ariSummary.moderate} ({ariSummary.total > 0 ? ((ariSummary.moderate / ariSummary.total) * 100).toFixed(1) : 0}%)
              </span>
              <span class="px-2 py-1 bg-red-100 text-red-700 rounded">
                Poor (&lt;0.3): {ariSummary.poor} ({ariSummary.total > 0 ? ((ariSummary.poor / ariSummary.total) * 100).toFixed(1) : 0}%)
              </span>
            </div>

            <RenderPlot options={$ariHeatmapOptions} />
            <p class="text-sm text-gray-600 mt-2">
              Adjusted Rand Index (ARI) values for each pair of regions. Green indicates high clustering consistency, yellow/red indicates lower consistency. The ARI is a key metric for clustering consistency discussed in the manuscript.
            </p>
          {:else}
            <div class="p-8 bg-gray-50 rounded-lg text-center">
              <p class="text-gray-600">No ARI data available for genotype <strong>{$selectedGenotype}</strong> at threshold <strong>{$selectedThreshold}</strong>.</p>
            </div>
          {/if}
        </div>
        
        <!-- Robinson-Foulds Tree Agreement Heatmap -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Robinson-Foulds Tree Agreement Heatmap<Tooltip text="RF distance measures phylogenetic tree topology differences. Lower values indicate more similar trees. The manuscript reports mean RF distance of 0.763 for genotype 1a (range: 0.288-0.931)." /></h2>
          {#if rfData.length > 0}
            <!-- RF Summary Statistics -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div class="bg-gray-50 p-3 rounded">
                <div class="text-sm text-gray-600">Mean RF Distance</div>
                <div class="text-xl font-bold">{rfSummary.mean.toFixed(3)}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded">
                <div class="text-sm text-gray-600">Min / Max</div>
                <div class="text-xl font-bold">{rfSummary.min.toFixed(3)} / {rfSummary.max.toFixed(3)}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded">
                <div class="text-sm text-gray-600">Total Comparisons</div>
                <div class="text-xl font-bold">{rfSummary.total}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded">
                <div class="text-sm text-gray-600">Different Trees (RF ≥ 0.3)</div>
                <div class="text-xl font-bold text-orange-600">
                  {rfSummary.different} ({rfSummary.total > 0 ? ((rfSummary.different / rfSummary.total) * 100).toFixed(1) : 0}%)
                </div>
              </div>
            </div>

            <!-- RF Tree Similarity Distribution -->
            <div class="flex flex-wrap gap-2 mb-4 text-sm">
              <span class="px-2 py-1 bg-green-100 text-green-700 rounded">
                Nearly Identical (RF &lt; 0.1): {rfSummary.identical} ({rfSummary.total > 0 ? ((rfSummary.identical / rfSummary.total) * 100).toFixed(1) : 0}%)
              </span>
              <span class="px-2 py-1 bg-blue-100 text-blue-700 rounded">
                Similar (0.1-0.3): {rfSummary.similar} ({rfSummary.total > 0 ? ((rfSummary.similar / rfSummary.total) * 100).toFixed(1) : 0}%)
              </span>
              <span class="px-2 py-1 bg-orange-100 text-orange-700 rounded">
                Different (≥0.3): {rfSummary.different} ({rfSummary.total > 0 ? ((rfSummary.different / rfSummary.total) * 100).toFixed(1) : 0}%)
              </span>
            </div>

            <RenderPlot options={$rfHeatmapOptions} />
            <p class="text-sm text-gray-600 mt-2">
              Normalized Robinson-Foulds distance between phylogenetic trees from different genomic regions. Lower values (darker) indicate more similar tree topologies, while higher values (lighter) indicate more different tree structures. This helps identify which genomic regions produce similar phylogenetic relationships.
            </p>
            <p class="text-sm text-gray-500 mt-2 italic">
              Note: This heatmap may include compound regions (e.g., "core-e2-ns5a-ns3") that represent concatenated multi-region alignments, which are not present in the Krippendorff's Alpha analysis above. The Alpha analysis compares network clustering patterns between individual genomic regions, while this analysis compares phylogenetic tree topologies from both single and concatenated region alignments.
            </p>
          {:else}
            <div class="p-8 bg-gray-50 rounded-lg">
              <h3 class="text-lg font-semibold text-gray-700 mb-3">Limited Tree Comparison Data</h3>
              <p class="text-gray-600 mb-3">No cross-region tree comparison data available for genotype <strong>{$selectedGenotype}</strong> at threshold <strong>{$selectedThreshold}</strong>.</p>
              
              <div class="text-sm text-gray-600">
                <p class="font-medium mb-2">Note about Data Coverage:</p>
                <ul class="list-disc list-inside space-y-1 mb-3">
                  <li><strong>Network Analysis:</strong> Multiple regions available per genotype</li>
                  <li><strong>Tree Comparisons:</strong> Some regions may have limited cross-region phylogenetic comparisons</li>
                </ul>

                <p class="text-gray-500">
                  The Robinson-Foulds analysis requires phylogenetic trees from multiple regions.
                  Some genotype/threshold combinations have limited sequence data or insufficient tree generation.
                  Try different genotypes (e.g., 3a or 2b) for more comprehensive coverage.
                </p>
              </div>
            </div>
          {/if}
        </div>
        
        <!-- Network Statistics Table -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Network Statistics by Region</h2>
          <div class="overflow-x-auto">
            <SvelteTable
              columns={[
              { key: 'region', title: 'Region', sortable: true, value: (row) => row.region || 'N/A', headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'total_sequences', title: 'Total Sequences', sortable: true, value: (row) => row.total_sequences || 'N/A', sortValue: (row) => row.total_sequences || 0, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'networked_sequences', title: 'Networked', sortable: true, value: (row) => row.networked_sequences || 'N/A', sortValue: (row) => row.networked_sequences || 0, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'singleton_sequences', title: 'Singletons', sortable: true, value: (row) => row.singleton_sequences || 'N/A', sortValue: (row) => row.singleton_sequences || 0, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'network_proportion', title: 'Network Proportion', sortable: true, value: (row) => typeof row.network_proportion === 'number' ? row.network_proportion.toFixed(3) : 'N/A', sortValue: (row) => row.network_proportion || 0, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'total_clusters', title: 'Clusters', sortable: true, value: (row) => row.total_clusters || 'N/A', sortValue: (row) => row.total_clusters || 0, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'largest_cluster', title: 'Largest Cluster', sortable: true, value: (row) => row.largest_cluster || 'N/A', sortValue: (row) => row.largest_cluster || 0, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'second_largest_cluster', title: 'Second Largest Cluster', sortable: true, value: (row) => row.second_largest_cluster || 'N/A', sortValue: (row) => row.second_largest_cluster || 0, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'edges', title: 'Edges', sortable: true, value: (row) => row.edges || 'N/A', sortValue: (row) => row.edges || 0, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' }
            ]}
            rows={networkStatsData}
            classNameTable={['min-w-full']}
            classNameThead={['bg-gray-50']}
              classNameTbody={['']}
              classNameRow={['hover:bg-gray-50']}
            />
          </div>
          <p class="text-sm text-gray-500 mt-2">
            Note: "Largest Cluster" and "Second Largest Cluster" may show N/A when cluster size data is not available for certain regions or when all sequences form a single connected component.
          </p>
        </div>

        <!-- Pairwise Comparisons Table -->
        <div class="bg-white p-4 rounded-lg shadow mt-6">
          <h2 class="text-2xl font-semibold mb-4">Pairwise Alpha Values</h2>
          <div class="overflow-x-auto">
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
        </div>
      {:else}
        <div class="bg-amber-50 border border-amber-200 p-6 rounded-lg mt-6 text-center">
          <p class="text-amber-700 font-medium text-lg">No Congruence Data Available</p>
          <p class="text-amber-600 text-sm mt-2">
            No network congruence results found for genotype <strong>{$selectedGenotype}</strong> at threshold <strong>{$selectedThreshold}</strong>.
          </p>
          <p class="text-amber-500 text-sm mt-1">
            Try selecting a different genotype or consensus threshold combination.
          </p>
        </div>
      {/if}
    </div>
  </div>
</div>