import { sveltekit } from '@sveltejs/kit/vite';
import copy from 'rollup-plugin-copy';

/** @type {import('vite').UserConfig} */
const config = {
	plugins: [
    sveltekit(), 
    copy({
      targets: [
        { src: './node_modules/**/files/*.tsv', dest: './node_modules/.vite/deps/files' }
      ]
    })
  ],
  assetsInclude: ['./node_modules/**/files/*.tsv']
};

export default config;
