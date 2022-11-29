<script>

  import { onMount, beforeUpdate } from "svelte";
  import { Runtime, Inspector } from "@observablehq/runtime";
  import notebook from "a209d879a3c7f5ca";

  let notebookRef;

  onMount(async () => {

    const runtime = new Runtime();

    let main = runtime.module(notebook, name => {

      const node = Inspector.into(notebookRef)(name);
      if(name == "viewof table1") {
        node._node.classList.add('table')
        node._node.classList.add('table-striped')
      }
      return node;

    });

  });

</script>

<div class="container" bind:this={notebookRef}>
</div>



