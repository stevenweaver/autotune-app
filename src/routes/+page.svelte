<style>
  .container {
      font-family:"Fontdiner Swanky";
      font-size : x-large;
    }

  .bg-container {
      background-image: url('./src/img/palmsprings.png');
      background-repeat: repeat-x;
      background-size: cover;
      padding: 0px;
      margin: 0px;
      height:100%;
      width:100%;
      max-width: 100% !important;
      max-height: 100% !important;
      min-height: 100vh !important;
    }

  .container {
      opacity: 1.0;
      min-height: 100vh;
      max-width: 100% !important;
      width: 100%;
  }


</style>

<script>
  import header from '../img/twitter-diamond.svg'
</script>

<div class="bg-container">
  <div class="container bg-slate-100/40">

    <div class="grid grid-rows-2 grid-cols-6 pt-4">
      <div class="col-start-2 col-span-4 row-span-1">
        <h1 class="text-6xl">✴ Welcome to ✴</h1>
        <h1 class="text-7xl"> 🎶 AUTO-TUNE 🎶</h1>
      </div>
      <div class="col-start-4 col-span-6 row-span-1">
        <h4 class="text-xl"><i>By Datamonkey </i><img class="object-scale-down h-10 w-8 inline" src={header} /></h4>
      </div>
    </div>

    <div class="items-center">
      <ul class="col-span-6 p-2">
        <li class="border-gray-400 mb-2"><a href="lanl">LANL</li>
        <!-- <li><a href="combos">Combos</li> -->
        <li class="border-gray-400 mb-2"><a href="mexico">Mexico</li>
        <li class="border-gray-400 mb-2"><a href="china">China</li>
        <li class="border-gray-400 mb-2"><a href="papers">Papers</li>
        <!-- <li><a href="singles">Singles</li> -->
        <li class="border-gray-400 mb-2"><a href="about">About</li>
      </ul>
    </div>

  </div>
</div>

