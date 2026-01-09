<script>
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';

  export let visible = false;
  export let networkUrl = null;
  export let meta = null; // { gene, genotype, threshold }
  export let onClose = () => {};

  let iframeRef;
  let isLoading = true;
  let hasError = false;
  let errorMessage = '';

  // View mode: 'network' or 'table'
  let viewMode = 'network';

  // Table data
  let networkData = null;
  let tableLoading = false;
  let sortColumn = 'cluster';
  let sortDirection = 'asc';

  // Expanded cluster rows (for pattern details)
  let expandedClusters = new Set();

  // Fetch network data for table view
  async function fetchNetworkData() {
    if (!networkUrl || networkData) return;

    tableLoading = true;
    try {
      const response = await fetch(networkUrl);
      if (!response.ok) throw new Error('Failed to load network data');
      networkData = await response.json();
    } catch (err) {
      console.error('Error fetching network data:', err);
      hasError = true;
      errorMessage = 'Failed to load network data for table view';
    } finally {
      tableLoading = false;
    }
  }

  // Switch view mode
  function setViewMode(mode) {
    viewMode = mode;
    if (mode === 'table' && !networkData) {
      fetchNetworkData();
    }
  }

  // Get sorted table rows
  // Region names to filter out (reference sequences)
  const ALL_REGIONS = ['core', 'e1', 'e2', 'ns2', 'ns3', 'ns4a', 'ns4b', 'ns5a', 'ns5b', 'p7'];

  // Check if a node ID is a region reference (should be filtered out)
  function isRegionReference(nodeId) {
    const id = nodeId?.toLowerCase() || '';
    return ALL_REGIONS.includes(id) || ALL_REGIONS.some(r => id.endsWith(`_${r}`));
  }

  $: tableRows = (() => {
    if (!networkData?.Nodes) return [];

    // Filter out region reference nodes
    const filteredNodes = networkData.Nodes.filter(node => !isRegionReference(node.id));

    // Build cluster size map
    const clusterSizes = {};
    filteredNodes.forEach(node => {
      const cluster = node.cluster ?? 'singleton';
      clusterSizes[cluster] = (clusterSizes[cluster] || 0) + 1;
    });

    const currentGene = meta?.gene?.toLowerCase() || '';
    const recommendedRegions = ['e2', 'ns2', 'ns3', 'ns5b'];

    // Map nodes to table rows
    const rows = filteredNodes.map((node, index) => {
      const pa = node.patient_attributes || {};
      const currentCluster = String(node.cluster);

      // Calculate which recommended regions share the same cluster
      const matchingRegions = [];
      for (const region of recommendedRegions) {
        if (region === currentGene) {
          // Current region always matches itself
          matchingRegions.push(region.toUpperCase());
        } else {
          const clusterInRegion = pa[`cluster_in_${region}`];
          if (clusterInRegion === currentCluster) {
            matchingRegions.push(region.toUpperCase());
          }
        }
      }

      return {
        id: node.id || `Node ${index}`,
        cluster: node.cluster ?? 'singleton',
        clusterSize: clusterSizes[node.cluster] || 1,
        recommendedCongruent: pa.recommended_congruent || 'N/A',
        membershipJaccard: pa.membership_jaccard,
        regionsPresent: pa.regions_present ?? 'N/A',
        recommendedRegionsPresent: pa.recommended_regions_present ?? 'N/A',
        matchingRegions: matchingRegions,
        matchingRegionsStr: matchingRegions.join(', ') || 'None'
      };
    });

    // Sort rows
    return rows.sort((a, b) => {
      let aVal = a[sortColumn];
      let bVal = b[sortColumn];

      // Handle numeric vs string comparison
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }

      // Handle 'singleton' specially - always sort to end
      if (aVal === 'singleton') aVal = sortDirection === 'asc' ? Infinity : -Infinity;
      if (bVal === 'singleton') bVal = sortDirection === 'asc' ? Infinity : -Infinity;

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }

      // String comparison
      const aStr = String(aVal).toLowerCase();
      const bStr = String(bVal).toLowerCase();
      return sortDirection === 'asc' ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr);
    });
  })();

  // Handle column sort
  function handleSort(column) {
    if (sortColumn === column) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortColumn = column;
      sortDirection = 'asc';
    }
  }

  // Get network summary stats
  $: networkSummary = networkData?.['Network Summary'] || {};

  // Calculate per-cluster statistics
  $: clusterStats = (() => {
    if (!networkData?.Nodes) return [];

    // Filter out region reference nodes
    const filteredNodes = networkData.Nodes.filter(node => !isRegionReference(node.id));

    const currentGene = meta?.gene?.toLowerCase() || '';
    const recommendedRegions = ['e2', 'ns2', 'ns3', 'ns5b'];

    // Group nodes by cluster
    const clusterMap = {};
    filteredNodes.forEach(node => {
      const cluster = node.cluster ?? 'singleton';
      if (!clusterMap[cluster]) {
        clusterMap[cluster] = {
          clusterId: cluster,
          nodes: [],
          size: 0,
          recommendedCongruentYes: 0,
          recommendedCongruentNo: 0,
          totalRegionsPresent: 0,
          totalRecommendedRegions: 0,
          regionsCount: 0,
          recommendedRegionsCount: 0,
          // Counts for Jaccard score ranges (aligned with congruence)
          jaccardHigh: 0,    // >= 0.8 (congruent)
          jaccardMedium: 0,  // 0.5 - 0.8
          jaccardLow: 0,     // < 0.5
          jaccardNA: 0,      // null/undefined
          // Pattern distribution: pattern string -> count
          patterns: {}
        };
      }

      const stats = clusterMap[cluster];
      stats.nodes.push(node);
      stats.size++;

      // Count congruence
      const recCong = node.patient_attributes?.recommended_congruent;
      if (recCong === 'Yes') stats.recommendedCongruentYes++;
      else if (recCong === 'No') stats.recommendedCongruentNo++;

      // Sum regions for averaging
      const regions = node.patient_attributes?.regions_present;
      if (typeof regions === 'number') {
        stats.totalRegionsPresent += regions;
        stats.regionsCount++;
      }

      const recRegions = node.patient_attributes?.recommended_regions_present;
      if (typeof recRegions === 'number') {
        stats.totalRecommendedRegions += recRegions;
        stats.recommendedRegionsCount++;
      }

      const pa = node.patient_attributes || {};

      // Count by Jaccard score range (aligned with congruence threshold of 0.8)
      const jaccard = pa.membership_jaccard;
      if (jaccard === null || jaccard === undefined) {
        stats.jaccardNA++;
      } else if (jaccard >= 0.8) {
        stats.jaccardHigh++;
      } else if (jaccard >= 0.5) {
        stats.jaccardMedium++;
      } else {
        stats.jaccardLow++;
      }

      // Track pattern distribution based on recommended_congruent status
      // Group by Yes/No/N/A for consistency
      const congStatus = pa.recommended_congruent || 'N/A';
      const jaccardStr = jaccard !== null && jaccard !== undefined ? jaccard.toFixed(2) : 'N/A';
      const patternKey = `${congStatus} (J=${jaccardStr})`;
      stats.patterns[patternKey] = (stats.patterns[patternKey] || 0) + 1;
    });

    // Calculate percentages and averages
    return Object.values(clusterMap)
      .map(stats => {
        // Convert patterns to sorted array for display
        const patternArray = Object.entries(stats.patterns)
          .map(([pattern, count]) => ({ pattern, count }))
          .sort((a, b) => b.count - a.count);

        return {
          clusterId: stats.clusterId,
          size: stats.size,
          recommendedCongruentYes: stats.recommendedCongruentYes,
          recommendedCongruentNo: stats.recommendedCongruentNo,
          recommendedCongruentPct: stats.size > 0
            ? ((stats.recommendedCongruentYes / stats.size) * 100).toFixed(1)
            : 0,
          avgRegionsPresent: stats.regionsCount > 0
            ? (stats.totalRegionsPresent / stats.regionsCount).toFixed(1)
            : 'N/A',
          avgRecommendedRegions: stats.recommendedRegionsCount > 0
            ? (stats.totalRecommendedRegions / stats.recommendedRegionsCount).toFixed(1)
            : 'N/A',
          // Jaccard score distribution (aligned with congruence)
          jaccardHigh: stats.jaccardHigh,
          jaccardMedium: stats.jaccardMedium,
          jaccardLow: stats.jaccardLow,
          jaccardNA: stats.jaccardNA,
          // Pattern distribution
          patterns: patternArray
        };
      })
      .sort((a, b) => {
        // Sort singletons to end, then by size descending
        if (a.clusterId === 'singleton') return 1;
        if (b.clusterId === 'singleton') return -1;
        return b.size - a.size;
      });
  })();

  // Overall recommended congruence stats
  $: overallStats = (() => {
    if (!clusterStats.length) return null;

    const nonSingletons = clusterStats.filter(c => c.clusterId !== 'singleton');
    const totalNodes = nonSingletons.reduce((sum, c) => sum + c.size, 0);
    const totalRecYes = nonSingletons.reduce((sum, c) => sum + c.recommendedCongruentYes, 0);

    return {
      clusteredNodes: totalNodes,
      singletonCount: clusterStats.find(c => c.clusterId === 'singleton')?.size || 0,
      overallRecommendedPct: totalNodes > 0 ? ((totalRecYes / totalNodes) * 100).toFixed(1) : 0
    };
  })();

  // Toggle cluster row expansion for pattern details
  function toggleClusterExpanded(clusterId) {
    if (expandedClusters.has(clusterId)) {
      expandedClusters.delete(clusterId);
    } else {
      expandedClusters.add(clusterId);
    }
    expandedClusters = expandedClusters; // Trigger reactivity
  }

  // Handle escape key to close
  function handleKeydown(event) {
    if (event.key === 'Escape' && visible) {
      onClose();
    }
  }

  // Build iframe URL with query parameters (this approach works!)
  $: iframeSrc = networkUrl && meta ?
    `/network-viewer.html?data=${encodeURIComponent(networkUrl)}&gene=${encodeURIComponent(meta.gene || '')}&genotype=${encodeURIComponent(meta.genotype || '')}&threshold=${encodeURIComponent(meta.threshold || '')}` :
    null;

  // Handle iframe load
  function onIframeLoad() {
    // Give hivtrace a moment to initialize
    setTimeout(() => {
      isLoading = false;
    }, 500);
  }

  // Handle iframe error
  function onIframeError() {
    hasError = true;
    errorMessage = 'Failed to load network viewer';
    isLoading = false;
  }

  // Listen for messages from iframe
  function handleMessage(event) {
    if (!browser) return;
    if (event.origin !== window.location.origin) return;

    if (event.data && event.data.type === 'NETWORK_READY') {
      isLoading = false;
    }
  }

  // Reset state when visibility changes
  $: if (visible) {
    isLoading = true;
    hasError = false;
    errorMessage = '';
    viewMode = 'network';
    networkData = null;
    expandedClusters = new Set();
  }

  onMount(() => {
    if (browser) {
      window.addEventListener('message', handleMessage);
      window.addEventListener('keydown', handleKeydown);
    }
  });

  onDestroy(() => {
    if (browser) {
      window.removeEventListener('message', handleMessage);
      window.removeEventListener('keydown', handleKeydown);
    }
  });
</script>

{#if visible}
  <!-- Modal overlay -->
  <div
    class="fixed inset-0 z-50 flex items-center justify-center"
    role="dialog"
    aria-modal="true"
    aria-labelledby="network-viewer-title"
  >
    <!-- Backdrop -->
    <div
      class="absolute inset-0 bg-black/60 backdrop-blur-sm"
      on:click={onClose}
      on:keydown={(e) => e.key === 'Enter' && onClose()}
      role="button"
      tabindex="0"
      aria-label="Close network viewer"
    ></div>

    <!-- Modal content -->
    <div class="relative w-[95vw] h-[90vh] max-w-7xl bg-white rounded-lg shadow-2xl overflow-hidden">
      <!-- Header -->
      <div class="absolute top-0 left-0 right-0 z-10 flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200">
        <div class="flex items-center gap-4">
          <h2 id="network-viewer-title" class="text-lg font-semibold text-gray-800">
            {#if meta}
              Network: {meta.gene?.toUpperCase() || 'Unknown'}
              <span class="text-sm font-normal text-gray-500">
                (Genotype {meta.genotype}, Threshold {meta.threshold})
              </span>
            {:else}
              Network Visualization
            {/if}
          </h2>

          <!-- View Toggle -->
          <div class="flex items-center bg-gray-100 rounded-lg p-0.5">
            <button
              on:click={() => setViewMode('network')}
              class="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md transition-colors {viewMode === 'network' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'}"
              aria-pressed={viewMode === 'network'}
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="5" r="2" stroke-width="2"/>
                <circle cx="6" cy="17" r="2" stroke-width="2"/>
                <circle cx="18" cy="17" r="2" stroke-width="2"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 7v4m-4.5 3.5L10 12m7 2.5L14 12"/>
              </svg>
              Network
            </button>
            <button
              on:click={() => setViewMode('table')}
              class="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md transition-colors {viewMode === 'table' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'}"
              aria-pressed={viewMode === 'table'}
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18M3 6h18M3 18h18"/>
              </svg>
              Table
            </button>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-500">Press ESC to close</span>
          <button
            on:click={onClose}
            class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Close"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Loading state -->
      {#if isLoading && !hasError}
        <div class="absolute inset-0 flex items-center justify-center bg-white z-20" style="top: 52px;">
          <div class="text-center">
            <div class="inline-block w-10 h-10 border-4 border-gray-200 border-t-indigo-600 rounded-full animate-spin"></div>
            <p class="mt-4 text-gray-600">Loading network visualization...</p>
          </div>
        </div>
      {/if}

      <!-- Error state -->
      {#if hasError}
        <div class="absolute inset-0 flex items-center justify-center bg-white z-20" style="top: 52px;">
          <div class="text-center max-w-md px-6">
            <div class="w-12 h-12 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
              <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-900 mb-2">Failed to Load Network</h3>
            <p class="text-gray-600 mb-4">{errorMessage}</p>
            <button
              on:click={onClose}
              class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      {/if}

      <!-- Content area -->
      <div class="w-full h-full pt-[52px]">
        {#if viewMode === 'network'}
          <!-- Network iframe -->
          {#if iframeSrc}
            <iframe
              bind:this={iframeRef}
              src={iframeSrc}
              title="Network Visualization"
              class="w-full h-full border-0"
              on:load={onIframeLoad}
              on:error={onIframeError}
            ></iframe>
          {/if}
        {:else}
          <!-- Table view -->
          <div class="w-full h-full overflow-auto bg-gray-50 p-4">
            {#if tableLoading}
              <div class="flex items-center justify-center h-64">
                <div class="text-center">
                  <div class="inline-block w-8 h-8 border-4 border-gray-200 border-t-indigo-600 rounded-full animate-spin"></div>
                  <p class="mt-3 text-gray-600">Loading table data...</p>
                </div>
              </div>
            {:else if tableRows.length > 0}
              <!-- Overall Summary stats -->
              <div class="mb-4 flex flex-wrap gap-4 text-sm">
                <div class="bg-white px-4 py-2 rounded-lg shadow-sm border border-gray-200">
                  <span class="text-gray-500">Nodes:</span>
                  <span class="font-semibold text-gray-900 ml-1">{networkSummary.Nodes || tableRows.length}</span>
                </div>
                <div class="bg-white px-4 py-2 rounded-lg shadow-sm border border-gray-200">
                  <span class="text-gray-500">Edges:</span>
                  <span class="font-semibold text-gray-900 ml-1">{networkSummary.Edges || 0}</span>
                </div>
                <div class="bg-white px-4 py-2 rounded-lg shadow-sm border border-gray-200">
                  <span class="text-gray-500">Clusters:</span>
                  <span class="font-semibold text-gray-900 ml-1">{networkSummary.Clusters || 0}</span>
                </div>
                <div class="bg-white px-4 py-2 rounded-lg shadow-sm border border-gray-200">
                  <span class="text-gray-500">Singletons:</span>
                  <span class="font-semibold text-gray-900 ml-1">{networkSummary.Singletons || 0}</span>
                </div>
                {#if overallStats}
                  <div class="bg-white px-4 py-2 rounded-lg shadow-sm border border-gray-200">
                    <span class="text-gray-500">Recommended Congruent:</span>
                    <span class="font-semibold ml-1 {parseFloat(overallStats.overallRecommendedPct) >= 80 ? 'text-green-600' : parseFloat(overallStats.overallRecommendedPct) >= 60 ? 'text-yellow-600' : 'text-red-600'}">
                      {overallStats.overallRecommendedPct}%
                    </span>
                  </div>
                {/if}
              </div>

              <!-- Per-Cluster Summary Table -->
              {#if clusterStats.length > 0}
                <div class="mb-6">
                  <h3 class="text-sm font-semibold text-gray-700 mb-2">
                    Cluster Summary (Recommended Regions)
                    <span class="font-normal text-gray-400 ml-2">Click row to see pattern distribution</span>
                  </h3>
                  <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                    <div class="overflow-x-auto">
                      <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                          <tr>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" title="Cluster identifier">Cluster</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" title="Number of nodes in cluster">Size</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" title="Nodes with membership Jaccard >= 0.8 across recommended regions (Yes/No counts)">Rec. Cong.</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" title="Percentage of nodes with Jaccard similarity >= 0.8 across recommended regions">% Cong.</th>
                            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider border-l border-gray-200" title="Nodes with high membership Jaccard (>= 0.8) - marked congruent">J≥0.8</th>
                            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" title="Nodes with medium membership Jaccard (0.5 - 0.8)">J 0.5-0.8</th>
                            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" title="Nodes with low membership Jaccard (less than 0.5)">{"J<0.5"}</th>
                            <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" title="Nodes without Jaccard score (insufficient data)">N/A</th>
                          </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                          {#each clusterStats as cluster}
                            <tr
                              class="hover:bg-gray-50 cursor-pointer"
                              on:click={() => toggleClusterExpanded(cluster.clusterId)}
                              on:keydown={(e) => e.key === 'Enter' && toggleClusterExpanded(cluster.clusterId)}
                              tabindex="0"
                              role="button"
                              aria-expanded={expandedClusters.has(cluster.clusterId)}
                            >
                              <td class="px-3 py-2 text-sm">
                                <div class="flex items-center gap-1">
                                  <svg
                                    class="w-3 h-3 text-gray-400 transition-transform {expandedClusters.has(cluster.clusterId) ? 'rotate-90' : ''}"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                  >
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                                  </svg>
                                  {#if cluster.clusterId === 'singleton'}
                                    <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                                      Singletons
                                    </span>
                                  {:else}
                                    <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-700">
                                      Cluster {cluster.clusterId}
                                    </span>
                                  {/if}
                                </div>
                              </td>
                              <td class="px-3 py-2 text-sm text-gray-700 font-medium">{cluster.size}</td>
                              <td class="px-3 py-2 text-sm text-gray-700">
                                <span class="text-green-600">{cluster.recommendedCongruentYes}</span>
                                <span class="text-gray-400">/</span>
                                <span class="text-red-600">{cluster.recommendedCongruentNo}</span>
                              </td>
                              <td class="px-3 py-2 text-sm">
                                <div class="flex items-center gap-2">
                                  <div class="w-12 h-2 bg-gray-200 rounded-full overflow-hidden">
                                    <div
                                      class="h-full rounded-full {parseFloat(cluster.recommendedCongruentPct) >= 80 ? 'bg-green-500' : parseFloat(cluster.recommendedCongruentPct) >= 60 ? 'bg-yellow-500' : 'bg-red-500'}"
                                      style="width: {cluster.recommendedCongruentPct}%"
                                    ></div>
                                  </div>
                                  <span class="text-xs font-medium {parseFloat(cluster.recommendedCongruentPct) >= 80 ? 'text-green-600' : parseFloat(cluster.recommendedCongruentPct) >= 60 ? 'text-yellow-600' : 'text-red-600'}">
                                    {cluster.recommendedCongruentPct}%
                                  </span>
                                </div>
                              </td>
                              <!-- Jaccard score distribution -->
                              <td class="px-3 py-2 text-sm text-center border-l border-gray-100 {cluster.jaccardHigh > 0 ? 'text-green-700 font-medium bg-green-50' : 'text-gray-400'}">{cluster.jaccardHigh}</td>
                              <td class="px-3 py-2 text-sm text-center {cluster.jaccardMedium > 0 ? 'text-yellow-600 font-medium' : 'text-gray-400'}">{cluster.jaccardMedium}</td>
                              <td class="px-3 py-2 text-sm text-center {cluster.jaccardLow > 0 ? 'text-orange-600 font-medium' : 'text-gray-400'}">{cluster.jaccardLow}</td>
                              <td class="px-3 py-2 text-sm text-center {cluster.jaccardNA > 0 ? 'text-gray-500' : 'text-gray-400'}">{cluster.jaccardNA}</td>
                            </tr>
                            <!-- Expanded pattern details row -->
                            {#if expandedClusters.has(cluster.clusterId)}
                              <tr class="bg-gray-50">
                                <td colspan="8" class="px-4 py-3">
                                  <div class="text-xs">
                                    <div class="font-medium text-gray-700 mb-2">Pattern Distribution:</div>
                                    <div class="flex flex-wrap gap-2">
                                      {#each cluster.patterns as p}
                                        <span class="inline-flex items-center gap-1 px-2 py-1 rounded bg-white border border-gray-200 shadow-sm">
                                          <span class="font-mono text-gray-600">{p.pattern}</span>
                                          <span class="font-semibold text-indigo-600">{p.count}</span>
                                        </span>
                                      {/each}
                                    </div>
                                  </div>
                                </td>
                              </tr>
                            {/if}
                          {/each}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              {/if}

              <!-- Node-level Data table -->
              <h3 class="text-sm font-semibold text-gray-700 mb-2">Node Details</h3>
              <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div class="overflow-x-auto">
                  <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                      <tr>
                        <th
                          class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                          on:click={() => handleSort('id')}
                        >
                          <div class="flex items-center gap-1">
                            Node ID
                            {#if sortColumn === 'id'}
                              <span class="text-indigo-600">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                            {/if}
                          </div>
                        </th>
                        <th
                          class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                          on:click={() => handleSort('cluster')}
                        >
                          <div class="flex items-center gap-1">
                            Cluster
                            {#if sortColumn === 'cluster'}
                              <span class="text-indigo-600">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                            {/if}
                          </div>
                        </th>
                        <th
                          class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                          on:click={() => handleSort('clusterSize')}
                        >
                          <div class="flex items-center gap-1">
                            Cluster Size
                            {#if sortColumn === 'clusterSize'}
                              <span class="text-indigo-600">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                            {/if}
                          </div>
                        </th>
                        <th
                          class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                          on:click={() => handleSort('recommendedCongruent')}
                        >
                          <div class="flex items-center gap-1">
                            Rec. Congruent
                            {#if sortColumn === 'recommendedCongruent'}
                              <span class="text-indigo-600">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                            {/if}
                          </div>
                        </th>
                        <th
                          class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                          on:click={() => handleSort('membershipJaccard')}
                          title="Membership Jaccard similarity across recommended regions (>= 0.8 = congruent)"
                        >
                          <div class="flex items-center gap-1">
                            Jaccard
                            {#if sortColumn === 'membershipJaccard'}
                              <span class="text-indigo-600">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                            {/if}
                          </div>
                        </th>
                        <th
                          class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                          on:click={() => handleSort('matchingRegionsStr')}
                          title="Which recommended regions share the same cluster ID (for debugging)"
                        >
                          <div class="flex items-center gap-1">
                            Cluster ID Match
                            {#if sortColumn === 'matchingRegionsStr'}
                              <span class="text-indigo-600">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                            {/if}
                          </div>
                        </th>
                        <th
                          class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                          on:click={() => handleSort('regionsPresent')}
                        >
                          <div class="flex items-center gap-1">
                            Regions Present
                            {#if sortColumn === 'regionsPresent'}
                              <span class="text-indigo-600">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                            {/if}
                          </div>
                        </th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                      {#each tableRows as row}
                        <tr class="hover:bg-gray-50">
                          <td class="px-4 py-2 text-sm text-gray-900 font-mono truncate max-w-xs" title={row.id}>
                            {row.id.length > 40 ? row.id.substring(0, 40) + '...' : row.id}
                          </td>
                          <td class="px-4 py-2 text-sm">
                            {#if row.cluster === 'singleton'}
                              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                                Singleton
                              </span>
                            {:else}
                              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-700">
                                Cluster {row.cluster}
                              </span>
                            {/if}
                          </td>
                          <td class="px-4 py-2 text-sm text-gray-700">{row.clusterSize}</td>
                          <td class="px-4 py-2 text-sm">
                            {#if row.recommendedCongruent === 'Yes'}
                              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700">Yes</span>
                            {:else if row.recommendedCongruent === 'No'}
                              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700">No</span>
                            {:else}
                              <span class="text-gray-400">{row.recommendedCongruent}</span>
                            {/if}
                          </td>
                          <td class="px-4 py-2 text-sm">
                            {#if row.membershipJaccard !== null && row.membershipJaccard !== undefined}
                              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium {row.membershipJaccard >= 0.8 ? 'bg-green-100 text-green-700' : row.membershipJaccard >= 0.5 ? 'bg-yellow-100 text-yellow-700' : 'bg-orange-100 text-orange-700'}">
                                {row.membershipJaccard.toFixed(3)}
                              </span>
                            {:else}
                              <span class="text-gray-400">N/A</span>
                            {/if}
                          </td>
                          <td class="px-4 py-2 text-sm">
                            {#if row.matchingRegions.length === 4}
                              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700">
                                {row.matchingRegionsStr}
                              </span>
                            {:else if row.matchingRegions.length === 3}
                              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-700">
                                {row.matchingRegionsStr}
                              </span>
                            {:else if row.matchingRegions.length >= 1}
                              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700">
                                {row.matchingRegionsStr}
                              </span>
                            {:else}
                              <span class="text-gray-400">None</span>
                            {/if}
                          </td>
                          <td class="px-4 py-2 text-sm text-gray-700">{row.regionsPresent}</td>
                        </tr>
                      {/each}
                    </tbody>
                  </table>
                </div>
              </div>

              <p class="mt-3 text-sm text-gray-500">
                Showing {tableRows.length} nodes. Click column headers to sort.
              </p>
            {:else}
              <div class="flex items-center justify-center h-64">
                <p class="text-gray-500">No data available</p>
              </div>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  /* Ensure modal is above everything */
  :global(body:has(.fixed.inset-0.z-50)) {
    overflow: hidden;
  }
</style>
