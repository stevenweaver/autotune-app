import adapter from '@sveltejs/adapter-auto';
import preprocess from "svelte-preprocess";
import { windi } from "svelte-windicss-preprocess";

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter()
	},
  preprocess: [
    windi({})
  ]
};

export default config;
