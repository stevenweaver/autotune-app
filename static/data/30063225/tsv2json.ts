import * as R from 'https://deno.land/x/ramda@v0.27.2/mod.ts';
import __ from 'https://deno.land/x/dirname/mod.ts';
import { DB } from 'https://deno.land/x/sqlite/mod.ts';
import { readCSV, writeCSV, readCSVObjects, writeCSVObjects } from 'https://deno.land/x/csv/mod.ts';
import * as d3Dsv from 'https://cdn.skypack.dev/d3-dsv';

const decoder = new TextDecoder();

//const tsv = decoder.decode(Deno.readFileSync('/Users/sweaver/Programming/autotune/papers/kpnet/kpnet-global/data/kp-data.tsv', 'utf-8'));
const tsv = decoder.decode(Deno.readFileSync('./Complete.Set.txt', 'utf-8'));

const data = d3Dsv.tsvParse(tsv);

Deno.writeTextFileSync('./attributes.json', JSON.stringify(data, null, 2));
