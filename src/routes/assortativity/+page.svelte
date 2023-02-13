<style>

div :global(.container h1) {
  @apply text-xxl font-semibold;
  font-size: xx-large;
}

div :global(.container h2) {
  @apply text-l font-semibold;
  font-size: large;
}

div :global(.container h3) {
  @apply text-l font-semibold;
  font-size: large;
}

</style>

<script>

	import { Wave } from 'svelte-loading-spinners';
  import { onMount, beforeUpdate, afterUpdate } from "svelte";
  import { Runtime, Inspector } from "@observablehq/runtime";
  import * as Plot from "@observablehq/plot";
  import * as d3 from 'd3';
	import * as R from "ramda";
  import RenderPlot from '../../Plot.svelte';
  import {default as dwh, computeFractions, decompress} from 'dwh';
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

	//let loading = true;

  let nodeCategoryRaw = (field, n) => {

		if(!n['patient_attributes']) {
				return null;
		}

    var desc = n['patient_attributes'][field];

    if (desc == "MSM") {
      return desc; 
    }

    //return desc + " (" + n['patient_attributes']['Gender'] + ")";
    return desc

  }

	$: {

			let network = content;

			// Read in all patient_attributes and get unique list
			patientAttributeKeys = R.filter(k=> k != "ehars_uid", R.keys(network.Nodes[0].patient_attributes));

			if(!R.includes(selectedKey, patientAttributeKeys)) {
				selectedKey = patientAttributeKeys[0];
				selected = patientAttributeKeys[0];
			}

			// Get unique values for each key
			patientAttributes = R.zipObj(patientAttributeKeys, R.map(key => R.uniq(R.map(d => { try { return d.patient_attributes[key]} catch { return null } }, network.Nodes)), patientAttributeKeys));

			// calculate dwh for each risk group just to try
			let records = patientAttributes[selectedKey];

			const nodeCategory = R.partial(nodeCategoryRaw, [selectedKey]);

			let f = d3.format(".3f");

			assortativity = R.map((record) => {
				const r = { "Record" : record, 
										"Field" : selectedKey, 
										"DWH" : f(dwh(network, nodeCategory , record)),
										"Panmictic range" : d3.extent(R.map ((r) => f(dwh(network, nodeCategory, record, true)), R.range (1, 200)))};
				return r;
			}, records);

			fractions = computeFractions(network, nodeCategory, false);

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

		//loading = false;
	}

	$: if (files) {

		// Note that `files` is of type `FileList`, not an Array:
		// https://developer.mozilla.org/en-US/docs/Web/API/FileList
    let file = files[0];

    file.text().then(fileContent => {

      let network = JSON.parse(fileContent);

  		if(network["trace_results"]) {
				network = network["trace_results"];
			}

			if (network.Settings && network.Settings.compact_json) {
				network = decompress(network);
			}

			content = network;

		});

	} else {
		content = resultsFile;
	}

  // Get DWH for the default selection

  const onAttributeChange = (e) => {
    selectedKey = e.target.value;
  }

</script>

<div class="container pt-3">

	<!-- <div class="loading"> -->
	<!-- 	<Wave size="300" color="teal" unit="px" duration="2s" /> -->
	<!-- </div> -->

	<div class="main">
		<h1>Assortativity</h1>

		<div>
			<h2>Instructions</h2>
			<div id="summary">
				<p>Please see <a href="/about#annotation"> the annotation section</a> of the About page for more information on how to generate the results necessary to use this page.</p>
				<p>Please see <a href="/about#assortativity"> the assortativity section</a> of the About page for more information on the algorithms (i.e. DWH) involved.</p>
			</div>
		</div>
	 
		<h2>Select HIV-TRACE Results File</h2>
		<input class="pt-3" id="results-file" bind:files type=file>

		<div class=pt-3>
			<h2>Assortativity / homophily analysis </h2>
				<select bind:value={selected} on:change={onAttributeChange}>
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
				
			<p>DWH (Degree-weighted homophily) ranges from -1 to 1. A DWH value of 0 indicates that there is no more homophily than expected with chance, while a value of 1 indicates that there is perfect homophily (e.g. Birds always link to birds). A value of -1 is achieved for perfectly disassortative networks (e.g. Bird never linking with another bird).</p>
			<p>Panmictic range is a label permutation test to compute the null distribution of DWH values.</p>

		</div>

		<div class=pt-3>
			<h3>Plot</h3>
			<RenderPlot options={fractionOptions} />
			<p class="py-1">Figure 1. Fractions of pairwise connections, scaled by degree, for each attribute that appears for the selected field.</p>
		</div>
	</div>

</div>
