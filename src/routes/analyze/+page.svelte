<script>
	import { onMount, beforeUpdate } from 'svelte';
	import { Runtime, Inspector } from '@observablehq/runtime';
	import * as Plot from '@observablehq/plot';
	import * as d3 from 'd3';
	import * as R from 'ramda';
	import RenderPlot from '../../Plot.svelte';

	import chiapasFile from '../../data/1a_0.2_ns5a.aligned.report.tsv?raw';
  
	import { init } from 'svelte/internal';

	const PAIRWISE_DIST_FILE_NAME = 'pairwise_distances.tn93.csv';
	const ALIGNMENT_FILE_NAME = 'alignment.fasta';

	let alignmentFiles;
	let thresholdFiles;
	let content;
	let thresholdPlotOptions;
	let clusterPlotOptions;
	let ratioPlotOptions;
	let CLI;
	let pyodide;
	let hivclusteringOutput = '';

	const aioliIsDefined = () => {	
		return new Promise((resolve) => {
			const checkInterval = setInterval(() => {
				if (typeof window !== 'undefined' && window.Aioli) {
					clearInterval(checkInterval);
					resolve();
				}
			}, 500);
		});
	} 

	const pyodideIsDefined = () => {
		new Promise((resolve) => {
		const checkInterval = setInterval(() => {
			if (typeof window !== 'undefined' && window.pyodide) {
				clearInterval(checkInterval);
				resolve();
			}
		}, 500);
	});
	}

	async function initTN93() {
		await aioliIsDefined;
		CLI = await new window.Aioli(['tn93/1.0.11']);
	}

	async function initPyodide() {
		await pyodideIsDefined;
		pyodide = await window.loadPyodide({
			stdout: (text) => {
				hivclusteringOutput += text + '\n';
			}
		});
		await pyodide.loadPackage('micropip');
		const micropip = pyodide.pyimport('micropip');
		await micropip.install('hivclustering');
	}

	onMount(() => {
		generatePlots(chiapasFile);
		initTN93();
		initPyodide();
	});

	function generateThresholdPlot(totalReport) {
		let thresholdPlotOptions = {
			grid: true,
			inset: 5,
			width: 800,
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
			width: 800,
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
			width: 800,
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
		let content = d3.tsvParse(data, d3.autoType);

		// map the content to include ratios
		let mappedContent = R.map((d) => {
			d['R1_2'] = d.LargestCluster / d.SecondLargestCluster;
			d['Degrees'] = d['Edges'] / d['Nodes'];
			return d;
		}, content);

		thresholdPlotOptions = generateThresholdPlot(mappedContent);
		clusterPlotOptions = generateClusterPlot(mappedContent);
		ratioPlotOptions = generateRatioPlot(mappedContent);
		logFASTA('done generating plots');
	}

	function logFASTA(text, clear = false) {
		const log = document.getElementById('upload-status-log');
		if (clear) {
			log.innerHTML = '';
		}

		const time = new Date().toLocaleTimeString();
		log.innerHTML += time + ': ' + text + '<br>';
	}

	function renderPlotsFromFASTA() {
		if (alignmentFiles.length == 0) {
			return;
		}

		logFASTA('starting renderPlotsFromFASTA', true);

		let file = alignmentFiles[0];

		file.text().then(async (fileContent) => {
			// TODO: add logging (through some kind of output ui?)
			logFASTA('writing file to biowasm');
			await CLI.fs.writeFile(ALIGNMENT_FILE_NAME, fileContent);

			logFASTA('running tn93');
			await CLI.exec(`tn93 -o ${PAIRWISE_DIST_FILE_NAME} -t 0.03 ${ALIGNMENT_FILE_NAME}`);

			// write tn93 to pyodide
			logFASTA('writing tn93 to pyodide');
			const outputDistances = await CLI.fs.readFile(PAIRWISE_DIST_FILE_NAME, {
				encoding: 'utf8'
			});
			pyodide.FS.writeFile(PAIRWISE_DIST_FILE_NAME, outputDistances, {
				encoding: 'utf8'
			});

			// run hivclustering on the file
			logFASTA('running hivclustering');
			try {
				// set global variables
				pyodide.globals.set('PAIRWISE_DIST_FILE_NAME', PAIRWISE_DIST_FILE_NAME);
				pyodide.runPython(
					await fetch('./hivclustering_browser.py').then((response) => response.text())
				);
			} catch (PythonError) {
				if (PythonError.message.includes('SystemExit: 0')) {
					logFASTA('hivclustering exited successfully');
				} else {
					logFASTA('Error running hivclustering:');
					logFASTA(PythonError);
					return;
				}
			}

			generatePlots(hivclusteringOutput);
		});
	}

	$: if (thresholdFiles) {
		// Note that `thresholdFiles` is of type `FileList`, not an Array:
		// https://developer.mozilla.org/en-US/docs/Web/API/FileList
		let file = thresholdFiles[0];
		file.text().then((fileContent) => {
			generatePlots(fileContent);
		});
	}
</script>

<svelte:head>
	<script src="https://biowasm.com/cdn/v3/aioli.js"></script>
	<script src="https://cdn.jsdelivr.net/pyodide/v0.23.4/full/pyodide.js"></script>
</svelte:head>

<div class="container pt-3">
	<h2>Analyze your own Results</h2>

  <div class="row">
      <div class="col-md-5">
          <h5 class="pt-3" style="font-size: 1.5em; font-weight: 'bold';">Upload a multiple sequence alignment (beta) 🧪:</h5>
          <input type="file" class="d-none" id="alignment-file" bind:files={alignmentFiles} on:change={renderPlotsFromFASTA}>
          <label for="alignment-file" class="btn btn-warning w-100">Choose file</label>
      </div>
      <div class="col-md-2 d-flex justify-content-center align-items-center">
          <span style="font-size: 2em; font-weight: bold;font-family: 'Fontdiner Swanky';">OR</span>
      </div>
      <div class="col-md-5">
          <h5 class="pt-3" style="font-size: 1.5em; font-weight: 'bold';">Upload an AUTO-TUNE results file :</h5>
          <input type="file" class="d-none" id="threshold-file" bind:files={thresholdFiles} accept="text/*">
          <label for="threshold-file" class="btn btn-primary w-100">Choose file</label>
      </div>
  </div>


	<h5 class="pt-3" style="font-size: 1.5em; font-weight: 'bold';">Plot Generation Console</h5>
	<div id="upload-status-log" />

	<div class="pt-3">
		<h2 class="text-xl">Instructions</h2>
		<div id="summary">
			<p>
				To generate a results file that is compatible with this page, use a multiple sequence
				alignment with the <a href="https://github.com/veg/tn93">tn93</a> fast pairwise distance calculator.
			</p>
			<p>
				Once a pairwise distance file is created, use the <a
					href="https://github.com/veg/hivclustering">hivnetworkcsv</a
				>
				script with the <code>-A</code> keyword argument to generate the tab-separated output compatible
				with this page.
			</p>
			<p class="mt-2">An example workflow is as follows:</p>
			<div class="bg-indigo-100 p-3 rounded">
				<code>
					./tn93 -t 0.03 pol.fasta > pairwise_distances.tn93.csv
        </code>
        <code>
          hivnetworkcsv -i pairwise_distances.tn93.csv -f plain -A 0 > autotune_report.tsv
				</code>
			</div>
			Please see<a
				class="underline text-blue-600 hover:text-blue-800 visited:text-purple-600"
				href="about">the About page</a
			> for documentation on how to interpret the results.
		</div>
	</div>

	<div class="pt-3">
		<h2 class="text-xl">Threshold Score Plot</h2>
		<RenderPlot options={thresholdPlotOptions} />
	</div>

	<div>
		<h2 class="text-xl">Cluster Plot</h2>
		<RenderPlot options={clusterPlotOptions} />
	</div>

	<div>
		<h2 class="text-xl">R1/R2 Plot</h2>
		<RenderPlot options={ratioPlotOptions} />
	</div>
</div>

<style>
	code {
		white-space: pre;
	}

	#upload-status-log {
		width: max(25vw, 200px);
		height: 200px;
		border: 1px solid black;
		border-radius: 2px;
	}
</style>
