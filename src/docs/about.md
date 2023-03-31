# About

Choosing an appropriate distance threshold is an important part of inferring a transmission network to determine the relative growth of clusters within a localized epidemic. This distance threshold determines how close two consensus sequences must be in order for a link to be created between them in the network. Using a distance threshold that is too high can result in a network with many unnecessary links, making it difficult to interpret and analyze. On the other hand, using a distance threshold that is too low can result in a network with too few links, which may not capture key insights into rapidly growing clusters among patients with shared attributes that could benefit from public health intervention measures.

Here, we present a heuristic scoring approach for tuning a distance threshold by associating each tested threshold against the maximal number of clusters created across all thresholds and the difference between the ratio ($R_{12}$) of the largest cluster in the network to the second largest cluster at each iteration. The number of clusters is normalized between $[0,1]$ then gated via a Gompertz function transform. Meanwhile, the distribution of all $R_{12}$ ratios are converted to $Z$ scores, and normalized relative to the largest positive $Z$ score across all candidate distances. The priority score is the sum of aforementioned two components.

Published research using the HIV-TRACE software package frequently use the default threshold of 1.5% for HIV pol gene sequences. We apply our scoring heuristic to outbreaks with different characteristics, such as regional or temporal variability, and demonstrate the utility of using the scoring mechanism's suggested distance threshold to identify clusters exhibiting risk factors that would have otherwise been more difficult to identify, such as a transmission network transitioning from primarily IDU transmission to MSM. Such identification may allow best intervention practices by respective public health officials.

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
   2. The number of clusters, $C_i$ at threshold $d_L^i$ is first normalized to $[0,1]$ through $\frac{{C_{max} - C_i}}{{C_{max} -C_{min}}}$ and next gated via a Gompertz function transform ${1-e}^{-e^{-25x+3}}$ This function provides an ad hoc means for penalizing having too few clusters relative to the maximum over all ranges. For example, a threshold that yields $95\%$ of the maximal number of clusters receives a score of $0.996$, while a threshold that yields $85\%$ - a score of $0.376$.
   3. The priority score for $d_L^i$ is the sum of the two components defined in (a) and (b).

3. The threshold with the highest priority score will be selected as the suggested automatic distance threshold, if the score is high enough ($1.9$ or more), and either of the two conditions hold.
   1. No other thresholds have priority scores of $1.9$ or higher
   2. If other thresholds have priority scores of $1.9$ or higher, then the range of thresholds represented by these options is small (no more than $log(N)$ times the mean step between successive $d_L^i$).
4. If no single threshold can be selected in step 3, then the one with the highest priority score is suggested, and an inspection of the plot like the one on the analyze page is recommended to ensure that the threshold is sensible.
