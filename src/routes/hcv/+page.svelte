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


  // twenty percent only
  let plotData = [];

  let selectedThreshold = writable('0.2');  // Default value as an example
  let selectedGenotype = writable('1a');  // Default value as an example

  $: plotData = allThresholds.filter(d => d.consensus === $selectedThreshold && d.genotype == $selectedGenotype);

  $: reportData = writable([]);

  $: if (reportData) {
    generatePlots($reportData);  // Ensure you are referencing the store with a `$` if it's a writable store
  }


  $: selectedPercentThresholds = {
    grid: true,
    inset: 5,
    //width: 800,
    paddingLeft: 250,
    marginBottom: 80,
    x: { 
      nice: true,
      tickRotate: -45,
      tickPadding: 10
    },
    marks: [
      Plot.frame(),
      Plot.dot(plotData, Plot.pointer({x: "gene", y: "threshold", fill: "green", r: 8})),
      Plot.dot(plotData, { x: 'gene', y: 'threshold', fill: (d) => d.score, r: 4 })
    ],
    color: {
      legend: true,
      label: 'AUTO-TUNE score',
      type: 'symlog'
    }
  }

  let eventListener = async (event) => {
      let plot = event.target;
      // 1a_0.2_ns5a.aligned.report
      let genotype = plot.value.genotype;
      let consensus = plot.value.consensus;
      let gene = plot.value.gene;
      let filename = `${genotype}_${consensus}_${gene}.aligned.report`;
      console.log(filename);
      
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
              obj[header] = values[index];
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
              obj[header] = values[index];
            });
            return obj;
          });
          
          reportData.set(data);
        }
      } catch (error) {
        console.error('Error loading default report data:', error);
      }

      // generatePlots(reportData);

			thresholdOptions = {
				grid: true,
				inset: 5,
				width: 800,
				height: 5000,
				paddingLeft: 250,
				facet: {
					data: allThresholds,
					y: 'gene',
					marginRight: 90
				},
				x: {
					nice: true
				},
				y: {
					domain: [-0.5, 2],
					transform: (d) => R.max(-0.5, d)
				},
				marks: [
					Plot.frame(),
					Plot.dot(allThresholds, { x: 'threshold', y: 'score', fill: (d) => d.consensus, r: 4 })
				],
				color: {
					legend: true,
					label: 'Consensus Threshold',
					type: 'symlog'
				}
			};


	});

	function generateThresholdPlot(totalReport) {
		let thresholdPlotOptions = {
			grid: true,
			inset: 5,
			width: 400,
			paddingLeft: 250,
			paddingTop: 250,
			marginTop: 30,
			marginBottom: 50,
			x: {
				nice: true,
				insetLeft: 36,
				tickSize: '10',
				tickPadding: '5'
			},
			y: {
				domain: [0, 2],
				transform: (y) => R.max(y, 0),
				tickSize: '10',
				tickPadding: '5'
			},
			style: { fontSize: '15px' },
			marks: [
				Plot.frame(),
				Plot.dot(totalReport, { x: 'Threshold', y: 'Score', fill: (d) => d.Score, r: 3 })
			],
			color: {
				legend: true,
				label: 'Score',
				type: 'symlog'
			}
		};

		return thresholdPlotOptions;
	}

	function generateClusterPlot(totalReport) {
		let clusterPlotOptions = {
			grid: true,
			inset: 5,
			width: 400,
			//height: 5000,
			paddingLeft: 250,
			x: {
				nice: true
			},
			marks: [
				Plot.frame(),
				Plot.dot(totalReport, { x: 'Threshold', y: 'Clusters', fill: (d) => d.Score, r: 3 })
			],
			color: {
				legend: true,
				label: 'Score',
				type: 'symlog'
			}
		};

		return clusterPlotOptions;
	}

	function generateRatioPlot(totalReport) {
		let ratioPlotOptions = {
			grid: true,
			inset: 5,
			width: 400,
			//height: 5000,
			paddingLeft: 250,
			x: {
				nice: true
			},
			marks: [
				Plot.frame(),
				Plot.dot(totalReport, { x: 'Threshold', y: 'R1_2', fill: (d) => d.Score, r: 3 })
			],
			color: {
				legend: true,
				label: 'Score',
				type: 'symlog'
			}
		};

		return ratioPlotOptions;
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
	}

</script>

<div class="container px-5">
  <div class="grid grid-cols-1 items-center my-5">
    <div class="col-start-1 col-span-2">
      <h1 class="text-5xl">CIENI HCV Report</h1>
      <p>This page visualizes data related to Hepatitis C Virus (HCV) genetic variations, focusing on consensus thresholds and genes and their implications for inferring clustering thresholds. Below, you can interact with the data by selecting different points on the plot and viewing detailed plots that describe the components that contributed to their AUTO-TUNE scores.</p>
      


      <div class="flex pt-4 space-x-4 items-center">
        <div>
          <h3>Select Genotype</h3>
          <select bind:value={$selectedGenotype}>
            {#each Array.from(new Set(allThresholds.map(d => d.genotype))) as genotype}
              <option value={genotype}>{genotype}</option>
            {/each}
          </select>
        </div>

        <div>
          <h3>Select Consensus Threshold</h3>
          <select bind:value={$selectedThreshold}>
            {#each Array.from(new Set(allThresholds.map(d => d.consensus))) as threshold}
              <option value={threshold}>{threshold}</option>
            {/each}
          </select>
        </div>
      </div>


      <div class="pt-2">
        <RenderPlot options={selectedPercentThresholds} eventL={eventListener} />
        <p>Displays the distribution of AUTO-TUNE scores across different gene regions for the selected consensus threshold.</p>
      </div>

      <div class="grid grid-cols-3 gap-4">
        <div class="pt-3">
          <h2 class="text-xl">Threshold Score Plot</h2>
          <RenderPlot options={$thresholdPlotOptions} />
        <p>AUTO-TUNE scores across candidate thresholds for selected point</p>
        </div>

        <div class="pt-3">
          <h2 class="text-xl">Cluster Plot</h2>
          <RenderPlot options={$clusterPlotOptions} />
          <p>Shows the number of clusters under the current consensus threshold setting for selected point.</p>
        </div>

        <div class="pt-3">
          <h2 class="text-xl">R1/R2 Ratio Plot</h2>
          <RenderPlot options={$ratioPlotOptions} />
          <p>Illustrates the ratio of the largest to the second largest clusters across candidate thresholds for selected point.</p>
        </div>
      </div>

      <RenderPlot options={thresholdOptions} />
    </div>
  </div>
</div>
<style>
	:global(#data) {
		display: none;
	}
</style>
