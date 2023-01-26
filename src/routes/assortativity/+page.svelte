<style>

</style>
<script>

  import { onMount, beforeUpdate } from "svelte";
  import { Runtime, Inspector } from "@observablehq/runtime";
  import * as Plot from "@observablehq/plot";
  import * as d3 from 'd3';
	import * as R from "ramda";
  import RenderPlot from '../../Plot.svelte';
  import {default as dwh, computeFractions} from 'dwh';
  import SvelteTable from "svelte-table";

  import resultsFile from '../../data/0.4-averaged-filtered.json';

  let files;
  let patientAttributeKeys;
  let patientAttributes;

  let selected;
  let selectedKey = 'Risk';

  let cols = [];
  let allItems = [];
  let assortativity;
  let content;
  let fractions;
  let fractionOptions;


  let nodeCategoryRaw = (field, n) => {

    var desc = n['patient_attributes'][field];

    if (desc == "MSM") {
      return desc; 
    }

    //return desc + " (" + n['patient_attributes']['Gender'] + ")";
    return desc

  }

	$: if (files) {

		// Note that `files` is of type `FileList`, not an Array:
		// https://developer.mozilla.org/en-US/docs/Web/API/FileList
    let file = files[0];
    file.text().then(fileContent => {
      content = JSON.parse(fileContent);
      });

	} else {

		content = resultsFile;

    // Read in all patient_attributes and get unique list
    patientAttributeKeys = R.keys(content.Nodes[0].patient_attributes);

    // Get unique values for each key
    patientAttributes = R.zipObj(patientAttributeKeys, R.map(key => R.uniq(R.map(d => d.patient_attributes[key], content.Nodes)), patientAttributeKeys));

    // calculate dwh for each risk group just to try
    let records = patientAttributes[selectedKey];

    const nodeCategory = R.partial(nodeCategoryRaw, [selectedKey]);

    assortativity = R.map((record) => {
      const r = { "Record" : record, 
                  "Field" : selectedKey, 
                  "DWH" : dwh(content, nodeCategory , record), 
                  "Panmictic range" : d3.extent (R.map ((r) => dwh(content, nodeCategory, record, true), R.range (1, 200)))};
      return r;
    }, records);

    fractions = computeFractions(content, nodeCategory, false);
    console.log(fractions);

    const xy = Plot.normalizeY({basis: "sum", y: "count"});

    fractionOptions = {
      color: {
          legend: true
      },
      x: {
        type: "band",
        label: null
      },
      facet: {data:fractions, x:"from", label:null},
      marks: [
        Plot.barY(fractions, {...xy, fill:"to"}),
        Plot.ruleY([0])
      ]
    };
  
    cols = R.map( key =>  { return {key:key, title:key, value: v => v[key], sortable: true }  }, R.keys(assortativity));


    cols = [ 
              {key:"Record", title: selectedKey, value: v => v["Record"], sortable: true },
              {key:"DWH", title:"DWH", value: v => v["DWH"], sortable: true },
              {key:"Panmictic range", title:"Panmictic range", value: v => v["Panmictic range"], sortable: true }
           ];


	}

  // Get DWH for the default selection

  const onAttributeChange = (e) => {
    selectedKey = e.target.value;
  }

</script>


<div class="container pt-3">
	<h2>Assortativity</h2>

  <div class=pt-3>
    <h2 class="text-xl">Instructions</h2>
    <div id="summary">
    </div>
  </div>
 
  <input class="pt-3" id="results-file" bind:files type=file accept="text/*">

  <div class=pt-3>
    <h2 class="text-xl">Assortativity / homophily analysis </h2>
    	<select value={selected} on:change={onAttributeChange}>
        {#each patientAttributeKeys as key}
          <option value={key}>
            {key}
          </option>
        {/each}
      </select>
  </div>

  <div class=pt-3>
    <h3 class="py-2">Table</h3>
    <SvelteTable 
      columns="{cols}" 
      rows="{assortativity}" 
      classNameTable={['table table-striped']}
      classNameThead={['table-warning']}
      />
  </div>

  <h3>Plot</h3>
  <RenderPlot options={fractionOptions} />


</div>
