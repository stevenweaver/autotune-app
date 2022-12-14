<svelte:head>
  <link rel="stylesheet" href="https://observablehq.com/_next/static/css/92c0a8010b575b66.css">
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/5.0.0-alpha1/css/bootstrap.min.css" integrity="sha384-r4NyP46KrjDleawBgD5tp8Y7UzmLA05oM1iAEQ17CSuDqnUK2+k9luXQOfXJCJ4I" crossorigin="anonymous">
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

<style windi:preflights:global>

  .header-logo {
    font-family:"Fontdiner Swanky";
    font-size: 20px;
  }

  h1 {
      @apply text-xl font-semibold;
  }


</style>
