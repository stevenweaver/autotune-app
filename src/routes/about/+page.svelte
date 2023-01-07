<style>

  .container :global(p) {
      margin-bottom: 5px;
    } 

  .container {
      margin-top: 15px;
    } 

  :global(.container h1) {
    @apply text-xxl font-semibold;
    font-size: xx-large;
    margin-top: 15px;
    margin-bottom: 15px;
  }

  :global(.container h2) {
    margin-top: 15px;
    margin-bottom: 15px;
  }


  :global(ol) {
    list-style-type: decimal;
    margin-left: 20px;
  }

  :global(li>ol) {
    list-style-type: lower-alpha;
    margin-left: 20px;
  }


</style>

<script>

  import { onMount, beforeUpdate } from "svelte";
  import About from '../../docs/about.md'

</script>

<div class="container">
  <About />
</div>
