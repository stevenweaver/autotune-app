import * as R from 'https://deno.land/x/ramda@v0.27.2/mod.ts';
import __ from 'https://deno.land/x/dirname/mod.ts';
import { DB } from 'https://deno.land/x/sqlite/mod.ts';
import { readCSV, writeCSV, readCSVObjects, writeCSVObjects } from 'https://deno.land/x/csv/mod.ts';
import * as d3Dsv from 'https://cdn.skypack.dev/d3-dsv';
import * as d3 from 'https://cdn.skypack.dev/d3';

const tn93Fn = Deno.args[0];
const decoder = new TextDecoder();

//const tsv = decoder.decode(Deno.readFileSync('/Users/sweaver/Programming/autotune/papers/kpnet/kpnet-global/data/kp-data.tsv', 'utf-8'));
const csv = decoder.decode(Deno.readFileSync(tn93Fn, 'utf-8'));
const data = d3Dsv.csvParse(csv, d3Dsv.autoType);

// mean, median, max, min, standard deviation, possibly histogram
const distances = R.map((d) => d.Distance, data);

let stats = {
	min: d3.min(distances),
	max: d3.max(distances),
	mean: d3.mean(distances),
	median: d3.median(distances),
	std: d3.deviation(distances),
	histogram: d3.bin()(distances)
};

console.log(JSON.stringify(stats, null, 2));
// Deno.writeTextFileSync('./attributes.json', JSON.stringify(data, null, 2));
