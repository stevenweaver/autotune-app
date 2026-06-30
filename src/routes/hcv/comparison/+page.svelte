<script>
  import * as Plot from '@observablehq/plot';
  import RenderPlot from '../../../Plot.svelte';
  import Tooltip from '$lib/Tooltip.svelte';
  import { selectedThreshold, thresholds as thresholdOptions } from '$lib/hcvStore.js';
  import {
    getRegionClassification,
    getClassificationDisplay
  } from '$lib/regionClassification.js';

  import allThresholdsRaw from '../../../data/hcv/autotune/all_thresholds.json';
  import congruenceData from '../../../data/hcv/autotune/network_congruence_analysis.json';

  // Parse all thresholds upfront
  const allThresholds = allThresholdsRaw.map(d => ({
    ...d,
    genotype: d.filename?.split('_')[0]?.split('/')[1],
    consensus: d.filename?.split('_')[1],
    gene: d.filename?.split('_')[2]?.split('.')[0],
    threshold: parseFloat(d.threshold)
  }));

  // Available genotypes for comparison
  const genotypes = ['1a', '1b', '2a', '2b', '3a', '4d'];

  // Selected genotypes for comparison
  let genotype1 = '1a';
  let genotype2 = '4d';

  // Reactive data for each genotype
  $: key1 = `${genotype1}_${$selectedThreshold}`;
  $: key2 = `${genotype2}_${$selectedThreshold}`;

  $: data1 = congruenceData[key1] || {};
  $: data2 = congruenceData[key2] || {};

  $: thresholds1 = allThresholds.filter(d => d.genotype === genotype1 && d.consensus === $selectedThreshold);
  $: thresholds2 = allThresholds.filter(d => d.genotype === genotype2 && d.consensus === $selectedThreshold);

  // The threshold and score in all_thresholds.json come from the per-region
  // *.threshold.json fallback ("best guess" emitted with hasError when AUTO-TUNE
  // finds no strong outlier), which contradicts the networks actually analyzed
  // (issue #7). Resolve them instead from the same authoritative source the rest of
  // the page uses: each network's HIV-TRACE output (Settings.threshold — the
  // threshold the network whose clusters we show was built at) and that threshold's
  // row in the AUTO-TUNE sweep report (its Score). Only regions with a real sweep
  // qualify; where AUTO-TUNE produced no network/sweep the threshold is a non-tune
  // default (e.g. 2a -> 0.005), so it is shown as N/A rather than mislabeled.
  let resolvedMetrics = {};

  function scoreAtThreshold(tsv, threshold) {
    const lines = tsv.trim().split('\n');
    if (lines.length < 2) return null;
    const header = lines[0].split('\t');
    const tIdx = header.indexOf('Threshold');
    const sIdx = header.indexOf('Score');
    if (tIdx === -1 || sIdx === -1) return null;
    for (let i = 1; i < lines.length; i++) {
      const cols = lines[i].split('\t');
      // The network threshold is always one of the swept rows, so match exactly
      // (tolerating only binary float noise).
      if (Math.abs(parseFloat(cols[tIdx]) - threshold) < 1e-9) {
        const score = parseFloat(cols[sIdx]);
        return Number.isFinite(score) ? score : null;
      }
    }
    return null;
  }

  async function resolveOneMetric(genotype, consensus, gene, out) {
    const base = `${genotype}_${consensus}_${gene}`;
    try {
      const hvResp = await fetch(`/results/${base}.hivtrace.json`);
      if (!hvResp.ok) return;
      const threshold = (await hvResp.json())?.Settings?.threshold;
      if (threshold === undefined || threshold === null) return;
      const repResp = await fetch(`/results/${base}.aligned.report.tsv`);
      if (!repResp.ok) return; // no AUTO-TUNE sweep -> default threshold, not a tune result
      out[base] = { threshold, score: scoreAtThreshold(await repResp.text(), threshold) };
    } catch (error) {
      console.warn(`Could not resolve AUTO-TUNE metrics for ${base}:`, error);
    }
  }

  async function resolveComparisonMetrics(g1, g2, consensus) {
    const next = {};
    const genes = (genotype) =>
      Object.keys(congruenceData[`${genotype}_${consensus}`]?.network_statistics || {});
    await Promise.all([
      ...genes(g1).map(gene => resolveOneMetric(g1, consensus, gene, next)),
      ...genes(g2).map(gene => resolveOneMetric(g2, consensus, gene, next))
    ]);
    // A late-arriving fetch for a previous selection must not clobber the current one.
    if (g1 === genotype1 && g2 === genotype2 && consensus === $selectedThreshold) {
      resolvedMetrics = next;
    }
  }

  $: resolveComparisonMetrics(genotype1, genotype2, $selectedThreshold);

  // Enrich with network stats, overriding the fallback threshold/score with the
  // authoritative values resolved above (null -> displayed as N/A).
  function enrichWithStats(thresholdData, networkStats, genotype, consensus, resolved) {
    return thresholdData.map(d => {
      const stats = networkStats?.[d.gene] || {};
      const classification = getRegionClassification(d.gene);
      const classDisplay = getClassificationDisplay(classification);
      const metrics = resolved[`${genotype}_${consensus}_${d.gene}`];
      return {
        ...d,
        threshold: metrics ? metrics.threshold : null,
        score: metrics ? metrics.score : null,
        clusters: stats.total_clusters || null,
        singletons: stats.singleton_sequences || null,
        networkedPct: stats.network_proportion ? (stats.network_proportion * 100).toFixed(1) : null,
        classification,
        classDisplay
      };
    });
  }

  $: enriched1 = enrichWithStats(thresholds1, data1.network_statistics, genotype1, $selectedThreshold, resolvedMetrics);
  $: enriched2 = enrichWithStats(thresholds2, data2.network_statistics, genotype2, $selectedThreshold, resolvedMetrics);

  // Comparison metrics
  $: comparison = {
    globalAlpha1: data1.krippendorff_alpha_global,
    globalAlpha2: data2.krippendorff_alpha_global,
    meanAlpha1: data1.pairwise_summary?.mean_pairwise_alpha,
    meanAlpha2: data2.pairwise_summary?.mean_pairwise_alpha,
    regions1: data1.regions_analyzed?.length || 0,
    regions2: data2.regions_analyzed?.length || 0
  };

  // No-op event listener for plots that don't need interaction
  const noopListener = () => {};

  // Combined data for plots
  $: combinedData = [
    ...enriched1.map(d => ({ ...d, genotypeLabel: genotype1 })),
    ...enriched2.map(d => ({ ...d, genotypeLabel: genotype2 }))
  ].filter(d => d.gene && d.threshold != null);

  // Check if we have data to display
  $: hasData = combinedData.length > 0;

  // Threshold comparison plot options (computed directly, not in a store)
  $: thresholdComparisonOptions = hasData ? {
    grid: true,
    width: 900,
    height: 400,
    marginBottom: 100,
    marginLeft: 80,
    x: {
      tickRotate: -45,
      label: "Gene Region"
    },
    y: {
      label: "Best Threshold"
    },
    marks: [
      Plot.frame(),
      Plot.dot(combinedData, {
        x: "gene",
        y: "threshold",
        fill: "genotypeLabel",
        r: 8,
        stroke: "white",
        strokeWidth: 1,
        title: d => `${d.genotypeLabel} - ${d.gene}\nThreshold: ${d.threshold?.toFixed(5)}\nScore: ${d.score?.toFixed(3)}`
      })
    ],
    color: {
      legend: true,
      domain: [genotype1, genotype2],
      range: ["#3b82f6", "#f97316"],
      label: "Genotype"
    }
  } : null;

  // Score comparison plot options
  $: combinedScores = combinedData.filter(d => d.score != null);

  $: scoreComparisonOptions = combinedScores.length > 0 ? {
    grid: true,
    width: 900,
    height: 400,
    marginBottom: 100,
    marginLeft: 80,
    x: {
      tickRotate: -45,
      label: "Gene Region"
    },
    y: {
      label: "AUTO-TUNE Score",
      domain: [0, 2]
    },
    marks: [
      Plot.frame(),
      Plot.dot(combinedScores, {
        x: "gene",
        y: "score",
        fill: "genotypeLabel",
        r: 8,
        stroke: "white",
        strokeWidth: 1,
        title: d => `${d.genotypeLabel} - ${d.gene}\nScore: ${d.score?.toFixed(3)}`
      }),
      Plot.ruleY([0])
    ],
    color: {
      legend: true,
      domain: [genotype1, genotype2],
      range: ["#3b82f6", "#f97316"],
      label: "Genotype"
    }
  } : null;
</script>

<div class="container px-5">
  <div class="grid grid-cols-1 items-center my-5">
    <div class="col-start-1 col-span-2">
      <h1 class="text-5xl">Genotype Comparison</h1>
      <p>Side-by-side comparison of clustering metrics between two HCV genotypes. The manuscript compares genotypes 1a and 4d, noting different clustering behaviors and threshold patterns.</p>

      <!-- Genotype Selection -->
      <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center bg-indigo-50 border border-indigo-200 p-4 rounded-lg mt-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Genotype 1 (Blue)</label>
          <select bind:value={genotype1} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            {#each genotypes as g}
              <option value={g}>{g}</option>
            {/each}
          </select>
        </div>

        <div class="text-2xl font-bold text-gray-400">vs</div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Genotype 2 (Orange)</label>
          <select bind:value={genotype2} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            {#each genotypes as g}
              <option value={g}>{g}</option>
            {/each}
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Consensus Threshold</label>
          <select bind:value={$selectedThreshold} class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            {#each thresholdOptions as threshold}
              <option value={threshold}>{threshold}</option>
            {/each}
          </select>
        </div>
      </div>

      <!-- Navigation Links -->
      <div class="flex flex-wrap gap-2 mt-4 mb-6">
        <a href="/hcv" class="px-3 py-1.5 sm:px-4 sm:py-2 text-sm sm:text-base bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors">
          Analysis Dashboard
        </a>
        <a href="/hcv/congruence" class="px-3 py-1.5 sm:px-4 sm:py-2 text-sm sm:text-base bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors">
          Congruence Analysis
        </a>
        <a href="/hcv/diversity" class="px-3 py-1.5 sm:px-4 sm:py-2 text-sm sm:text-base bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors">
          Diversity Analysis
        </a>
        <a href="/hcv/comparison" class="px-3 py-1.5 sm:px-4 sm:py-2 text-sm sm:text-base bg-teal-600 text-white rounded-md hover:bg-teal-700 transition-colors">
          Genotype Comparison
        </a>
      </div>

      <!-- Summary Comparison Cards -->
      <div class="bg-white p-4 rounded-lg shadow mt-6">
        <h2 class="text-2xl font-semibold mb-4">Congruence Summary Comparison</h2>
        <div class="grid grid-cols-2 gap-6">
          <!-- Genotype 1 -->
          <div class="bg-blue-50 p-4 rounded-lg border-2 border-blue-200">
            <h3 class="text-lg font-bold text-blue-700 mb-3">Genotype {genotype1}</h3>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-gray-600">Global Alpha:</span>
                <span class="font-mono font-bold">{comparison.globalAlpha1?.toFixed(4) || 'N/A'}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Mean Pairwise Alpha:</span>
                <span class="font-mono">{comparison.meanAlpha1?.toFixed(4) || 'N/A'}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Regions Analyzed:</span>
                <span class="font-mono">{comparison.regions1}</span>
              </div>
            </div>
          </div>

          <!-- Genotype 2 -->
          <div class="bg-orange-50 p-4 rounded-lg border-2 border-orange-200">
            <h3 class="text-lg font-bold text-orange-700 mb-3">Genotype {genotype2}</h3>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-gray-600">Global Alpha:</span>
                <span class="font-mono font-bold">{comparison.globalAlpha2?.toFixed(4) || 'N/A'}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Mean Pairwise Alpha:</span>
                <span class="font-mono">{comparison.meanAlpha2?.toFixed(4) || 'N/A'}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Regions Analyzed:</span>
                <span class="font-mono">{comparison.regions2}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Threshold Comparison Plot -->
      <div class="bg-white p-4 rounded-lg shadow mt-6">
        <h2 class="text-2xl font-semibold mb-4">Threshold Comparison by Region<Tooltip text="Compares the optimal thresholds identified by AUTO-TUNE for each region between the two genotypes. The manuscript notes different threshold patterns across genotypes." /></h2>
        {#if thresholdComparisonOptions}
          <RenderPlot options={thresholdComparisonOptions} eventL={noopListener} />
        {:else}
          <div class="p-8 text-center text-gray-500">No network-derived AUTO-TUNE thresholds available for this genotype/threshold combination.</div>
        {/if}
        <p class="text-sm text-gray-600 mt-2">
          Comparison of optimal clustering thresholds for each gene region. Blue dots represent genotype {genotype1}, orange dots represent genotype {genotype2}.
        </p>
      </div>

      <!-- Score Comparison Plot -->
      <div class="bg-white p-4 rounded-lg shadow mt-6">
        <h2 class="text-2xl font-semibold mb-4">AUTO-TUNE Score Comparison<Tooltip text="Compares the AUTO-TUNE scores (clustering quality) for each region between genotypes. Higher scores indicate better threshold performance." /></h2>
        {#if scoreComparisonOptions}
          <RenderPlot options={scoreComparisonOptions} eventL={noopListener} />
        {:else}
          <div class="p-8 text-center text-gray-500">No network-derived AUTO-TUNE scores available for this genotype/threshold combination.</div>
        {/if}
        <p class="text-sm text-gray-600 mt-2">
          Comparison of AUTO-TUNE scores for each gene region. Higher scores indicate better clustering performance.
        </p>
      </div>

      <!-- Side-by-Side Tables -->
      <div class="bg-white p-4 rounded-lg shadow mt-6">
        <h2 class="text-2xl font-semibold mb-4">Detailed Metrics Comparison</h2>
        <div class="grid grid-cols-2 gap-4">
          <!-- Table 1 -->
          <div>
            <h3 class="text-lg font-medium text-blue-700 mb-2">Genotype {genotype1}</h3>
            <div class="overflow-x-auto">
              <table class="min-w-full text-sm divide-y divide-gray-200">
                <thead class="bg-blue-50">
                  <tr>
                    <th class="px-2 py-1 text-left text-xs font-medium text-gray-700">Region</th>
                    <th class="px-2 py-1 text-left text-xs font-medium text-gray-700">Type</th>
                    <th class="px-2 py-1 text-left text-xs font-medium text-gray-700">Threshold</th>
                    <th class="px-2 py-1 text-left text-xs font-medium text-gray-700">Score</th>
                    <th class="px-2 py-1 text-left text-xs font-medium text-gray-700">Clusters</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  {#each enriched1.filter(d => d.gene) as row}
                    <tr class="hover:bg-gray-50">
                      <td class="px-2 py-1 font-medium">{row.gene?.toUpperCase()}</td>
                      <td class="px-2 py-1">
                        <span class="text-xs px-1 rounded {row.classDisplay?.bgColor} {row.classDisplay?.color}">
                          {row.classDisplay?.label}
                        </span>
                      </td>
                      <td class="px-2 py-1 font-mono">{row.threshold != null ? row.threshold.toFixed(5) : 'N/A'}</td>
                      <td class="px-2 py-1 font-mono">{row.score != null ? row.score.toFixed(3) : 'N/A'}</td>
                      <td class="px-2 py-1">{row.clusters ?? 'N/A'}</td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          </div>

          <!-- Table 2 -->
          <div>
            <h3 class="text-lg font-medium text-orange-700 mb-2">Genotype {genotype2}</h3>
            <div class="overflow-x-auto">
              <table class="min-w-full text-sm divide-y divide-gray-200">
                <thead class="bg-orange-50">
                  <tr>
                    <th class="px-2 py-1 text-left text-xs font-medium text-gray-700">Region</th>
                    <th class="px-2 py-1 text-left text-xs font-medium text-gray-700">Type</th>
                    <th class="px-2 py-1 text-left text-xs font-medium text-gray-700">Threshold</th>
                    <th class="px-2 py-1 text-left text-xs font-medium text-gray-700">Score</th>
                    <th class="px-2 py-1 text-left text-xs font-medium text-gray-700">Clusters</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  {#each enriched2.filter(d => d.gene) as row}
                    <tr class="hover:bg-gray-50">
                      <td class="px-2 py-1 font-medium">{row.gene?.toUpperCase()}</td>
                      <td class="px-2 py-1">
                        <span class="text-xs px-1 rounded {row.classDisplay?.bgColor} {row.classDisplay?.color}">
                          {row.classDisplay?.label}
                        </span>
                      </td>
                      <td class="px-2 py-1 font-mono">{row.threshold != null ? row.threshold.toFixed(5) : 'N/A'}</td>
                      <td class="px-2 py-1 font-mono">{row.score != null ? row.score.toFixed(3) : 'N/A'}</td>
                      <td class="px-2 py-1">{row.clusters ?? 'N/A'}</td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Manuscript Context -->
      <div class="bg-amber-50 border border-amber-200 p-4 rounded-lg mt-6">
        <h3 class="text-lg font-semibold text-amber-800 mb-2">Manuscript Context</h3>
        <p class="text-sm text-amber-700">
          The manuscript compares genotypes 1a and 4d throughout, noting dramatically different clustering behaviors:
        </p>
        <ul class="list-disc list-inside text-sm text-amber-700 mt-2 space-y-1">
          <li><strong>ARI Distribution:</strong> 69.1% of region pairs showed very poor agreement (ARI &lt; 0.3) for genotype 1a vs 89.1% for genotype 4d</li>
          <li><strong>Threshold Patterns:</strong> Different optimal thresholds identified across genotypes</li>
          <li><strong>Clustering Quality:</strong> Varying cluster count and singleton patterns</li>
        </ul>
      </div>
    </div>
  </div>
</div>
