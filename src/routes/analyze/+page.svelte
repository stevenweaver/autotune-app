<style>

code { 
  white-space: pre; 
  }

</style>
<script>

  import { onMount, beforeUpdate } from "svelte";
  import { Runtime, Inspector } from "@observablehq/runtime";
  import * as Plot from "@observablehq/plot";
  import * as d3 from 'd3';
	import * as R from "ramda";
  import RenderPlot from '../../Plot.svelte'

  import chiapasFile from '../../data/chiapas_seguro_report.tsv?raw'


  let files;
  let content;
  let thresholdPlotOptions;
  let clusterPlotOptions;
  let ratioPlotOptions;

  function generateThresholdPlot(totalReport) {
    let thresholdPlotOptions = {
        grid: true,
        inset: 5,
        width: 800,
        //height: 5000,
        paddingLeft:250,
        x: {
          nice: true
        },
        marks: [
          Plot.frame(),
          Plot.dot(totalReport, {x: "Threshold", y: "Score", fill: d => d.Score, r: 3}),
        ],
        color: {
          legend: true, 
          label: "Score",
          type: "symlog"
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
        paddingLeft:250,
        x: {
          nice: true
        },
        marks: [
          Plot.frame(),
          Plot.dot(totalReport, {x: "Threshold", y: "Clusters", fill: d => d.Score, r: 3}),
        ],
        color: {
          legend: true, 
          label: "Score",
          type: "symlog"
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
          paddingLeft:250,
          x: {
            nice: true
          },
          marks: [
            Plot.frame(),
            Plot.dot(totalReport, {x: "Threshold", y: "R1_2", fill: d => d.Score, r: 3}),
          ],
          color: {
            legend: true, 
            label: "Score",
            type: "symlog"
          }
        };

        return ratioPlotOptions;

      }



	$: if (files) {
		// Note that `files` is of type `FileList`, not an Array:
		// https://developer.mozilla.org/en-US/docs/Web/API/FileList
    let file = files[0];
    file.text().then(fileContent => {
      let content = d3.tsvParse(fileContent, d3.autoType);

      // map the content to include ratios

			let mappedContent = R.map(d => { 
				d["R1_2"] = d.LargestCluster/d.SecondLargestCluster; 
				d["Degrees"] = d["Edges"]/d["Nodes"]; 
				return d}, content);

      thresholdPlotOptions = generateThresholdPlot(mappedContent);
      clusterPlotOptions = generateClusterPlot(mappedContent);
      ratioPlotOptions = generateRatioPlot(mappedContent);

      });
	} else {

		let content = d3.tsvParse(chiapasFile, d3.autoType);

		// map the content to include ratios

		let mappedContent = R.map(d => { 
			d["R1_2"] = d.LargestCluster/d.SecondLargestCluster; 
			d["Degrees"] = d["Edges"]/d["Nodes"]; 
			return d}, content);

		thresholdPlotOptions = generateThresholdPlot(mappedContent);
		clusterPlotOptions = generateClusterPlot(mappedContent);
		ratioPlotOptions = generateRatioPlot(mappedContent);

	}

</script>


<div class="container pt-3">
	<h2> Analyze your own Results </h2>

  <input class="pt-3" id="threshold-file" bind:files type=file accept="text/*">

  <div class=pt-3>
    <h2 class="text-xl">How</h2>
    <div id="summary">
      <p>To generate a results file that is compatible with this page, use a multiple sequence alignment with the <a href="https://github.com/veg/tn93">tn93</a> fast pairwise distance calculator.</p>
      <p>Once a pairwise distance file is created, use the <a href="https://github.com/veg/hivclustering">hivnetworkcsv</a> script with the <code>-A</code> keyword argument to generate the tab-separated output compatible with this page.</p>
      <p class="mt-2">An example workflow is as follows: </p>
      <div class="bg-indigo-100 p-3 rounded">
        <code>
./tn93 -t 0.015 pol.fasta > pairwise_distances.15.tn93.csv
hivnetworkcsv -i pairwise_distances.15.tn93.csv -f plain -A 0 > autotune_report.tsv
        </code>
      </div>
    </div>
  </div>
 

  <div class=pt-3>
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
