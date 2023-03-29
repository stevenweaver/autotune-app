## Annotating your HIV-TRACE Results Files

- Run HIV-TRACE

With your FASTA File, execute a command similar to the following. A full list of arguments one can use with HIV-TRACE is provided [here](https://github.com/veg/hivtrace/blob/master/README.md).

`hivtrace -i ./INPUT.FASTA -a resolve -r HXB2_prrt -t .015 -m 500 -g .05 > hivtrace.results.json`

- Annotate your results file

Use the `hivnetworkannotate` script to annotate your results from HIV-TRACE with attributes. The script should already be installed on your machine if you have already installed `hivtrace`.

An example command is:

`hivnetworkannotate -n hivtrace.results.json -a node_attributes.json -g schema.json -r`

Please see the [hivnetworkannotate documentation](https://github.com/veg/hivclustering/wiki/hivnetworkannotate) for more information.

Once the results file has been annotated, please use the [assortativity](/assortativity) page for analysis.
