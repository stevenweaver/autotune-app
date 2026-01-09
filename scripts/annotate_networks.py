#!/usr/bin/env python3
"""
Annotate hivtrace network JSON files with cross-region cluster membership.

This script adds patient_attributes to each node indicating:
- main_cluster_congruent: Whether the node is always in cluster 1 across all regions
- regions_present: How many regions the node appears in
- cluster_in_{region}: The cluster ID in each other region (for comparison)

Usage:
    python annotate_networks.py --genotype 1a --threshold 0.2 --results-dir ./results
"""

import json
import csv
import os
import argparse
from collections import defaultdict
from itertools import combinations


REGIONS = ['core', 'e1', 'e2', 'ns2', 'ns3', 'ns4a', 'ns4b', 'ns5a', 'ns5b', 'p7', 'whole']

# Recommended regions for epidemiological clustering (from manuscript findings)
# These regions produce distinct clusters with balanced R1/R2 ratios and cross-region stability
RECOMMENDED_REGIONS = ['e2', 'ns2', 'ns3', 'ns5b']

# Minimum Jaccard similarity threshold for membership congruence
JACCARD_THRESHOLD = 0.8


def jaccard_similarity(set_a, set_b):
    """Calculate Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 1.0  # Both empty = identical
    if not set_a or not set_b:
        return 0.0  # One empty, one not = no similarity
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def collect_cluster_membership(results_dir, genotype, threshold):
    """Collect cluster membership (set of cluster-mates) for each node across regions."""
    node_cluster_mates = defaultdict(dict)  # node_id -> {region: set of cluster_mates}

    for region in REGIONS:
        filepath = os.path.join(results_dir, f"{genotype}_{threshold}_{region}.hivtrace.json")
        if os.path.exists(filepath):
            with open(filepath) as f:
                data = json.load(f)

            # Build cluster -> nodes map
            cluster_nodes = defaultdict(set)
            for node in data.get("Nodes", []):
                node_id = node["id"]
                # Skip region reference nodes
                if node_id == region or node_id.endswith(f"_{region}"):
                    continue
                cluster_id = node.get("cluster")
                if cluster_id is not None:
                    cluster_nodes[cluster_id].add(node_id)

            # For each node, store its cluster-mates
            for node in data.get("Nodes", []):
                node_id = node["id"]
                # Skip region reference nodes
                if node_id == region or node_id.endswith(f"_{region}"):
                    continue
                cluster_id = node.get("cluster")
                if cluster_id is not None:
                    # Cluster-mates = all nodes in same cluster, excluding self
                    cluster_mates = cluster_nodes[cluster_id] - {node_id}
                    node_cluster_mates[node_id][region] = cluster_mates
                else:
                    # Singleton - no cluster-mates
                    node_cluster_mates[node_id][region] = set()

    return node_cluster_mates


def calculate_membership_jaccard(node_cluster_mates, node_id, regions):
    """Calculate average Jaccard similarity of cluster-mates across regions."""
    region_mates = {r: node_cluster_mates[node_id].get(r) for r in regions}

    # Get regions where node has cluster data
    available_regions = [r for r in regions if region_mates.get(r) is not None]

    if len(available_regions) < 2:
        return None  # Can't compare with fewer than 2 regions

    # Calculate pairwise Jaccard similarities
    similarities = []
    for i, r1 in enumerate(available_regions):
        for r2 in available_regions[i+1:]:
            sim = jaccard_similarity(region_mates[r1], region_mates[r2])
            similarities.append(sim)

    if not similarities:
        return None

    return sum(similarities) / len(similarities)


def count_congruent_regions(node_cluster_mates, node_id, regions, threshold=0.8):
    """Count how many regions have mutually congruent cluster membership.

    Returns the size of the largest set of regions where all pairwise
    Jaccard similarities >= threshold.
    """
    region_mates = {r: node_cluster_mates[node_id].get(r) for r in regions}

    # Get regions where node has non-empty cluster data (actually clustered, not singleton)
    available_regions = [r for r in regions
                        if region_mates.get(r) is not None and len(region_mates.get(r, set())) > 0]

    if len(available_regions) < 2:
        return len(available_regions)  # 0 or 1 region = that many congruent

    # Build adjacency: which regions are congruent with each other?
    congruent_pairs = set()
    for i, r1 in enumerate(available_regions):
        for r2 in available_regions[i+1:]:
            sim = jaccard_similarity(region_mates[r1], region_mates[r2])
            if sim >= threshold:
                congruent_pairs.add((r1, r2))

    # Find largest clique of mutually congruent regions
    # For 4 regions, we can just check all subsets
    max_congruent = 1  # At minimum, each region is congruent with itself

    for size in range(len(available_regions), 1, -1):
        for subset in combinations(available_regions, size):
            # Check if all pairs in this subset are congruent
            all_congruent = True
            for i, r1 in enumerate(subset):
                for r2 in subset[i+1:]:
                    pair = (r1, r2) if r1 < r2 else (r2, r1)
                    if pair not in congruent_pairs and (r2, r1) not in congruent_pairs:
                        # Check directly
                        sim = jaccard_similarity(region_mates[r1], region_mates[r2])
                        if sim < threshold:
                            all_congruent = False
                            break
                if not all_congruent:
                    break

            if all_congruent:
                return size  # Found largest clique

    return max_congruent


def collect_cross_region_clusters(results_dir, genotype, threshold):
    """Collect cluster membership for each node across all regions."""
    node_clusters = defaultdict(dict)

    for region in REGIONS:
        filepath = os.path.join(results_dir, f"{genotype}_{threshold}_{region}.hivtrace.json")
        if os.path.exists(filepath):
            with open(filepath) as f:
                data = json.load(f)
            for node in data.get("Nodes", []):
                node_id = node["id"]
                # Skip region reference nodes
                if node_id == region or node_id.endswith(f"_{region}"):
                    continue
                node_clusters[node_id][region] = node.get("cluster")

    return node_clusters


def create_annotations(node_clusters, node_cluster_mates):
    """Create annotation dictionary from cross-region cluster data.

    Uses membership-based congruence: compares which nodes cluster together
    across regions using Jaccard similarity, rather than comparing cluster IDs.
    """
    annotations = {}

    for node_id, clusters in node_clusters.items():
        regions_present = len([r for r in REGIONS if r in clusters])
        cluster_values = [c for c in clusters.values() if c is not None]
        all_main = all(c == 1 for c in cluster_values) if cluster_values else False

        # Count how many recommended regions have congruent cluster membership
        congruent_region_count = count_congruent_regions(
            node_cluster_mates, node_id, RECOMMENDED_REGIONS, JACCARD_THRESHOLD
        )

        # Calculate membership-based congruence using Jaccard similarity
        # This compares which nodes cluster together, not cluster ID numbers
        membership_jaccard = calculate_membership_jaccard(
            node_cluster_mates, node_id, RECOMMENDED_REGIONS
        )

        # Node is congruent if average Jaccard >= threshold (0.8)
        # None means insufficient data to compare
        if membership_jaccard is not None:
            recommended_congruent = membership_jaccard >= JACCARD_THRESHOLD
        else:
            recommended_congruent = False

        annotations[node_id] = {
            "main_cluster_congruent": "Yes" if all_main else "No",
            "recommended_congruent": "Yes" if recommended_congruent else "No",
            "membership_jaccard": round(membership_jaccard, 3) if membership_jaccard is not None else None,
            "regions_present": regions_present,
            "congruent_region_count": congruent_region_count,
            "clusters": clusters
        }

    return annotations


def annotate_network_file(filepath, annotations, output_path=None):
    """Add cross-region annotations to a network JSON file."""
    with open(filepath) as f:
        data = json.load(f)

    # Determine current region from filename
    basename = os.path.basename(filepath)
    current_region = None
    for r in REGIONS:
        if f"_{r}." in basename:
            current_region = r
            break

    # Define the patient_attribute_schema
    schema = {
        "main_cluster_congruent": {
            "label": "Main Cluster Congruent",
            "type": "String"
        },
        "recommended_congruent": {
            "label": "Membership Congruent (Jaccard >= 0.8)",
            "type": "String"
        },
        "membership_jaccard": {
            "label": "Membership Jaccard Similarity",
            "type": "Number"
        },
        "regions_present": {
            "label": "Regions Present",
            "type": "Number"
        },
        "congruent_region_count": {
            "label": "Congruent Regions (of 4)",
            "type": "Number"
        }
    }

    # Add cluster comparison attributes for other regions
    for region in REGIONS:
        if region != current_region:
            # Add (Recommended) suffix for recommended regions
            suffix = " (Recommended)" if region in RECOMMENDED_REGIONS else ""
            schema[f"cluster_in_{region}"] = {
                "label": f"Cluster in {region.upper()}{suffix}",
                "type": "String"
            }

    data["patient_attribute_schema"] = schema

    # Add patient_attributes to each node
    for node in data.get("Nodes", []):
        node_id = node["id"]
        if node_id in annotations:
            ann = annotations[node_id]
            patient_attrs = {
                "main_cluster_congruent": ann["main_cluster_congruent"],
                "recommended_congruent": ann["recommended_congruent"],
                "membership_jaccard": ann["membership_jaccard"],
                "regions_present": ann["regions_present"],
                "congruent_region_count": ann["congruent_region_count"]
            }

            # Add cluster IDs from other regions
            for region in REGIONS:
                if region != current_region:
                    cluster_val = ann["clusters"].get(region)
                    patient_attrs[f"cluster_in_{region}"] = str(cluster_val) if cluster_val is not None else "N/A"

            node["patient_attributes"] = patient_attrs

    # Write output
    if output_path is None:
        output_path = filepath.replace(".hivtrace.json", ".annotated.json")

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Annotate hivtrace networks with cross-region cluster data")
    parser.add_argument("--genotype", "-g", required=True, help="Genotype (e.g., 1a)")
    parser.add_argument("--threshold", "-t", required=True, help="Threshold (e.g., 0.2)")
    parser.add_argument("--results-dir", "-d", default="./results", help="Results directory")
    parser.add_argument("--output-suffix", "-o", default=".annotated", help="Suffix for output files")
    parser.add_argument("--inplace", "-i", action="store_true", help="Modify files in place")
    args = parser.parse_args()

    print(f"Collecting cross-region cluster data for {args.genotype} @ {args.threshold}...")
    node_clusters = collect_cross_region_clusters(args.results_dir, args.genotype, args.threshold)
    print(f"Found {len(node_clusters)} unique nodes across regions")

    print(f"Collecting cluster membership data for Jaccard comparison...")
    node_cluster_mates = collect_cluster_membership(args.results_dir, args.genotype, args.threshold)

    annotations = create_annotations(node_clusters, node_cluster_mates)
    main_count = sum(1 for a in annotations.values() if a["main_cluster_congruent"] == "Yes")
    recommended_count = sum(1 for a in annotations.values() if a["recommended_congruent"] == "Yes")

    # Calculate average Jaccard for nodes that have it
    jaccard_values = [a["membership_jaccard"] for a in annotations.values() if a["membership_jaccard"] is not None]
    avg_jaccard = sum(jaccard_values) / len(jaccard_values) if jaccard_values else 0

    print(f"Nodes always in main cluster (all regions): {main_count}/{len(annotations)}")
    print(f"Nodes membership-congruent (Jaccard >= 0.8): {recommended_count}/{len(annotations)}")
    print(f"Average membership Jaccard similarity: {avg_jaccard:.3f}")

    # Annotate each region's network file
    for region in REGIONS:
        filepath = os.path.join(args.results_dir, f"{args.genotype}_{args.threshold}_{region}.hivtrace.json")
        if os.path.exists(filepath):
            if args.inplace:
                output_path = filepath
            else:
                output_path = filepath.replace(".hivtrace.json", f"{args.output_suffix}.json")

            annotate_network_file(filepath, annotations, output_path)
            print(f"  Annotated: {os.path.basename(output_path)}")

    print("Done!")


if __name__ == "__main__":
    main()
