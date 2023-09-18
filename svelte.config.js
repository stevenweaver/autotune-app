//import adapter from '@sveltejs/adapter-auto';
import adapter from '@sveltejs/adapter-static';
import preprocess from 'svelte-preprocess';
import { windi } from 'svelte-windicss-preprocess';
import { mdsvex } from 'mdsvex';
import mdsvexConfig from './mdsvex.config.js';


/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
    appDir:'static',
		adapter: adapter({
      			out: 'build',
      			assets: 'build',
      			precompress: false,
      			envPrefix: 'AUTOTUNE_',
      			polyfill: true
        })
	},
	extensions: ['.svelte', '.svx', '.md'],
	preprocess: [windi({}), mdsvex(mdsvexConfig)]
};

export default config;
