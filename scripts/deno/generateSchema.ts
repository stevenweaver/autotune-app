import * as R from "https://deno.land/x/ramda@v0.27.2/mod.ts";
import  __ from 'https://deno.land/x/dirname/mod.ts';
import { DB } from "https://deno.land/x/sqlite/mod.ts";
import { readCSV, writeCSV, readCSVObjects, writeCSVObjects } from "https://deno.land/x/csv/mod.ts";
import * as d3Dsv from "https://cdn.skypack.dev/d3-dsv";

function mapKey(key) {
  return {
      "type" : "String",
      "label" : key,
  }
}

const decoder = new TextDecoder();

const data = decoder.decode(Deno.readFileSync('./attributes.json', 'utf-8'));
const attributes = JSON.parse(data);

let keys = R.keys(attributes[0]);

let schema = R.zipObj(keys, R.map(mapKey, keys));

Deno.writeTextFileSync('./schema.json', JSON.stringify(schema, null, 2));
