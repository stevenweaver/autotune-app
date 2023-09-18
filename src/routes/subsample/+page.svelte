<script>
	import SvelteTable from 'svelte-table';
	import { onMount, beforeUpdate } from 'svelte';
	import * as R from 'ramda';
	import * as d3 from 'd3';

	import * as Plot from '@observablehq/plot';
	import RenderPlot from '../../Plot.svelte';

  import val25_1 from '../../data/30063225/25/1/sampled.tn93output.report.tsv?raw';
  import val25_2 from '../../data/30063225/25/2/sampled.tn93output.report.tsv?raw';
  import val25_3 from '../../data/30063225/25/3/sampled.tn93output.report.tsv?raw';
  import val25_4 from '../../data/30063225/25/4/sampled.tn93output.report.tsv?raw';
  import val25_5 from '../../data/30063225/25/5/sampled.tn93output.report.tsv?raw';
  import val25_6 from '../../data/30063225/25/6/sampled.tn93output.report.tsv?raw';
  import val25_7 from '../../data/30063225/25/7/sampled.tn93output.report.tsv?raw';
  import val25_8 from '../../data/30063225/25/8/sampled.tn93output.report.tsv?raw';
  import val25_9 from '../../data/30063225/25/9/sampled.tn93output.report.tsv?raw';
  import val25_10 from '../../data/30063225/25/10/sampled.tn93output.report.tsv?raw';
  import val50_1 from '../../data/30063225/50/1/sampled.tn93output.report.tsv?raw';
  import val50_2 from '../../data/30063225/50/2/sampled.tn93output.report.tsv?raw';
  import val50_3 from '../../data/30063225/50/3/sampled.tn93output.report.tsv?raw';
  import val50_4 from '../../data/30063225/50/4/sampled.tn93output.report.tsv?raw';
  import val50_5 from '../../data/30063225/50/5/sampled.tn93output.report.tsv?raw';
  import val50_6 from '../../data/30063225/50/6/sampled.tn93output.report.tsv?raw';
  import val50_7 from '../../data/30063225/50/7/sampled.tn93output.report.tsv?raw';
  import val50_8 from '../../data/30063225/50/8/sampled.tn93output.report.tsv?raw';
  import val50_9 from '../../data/30063225/50/9/sampled.tn93output.report.tsv?raw';
  import val50_10 from '../../data/30063225/50/10/sampled.tn93output.report.tsv?raw';
  import val75_1 from '../../data/30063225/75/1/sampled.tn93output.report.tsv?raw';
  import val75_2 from '../../data/30063225/75/2/sampled.tn93output.report.tsv?raw';
  import val75_3 from '../../data/30063225/75/3/sampled.tn93output.report.tsv?raw';
  import val75_4 from '../../data/30063225/75/4/sampled.tn93output.report.tsv?raw';
  import val75_5 from '../../data/30063225/75/5/sampled.tn93output.report.tsv?raw';
  import val75_6 from '../../data/30063225/75/6/sampled.tn93output.report.tsv?raw';
  import val75_7 from '../../data/30063225/75/7/sampled.tn93output.report.tsv?raw';
  import val75_8 from '../../data/30063225/75/8/sampled.tn93output.report.tsv?raw';
  import val75_9 from '../../data/30063225/75/9/sampled.tn93output.report.tsv?raw';
  import val75_10 from '../../data/30063225/75/10/sampled.tn93output.report.tsv?raw';

  import json25_1 from '../../data/30063225/25/1/sampledSummaryStatsTN93.json';
  import json25_2 from '../../data/30063225/25/2/sampledSummaryStatsTN93.json';
  import json25_3 from '../../data/30063225/25/3/sampledSummaryStatsTN93.json';
  import json25_4 from '../../data/30063225/25/4/sampledSummaryStatsTN93.json';
  import json25_5 from '../../data/30063225/25/5/sampledSummaryStatsTN93.json';
  import json25_6 from '../../data/30063225/25/6/sampledSummaryStatsTN93.json';
  import json25_7 from '../../data/30063225/25/7/sampledSummaryStatsTN93.json';
  import json25_8 from '../../data/30063225/25/8/sampledSummaryStatsTN93.json';
  import json25_9 from '../../data/30063225/25/9/sampledSummaryStatsTN93.json';
  import json25_10 from '../../data/30063225/25/10/sampledSummaryStatsTN93.json';
  import json50_1 from '../../data/30063225/50/1/sampledSummaryStatsTN93.json';
  import json50_2 from '../../data/30063225/50/2/sampledSummaryStatsTN93.json';
  import json50_3 from '../../data/30063225/50/3/sampledSummaryStatsTN93.json';
  import json50_4 from '../../data/30063225/50/4/sampledSummaryStatsTN93.json';
  import json50_5 from '../../data/30063225/50/5/sampledSummaryStatsTN93.json';
  import json50_6 from '../../data/30063225/50/6/sampledSummaryStatsTN93.json';
  import json50_7 from '../../data/30063225/50/7/sampledSummaryStatsTN93.json';
  import json50_8 from '../../data/30063225/50/8/sampledSummaryStatsTN93.json';
  import json50_9 from '../../data/30063225/50/9/sampledSummaryStatsTN93.json';
  import json50_10 from '../../data/30063225/50/10/sampledSummaryStatsTN93.json';
  import json75_1 from '../../data/30063225/75/1/sampledSummaryStatsTN93.json';
  import json75_2 from '../../data/30063225/75/2/sampledSummaryStatsTN93.json';
  import json75_3 from '../../data/30063225/75/3/sampledSummaryStatsTN93.json';
  import json75_4 from '../../data/30063225/75/4/sampledSummaryStatsTN93.json';
  import json75_5 from '../../data/30063225/75/5/sampledSummaryStatsTN93.json';
  import json75_6 from '../../data/30063225/75/6/sampledSummaryStatsTN93.json';
  import json75_7 from '../../data/30063225/75/7/sampledSummaryStatsTN93.json';
  import json75_8 from '../../data/30063225/75/8/sampledSummaryStatsTN93.json';
  import json75_9 from '../../data/30063225/75/9/sampledSummaryStatsTN93.json';
  import json75_10 from '../../data/30063225/75/10/sampledSummaryStatsTN93.json';



  let tn93reports = {
    val25_1: val25_1,
    val25_2: val25_2,
    val25_3: val25_3,
    val25_4: val25_4,
    val25_5: val25_5,
    val25_6: val25_6,
    val25_7: val25_7,
    val25_8: val25_8,
    val25_9: val25_9,
    val25_10: val25_10,
    val50_1: val50_1,
    val50_2: val50_2,
    val50_3: val50_3,
    val50_4: val50_4,
    val50_5: val50_5,
    val50_6: val50_6,
    val50_7: val50_7,
    val50_8: val50_8,
    val50_9: val50_9,
    val50_10: val50_10,
    val75_1: val75_1,
    val75_2: val75_2,
    val75_3: val75_3,
    val75_4: val75_4,
    val75_5: val75_5,
    val75_6: val75_6,
    val75_7: val75_7,
    val75_8: val75_8,
    val75_9: val75_9,
    val75_10: val75_10
  };

  let jsonReports = {
    json25_1: json25_1,
    json25_2: json25_2,
    json25_3: json25_3,
    json25_4: json25_4,
    json25_5: json25_5,
    json25_6: json25_6,
    json25_7: json25_7,
    json25_8: json25_8,
    json25_9: json25_9,
    json25_10: json25_10,
    json50_1: json50_1,
    json50_2: json50_2,
    json50_3: json50_3,
    json50_4: json50_4,
    json50_5: json50_5,
    json50_6: json50_6,
    json50_7: json50_7,
    json50_8: json50_8,
    json50_9: json50_9,
    json50_10: json50_10,
    json75_1: json75_1,
    json75_2: json75_2,
    json75_3: json75_3,
    json75_4: json75_4,
    json75_5: json75_5,
    json75_6: json75_6,
    json75_7: json75_7,
    json75_8: json75_8,
    json75_9: json75_9,
    json75_10: json75_10
  };


	let dataValues = [];
	let allItems = [];
	let totalReport = [];
	let cols = [];

	let summaryStatCols = [];
	let summaryStatValues = [];
	let allSummaryStats = [];

	let a = 100;
	let b = 0;

	let scoreRangeOptions;
	let thresholdRangeOptions;
	let scoreOptions;
	let fullSamplingScoreOptions;
	let thresholdRanges;


	// Get all data to import
	let paths = R.flatten(
		R.map(
			(i) =>
				R.map((j) => {
					return {
						sample: i,
						iteration: j,
						name: `${i}_${j}`,
            value : tn93reports[`val${i}_${j}`],
						path: `../../data/30063225/${i}/${j}/sampled.tn93output.report.tsv?raw`
					};
				}, R.range(1, 11)),
			[25, 50, 75]
		)
	);

	let dataValuesRaw = R.map((p) => p['value'], paths);

	//let dataPromise = R.map((p) => import(p['path']), paths);

	// Get all summary stats to import
	let summaryStatisticPaths = R.flatten(
		R.map(
			(i) =>
				R.map((j) => {
					return {
						sample: i,
						iteration: j,
						name: `${i}_${j}`,
            value : jsonReports[`json${i}_${j}`],
						path: `../../data/30063225/${i}/${j}/sampledSummaryStatsTN93.json`
					};
				}, R.range(1, 11)),
			[25, 50, 75]
		)
	);

	let summaryStatisticValuesRaw = R.map((p) => p['value'], summaryStatisticPaths);

	import fullSampleValuesRaw from '../../data/30063225/100/sequence.tn93output.report.tsv?raw';
	let fullSampleValues = d3.tsvParse(fullSampleValuesRaw, d3.autoType);

	import totalSummaryStats from '../../data/30063225/100/summaryStats.json';

	function isFloat(x) {
		return !!(x % 1);
	}

	function formatValue(x) {
		if (isFloat(x)) {
			return d3.format('.3f')(x);
		} else {
			return x;
		}
	}

	function getMinThreshold(data) {
		return data.reduce((min, p) => (p.Threshold < min ? p.Threshold : min), data[0].Threshold);
	}

	function getMaxThreshold(data) {
		return data.reduce((max, p) => (p.Threshold > max ? p.Threshold : max), data[0].Threshold);
	}

	function getThresholdRange(data) {
		return [getMinThreshold(data), getMaxThreshold(data)];
	}

  function getThresholdIQR(data) {
    let thresholds = R.map(d => d.Threshold, data)
    const Q1 = d3.quantile(thresholds, 0.25);
    const Q3 = d3.quantile(thresholds, 0.75);
  }

  function getThresholdAvg(data) {
    let thresholds = R.map(d => d.Threshold, data)
    const mean = d3.mean(thresholds);
    const median = d3.median(thresholds);
    const std = d3.deviation(thresholds);
  }

  function getScoreAvg(data) {

    let scores = R.map(d => d.Score, data)
    const mean = d3.mean(scores);
    const median = d3.median(scores);
    const std = d3.deviation(scores);

  }

	onMount(async () => {

			dataValues = R.map((d) => d3.tsvParse(d, d3.autoType), dataValuesRaw);

			const mapIndexed = R.addIndex(R.map);
			dataValues = mapIndexed(
				(items, i) => R.map((item) => R.assoc('Name', paths[i]['name'], item), items),
				dataValues
			);
			dataValues = mapIndexed(
				(items, i) => R.map((item) => R.assoc('Sample', paths[i]['sample'], item), items),
				dataValues
			);
			dataValues = mapIndexed(
				(items, i) => R.map((item) => R.assoc('Iteration', paths[i]['iteration'], item), items),
				dataValues
			);
			totalReport = R.flatten(dataValues);

			let maxItem = R.map(
				(items) =>
					items.reduce(function (a, b) {
						return a.Score >= b.Score ? a : b;
					}, {}),
				dataValues
			);

			allItems = mapIndexed((item, i) => R.assoc('Name', paths[i]['name'], item), maxItem);
			allItems = mapIndexed((item, i) => R.assoc('Sample', paths[i]['sample'], item), allItems);
			allItems = mapIndexed(
				(item, i) => R.assoc('Iteration', paths[i]['iteration'], item),
				allItems
			);

			let twentyFivePercents = R.filter((d) => d.Sample == 25, allItems);
			let twentyFivePercentRange = getThresholdRange(twentyFivePercents);

			let fiftyPercents = R.filter((d) => d.Sample == 50, allItems);
			let fiftyPercentRange = getThresholdRange(fiftyPercents);

			let seventyFivePercents = R.filter((d) => d.Sample == 75, allItems);
			let seventyFivePercentRange = getThresholdRange(seventyFivePercents);

			thresholdRanges = {
				'25': twentyFivePercentRange,
				'50': fiftyPercentRange,
				'75': seventyFivePercentRange
			};


      //console.log('25');
      //getScoreAvg(twentyFivePercents);
      //console.log('50');
      //getScoreAvg(fiftyPercents);
      //console.log('75');
      //getScoreAvg(seventyFivePercents);

			const thresholdXy = { z: 'Sample', x: 'Iteration', y: 'Threshold' };

			thresholdRangeOptions = {
				paddingLeft: 250,
				paddingTop: 250,
				marginTop: 30,
				marginBottom: 50,

				y: {
					grid: true,
					inset: 6
				},

				style: { fontSize: '15px' },

				marks: [Plot.boxY(allItems, { x: 'Sample', y: 'Threshold' })]
			};

			cols = R.map((key) => {
				return { key: key, title: key, value: (v) => formatValue(v[key]), sortable: true };
			}, R.keys(allItems[0]));
			summaryStatCols = R.map((key) => {
				return { key: key, title: key, value: (v) => formatValue(v[key]), sortable: true };
			}, R.keys(R.omit(['histogram'], totalSummaryStats)));

			const xy = { z: 'Sample', x: 'Iteration', y: 'Score' };

			scoreRangeOptions = {
				paddingLeft: 250,
				paddingTop: 250,
				marginTop: 30,
				marginBottom: 50,

				y: {
					grid: true,
					inset: 6
				},

				style: { fontSize: '15px' },

				color: {
					legend: true,
					label: 'Score',
					type: 'symlog',
          scheme: 'sinebow'
				},
				facet: { data: allItems, y: 'Sample', marginRight: 90 },
				marks: [Plot.dot(allItems, { x: 'Score', y: 'Threshold', fill: (d) => d.Score, stroke: 'Score', r:6 })]
			};

			scoreOptions = {
				grid: true,
				inset: 5,
				width: 800,
				height: 5000,
				paddingLeft: 250,
				facet: {
					data: totalReport,
					y: 'Name',
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
					Plot.dot(totalReport, { x: 'Threshold', y: 'Score', fill: (d) => d.Score, r: 3 })
				],
				color: {
					legend: true,
					label: 'Threshold score',
					type: 'symlog'
				}
			};

		fullSamplingScoreOptions = {
			grid: true,
			inset: 5,
			width: 800,
			height: 300,
			paddingLeft: 250,
			x: {
				nice: true
			},
			marks: [
				Plot.frame(),
				Plot.dot(fullSampleValues, { x: 'Threshold', y: 'Score', fill: (d) => d.Score, r: 3 })
			],
			color: {
				legend: true,
				label: 'Threshold score',
				type: 'symlog'
			}
		};

			summaryStatValues = R.map((d) => R.omit(['histogram'], d), summaryStatisticValuesRaw);
			summaryStatValues = mapIndexed(
				(item, i) => R.assoc('name', summaryStatisticPaths[i]['name'], item),
				summaryStatValues
			);
			summaryStatValues = mapIndexed(
				(item, i) => R.assoc('sample', summaryStatisticPaths[i]['sample'], item),
				summaryStatValues
			);
			summaryStatValues = mapIndexed(
				(item, i) => R.assoc('iteration', summaryStatisticPaths[i]['iteration'], item),
				summaryStatValues
			);

			let ttotalSummaryStats = R.omit(['histogram'], totalSummaryStats);
			ttotalSummaryStats = R.assoc('name', 'total', ttotalSummaryStats);
			ttotalSummaryStats = R.assoc('sample', '100', ttotalSummaryStats);
			ttotalSummaryStats = R.assoc('iteration', '', ttotalSummaryStats);

			summaryStatCols = R.map((key) => {
				return { key: key, title: key, value: (v) => formatValue(v[key]), sortable: true };
			}, R.keys(R.omit(['histogram'], summaryStatValues[0])));
			allSummaryStats = R.concat([ttotalSummaryStats], summaryStatValues);
	});
</script>

<div class="container px-5">
	<div class="grid grid-cols-1 items-center my-5">
		<div class="col-start-1 col-span-2">
			<h1 class="text-6xl">Subsampling with AUTO-TUNE</h1>
		</div>
	</div>

	<div class="grid grid-cols-1 my-5">
		<p>
			This data is from Rhee et. all (1). The dataset in this study consists of 6,034 complete HIV-1
			pol gene sequences, which were obtained from publicly available databases such as GenBank, the
			Los Alamos National Laboratories (LANL) HIV Sequence Database, and the HIV Drug Resistance
			Database. These sequences were annotated by country and year and were classified into 11 pure
			subtypes and 70 circulating recombinant forms (CRFs) using established taxonomic criteria. To
			test the robustness of AUTO-TUNE, the researchers generated 10 random subsamples at 25%, 50%,
			and 75% each.
		</p>
    <p> Network visualizations of each subsample run can be found <a href="/hivtrace-viz/index.html">here</a>.
	</div>

	<div class="summary flex-1 p-3 overflow-hidden panel">
		<div class="thresholds">
			<h1 class="text-xl py-2">Threshold</h1>

			<h3>Range</h3>

			<RenderPlot options={thresholdRangeOptions} />

			{#if thresholdRanges}
				<p class="py-5">
					A plot of the ranges of inferred thresholds per subsampling percentage. The ranges are 25
					: [{thresholdRanges['25'][0]}, {thresholdRanges['25'][1]}], 50 : [{thresholdRanges[
						'50'
					][0]}, {thresholdRanges['50'][1]}], 75 : [{thresholdRanges['75'][0]}, {thresholdRanges[
						'75'
					][1]}]
				</p>
			{/if}
		</div>

		<div class="scores">
			<h1 class="text-xl py-2">Scores</h1>

			<h3>Range</h3>
			<RenderPlot options={scoreRangeOptions} />
			<p class="py-5">
				This figure shows a plot with years on the x-axis and a heuristic score on the y-axis. The
				heuristic score is based on the number of clusters and the ratio of the largest cluster to
				the second largest cluster. The points on the scatter plot are colored by proportion of
				random samples from original dataset. Each point represents the year and the corresponding
				heuristic score for each respective sample.
			</p>
		</div>

		<div class="summary-statistics">
			<h1 class="text-xl py-2">Summary Statistics</h1>

			<SvelteTable
				columns={summaryStatCols}
				rows={allSummaryStats}
				classNameTable={['table table-striped']}
				classNameThead={['table-warning']}
			/>
		</div>

		<div class="all-scores">
			<h1 class="text-xl py-2">Detailed Scores</h1>

			<h3>Plot</h3>
			<RenderPlot options={scoreOptions} />
			<p class="py-5">
				This figure shows a plot with years on the x-axis and a heuristic score on the y-axis. The
				heuristic score is based on the number of clusters and the ratio of the largest cluster to
				the second largest cluster. The points on the scatter plot are colored by proportion of
				random samples from original dataset. Each point represents the year and the corresponding
				heuristic score for each respective sample.
			</p>
		</div>

		<div class="full-scores">
			<h1 class="text-xl py-2">Full Sampling Scores</h1>

			<h3>Plot</h3>
			<RenderPlot options={fullSamplingScoreOptions} />
			<p class="py-5">
				This figure shows a plot with years on the x-axis and a heuristic score on the y-axis. The
				heuristic score is based on the number of clusters and the ratio of the largest cluster to
				the second largest cluster. The points on the scatter plot are colored by proportion of
				random samples from original dataset. Each point represents the year and the corresponding
				heuristic score for each respective sample.
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

	<div class="references">
		<h2 class="text-xl">References</h2>
		<ul class="list-disc ml-5">
			<li>
				Rhee SY, Shafer RW. Geographically-stratified HIV-1 group M pol subtype and circulating
				recombinant form sequences. Sci Data. 2018 Jul 31;5:180148. doi: 10.1038/sdata.2018.148.
				PMID: 30063225; PMCID: PMC6067049.
			</li>
		</ul>
	</div>

	<!-- <div class="observable-notebook bg-white-300 flex-1 p-3 overflow-hidden panel" bind:this={notebookRef}></div> -->
</div>
