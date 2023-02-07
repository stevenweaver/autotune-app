import * as R from "https://deno.land/x/ramda@v0.27.2/mod.ts";
import  __ from 'https://deno.land/x/dirname/mod.ts';
import { DB } from "https://deno.land/x/sqlite/mod.ts";
import { readCSV, writeCSV, readCSVObjects, writeCSVObjects } from "https://deno.land/x/csv/mod.ts";
import { pooledMap } from "https://deno.land/std/async/mod.ts";
import genbankParser from 'https://cdn.skypack.dev/genbank-parser';

function getMetadata(item) {

  let accessionID = item["name"];

  let featureNotes = item.features[0]["notes"];

  let natHost = featureNotes["host"] && featureNotes["host"][0];
  let country = featureNotes["country"] && featureNotes["country"][0];
  let collectionDate = featureNotes["collection_date"] && featureNotes["collection_date"][0];
  let subtype = featureNotes["note"] && featureNotes["note"][0];
  
  let attributes = {
    "accessionID" : accessionID,
    "natHost" : natHost,
    "country" : country,
    "collectionDate" : collectionDate,
    "subtype" : subtype
  }

  return attributes;

}

const decoder = new TextDecoder();
const genbank = decoder.decode(Deno.readFileSync('./sequence.gb', 'utf-8'));
const items = genbankParser(genbank);

let attributes = R.map(getMetadata, items);

Deno.writeTextFileSync('./attributes.json', JSON.stringify(attributes, null, 2));
