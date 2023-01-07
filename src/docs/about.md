# About

## Introduction
Choosing an appropriate distance threshold is an important part of using a transmission network to track the spread of a contagious disease. This distance threshold determines how close two individuals must be in order for a link to be created between them in the network.
Using a distance threshold that is too small can result in a network with many unnecessary links, making it difficult to interpret and analyze. On the other hand, using a distance threshold that is too large can result in a network with too few links, making it difficult to accurately track the spread of the disease.

To ensure that the transmission network is useful and informative, it is important to carefully consider the appropriate distance threshold. This may vary depending on the specific disease and the context in which it is spreading. For example, a highly contagious respiratory illness may require a smaller distance threshold than a less contagious illness that is primarily spread through direct contact.
In general, the goal is to strike a balance between having enough links to accurately track the spread of the disease, while not having so many links that the network becomes difficult to interpret. This can be achieved through careful analysis and consideration of the specific disease and context.

Overall, choosing an appropriate distance threshold is an important step in using a transmission network to track the spread of a contagious disease. It can help ensure that the network is useful and informative, and can ultimately aid in efforts to control and prevent the spread of the disease.

## Example Usage

To use the algorithm, you first must use a multiple sequence alignment with the [tn93](https://github.com/veg/tn93) fast pairwise distance calculator.
Once a pairwise distance file is created, use the [hivnetworkcsv](https://github.com/veg/hivclustering) script with the -A keyword argument to generate the tab-separated output compatible with this page.

An example workflow is as follows:

```
      ./tn93 -t 0.015 pol.fasta > pairwise_distances.15.tn93.csv
      hivnetworkcsv -i pairwise_distances.15.tn93.csv -f plain -A 0 > autotune_report.tsv
```

## Intepreting Results

Network threshold selection procedure proceeds as follows:

  1. For each candidate threshold $d_L$, in increasing order, ranging from the smallest genetic distance in the dataset, up to either the largest distance or a predetermined maximal threshold, we compute two network statistics: $R_{12}$, the ratio of the largest cluster to the second largest cluster, and $C$ – the number of clusters in the network.

  2. A priority score is assigned to each $d_L$. This score measures two properties of the threshold: Does $R_{12}$ jump at $d_L$? How far is the number of clusters $C$ at $d_L$ from the maximal number of clusters over all threshold values? Let there be $N$ overall $d_L$ candidate values, and assume we are examining the ith candidate, $d_L^i$ with $W < i \leq N - W$ ($W$ is a positive integer defined below).
        1. The $R_{12}$ jump is computed by looking at the normalized ratio of the mean $R_{12}$ values computed over the leading window $d_L^{i+1}…d_L^{i+W}$ and the trailing window $d_L^{i-W}… d_L^{i-1}$. The width of the window, $W$, is defined as $((⌊\frac{N}{100}⌋,3),30)$. The distribution of ratios is converted to $Z$ scores, and normalized relative to the largest positive $Z$ score across all candidate distances, yielding the jump component of the score.
        2. The number of clusters, $C_i$ at threshold $d_L^i$ is first normalized to $[0,1]$ through $\frac{{C_k - C_i}}{{C_k -C_k}}$  and next gated via a Gompertz function transform ${1-e}^{-e^{-25x+3}}$  This function provides an ad hoc means for penalizing having too few clusters relative to the maximum over all ranges. For example, a threshold that yields $95%$ of the maximal number of clusters receives a score of $0.996$, while a threshold that yields $85%$ - a score of 0.376.
        3. The priority score for $d_L^i$ is the sum of the two components defined in (a) and (b).

  3. The threshold with the highest priority score will be selected as the suggested automatic distance threshold, if the score is high enough ($1.9$ or more), and either of the two conditions hold.
        1. No other thresholds have priority scores of $1.9$ or higher
        2. If other thresholds have priority scores of $1.9$ or higher, then the range of thresholds represented by these options is small (no more than $log(N)$ times the mean step between successive $d_L^i$).
  4. If no single threshold can be selected in step 3, then the one with the highest priority score is suggested, and an inspection of the plot like the one on the analyze page is recommended to ensure that the threshold is sensible. 

