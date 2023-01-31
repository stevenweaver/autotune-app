import * as R from "https://deno.land/x/ramda@v0.27.2/mod.ts";    
import  __ from 'https://deno.land/x/dirname/mod.ts';    
import { DB } from "https://deno.land/x/sqlite/mod.ts";    
import { readCSV, writeCSV, readCSVObjects, writeCSVObjects } from "https://deno.land/x/csv/mod.ts";    
import { pooledMap } from "https://deno.land/std/async/mod.ts";    
import { parse } from "https://deno.land/x/xml/mod.ts";

const decoder = new TextDecoder();
const xml = decoder.decode(Deno.readFileSync('sequence.xml', 'utf-8'));
const data = parse(xml);

function getMetadata(item) {
  // "Seq-entry_set": {
  //   "Bioseq-set": {
  //     "Bioseq-set_class": [Object],
  //     "Bioseq-set_descr"

  let accessionID = item["Seq-entry_set"]["Bioseq-set"]["Bioseq-set_seq-set"]["Seq-entry"][0]["Seq-entry_seq"].Bioseq.Bioseq_id["Seq-id"][0]["Seq-id_genbank"]["Textseq-id"]["Textseq-id_accession"];

  let bioSource = item["Seq-entry_set"]["Bioseq-set"]["Bioseq-set_descr"]["Seq-descr"]["Seqdesc"]["Seqdesc_source"]["BioSource"];
  let orgMods = bioSource["BioSource_org"]["Org-ref"]["Org-ref_orgname"]["OrgName"]["OrgName_mod"]["OrgMod"];
  let subTypes =  bioSource["BioSource_subtype"]["SubSource"];

  let natHost = R.filter(orgMod => orgMod["OrgMod_subtype"]["@value"] == "nat-host", orgMods)[0]["OrgMod_subname"];

  let genoType = R.filter(subType => subType["SubSource_subtype"]["@value"] == "genotype", subTypes)[0]["SubSource_name"];
  let country = R.filter(subType => subType["SubSource_subtype"]["@value"] == "country", subTypes)[0]["SubSource_name"];
  let collectionDate = R.filter(subType => subType["SubSource_subtype"]["@value"] == "collection-date", subTypes)[0]["SubSource_name"];
  let riskGroup = R.filter(subType => subType["SubSource_subtype"]["@value"] == "other", subTypes)[0]["SubSource_name"];
  
  let attributes = {
    "accessionID" : accessionID,
    "natHost" : natHost,
    "genoType" : genoType,
    "country" : country,
    "collectionDate" : collectionDate,
    "riskGroup" : riskGroup
  }

  console.log(attributes);
  return attributes;

}

let items = data['Bioseq-set']["Bioseq-set_seq-set"]["Seq-entry"]["Seq-entry_set"]["Bioseq-set"]["Bioseq-set_seq-set"]["Seq-entry"];

let attributes = R.map(getMetadata, items)
Deno.writeTextFileSync('./attributes.json', JSON.stringify(attributes));
