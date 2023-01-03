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



</style>

<script>

  import { onMount, beforeUpdate } from "svelte";
  import SvelteMarkdown from 'svelte-markdown';

  const source = `
  # About

Choosing an appropriate distance threshold is an important part of using a transmission network to track the spread of a contagious disease. This distance threshold determines how close two individuals must be in order for a link to be created between them in the network.
Using a distance threshold that is too small can result in a network with many unnecessary links, making it difficult to interpret and analyze. On the other hand, using a distance threshold that is too large can result in a network with too few links, making it difficult to accurately track the spread of the disease.

To ensure that the transmission network is useful and informative, it is important to carefully consider the appropriate distance threshold. This may vary depending on the specific disease and the context in which it is spreading. For example, a highly contagious respiratory illness may require a smaller distance threshold than a less contagious illness that is primarily spread through direct contact.
In general, the goal is to strike a balance between having enough links to accurately track the spread of the disease, while not having so many links that the network becomes difficult to interpret. This can be achieved through careful analysis and consideration of the specific disease and context.

Overall, choosing an appropriate distance threshold is an important step in using a transmission network to track the spread of a contagious disease. It can help ensure that the network is useful and informative, and can ultimately aid in efforts to control and prevent the spread of the disease.


  `

</script>

<div class="container">
  <SvelteMarkdown {source} />
</div>
