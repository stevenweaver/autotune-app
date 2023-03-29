<script>
	import SvelteTable from 'svelte-table';
	import { onMount, beforeUpdate } from 'svelte';
	import { Runtime, Inspector } from '@observablehq/runtime';
	import * as R from 'ramda';
	import notebook from 'c4009c8fe5e447bf';

	import * as Plot from '@observablehq/plot';
	import RenderPlot from '../../Plot.svelte';

	let notebookRef;
	let variableNames = [];
	let dataValues = [];
	let allItems = [];
	let cols = [];

	let a = 100;
	let b = 0;

	let options;
	let thresholdOptions;

	onMount(async () => {
		const runtime = new Runtime();
		let main = runtime.module(notebook, (name) => {
			// Get list of all names
			variableNames.push(name);
			const node = Inspector.into(notebookRef)(name);

			if (name == 'viewof table1') {
				node._node.classList.add('table');
				node._node.classList.add('table-striped');
			}

			return node;
		});

		let justData = R.filter((x) => {
			if (x && x != 'total_report') {
				return R.includes('report', x);
			} else {
				return false;
			}
		}, variableNames);

		// add data values to global view

		const values = await Promise.all(R.map((d) => main.value(d), justData));
		let maxItem = R.map(
			(items) =>
				items.reduce(function (a, b) {
					return a.Score >= b.Score ? a : b;
				}, {}),
			values
		);

		const mapIndexed = R.addIndex(R.map);

		allItems = mapIndexed((item, i) => R.assoc('Name', justData[i], item), maxItem);
		allItems[0]['Name'].split('report')[1].split('_');

		R.forEach((item) => {
			let [year, sample] = item['Name'].split('report')[1].split('_');
			item['Year'] = year;
			item['Sample'] = sample;
		}, allItems);

		allItems = R.filter((item) => {
			return item['Sample'];
		}, allItems);

		cols = R.map((key) => {
			return { key: key, title: key, value: (v) => v[key], sortable: true };
		}, R.keys(allItems[0]));

		const xy = Plot.normalizeY({ z: 'Sample', x: 'Year', y: 'Score' });

		options = {
			height: 300,
			width: 1024,
			grid: true,
			x: {
				axis: 'top',
				label: 'Year →'
			},
			y: {
				//domain: d3.groupSort(stateage, g => -g.find(d => d.age === "≥80").population / d3.sum(g, d => d.population), d => d.state),
				//axis: null
			},
			color: {
				type: 'ordinal',
				scheme: 'category10',
				domain: allItems.Sample,
				legend: true,
				transform: (d) => parseInt(d)
			},
			marks: [
				Plot.ruleX([0]),
				Plot.ruleY(allItems, Plot.groupY({ x1: 'min', x2: 'max' }, xy)),
				Plot.dot(allItems, { ...xy, fill: 'Sample' }),
				Plot.text(allItems, Plot.selectMinX({ ...xy, textAnchor: 'end', dx: -6, text: 'Year' }))
			]
		};

		const thresholdXy = Plot.normalizeY({ z: 'Sample', x: 'Year', y: 'Threshold' });

		thresholdOptions = {
			height: 300,
			width: 1024,
			grid: true,
			x: {
				axis: 'top',
				label: 'Year →'
			},
			color: {
				type: 'ordinal',
				scheme: 'category10',
				domain: allItems.Sample,
				legend: true,
				transform: (d) => parseInt(d)
			},
			marks: [
				Plot.ruleX([0]),
				Plot.ruleY(allItems, Plot.groupY({ x1: 'min', x2: 'max' }, thresholdXy)),
				Plot.dot(allItems, { ...thresholdXy, fill: 'Sample' }),
				Plot.text(
					allItems,
					Plot.selectMinX({ ...thresholdXy, textAnchor: 'end', dx: -6, text: 'Year' })
				)
			]
		};
	});
</script>

<div class="container px-5">
	<div class="grid grid-cols-3 items-center my-5">
		<div class="col-start-1 col-span-2">
			<h1 class="text-6xl">Subsampling with LANL</h1>
		</div>
	</div>

	<div class="grid grid-cols-2 my-5">
		<p>
			This is an analysis of a new algorithm designed to determine the most appropriate threshold
			for clustering HIV sequences to reconstruct potential transmission networks. The dataset used
			in this analysis is from the Los Alamos National Laboratory, and was partitioned by year. In
			order to assess the performance of the algorithm under different sampling conditions, the
			datasets were subsampled randomly at 75%, 50%, and 25% for each respective year. The algorithm
			was then run on each subsample to determine the variability of the inferred best threshold
			based on the sparsity of the resulting network. The results of this analysis will provide
			insight into the effectiveness of the algorithm under different sampling conditions.
		</p>
	</div>

	<div class="summary flex-1 p-3 overflow-hidden panel">
		<div class="thresholds">
			<h1 class="text-xl py-2">Threshold</h1>

			<h3>Plot</h3>
			<RenderPlot options={thresholdOptions} />
			<p class="py-5">
				Figure 1. In this figure, the x axis represents the year, while the y axis represents the
				optimal distance threshold used to link pairs of sequences into a cluster. The optimal
				distance threshold is determined by a heuristic score, which is described later in the page.
				Each dot in the figure is colored according to the sampling proportion of the original
				dataset for each respective year.
			</p>
		</div>

		<div class="scores">
			<h1 class="text-xl py-2">Scores</h1>

			<h3>Plot</h3>
			<RenderPlot {options} />
			<p class="py-5">
				Figure 2. This figure shows a plot with years on the x-axis and a heuristic score on the
				y-axis. The heuristic score is based on the number of clusters and the ratio of the largest
				cluster to the second largest cluster. The points on the scatter plot are colored by
				proportion of random samples from original dataset. Each point represents the year and the
				corresponding heuristic score for each respective sample.
			</p>
		</div>

		<h3 class="py-2">Table</h3>
		<SvelteTable
			columns={cols}
			rows={allItems}
			classNameTable={['table table-striped']}
			classNameThead={['table-warning']}
		/>
	</div>

	<div
		class="observable-notebook bg-white-300 flex-1 p-3 overflow-hidden panel"
		bind:this={notebookRef}
	/>
</div>
