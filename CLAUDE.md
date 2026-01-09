# Claude Development Notes

## Server Management
- **DO NOT** kill or restart dev servers - the user manages these separately
- Avoid using `pkill`, process termination, or `npm run dev` commands
- The user will handle server restarts when needed

## Development Guidelines
- Focus on code changes and functionality
- Let the user handle their own development environment

## Membership-Based Cluster Congruence (Jaccard Index)

### Problem
Cluster IDs are arbitrarily assigned per region. "Cluster 3" in NS2 might contain the exact same nodes as "Cluster 4" in NS3 - comparing IDs causes false negatives.

### Solution: Jaccard Similarity of Cluster-Mates
Instead of comparing cluster IDs, we compare **who clusters together** across regions.

For each node in each region, we collect its "cluster-mates" (other nodes in the same cluster). Then we calculate pairwise Jaccard similarity:

```
Jaccard = |intersection| / |union|
```

**Example:**
- In E2, node X clusters with: {A, B, C, D}
- In NS3, node X clusters with: {A, B, C, E}
- Intersection = {A, B, C} = 3 nodes
- Union = {A, B, C, D, E} = 5 nodes
- Jaccard = 3/5 = 0.6

The final `membership_jaccard` score is the **average** of all pairwise region comparisons across recommended regions (E2, NS2, NS3, NS5B).

### Interpretation
- **J ≥ 0.8**: Congruent - node clusters with ~80%+ same people across regions
- **J 0.5-0.8**: Moderate consistency
- **J < 0.5**: Low consistency - different cluster-mates per region
- **N/A**: Insufficient data (node present in < 2 recommended regions)

### Key Files
- `scripts/annotate_networks.py`: Calculates Jaccard and adds to annotations
- `src/lib/NetworkViewer.svelte`: Displays Jaccard-based congruence in UI
- `src/lib/regionClassification.js`: Defines recommended regions

### Recommended Regions
E2, NS2, NS3, NS5B - these produce distinct clusters with balanced sizes and cross-region stability.