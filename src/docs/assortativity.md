## Assortativity

Degree-weighted homophily (DWH) is a measure of similarity between nodes in a
network based on their attributes (such as demographic characteristics or
behaviors) and their degree (i.e., the number of connections they have to other
nodes in the network). It is used to quantify the extent to which nodes with
similar attributes tend to be connected to each other more frequently than
would be expected by chance.

DWH is calculated as the ratio of the observed number of connections between
nodes with similar attributes to the expected number of connections between
such nodes, based on their degree.

In mathematical terms, it is defined as:
$DWH = (W_M + W_C - 2*W_X) / (d_{in}/nodes_{in}/nodes_{in} + d_{out}/nodes_{out}/nodes_{out} )$

Where:
* $W_M$ : Weight of in-group connections
* $W_C$ : Weight of out-group connections
* $W_X$ : Weight of cross-group connections
* $d_{in}$ : In-group degree
* $d_{out}$ : Out-group degree
* $nodes_{in}$ : number of in-group nodes
* $nodes_{out}$ : number of out-group nodes


DWH ranges from -1 to 1. A DWH value of 0 indicates that there is no more homophily than expected with chance, while a value of 1
indicates that there is perfect homophily (e.g. Birds always link to birds). A value of -1 is achieved for perfectly disassortative networks (e.g. Bird never linking with another bird). 


DWH is used in social network analysis and in the study of how different
attributes are related to the formation of connections between individuals. It
is used as a way to measure the similarity of attributes between individuals in
a network.


Please see [Benjamin Golub, Matthew O. Jackson, How Homophily Affects the Speed of Learning and Best-Response Dynamics, The Quarterly Journal of Economics, Volume 127, Issue 3, August 2012, Pages 1287–1338](https://academic.oup.com/qje/article-abstract/127/3/1287/1923572) for more information
