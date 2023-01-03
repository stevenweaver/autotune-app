<style>

  :global(.container h1) {
    @apply text-xxl font-semibold;
    font-size: xx-large;
    margin-top: 15px;
    margin-bottom: 15px;
  }

  :global(#data) {
    display:none;
  }

</style>

<script>

  import { onMount, beforeUpdate } from "svelte";
  import { Runtime, Inspector } from "@observablehq/runtime";
  import notebook from "f2e663c52265f41c";

  let notebookRef;
	let variableNames = [];
  let viewFlag = true;

  onMount(async () => {

    const runtime = new Runtime();

    let main = runtime.module(notebook, name => {

      const node = Inspector.into(notebookRef)(name);
			variableNames.push(name);

      if(name != undefined) {
        viewFlag = false;
      }

      if(viewFlag) {

        // Once we reach the "data" name, turn off appending

        if(name == "viewof table1") {
          node._node.classList.add('table')
          node._node.classList.add('table-striped')
        }

        return node;

      } else {

          return null;

        }

    });

  });

</script>

<div class="container" bind:this={notebookRef}>
</div>



