<svelte:head>
  <link rel="stylesheet" href="https://observablehq.com/_next/static/css/92c0a8010b575b66.css">
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/5.0.0-alpha1/css/bootstrap.min.css" integrity="sha384-r4NyP46KrjDleawBgD5tp8Y7UzmLA05oM1iAEQ17CSuDqnUK2+k9luXQOfXJCJ4I" crossorigin="anonymous">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.css" integrity="sha384-AfEj0r4/OFrOo5t7NnNe46zW/tFgW6x/bCJG8FqQCEo3+Aro6EYUG4+cU+KJWu/X" crossorigin="anonymous">
  <!-- <link rel="stylesheet" href="https://datamonkey.org/assets/css/datamonkey.css" integrity="sha384-r4NyP46KrjDleawBgD5tp8Y7UzmLA05oM1iAEQ17CSuDqnUK2+k9luXQOfXJCJ4I" crossorigin="anonymous"> -->
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Major+Mono+Display">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fontdiner+Swanky">
</svelte:head>

<script>
  import header from '../img/twitter-diamond.svg'
</script>

<nav class="bg-orange-200 p-2">
   <a class="border-none text-black px-3" href="/"> <img class="object-scale-down h-10 w-8 inline" src={header} /> <span class="header-logo px-2">AUTO-TUNE 🎶</span></a>
</nav>

<slot></slot>

<footer class="p-4 mt-2 bg-orange-200 rounded-lg shadow md:flex md:items-center md:justify-between md:p-6 dark:bg-gray-800">
    <span class="text-sm text-gray-500 sm:text-center dark:text-gray-400">2023 <a href="http://stevenweaver.org/" class="hover:underline">Steven Weaver</a>. All Rights Reserved.
    </span>
    <ul class="flex flex-wrap items-center mt-3 text-sm text-gray-500 dark:text-gray-400 sm:mt-0">
        <li>
            <a href="#" class="mr-4 hover:underline md:mr-6">Careers</a>
        </li>
        <li>
            <a href="http://stevenweaver.org/" class="hover:underline">Steven Weaver</a>
        </li>
    </ul>
</footer>

<style windi:preflights:global>

  .header-logo {
    font-family:"Fontdiner Swanky";
    font-size: 20px;
  }

  :global(h1) {
      @apply text-xxl font-semibold;
  }

  :global(h2) {
      @apply text-xl font-semibold;
  }

</style>
