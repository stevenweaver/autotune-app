import adapter from '@sveltejs/adapter-auto';
import preprocess from "svelte-preprocess";
import { windi } from "svelte-windicss-preprocess";
import { mdsvex } from 'mdsvex'
import mdsvexConfig from "./mdsvex.config.js";

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter()
	},
  extensions: ['.svelte', '.svx', '.md'],
  preprocess: [
    windi({}),
    mdsvex(mdsvexConfig)
  ]
};

export default config;
