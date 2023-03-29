<script>
	import { onMount, beforeUpdate } from 'svelte';
	import About from '../../docs/about.md';
	import Assortativity from '../../docs/assortativity.md';
	import HIVTRACEInstructions from '../../docs/hivtrace_instructions.md';
</script>

<div class="container">
	<About />
	<div id="assortativity">
		<Assortativity />
	</div>
	<div id="annotation">
		<HIVTRACEInstructions />
	</div>
</div>

<style>
	.container :global(p) {
		margin-bottom: 10px;
	}

	.container :global(ul) {
		margin-bottom: 10px;
	}

	.container {
		margin-top: 15px;
	}

	div :global(.container h1) {
		@apply text-xxl font-semibold;
		font-size: xx-large;
		margin-top: 15px;
		margin-bottom: 15px;
	}

	div :global(.container h2) {
		margin-top: 15px;
		margin-bottom: 15px;
	}

	div :global(ol) {
		list-style-type: decimal;
		margin-left: 20px;
	}

	div :global(a) {
		outline: none;
		text-decoration: none;
		padding: 2px 1px 0;
	}

	div :global(a:link) {
		color: teal;
	}

	div :global(a:visited) {
		color: teal;
	}

	div :global(a:focus) {
		border-bottom: 1px solid;
		background: #bae498;
	}

	div :global(a:hover) {
		border-bottom: 1px solid;
		background: #cdfeaa;
	}

	div :global(a:active) {
		background: #265301;
		color: #cdfeaa;
	}

	div :global(li > ol) {
		list-style-type: lower-alpha;
		margin-left: 20px;
	}
</style>
