<script>

  import SvelteTable from "svelte-table";
  import { onMount, beforeUpdate } from "svelte";
	import * as R from "ramda";
  import * as d3 from "d3";

  import * as Plot from "@observablehq/plot";
  import RenderPlot from '../../Plot.svelte';

	let dataValues = [];
  let allItems = [];
  let totalReport = [];
  let cols = [];

  let a = 100;
	let b = 0;

  let options; 
  let thresholdOptions; 
  let scoreOptions; 
  let fullSamplingScoreOptions; 

  // Get all data to import
  let paths = R.flatten(R.map(i => R.map( j =>  { return { "sample": i, "iteration": j, "name": `${i}_${j}`, "path": `../../data/30063225/${i}/${j}/sampled.tn93output.report.tsv?raw` } }, R.range(1,11)), [25,50,75]));
  let dataPromise = R.map(p => import(p['path']), paths);

  import fullSampleValuesRaw from '../../data/30063225/100/sequence.tn93output.report.tsv?raw';
  let fullSampleValues = d3.tsvParse(fullSampleValuesRaw , d3.autoType);

  onMount(async () => {

    Promise.all(dataPromise).then((values) => {

      dataValues = R.map(d => d3.tsvParse(d.default, d3.autoType), values);

      const mapIndexed = R.addIndex(R.map);
      dataValues = mapIndexed((items, i) => R.map(item => R.assoc('Name', paths[i]['name'], item), items), dataValues);
      dataValues = mapIndexed((items, i) => R.map(item => R.assoc('Sample', paths[i]['sample'], item), items), dataValues);
      dataValues = mapIndexed((items, i) => R.map(item => R.assoc('Iteration', paths[i]['iteration'], item), items), dataValues);
      totalReport = R.flatten(dataValues);

      let maxItem = R.map(items => items.reduce(function(a, b) { return a.Score >= b.Score ? a : b }, {}), dataValues);

      allItems = mapIndexed((item, i) => R.assoc('Name', paths[i]['name'], item), maxItem);
      allItems = mapIndexed((item, i) => R.assoc('Sample', paths[i]['sample'], item), allItems);
      allItems = mapIndexed((item, i) => R.assoc('Iteration', paths[i]['iteration'], item), allItems);

      const thresholdXy = {z: "Sample", x: "Iteration", y: "Threshold"};

      thresholdOptions = {
        height: 300,
        width: 1024,
        grid: true,
        x: {
          axis: "top",
          label: "Sample →"
        },
        y: {
            transform: d => d*100
        },
        color: {
          type: "ordinal",
          scheme: "category10",
          domain: allItems.Sample,
          legend: true,
          transform: d => parseInt(d)
        },
        marks: [
          Plot.ruleX([0]),
          Plot.dot(allItems, {...thresholdXy , fill: "Sample"})
        ]

      }

      cols = R.map( key =>  { return {key:key, title:key, value: v => v[key], sortable: true }  }, R.keys(allItems[0]));

      const xy = {z: "Sample", x: "Iteration", y: "Score"};

      options = {

        height: 300,
        width: 1024,
        grid: true,
        x: {
          axis: "top",
          label: "Iteration →"
        },
        color: {
          type: "ordinal",
          scheme: "category10",
          domain: allItems.Sample,
          legend: true,
          transform: d => parseInt(d)
        },
        marks: [
          Plot.ruleX([0]),
          Plot.dot(allItems, {...xy, fill: "Sample"})
        ]

      }

      scoreOptions = {
        grid: true,
        inset: 5,
        width: 800,
        height: 5000,
        paddingLeft:250,
        facet: {
          data: totalReport,
          y: "Name",
          marginRight: 90
        },
        x: {
          nice: true
        },
        y: {
          domain: [-0.5,2],
          transform: d => R.max(-0.5, d)
        },
        marks: [
          Plot.frame(),
          Plot.dot(totalReport, {x: "Threshold", y: "Score", fill: d => d.Score, r: 3}),
        ],
        color: {
          legend: true, 
          label: "Threshold score",
          type: "symlog"
        }
      }

    });

    fullSamplingScoreOptions = {
      grid: true,
      inset: 5,
      width: 800,
      height: 300,
      paddingLeft:250,
      x: {
        nice: true
      },
      marks: [
        Plot.frame(),
        Plot.dot(fullSampleValues, {x: "Threshold", y: "Score", fill: d => d.Score, r: 3}),
      ],
      color: {
        legend: true, 
        label: "Threshold score",
        type: "symlog"
      }
    }


});

</script>

<div class="container px-5">

  <div class="grid grid-cols-3 items-center my-5">
    <div class="col-start-1 col-span-2">
      <h1 class="text-6xl">Subsampling with AUTO-TUNE</h1>
    </div>
  </div>

	<div class="summary flex-1 p-3 overflow-hidden panel">

    <div class="thresholds">
      <h1 class="text-xl py-2">Threshold</h1>

      <h3>Plot</h3>
      <RenderPlot options={thresholdOptions} />
      <p class="py-5">Figure 1. In this figure, the x axis represents the sample iteration, while the y axis represents the optimal distance threshold used to link pairs of sequences into a cluster. The optimal distance threshold is determined by a heuristic score, which is described later in the page. Each dot in the figure is colored according to the sampling proportion of the original dataset for each respective iteration.</p>
    </div>


    <div class="scores">

      <h1 class="text-xl py-2">Scores</h1>

      <h3>Plot</h3>
      <RenderPlot options={options} />
      <p class="py-5"> Figure 2. This figure shows a plot with years on the x-axis and a heuristic score on the y-axis. The heuristic score is based on the number of clusters and the ratio of the largest cluster to the second largest cluster. The points on the scatter plot are colored by proportion of random samples from original dataset. Each point represents the year and the corresponding heuristic score for each respective sample. </p>

    </div>

    <div class="all-scores">

      <h1 class="text-xl py-2">Detailed Scores</h1>

      <h3>Plot</h3>
      <RenderPlot options={scoreOptions} />
      <p class="py-5"> Figure 2. This figure shows a plot with years on the x-axis and a heuristic score on the y-axis. The heuristic score is based on the number of clusters and the ratio of the largest cluster to the second largest cluster. The points on the scatter plot are colored by proportion of random samples from original dataset. Each point represents the year and the corresponding heuristic score for each respective sample. </p>

    </div>

    <div class="full-scores">

      <h1 class="text-xl py-2">Full Sampling Scores</h1>

      <h3>Plot</h3>
      <RenderPlot options={fullSamplingScoreOptions} />
      <p class="py-5"> Figure 2. This figure shows a plot with years on the x-axis and a heuristic score on the y-axis. The heuristic score is based on the number of clusters and the ratio of the largest cluster to the second largest cluster. The points on the scatter plot are colored by proportion of random samples from original dataset. Each point represents the year and the corresponding heuristic score for each respective sample. </p>

    </div>



    <h3 class="py-2">Table</h3>
    <SvelteTable 
      columns="{cols}" 
      rows="{allItems}" 
      classNameTable={['table table-striped']}
      classNameThead={['table-warning']}
      />
  </div>

	<!-- <div class="observable-notebook bg-white-300 flex-1 p-3 overflow-hidden panel" bind:this={notebookRef}></div> -->

</div>

