import { sveltekit } from '@sveltejs/kit/vite';
import WindiCSS from 'vite-plugin-windicss';
import { exec } from 'node:child_process';
import { viteStaticCopy } from 'vite-plugin-static-copy';

/** @type {import('vite').UserConfig} */
const config = {
	plugins: [
		WindiCSS(),
		sveltekit(),
		viteStaticCopy({
			targets: [
				{ src: './node_modules/**/files/*.tsv', dest: 'files' },
				{ src: './node_modules/**/files/*.tsv', dest: './node_modules/.vite/deps/files' }
			]
		})
	]
};

export default config;
