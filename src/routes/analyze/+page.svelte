<script>

  import { onMount, beforeUpdate } from "svelte";
  import { Runtime, Inspector } from "@observablehq/runtime";
  import * as Plot from "@observablehq/plot";
  import * as d3 from 'd3';
  import RenderPlot from '../../Plot.svelte'

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
        facet: {
          data: totalReport,
          y: "location",
          marginRight: 90
        },
        x: {
          nice: true
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
        facet: {
          data: totalReport,
          y: "location",
          marginRight: 90
        },
        x: {
          nice: true
        },
        marks: [
          Plot.frame(),
          Plot.dot(totalReport, {x: "Threshold", y: "Clusters", fill: d => d.Score, r: 3}),
        ],
        color: {
          legend: true, 
          label: "Number of Clusters",
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
          facet: {
            data: totalReport,
            y: "location",
            marginRight: 90
          },
          x: {
            nice: true
          },
          marks: [
            Plot.frame(),
            Plot.dot(totalReport, {x: "Threshold", y: "Clusters", fill: d => d.Score, r: 3}),
          ],
          color: {
            legend: true, 
            label: "R1/R2",
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
      thresholdPlotOptions = generateThresholdPlot(content);
      clusterPlotOptions = generateClusterPlot(content);
      ratioPlotOptions = generateRatioPlot(content);

      });
	}

</script>


<div class="container">

  <input id="threshold-file" bind:files type=file accept="text/*">

  <div>
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
