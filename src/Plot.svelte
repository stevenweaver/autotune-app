<script>
	import * as Plot from '@observablehq/plot';

	export let options;
	export let eventL;

	function myplot(node) {

    let plot = Plot.plot(options);
		node.appendChild(plot);
    plot.addEventListener("input", eventL);

	}
</script>

{#key options}
	<div use:myplot {...$$restProps} />
{/key}
