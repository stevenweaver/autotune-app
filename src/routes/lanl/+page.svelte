

<script>

  import SvelteTable from "svelte-table";
  import { onMount, beforeUpdate } from "svelte";
  import { Runtime, Inspector } from "@observablehq/runtime";
	import * as R from "ramda";
  import notebook from "c4009c8fe5e447bf";

  import * as Plot from "@observablehq/plot";
  import RenderPlot from '../../Plot.svelte'

  let notebookRef;
	let variableNames = [];
	let dataValues = [];
  let allItems = [];
  let cols = [];

  let a = 100;
	let b = 0;

let options; 


  onMount(async () => {

    const runtime = new Runtime();
    let main = runtime.module(notebook, name => {

			// Get list of all names
			variableNames.push(name);
      const node = Inspector.into(notebookRef)(name);

      if(name == "viewof table1") {

        node._node.classList.add('table');
        node._node.classList.add('table-striped');

      }

      return node;

    });

		let justData = R.filter(x => { if(x && x != "total_report") { return R.includes('report', x) } else { return false }} , variableNames);

		// add data values to global view

		const values = await Promise.all(R.map(d => main.value(d), justData));
		let maxItem = R.map(items => items.reduce(function(a, b) { return a.Score >= b.Score ? a : b }, {}), values);
    const mapIndexed = R.addIndex(R.map);

    allItems = mapIndexed((item, i) => R.assoc('Name', justData[i], item), maxItem);
    allItems[0]['Name'].split('report')[1].split('_');

    R.forEach(item => { 
      let [year, sample] = item['Name'].split('report')[1].split('_');
      item['Year'] =  year; 
      item['Sample'] = sample;}, allItems)

    allItems = R.filter(item => { return item['Sample'] }, allItems);
    console.log(allItems);

    cols = R.map( key =>  { return {key:key, title:key, value: v => v[key], sortable: true }  }, R.keys(allItems[0]));

    const xy = Plot.normalizeY({z: "Sample", x: "Year", y: "Score"});

    options = {

      height: 300,
      width: 1024,
      grid: true,
      x: {
        axis: "top",
        label: "Year →"
      },
      y: {
        //domain: d3.groupSort(stateage, g => -g.find(d => d.age === "≥80").population / d3.sum(g, d => d.population), d => d.state),
        //axis: null
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
        Plot.ruleY(allItems, Plot.groupY({x1: "min", x2: "max"}, xy)),
        Plot.dot(allItems, {...xy, fill: "Sample"}),
        Plot.text(allItems, Plot.selectMinX({...xy, textAnchor: "end", dx: -6, text: "Year"}))
      ]

    }


});

</script>

<div class="container">
	<div class="summary flex-1 p-3 overflow-hidden panel">

    <h1>Scores</h1>
    <h2>Plot</h2>
    <RenderPlot options={options} />


    <h2>Table</h2>
    <SvelteTable 
      columns="{cols}" 
      rows="{allItems}" 
      classNameTable={['table table-striped']}
      classNameThead={['table-warning']}
      />
  </div>
	<div class="observable-notebook bg-white-300 flex-1 p-3 overflow-hidden panel" bind:this={notebookRef}></div>
</div>



