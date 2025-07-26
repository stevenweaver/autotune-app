<script>
  import SvelteTable from 'svelte-table';
	import { onMount, beforeUpdate } from 'svelte';
  import { writable } from 'svelte/store';
	import * as R from 'ramda';
	import * as d3 from 'd3';

	import * as Plot from '@observablehq/plot';
	import RenderPlot from '../../Plot.svelte';


  import allThresholds from '../../data/hcv/all_thresholds.json';

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

  let selectedThreshold = writable('0.2');  // Default value as an example
  let selectedGenotype = writable('1a');  // Default value as an example
  let isLoading = writable(false);
  let selectedPoint = writable(null);

  $: plotData = allThresholds.filter(d => d.consensus === $selectedThreshold && d.genotype == $selectedGenotype);

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
      label: "Threshold"
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
      let genotype = plot.value.genotype;
      let consensus = plot.value.consensus;
      let gene = plot.value.gene;
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
				label: "Threshold",
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
				label: "Threshold",
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
				label: "Threshold",
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
				label: "Threshold",
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


      <div class="flex pt-4 space-x-6 items-center bg-gray-50 p-4 rounded-lg">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Select Genotype</label>
          <select bind:value={$selectedGenotype} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            {#each Array.from(new Set(allThresholds.map(d => d.genotype).filter(g => g))) as genotype}
              <option value={genotype}>{genotype}</option>
            {/each}
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Select Consensus Threshold</label>
          <select bind:value={$selectedThreshold} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            {#each Array.from(new Set(allThresholds.map(d => d.consensus).filter(c => c))) as threshold}
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
                <h4 class="text-md font-medium mb-2">Threshold Score Analysis</h4>
                <RenderPlot options={$thresholdPlotOptions} />
                <p class="text-sm text-gray-600 mt-2">AUTO-TUNE scores across candidate thresholds. Higher scores indicate better clustering performance.</p>
              </div>

              <div class="bg-gray-50 p-4 rounded">
                <h4 class="text-md font-medium mb-2">Cluster Count Analysis</h4>
                <RenderPlot options={$clusterPlotOptions} />
                <p class="text-sm text-gray-600 mt-2">Number of clusters formed at different thresholds. Optimal thresholds balance cluster count with biological relevance.</p>
              </div>

              <div class="bg-gray-50 p-4 rounded">
                <h4 class="text-md font-medium mb-2">Cluster Size Ratio</h4>
                <RenderPlot options={$ratioPlotOptions} />
                <p class="text-sm text-gray-600 mt-2">Ratio of largest to second largest cluster. Higher ratios may indicate dominant cluster structures.</p>
              </div>

              <div class="bg-gray-50 p-4 rounded">
                <h4 class="text-md font-medium mb-2">Singletons Analysis</h4>
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

      <!-- Best Candidate Thresholds Table -->
      <div class="pt-6">
        <h2 class="text-2xl font-semibold mb-4">Best Candidate Thresholds</h2>
        <div class="bg-white p-4 rounded-lg shadow">
          <SvelteTable 
            columns={[
              { key: 'gene', title: 'Gene Region', sortable: true, value: (row) => row.gene || 'N/A', headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'threshold', title: 'Best Threshold', sortable: true, value: (row) => typeof row.threshold === 'number' ? row.threshold.toFixed(5) : 'N/A', sortValue: (row) => typeof row.threshold === 'number' ? row.threshold : -Infinity, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'score', title: 'AUTO-TUNE Score', sortable: true, value: (row) => typeof row.score === 'number' ? row.score.toFixed(5) : 'N/A', sortValue: (row) => typeof row.score === 'number' ? row.score : -Infinity, headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'genotype', title: 'Genotype', sortable: true, value: (row) => row.genotype || 'N/A', headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' },
              { key: 'consensus', title: 'Consensus', sortable: true, value: (row) => row.consensus || 'N/A', headerClass: 'px-4 py-2 text-left text-sm font-medium text-gray-700', class: 'px-4 py-2 text-sm text-gray-700' }
            ]}
            rows={plotData.filter(item => item.threshold !== undefined && item.score !== undefined)}
            classNameTable={['min-w-full']}
            classNameThead={['bg-gray-50']}
            classNameTbody={['']}
            classNameRow={['hover:bg-gray-50']}
          />
          <p class="text-sm text-gray-600 mt-2">This table shows the optimal clustering thresholds identified by AUTO-TUNE for each gene region. Click column headers to sort.</p>
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
<style>
	:global(#data) {
		display: none;
	}
</style>