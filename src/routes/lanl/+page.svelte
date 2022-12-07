

<script>

  import SvelteTable from "svelte-table";
  import { onMount, beforeUpdate } from "svelte";
  import { Runtime, Inspector } from "@observablehq/runtime";
	import * as R from "ramda";
  import notebook from "c4009c8fe5e447bf";

  let notebookRef;
	let variableNames = [];
	let dataValues = [];
  let allItems = [];
  let cols = [];

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
    cols = R.map( key =>  { return {key:key, title:key, value: v => v[key], sortable: true }  }, R.keys(allItems[0]));

    console.log(allItems);
    console.log(cols);

  });

</script>

<div class="container">
	<div class="summary flex-1 p-3 overflow-hidden panel">
    <h1>Scores</h1>
    <SvelteTable 
      columns="{cols}" 
      rows="{allItems}" 
      classNameTable={['table table-striped']}
      classNameThead={['table-warning']}
      />
  </div>
	<div class="observable-notebook bg-white-300 flex-1 p-3 overflow-hidden panel" bind:this={notebookRef}></div>
</div>



