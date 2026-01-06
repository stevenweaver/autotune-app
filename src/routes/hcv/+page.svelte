<script>
  import SvelteTable from 'svelte-table';
	import { onMount, beforeUpdate } from 'svelte';
  import { writable } from 'svelte/store';
	import * as R from 'ramda';
	import * as d3 from 'd3';

	import * as Plot from '@observablehq/plot';
	import RenderPlot from '../../Plot.svelte';
  import Tooltip from '$lib/Tooltip.svelte';
  import NetworkViewer from '$lib/NetworkViewer.svelte';
  import { selectedGenotype, selectedThreshold, genotypes, thresholds, selectedNetworkRegion } from '$lib/hcvStore.js';
  import {
    getThresholdSource,
    getThresholdSourceDisplay,
    getRegionClassification,
    getClassificationDisplay
  } from '$lib/regionClassification.js';

  import allThresholds from '../../data/hcv/all_thresholds.json';
  import networkCongruence from '../../data/hcv/autotune/network_congruence_analysis.json';

  //"filename": "results/1a_0.01_core.threshold.txt",
  // From the filename, extract the genotype, consensus threshold, and gene region and add to each object

  R.forEach(d => {
    d.genotype = d.filename.split('_')[0].split('/')[1]
    d.consensus = d.filename.split('_')[1]
    d.gene = d.filename.split('_')[2].split('.')[0]
    d.threshold = parseFloat(d.threshold);
  }, allThresholds);

	let thresholdOptions;
	let selectedPercentThresholds;

	let thresholdPlotOptions = writable({});
	let clusterPlotOptions = writable({});
	let ratioPlotOptions = writable({});
	let singletonsPlotOptions = writable({});


  // twenty percent only
  let plotData = [];

  let isLoading = writable(false);
  let selectedPoint = writable(null);

  // Network viewer modal state
  let showNetworkModal = false;

  function openNetworkViewer(row) {
    if (!row.gene) return;
    selectedNetworkRegion.set({
      gene: row.gene,
      genotype: $selectedGenotype,
      threshold: $selectedThreshold
    });
    showNetworkModal = true;
  }

  function closeNetworkViewer() {
    showNetworkModal = false;
    selectedNetworkRegion.set(null);
  }

  // Get the network congruence key for the current selection
$: congruenceKey = `${$selectedGenotype}_${$selectedThreshold}`;
$: currentCongruence = networkCongruence[congruenceKey] || {};
$: networkStats = currentCongruence.network_statistics || {};
$: handpickedThresholds = currentCongruence.autotune_thresholds || {};

// Build plotData from handpicked thresholds when available, falling back to allThresholds
$: plotData = (() => {
  // If we have handpicked thresholds, use those as the primary source
  if (Object.keys(handpickedThresholds).length > 0) {
    return Object.entries(handpickedThresholds)
      .filter(([gene]) => gene !== 'ns5a-ns5b-ns3') // Exclude compound regions
      .map(([gene, threshold]) => {
        const stats = networkStats[gene] || {};
        const thresholdValue = parseFloat(threshold);
        const thresholdSource = getThresholdSource(thresholdValue);
        const sourceDisplay = getThresholdSourceDisplay(thresholdSource);

        // Find matching score from allThresholds
        const matchingEntry = allThresholds.find(
          d => d.gene === gene && d.genotype === $selectedGenotype && d.consensus === $selectedThreshold
        );

        return {
          gene,
          genotype: $selectedGenotype,
          consensus: $selectedThreshold,
          threshold: thresholdValue,
          score: matchingEntry?.score || null,
          // Network statistics
          clusters: stats.total_clusters || null,
          singletons: stats.singleton_sequences || null,
          networkedPct: stats.network_proportion ? (stats.network_proportion * 100).toFixed(1) : null,
          totalSequences: stats.total_sequences_analyzed || null,
          // Threshold source
          thresholdSource,
          sourceDisplay
        };
      });
  }

  // Fallback to allThresholds if no handpicked thresholds available
  return allThresholds
    .filter(d => d.consensus === $selectedThreshold && d.genotype == $selectedGenotype)
    .map(d => {
      const stats = networkStats[d.gene] || {};
      const thresholdSource = getThresholdSource(d.threshold);
      const sourceDisplay = getThresholdSourceDisplay(thresholdSource);

      return {
        ...d,
        clusters: stats.total_clusters || null,
        singletons: stats.singleton_sequences || null,
        networkedPct: stats.network_proportion ? (stats.network_proportion * 100).toFixed(1) : null,
        totalSequences: stats.total_sequences_analyzed || null,
        thresholdSource,
        sourceDisplay
      };
    });
})();

  $: reportData = writable([]);

  $: if (reportData) {
    generatePlots($reportData);  // Ensure you are referencing the store with a `$` if it's a writable store
  }


  $: selectedPercentThresholds = {
    grid: true,
    inset: 10,
    width: 900,
    height: 400,
    marginBottom: 80,
    marginLeft: 80,
    marginRight: 100,
    x: { 
      nice: true,
      tickRotate: -45,
      tickPadding: 10,
      label: "Gene Region"
    },
    y: {
      label: "Best Threshold"
    },
    marks: [
      Plot.frame(),
      Plot.dot(plotData, Plot.pointer({
        x: "gene", 
        y: "threshold", 
        fill: "steelblue", 
        r: 8,
        stroke: "white",
        strokeWidth: 2,
        title: (d) => `${d.gene}\nThreshold: ${d.threshold}\nScore: ${d.score}\nGenotype: ${d.genotype}\nConsensus: ${d.consensus}`
      })),
      Plot.dot(plotData, { 
        x: 'gene', 
        y: 'threshold', 
        fill: (d) => d.score, 
        r: 6,
        stroke: "white",
        strokeWidth: 1,
        title: (d) => `${d.gene}\nThreshold: ${d.threshold}\nScore: ${d.score}\nGenotype: ${d.genotype}\nConsensus: ${d.consensus}`
      })
    ],
    color: {
      legend: true,
      label: 'AUTO-TUNE Score',
      scheme: 'viridis',
      type: 'sqrt',
      domain: [1.0, 2.0]
    }
  }

  let eventListener = async (event) => {
      let plot = event.target;
      // Guard against clicking on empty space
      if (!plot.value) return;
      let genotype = plot.value.genotype;
      let consensus = plot.value.consensus;
      let gene = plot.value.gene;
      if (!genotype || !consensus || !gene) return;
      let filename = `${genotype}_${consensus}_${gene}.aligned.report`;
      
      // Set loading state and selected point
      isLoading.set(true);
      selectedPoint.set({ genotype, consensus, gene });
      
      try {
        // Load individual TSV file and parse it
        const response = await fetch(`/src/data/hcv/autotune/${genotype}_${consensus}_${gene}.aligned.report.tsv`);
        if (response.ok) {
          const tsvText = await response.text();
          const lines = tsvText.trim().split('\n');
          const headers = lines[0].split('\t');
          
          const data = lines.slice(1).map(line => {
            const values = line.split('\t');
            const obj = {};
            headers.forEach((header, index) => {
              const value = values[index];
              // Convert numeric columns to numbers
              if (['Threshold', 'Score', 'Clusters', 'LargestCluster', 'SecondLargestCluster', 'Singletons', 'Nodes', 'Edges'].includes(header)) {
                obj[header] = value ? parseFloat(value) : null;
              } else {
                obj[header] = value;
              }
            });
            return obj;
          });
          
          reportData.set(data);
        } else {
          console.error('Failed to load report data for', filename);
          reportData.set([]);
        }
      } catch (error) {
        console.error('Error loading report data:', error);
        reportData.set([]);
      } finally {
        isLoading.set(false);
      }
    }

	onMount(async () => {
      // Load default report data
      try {
        const response = await fetch('/src/data/hcv/autotune/1a_0.2_ns5a.aligned.report.tsv');
        if (response.ok) {
          const tsvText = await response.text();
          const lines = tsvText.trim().split('\n');
          const headers = lines[0].split('\t');
          
          const data = lines.slice(1).map(line => {
            const values = line.split('\t');
            const obj = {};
            headers.forEach((header, index) => {
              const value = values[index];
              // Convert numeric columns to numbers
              if (['Threshold', 'Score', 'Clusters', 'LargestCluster', 'SecondLargestCluster', 'Singletons', 'Nodes', 'Edges'].includes(header)) {
                obj[header] = value ? parseFloat(value) : null;
              } else {
                obj[header] = value;
              }
            });
            return obj;
          });
          
          reportData.set(data);
        }
      } catch (error) {
        console.error('Error loading default report data:', error);
      }

      // generatePlots(reportData);

		// Removed the overwhelming large faceted plot for better UX


	});

	function generateThresholdPlot(totalReport) {
		// Filter data to only include thresholds <= 0.05
		let filteredReport = totalReport.filter(d => d.Threshold <= 0.05);
		
		let thresholdPlotOptions = {
			grid: true,
			inset: 10,
			width: 350,
			height: 300,
			marginTop: 20,
			marginBottom: 40,
			marginLeft: 60,
			marginRight: 40,
			x: {
				nice: true,
				label: "Best Threshold",
				domain: [0, 0.05]
			},
			y: {
				domain: [0, 2],
				transform: (y) => R.max(y, 0),
				label: "AUTO-TUNE Score"
			},
			marks: [
				Plot.frame(),
				Plot.dot(filteredReport, { 
					x: 'Threshold', 
					y: 'Score', 
					fill: (d) => d.Score, 
					r: 4,
					stroke: "white",
					strokeWidth: 0.5,
					title: (d) => `Threshold: ${d.Threshold}\nScore: ${d.Score}\nClusters: ${d.Clusters}`
				}),
				Plot.line(filteredReport, {
					x: 'Threshold', 
					y: 'Score', 
					stroke: "steelblue",
					strokeWidth: 1,
					strokeOpacity: 0.5
				})
			],
			color: {
				legend: false,
				scheme: 'viridis',
				type: 'sqrt',
				domain: [1.0, 2.0]
			}
		};

		return thresholdPlotOptions;
	}

	function generateClusterPlot(totalReport) {
		// Filter data to only include thresholds <= 0.05
		let filteredReport = totalReport.filter(d => d.Threshold <= 0.05);
		
		let clusterPlotOptions = {
			grid: true,
			inset: 10,
			width: 350,
			height: 300,
			marginTop: 20,
			marginBottom: 40,
			marginLeft: 60,
			marginRight: 40,
			x: {
				nice: true,
				label: "Best Threshold",
				domain: [0, 0.05]
			},
			y: {
				label: "Number of Clusters"
			},
			marks: [
				Plot.frame(),
				Plot.dot(filteredReport, { 
					x: 'Threshold', 
					y: 'Clusters', 
					fill: (d) => d.Score, 
					r: 4,
					stroke: "white",
					strokeWidth: 0.5,
					title: (d) => `Threshold: ${d.Threshold}\nClusters: ${d.Clusters}\nScore: ${d.Score}`
				}),
				Plot.line(filteredReport, {
					x: 'Threshold', 
					y: 'Clusters', 
					stroke: "steelblue",
					strokeWidth: 1,
					strokeOpacity: 0.5
				})
			],
			color: {
				legend: false,
				scheme: 'viridis',
				type: 'sqrt',
				domain: [1.0, 2.0]
			}
		};

		return clusterPlotOptions;
	}

	function generateRatioPlot(totalReport) {
		// Filter data to only include thresholds <= 0.05
		let filteredReport = totalReport.filter(d => d.Threshold <= 0.05);
		
		let ratioPlotOptions = {
			grid: true,
			inset: 10,
			width: 350,
			height: 300,
			marginTop: 20,
			marginBottom: 40,
			marginLeft: 60,
			marginRight: 40,
			x: {
				nice: true,
				label: "Best Threshold",
				domain: [0, 0.05]
			},
			y: {
				label: "Cluster Size Ratio (R1/R2)"
			},
			marks: [
				Plot.frame(),
				Plot.dot(filteredReport, { 
					x: 'Threshold', 
					y: 'R1_2', 
					fill: (d) => d.Score, 
					r: 4,
					stroke: "white",
					strokeWidth: 0.5,
					title: (d) => `Threshold: ${d.Threshold}\nRatio: ${d.R1_2?.toFixed(2)}\nScore: ${d.Score}`
				}),
				Plot.line(filteredReport, {
					x: 'Threshold', 
					y: 'R1_2', 
					stroke: "steelblue",
					strokeWidth: 1,
					strokeOpacity: 0.5
				})
			],
			color: {
				legend: false,
				scheme: 'viridis',
				type: 'sqrt',
				domain: [1.0, 2.0]
			}
		};

		return ratioPlotOptions;
	}

	function generateSingletonsPlot(totalReport) {
		// Filter data to only include thresholds <= 0.05
		let filteredReport = totalReport.filter(d => d.Threshold <= 0.05);
		
		let singletonsPlotOptions = {
			grid: true,
			inset: 10,
			width: 350,
			height: 300,
			marginTop: 20,
			marginBottom: 40,
			marginLeft: 60,
			marginRight: 40,
			x: {
				nice: true,
				label: "Best Threshold",
				domain: [0, 0.05]
			},
			y: {
				label: "Number of Singletons"
			},
			marks: [
				Plot.frame(),
				Plot.dot(filteredReport, { 
					x: 'Threshold', 
					y: 'Singletons', 
					fill: (d) => d.Score, 
					r: 4,
					stroke: "white",
					strokeWidth: 0.5,
					title: (d) => `Threshold: ${d.Threshold}\nSingletons: ${d.Singletons}\nScore: ${d.Score}`
				}),
				Plot.line(filteredReport, {
					x: 'Threshold', 
					y: 'Singletons', 
					stroke: "steelblue",
					strokeWidth: 1,
					strokeOpacity: 0.5
				})
			],
			color: {
				legend: false,
				scheme: 'viridis',
				type: 'sqrt',
				domain: [1.0, 2.0]
			}
		};

		return singletonsPlotOptions;
	}


	function generatePlots(data) {

     // Validate if the input is a string and a valid number format
    const isValidNumberString = R.both(
      R.is(String),
      R.pipe(R.trim, R.test(/^-?\d+(\.\d+)?$/))
    );

    // Function to safely parse floats, returns null if conversion fails
    const safeParseFloat = R.ifElse(
      isValidNumberString,
      parseFloat,
      R.always(null) // Return null if not a valid number or not a string
    );

    // Function to convert all string values in an object to floats
    const convertToFloats = R.map(parseFloat);

    // Apply the function to each object in the array
    let content = R.map(convertToFloats, data);

    // map the content to include ratios
    let mappedContent = R.map((d) => {
      // Ensure the denominator is not zero to avoid division by zero errors
      d['R1_2'] = d.SecondLargestCluster ? d.LargestCluster / d.SecondLargestCluster : 0;
      d['Degrees'] = d.Nodes ? d.Edges / d.Nodes : 0;
      return d;
    }, content);

		thresholdPlotOptions.set(generateThresholdPlot(mappedContent));
		clusterPlotOptions.set(generateClusterPlot(mappedContent));
		ratioPlotOptions.set(generateRatioPlot(mappedContent));
		singletonsPlotOptions.set(generateSingletonsPlot(mappedContent));
	}

</script>

<div class="container px-5">
  <div class="grid grid-cols-1 items-center my-5">
    <div class="col-start-1 col-span-2">
      <h1 class="text-5xl">CIENI HCV Report</h1>
      <p>This page visualizes data related to Hepatitis C Virus (HCV) genetic variations, focusing on consensus thresholds and genes and their implications for inferring clustering thresholds. Below, you can interact with the data by selecting different points on the plot and viewing detailed plots that describe the components that contributed to their AUTO-TUNE scores.</p>

      <!-- Global Selection Controls (persist across all HCV pages) -->
      <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center bg-indigo-50 border border-indigo-200 p-4 rounded-lg mt-4">
        <div>
          <label for="genotype-select" class="block text-sm font-medium text-gray-700 mb-1">Select Genotype</label>
          <select id="genotype-select" bind:value={$selectedGenotype} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            {#each genotypes as genotype}
              <option value={genotype}>{genotype}</option>
            {/each}
          </select>
        </div>

        <div>
          <label for="threshold-select" class="block text-sm font-medium text-gray-700 mb-1">Select Consensus Threshold</label>
          <select id="threshold-select" bind:value={$selectedThreshold} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            {#each thresholds as threshold}
              <option value={threshold}>{threshold}</option>
            {/each}
          </select>
        </div>

        {#if $selectedPoint}
          <div class="bg-white p-3 rounded border">
            <div class="text-sm font-medium text-gray-700">Selected Point:</div>
            <div class="text-sm text-gray-600">{$selectedPoint.genotype} - {$selectedPoint.consensus} - {$selectedPoint.gene}</div>
          </div>
        {/if}
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

      <div class="pt-6">
        <h2 class="text-2xl font-semibold mb-4">Gene Region Overview</h2>
        <div class="bg-white p-4 rounded-lg shadow">
          <RenderPlot options={selectedPercentThresholds} eventL={eventListener} />
          <p class="text-sm text-gray-600 mt-2">Click on any point to view detailed analysis below. This plot shows the distribution of AUTO-TUNE scores across different gene regions for the selected genotype and consensus threshold.</p>
        </div>
      </div>

      <div class="pt-6">
        <h2 class="text-2xl font-semibold mb-4">Detailed Analysis</h2>
        {#if $isLoading}
          <div class="bg-gray-50 p-8 rounded-lg text-center">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            <p class="mt-2 text-gray-600">Loading detailed analysis...</p>
          </div>
        {:else if $selectedPoint}
          <div class="bg-white p-4 rounded-lg shadow">
            <h3 class="text-lg font-medium mb-4">Analysis for {$selectedPoint.genotype} - {$selectedPoint.consensus} - {$selectedPoint.gene}</h3>
            <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-6">
              <div class="bg-gray-50 p-4 rounded">
                <h4 class="text-md font-medium mb-2">AUTO-TUNE Score<Tooltip text="A composite score (0-2.0) that evaluates clustering threshold performance based on network structure metrics. Higher scores indicate better threshold choices. Scores of 0 indicate analysis errors." /></h4>
                <RenderPlot options={$thresholdPlotOptions} />
                <p class="text-sm text-gray-600 mt-2">AUTO-TUNE scores across candidate thresholds. Higher scores indicate better clustering performance.</p>
              </div>

              <div class="bg-gray-50 p-4 rounded">
                <h4 class="text-md font-medium mb-2">Cluster Count<Tooltip text="The number of distinct transmission clusters formed at each threshold. Too few clusters may miss transmission chains; too many may split related sequences." /></h4>
                <RenderPlot options={$clusterPlotOptions} />
                <p class="text-sm text-gray-600 mt-2">Number of clusters formed at different thresholds. Optimal thresholds balance cluster count with biological relevance.</p>
              </div>

              <div class="bg-gray-50 p-4 rounded">
                <h4 class="text-md font-medium mb-2">Cluster Size Ratio<Tooltip text="Ratio of the largest cluster to the second largest. High ratios indicate one dominant cluster; more even ratios suggest diverse clustering patterns." /></h4>
                <RenderPlot options={$ratioPlotOptions} />
                <p class="text-sm text-gray-600 mt-2">Ratio of largest to second largest cluster. Higher ratios may indicate dominant cluster structures.</p>
              </div>

              <div class="bg-gray-50 p-4 rounded">
                <h4 class="text-md font-medium mb-2">Singletons<Tooltip text="Sequences that don't cluster with any other sequences at the given threshold. High singleton counts may indicate the threshold is too stringent." /></h4>
                <RenderPlot options={$singletonsPlotOptions} />
                <p class="text-sm text-gray-600 mt-2">Number of singleton sequences at different thresholds. Singletons are sequences that don't cluster with others.</p>
              </div>
            </div>
          </div>
        {:else}
          <div class="bg-gray-50 p-8 rounded-lg text-center">
            <p class="text-gray-600">Click on a point in the overview plot above to see detailed analysis</p>
          </div>
        {/if}
      </div>

      <!-- Selected Candidate Thresholds Table -->
      <div class="pt-6">
        <h2 class="text-2xl font-semibold mb-4">Selected Candidate Thresholds<Tooltip text="Handpicked thresholds based on the manuscript's 3-criteria framework: (1) optimal cluster count, (2) low singleton prevalence, and (3) balanced cluster sizes." /></h2>
        <div class="bg-white p-4 rounded-lg shadow overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Gene Region</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Recommended</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Selected Threshold</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Source</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">AUTO-TUNE Score</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Clusters</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Singletons</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">% Networked</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Network</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              {#each plotData.filter(item => item.threshold !== undefined) as row}
                {@const regionClass = getRegionClassification(row.gene)}
                {@const classDisplay = getClassificationDisplay(regionClass)}
                <tr class="hover:bg-indigo-50 cursor-pointer transition-colors" on:click={() => openNetworkViewer(row)}>
                  <td class="px-3 py-2 text-sm text-gray-700 font-medium">{row.gene?.toUpperCase() || 'N/A'}</td>
                  <td class="px-3 py-2 text-sm">
                    {#if regionClass === 'optimal'}
                      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700 border border-green-300">
                        Yes
                      </span>
                    {:else}
                      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600 border border-gray-300">
                        No
                      </span>
                    {/if}
                  </td>
                  <td class="px-3 py-2 text-sm text-gray-700 font-mono">{typeof row.threshold === 'number' ? row.threshold.toFixed(5) : 'N/A'}</td>
                  <td class="px-3 py-2 text-sm">
                    <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium {row.sourceDisplay?.bgColor} {row.sourceDisplay?.color} border {row.sourceDisplay?.borderColor}">
                      {row.sourceDisplay?.label || 'Unknown'}
                    </span>
                  </td>
                  <td class="px-3 py-2 text-sm text-gray-700">{typeof row.score === 'number' ? row.score.toFixed(5) : 'N/A'}</td>
                  <td class="px-3 py-2 text-sm text-gray-700">{row.clusters ?? 'N/A'}</td>
                  <td class="px-3 py-2 text-sm text-gray-700">{row.singletons ?? 'N/A'}</td>
                  <td class="px-3 py-2 text-sm text-gray-700">
                    {#if row.networkedPct}
                      <span class="{parseFloat(row.networkedPct) >= 90 ? 'text-green-600' : parseFloat(row.networkedPct) >= 80 ? 'text-yellow-600' : 'text-red-600'}">
                        {row.networkedPct}%
                      </span>
                    {:else}
                      N/A
                    {/if}
                  </td>
                  <td class="px-3 py-2 text-sm">
                    <span class="inline-flex items-center text-indigo-600 hover:text-indigo-800">
                      <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                      </svg>
                      View
                    </span>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
          <p class="text-sm text-gray-600 mt-2">Click on any row to view the interactive network visualization for that gene region.</p>
        </div>
      </div>

      <!-- Selected Region Detail Table -->
      {#if $selectedPoint && $reportData.length > 0}
        <div class="pt-6">
          <h2 class="text-2xl font-semibold mb-4">Threshold Analysis for {$selectedPoint.gene}</h2>
          <div class="bg-white p-4 rounded-lg shadow">
            <SvelteTable 
              columns={[
                { key: 'Threshold', title: 'Threshold', sortable: true, value: (row) => row.Threshold ? parseFloat(row.Threshold).toFixed(5) : 'N/A', sortValue: (row) => row.Threshold ? parseFloat(row.Threshold) : -Infinity, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
                { key: 'Score', title: 'AUTO-TUNE Score', sortable: true, value: (row) => row.Score ? parseFloat(row.Score).toFixed(5) : 'N/A', sortValue: (row) => row.Score ? parseFloat(row.Score) : -Infinity, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
                { key: 'Clusters', title: 'Clusters', sortable: true, value: (row) => row.Clusters || 'N/A', sortValue: (row) => row.Clusters ? parseInt(row.Clusters) : -Infinity, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
                { key: 'LargestCluster', title: 'Largest Cluster', sortable: true, value: (row) => row.LargestCluster || 'N/A', sortValue: (row) => row.LargestCluster ? parseInt(row.LargestCluster) : -Infinity, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
                { key: 'SecondLargestCluster', title: 'Second Largest', sortable: true, value: (row) => row.SecondLargestCluster || 'N/A', sortValue: (row) => row.SecondLargestCluster ? parseInt(row.SecondLargestCluster) : -Infinity, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
                { key: 'R1_2', title: 'Ratio (R1/R2)', sortable: true, value: (row) => row.SecondLargestCluster && row.LargestCluster ? (parseFloat(row.LargestCluster) / parseFloat(row.SecondLargestCluster)).toFixed(2) : 'N/A', sortValue: (row) => row.SecondLargestCluster && row.LargestCluster ? (parseFloat(row.LargestCluster) / parseFloat(row.SecondLargestCluster)) : -Infinity, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
                { key: 'Singletons', title: 'Singletons', sortable: true, value: (row) => row.Singletons || 'N/A', sortValue: (row) => row.Singletons ? parseInt(row.Singletons) : -Infinity, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
                { key: 'Nodes', title: 'Nodes', sortable: true, value: (row) => row.Nodes || 'N/A', sortValue: (row) => row.Nodes ? parseInt(row.Nodes) : -Infinity, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
                { key: 'Edges', title: 'Edges', sortable: true, value: (row) => row.Edges || 'N/A', sortValue: (row) => row.Edges ? parseInt(row.Edges) : -Infinity, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' }
              ]}
              rows={$reportData.filter(d => d.Threshold !== undefined && d.Threshold !== null && parseFloat(d.Threshold) <= 0.05)}
              classNameTable={['min-w-full']}
              classNameThead={['bg-gray-50']}
              classNameTbody={['']}
              classNameRow={['hover:bg-gray-50']}
            />
            <p class="text-sm text-gray-600 mt-2">Detailed analysis data for all candidate thresholds ≤ 0.05 in the selected region. Click column headers to sort.</p>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>

<!-- Network Viewer Modal -->
{#if showNetworkModal && $selectedNetworkRegion}
  <NetworkViewer
    visible={showNetworkModal}
    networkUrl={`/results/${$selectedNetworkRegion.genotype}_${$selectedNetworkRegion.threshold}_${$selectedNetworkRegion.gene}.annotated.json`}
    meta={$selectedNetworkRegion}
    onClose={closeNetworkViewer}
  />
{/if}

<style>
	:global(#data) {
		display: none;
	}
</style>