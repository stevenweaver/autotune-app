// mdsvex.config.js
import remarkMath from 'remark-math';
import rehypeKatexSvelte from 'rehype-katex-svelte';

export default {
	extensions: ['.svx', '.md'],
	remarkPlugins: [remarkMath],
	rehypePlugins: [rehypeKatexSvelte]
};
