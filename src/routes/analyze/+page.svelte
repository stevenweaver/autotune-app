<script>
	import { onMount, beforeUpdate } from 'svelte';
	import { Runtime, Inspector } from '@observablehq/runtime';
	import * as Plot from '@observablehq/plot';
	import * as d3 from 'd3';
	import * as R from 'ramda';
	import RenderPlot from '../../Plot.svelte';

	import chiapasFile from '../../data/chiapas_seguro_report.tsv?raw';

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

	function initTN93() {
		return new Promise((resolve, reject) => {
			const checkAioli = setInterval(async () => {
				if (window.Aioli) {
					clearInterval(checkAioli);
					CLI = await new window.Aioli(['tn93/1.0.11']);
					resolve();
				}
			}, 500);
		});
	}

	function initPyodide() {
		return new Promise((resolve, reject) => {
			const checkPyodide = setInterval(async () => {
				if (window.loadPyodide) {
					clearInterval(checkPyodide);
					pyodide = await window.loadPyodide({
						stdout: (text) => {
							hivclusteringOutput += text + '\n';
						}
					});
					await pyodide.loadPackage('micropip');
					const micropip = pyodide.pyimport('micropip');
					await micropip.install('hivclustering');
					resolve();
				}
			}, 500);
		});
	}

	onMount(async () => {
		await Promise.all([initTN93(), initPyodide()]);
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
	}

	function logFASTA(text) {
		console.log(text);
	}

	function renderPlotsFromFASTA() {
		if (alignmentFiles.length == 0) {
			return;
		}

		if (pyodide === undefined || CLI === undefined) {
			setTimeout(() => {
				renderPlotsFromFASTA();
			}, 250);
		}

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
	} else {
		generatePlots(chiapasFile);
	}
</script>

<svelte:head>
	<script src="https://biowasm.com/cdn/v3/aioli.js"></script>
	<script src="https://cdn.jsdelivr.net/pyodide/v0.23.4/full/pyodide.js"></script>
</svelte:head>

<div class="container pt-3">
	<h2>Analyze your own Results</h2>

	<h5 class="pt-3">Upload a multiple sequence alignment:</h5>
	<input
		class="pt-2"
		id="alignment-file"
		bind:files={alignmentFiles}
		on:change={renderPlotsFromFASTA}
		type="file"
	/>

	<h5 class="pt-3">Upload a threshold file:</h5>
	<input class="pt-2" id="threshold-file" bind:files={thresholdFiles} type="file" accept="text/*" />

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
					./tn93 -t 0.03 pol.fasta > pairwise_distances.tn93.csv hivnetworkcsv -i
					pairwise_distances.tn93.csv -f plain -A 0 > autotune_report.tsv
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
</style>
