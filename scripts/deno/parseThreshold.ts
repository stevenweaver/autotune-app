import * as R from "https://deno.land/x/ramda@v0.27.2/mod.ts";
import  __ from 'https://deno.land/x/dirname/mod.ts';
import { DB } from "https://deno.land/x/sqlite/mod.ts";
import { readCSV, writeCSV, readCSVObjects, writeCSVObjects } from "https://deno.land/x/csv/mod.ts";
import * as d3Dsv from "https://cdn.skypack.dev/d3-dsv";

const thresholdFn = Deno.args[0];

const decoder = new TextDecoder();
let threshold = '';

//const tsv = decoder.decode(Deno.readFileSync('/Users/sweaver/Programming/autotune/papers/kpnet/kpnet-global/data/kp-data.tsv', 'utf-8'));
const threshold_text = decoder.decode(Deno.readFileSync(thresholdFn, 'utf-8'));

// Check for Multiple thresholds 
if (R.includes("Multiple candidate thresholds")) {
  let txt = R.replace(/ +/g,' ', threshold_text)
  threshold = R.split("Multiple candidate thresholds: %s ")(txt)[1].split(' ')[0].trim();
} else {
  try {
    threshold = R.split('guess ')(threshold_text)[1].split(' (')[0];
  } catch (e) {
    // Remove spaces
    let txt = R.replace(/ +/g,' ', threshold_text)
    threshold = R.split('Selected distance threshold of')(txt)[1].split('\n')[0].trim()
  }
}

console.log(threshold);
