<script>
	import header from '../img/twitter-diamond.svg';
	import palmsprings from '../img/palmsprings.png';
</script>

<div class="bg-container" style="background-image: url({palmsprings})">
	<div class="container bg-slate-100/40">
		<div class="grid grid-rows-2 grid-cols-6 pt-4">
			<div class="col-start-2 col-span-4 row-span-1">
				<h1 class="text-6xl">✴ Welcome to ✴</h1>
				<h1 class="text-7xl">🎶 AUTO-TUNE 🎶</h1>
			</div>
			<div class="col-start-4 col-span-6 row-span-1">
				<h4 class="text-xl">
					<i>By Datamonkey </i><img class="object-scale-down h-10 w-8 inline" src={header} />
				</h4>
			</div>
		</div>

		<div class="items-center">
			<ul class="col-span-6 p-2">
				<li class="border-gray-400 mb-2"><a href="analyze">Analyze your Own Results</a></li>
				<li class="border-gray-400 mb-2"><a href="assortativity">Assortativity</a></li>
				<li class="border-gray-400 mb-2"><a href="subsample">Subsampling</a></li>
				<li class="border-gray-400 mb-2"><a href="lanl">LANL</a></li>
				<!-- <li><a href="combos">Combos</li> -->
				<!-- <li class="border-gray-400 mb-2"><a href="mexico">Mexico</li> -->
				<li class="border-gray-400 mb-2"><a href="china">China</a></li>
				<li class="border-gray-400 mb-2"><a href="papers">Papers</a></li>
				<!-- <li><a href="singles">Singles</li> -->
				<li class="border-gray-400 mb-2"><a href="about">About</a></li>
			</ul>
		</div>
	</div>
</div>

<style>
	.container {
		font-family: 'Fontdiner Swanky';
		font-size: x-large;
	}

	.bg-container {
		background-image: var(--background-image);
		background-repeat: repeat-x;
		background-size: cover;
		padding: 0px;
		margin: 0px;
		height: 100%;
		width: 100%;
		max-width: 100% !important;
		max-height: 100% !important;
		min-height: 100vh !important;
	}

	.container {
		opacity: 1;
		min-height: 100vh;
		max-width: 100% !important;
		width: 100%;
	}

	.container :global(a) {
		outline: none;
		text-decoration: none;
		padding: 2px 1px 0;
	}

	.container :global(a:link) {
		color: black;
	}

	.container :global(a:visited) {
		color: black;
	}
</style>
