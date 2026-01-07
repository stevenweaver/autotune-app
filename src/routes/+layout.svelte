<script>
	import header from '../img/twitter-diamond.svg';
	import palmsprings from '../img/palmsprings.png';
  import 'bootstrap/dist/css/bootstrap.min.css';
</script>

<svelte:head>

	<link rel="stylesheet" href="https://observablehq.com/_next/static/css/92c0a8010b575b66.css" />
	<link
		rel="stylesheet"
		href="https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.css"
		integrity="sha384-AfEj0r4/OFrOo5t7NnNe46zW/tFgW6x/bCJG8FqQCEo3+Aro6EYUG4+cU+KJWu/X"
		crossorigin="anonymous"
	/>
	<!-- <link rel="stylesheet" href="https://datamonkey.org/assets/css/datamonkey.css" integrity="sha384-r4NyP46KrjDleawBgD5tp8Y7UzmLA05oM1iAEQ17CSuDqnUK2+k9luXQOfXJCJ4I" crossorigin="anonymous"> -->
	<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Major+Mono+Display" />
	<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fontdiner+Swanky" />
</svelte:head>

<nav style="background-color: #fed7aa; padding: 0.5rem;">
	<a style="border: none; color: black; padding-left: 0.75rem; padding-right: 0.75rem; text-decoration: none;" href="/">
		<img style="height: 2.5rem; width: 2rem; object-fit: scale-down; display: inline; vertical-align: middle;" src={header} alt="AUTO-TUNE logo" />
		<span style="font-family: 'Fontdiner Swanky', cursive; font-size: 20px; padding: 0 0.5rem;">AUTO-TUNE 🎶</span></a
	>
</nav>

<slot />

<footer style="padding: 1rem; margin-top: 0.5rem; background-color: #fed7aa; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; align-items: center; justify-content: space-between;">
	<ul style="display: flex; flex-wrap: wrap; align-items: center; margin: 0.75rem 0 0 0; padding: 0; font-size: 0.875rem; color: #6b7280; list-style: none;">
		<li>
			<a href="http://stevenweaver.org/" style="color: #6b7280;">Steven Weaver</a>
		</li>
	</ul>
</footer>

<style windi:preflights:global>
	.header-logo {
		font-family: 'Fontdiner Swanky';
		font-size: 20px;
		outline: none !important;
		text-decoration: none !important;
		padding: 2px 1px 0;
	}

	:global(h1) {
		@apply text-xxl font-semibold;
	}

	:global(h2) {
		@apply text-xl font-semibold;
    margin-top: 15px;
    margin-bottom: 5px;
	}

	:global(.container h1) {
		@apply text-xxl font-semibold;
		font-size: xx-large;
		margin-top: 15px;
		margin-bottom: 15px;
	}

	:global(a) {
		outline: none;
		text-decoration: none;
		padding: 2px 1px 0;
	}

	:global(a:link) {
		color: teal;
	}

	:global(a:visited) {
		color: teal;
	}

  :global(#annotation ul) {
		@apply font-medium italic underline;
	}

</style>
