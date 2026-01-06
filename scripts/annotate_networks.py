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


REGIONS = ['core', 'e1', 'e2', 'ns2', 'ns3', 'ns4a', 'ns4b', 'ns5a', 'ns5b', 'p7']

# Recommended regions for epidemiological clustering (from manuscript findings)
# These regions produce distinct clusters with balanced R1/R2 ratios and cross-region stability
RECOMMENDED_REGIONS = ['e1', 'e2', 'ns2', 'ns3', 'ns5b']


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


def create_annotations(node_clusters):
    """Create annotation dictionary from cross-region cluster data."""
    annotations = {}

    for node_id, clusters in node_clusters.items():
        regions_present = len([r for r in REGIONS if r in clusters])
        cluster_values = [c for c in clusters.values() if c is not None]
        all_main = all(c == 1 for c in cluster_values) if cluster_values else False

        # Check recommended regions congruence (same cluster across all recommended regions)
        recommended_clusters = {r: c for r, c in clusters.items()
                                if r in RECOMMENDED_REGIONS and c is not None}
        recommended_regions_present = len(recommended_clusters)

        if recommended_clusters:
            cluster_values_recommended = list(recommended_clusters.values())
            # Congruent if all clusters are the same (regardless of which cluster number)
            recommended_congruent = len(set(cluster_values_recommended)) == 1
        else:
            recommended_congruent = False

        annotations[node_id] = {
            "main_cluster_congruent": "Yes" if all_main else "No",
            "recommended_congruent": "Yes" if recommended_congruent else "No",
            "regions_present": regions_present,
            "recommended_regions_present": recommended_regions_present,
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
            "label": "Recommended Regions Congruent",
            "type": "String"
        },
        "regions_present": {
            "label": "Regions Present",
            "type": "Number"
        },
        "recommended_regions_present": {
            "label": "Recommended Regions Present",
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
                "regions_present": ann["regions_present"],
                "recommended_regions_present": ann["recommended_regions_present"]
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

    annotations = create_annotations(node_clusters)
    main_count = sum(1 for a in annotations.values() if a["main_cluster_congruent"] == "Yes")
    recommended_count = sum(1 for a in annotations.values() if a["recommended_congruent"] == "Yes")
    print(f"Nodes always in main cluster (all regions): {main_count}/{len(annotations)}")
    print(f"Nodes congruent in recommended regions (E1,E2,NS2,NS3,NS5B): {recommended_count}/{len(annotations)}")

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
