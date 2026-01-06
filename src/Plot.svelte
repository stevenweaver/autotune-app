<script>
	import * as Plot from '@observablehq/plot';

	export let options;
	export let eventL = null;

	function myplot(node) {
		if (!options || Object.keys(options).length === 0) return;

		let plot = Plot.plot(options);
		node.appendChild(plot);

		if (eventL) {
			plot.addEventListener("input", eventL);
		}

		return {
			destroy() {
				plot.remove();
			}
		};
	}
</script>

{#key options}
	<div use:myplot {...$$restProps} />
{/key}
