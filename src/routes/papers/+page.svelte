<script>
	import { onMount, beforeUpdate } from 'svelte';
	import * as d3 from 'd3';
	import * as R from 'ramda';
	import { Runtime, Inspector } from '@observablehq/runtime';
	import notebook from '8f6e4b51e21a4d45';
	import { Cite } from '@citation-js/core';
	import '@citation-js/plugin-csl';
	import * as Plot from '@observablehq/plot';
	import RenderPlot from '../../Plot.svelte';

	let notebookRef;
	let variableNames = [];
	let totalReport;
	let viewFlag = true;
	let references = [];
	let thresholdPlotOptions = {};
	let clusterRatioOptions = {};

	onMount(async () => {

		const runtime = new Runtime();

		let main = runtime.module(notebook, (name) => {
			const node = Inspector.into(notebookRef)(name);
			variableNames.push(name);

			if (name == 'thresholds') {
				viewFlag = false;
			}

			if (viewFlag) {
				// Once we reach the "thresholds" name, turn off appending

				if (name == 'viewof table1') {
					node._node.classList.add('table');
					node._node.classList.add('table-striped');
				}

				return node;
			} else {
				return null;
			}
		});

		totalReport = await main.value('total_report');

		thresholdPlotOptions = {
			grid: true,
			inset: 5,
			width: 800,
			//height: 5000,
			paddingLeft: 250,
			facet: {
				data: totalReport,
				y: 'location',
				marginRight: 90
			},
			x: {
				nice: true
			},
			marks: [
				Plot.frame(),
				Plot.dot(totalReport, { x: 'Threshold', y: 'Score', fill: (d) => d.Score, r: 3 })
			],
			color: {
				legend: true,
				label: 'Threshold score',
				type: 'symlog'
			}
		};

		clusterRatioOptions = {
			y: { type: 'log' },
			className: 'plot',
			grid: true,
			inset: 10,
			facet: {
				data: totalReport,
				y: 'location',
				marginRight: 90
			},
			marks: [
				Plot.frame(),
				Plot.dot(totalReport, { x: 'Threshold', y: 'R1_2', fill: (d) => d.R1_2, r: 3 })
			],
			color: {
				legend: true,
				label: 'C1/C2 ratio',
				type: 'log'
			}
		};

		let items = await d3.json('https://api.zotero.org/groups/4394378/collections/9CK2HUNJ/items');

		// Get ID from data.extra
		let itemIds = R.map((item) => {
			if (item.data.extra) {
				let pmid = item.data.extra.split('PMID: ')[1];
				try {
					return pmid.split('\n')[0];
				} catch {
					return pmid;
				}
			} else {
				return null;
			}
		}, items);

		const produceRef = function (pmid, item) {
			if (!pmid) {
				return null;
			} else {
				item.data['pmid'] = pmid;
				return item.data;
			}
		};

		const formatRef = function (item) {
			const citation = new Cite(item);
			let formattedHTML = citation.format('bibliography', {
				format: 'text',
				template: 'wikipedia'
			});

			return '<li class="p-2"><b>' + item.pmid + '</b> ' + formattedHTML + '</li>';
		};

		let zippedItems = R.zipWith(produceRef, itemIds, items);
		let filteredZippedItems = R.filter((d) => d, zippedItems);

		references = R.map(formatRef, filteredZippedItems).join('');

	});
</script>

<div class="container">
	<div class="notebook-container" bind:this={notebookRef} />

	<div>
		<h2 class="text-xl">Threshold Score Plots</h2>
		<RenderPlot options={thresholdPlotOptions} />
	</div>

	<div class="references">
		<h2 class="text-xl">References</h2>
		<ul class="list-disc ml-5">
			{@html references}
		</ul>
	</div>
</div>

<style>
	:global(#data) {
		display: none;
	}

	:global(#papers-network-properties-as-a-function-of-distance-threshold) {
		@apply text-xxl font-semibold;
		font-size: xx-large;
		margin-top: 15px;
		margin-bottom: 15px;
	}

	:global(#overview) {
		@apply text-xxl font-semibold;
		font-size: x-large;
		margin-top: 10px;
		margin-bottom: 10px;
	}

	:global(.container h2) {
		@apply text-xl font-semibold;
		font-size: x-large;
	}
</style>
