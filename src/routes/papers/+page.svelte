<style>

:global(#data) {
  display:none;
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

<script>

  import { onMount, beforeUpdate } from "svelte";
  import * as d3 from "d3";
  import * as R from "ramda";
  import { Runtime, Inspector } from "@observablehq/runtime";
  import notebook from "8f6e4b51e21a4d45";
  import {Cite} from '@citation-js/core';
  import "@citation-js/plugin-csl";

  let notebookRef;
  let viewFlag = true;
  let references = [];

  onMount(async () => {

    const runtime = new Runtime();

    let main = runtime.module(notebook, name => {

      const node = Inspector.into(notebookRef)(name);

      if(name == "thresholds") {
        viewFlag = false;
      }

      if(viewFlag) {

        // Once we reach the "thresholds" name, turn off appending

        if(name == "viewof table1") {
          node._node.classList.add('table')
          node._node.classList.add('table-striped')
        }

        return node;

      } else {

          return null;

        }

    });

    let items = await d3.json("https://api.zotero.org/groups/4394378/collections/9CK2HUNJ/items");

    // Get ID from data.extra
    let itemIds = R.map(item => { 
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

    const produceRef = function(pmid, item) {
      if(!pmid) {
          return null;
        } else {
          item.data['pmid'] = pmid;
          return item.data;
        }
      }

    const formatRef = function(item) {

      const citation = new Cite(item);
      let formattedHTML = citation.format('bibliography', {
            format: 'text',
            template: 'wikipedia'
          })

      return '<li><b>' + item.pmid + '</b> ' + formattedHTML + '</li>'

    }

    let zippedItems = R.zipWith(produceRef, itemIds, items)
    let filteredZippedItems = R.filter(d => d, zippedItems);

    references = R.map(formatRef, filteredZippedItems).join('');

  });

</script>

<div class="container">

  <div class="notebook-container" bind:this={notebookRef}></div>

  <div class="references">
    <h2 class="text-xl">References</h2>
    <ul>
      {@html references}
    </ul>
  </div>

</div>

