import { sveltekit } from '@sveltejs/kit/vite';

/** @type {import('vite').UserConfig} */
const config = {
	plugins: [
		sveltekit()
	],
	optimizeDeps: {
		exclude: ['hyphy-scope', 'hivtrace-viz']
	},
	ssr: {
		external: ['hyphy-scope', 'hivtrace-viz']
	}
};

export default config;
