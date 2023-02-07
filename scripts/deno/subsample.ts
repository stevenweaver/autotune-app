import * as R from "https://deno.land/x/ramda@v0.27.2/mod.ts";    
import  __ from 'https://deno.land/x/dirname/mod.ts';    
import { DB } from "https://deno.land/x/sqlite/mod.ts";    
import { readCSV, writeCSV, readCSVObjects, writeCSVObjects } from "https://deno.land/x/csv/mod.ts";    
import { pooledMap } from "https://deno.land/std/async/mod.ts";    
import { parse } from "https://deno.land/std/flags/mod.ts"

import * as d3Dsv from "https://cdn.skypack.dev/d3-dsv";

const decoder = new TextDecoder();
const csv = decoder.decode(Deno.readFileSync('counts.csv', 'utf-8'));
const data = d3Dsv.csvParse(csv);

function runSeqSample(item) {

  let fasta = item.year + ".fasta";

  let twentyFive = item["25"];
  let fifty = item["50"];
  let seventyFive = item["75"];

  let twentyFiveFasta = item.year + ".25.fasta";
  let fiftyFasta = item.year + ".50.fasta";
  let seventyFiveFasta = item.year + ".75.fasta";



  //const twentyFiveCmd = ["seqsample", "--fasta", fasta, "--number", twentyFive, ">", twentyFiveFasta].join(" ");
  //const fiftyCmd = ["seqsample", "--fasta", fasta, "--number", fifty, ">", fiftyFasta].join(" ");
  //const seventyFiveCmd = ["seqsample", "--fasta", fasta, "--number", seventyFive, ">", seventyFiveFasta].join(" ");

  const twentyFiveCmd = ["tn93", "-t", "0.025", twentyFiveFasta, ">", item.year + ".25.tn93.csv"].join(" ");
  const fiftyCmd = ["tn93", "-t", "0.025", fiftyFasta, ">", item.year + ".50.tn93.csv"].join(" ");
  const seventyFiveCmd = ["tn93", "-t", "0.025", seventyFiveFasta, ">", item.year + ".75.tn93.csv"].join(" ");

  console.log(twentyFiveCmd);
  console.log(fiftyCmd);
  console.log(seventyFiveCmd);
  return true;


}

R.forEach(runSeqSample, data)

