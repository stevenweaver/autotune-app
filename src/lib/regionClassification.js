/**
 * Region Classification Utility
 *
 * Based on manuscript findings, regions are classified as:
 * - Optimal: Good clustering potential for epidemiological analysis (E1, E2, NS2, NS3, NS5B)
 * - Poor: Limited clustering potential due to conserved sequences (core, NS4A, NS4B, NS5A, whole)
 * - Neutral: Moderate clustering potential (P7)
 */

// Optimal regions for epidemiological analysis (R1/R2 ratios 2.0-2.7)
export const OPTIMAL_REGIONS = ['e1', 'e2', 'ns2', 'ns3', 'ns5b'];

// Poor clustering regions (conserved sequences, R1/R2 ratios 13.7-19.8)
export const POOR_REGIONS = ['core', 'ns4a', 'ns4b', 'ns5a', 'whole'];

// Neutral regions
export const NEUTRAL_REGIONS = ['p7'];

// Compound regions (excluded from some analyses)
export const COMPOUND_REGIONS = ['ns5a-ns5b-ns3'];

/**
 * Get the classification of a gene region
 * @param {string} region - The gene region name (case-insensitive)
 * @returns {'optimal' | 'poor' | 'neutral' | 'compound'} The classification
 */
export function getRegionClassification(region) {
  const normalizedRegion = region?.toLowerCase();

  if (OPTIMAL_REGIONS.includes(normalizedRegion)) {
    return 'optimal';
  }
  if (POOR_REGIONS.includes(normalizedRegion)) {
    return 'poor';
  }
  if (COMPOUND_REGIONS.includes(normalizedRegion)) {
    return 'compound';
  }
  return 'neutral';
}

/**
 * Get display info for a region classification
 * @param {string} classification - The classification type
 * @returns {{ label: string, color: string, bgColor: string, description: string }}
 */
export function getClassificationDisplay(classification) {
  const displays = {
    optimal: {
      label: 'Optimal',
      color: 'text-green-700',
      bgColor: 'bg-green-100',
      borderColor: 'border-green-300',
      description: 'Recommended for epidemiological analysis - good clustering with balanced cluster sizes'
    },
    poor: {
      label: 'Conserved',
      color: 'text-orange-700',
      bgColor: 'bg-orange-100',
      borderColor: 'border-orange-300',
      description: 'Limited clustering potential - highly conserved sequences tend to form single dominant clusters'
    },
    neutral: {
      label: 'Moderate',
      color: 'text-gray-700',
      bgColor: 'bg-gray-100',
      borderColor: 'border-gray-300',
      description: 'Moderate clustering potential'
    },
    compound: {
      label: 'Compound',
      color: 'text-purple-700',
      bgColor: 'bg-purple-100',
      borderColor: 'border-purple-300',
      description: 'Multi-region concatenated sequence'
    }
  };

  return displays[classification] || displays.neutral;
}

/**
 * Check if a region is optimal for epidemiological analysis
 * @param {string} region - The gene region name
 * @returns {boolean}
 */
export function isOptimalRegion(region) {
  return getRegionClassification(region) === 'optimal';
}

/**
 * Check if a region is conserved/poor for clustering
 * @param {string} region - The gene region name
 * @returns {boolean}
 */
export function isConservedRegion(region) {
  return getRegionClassification(region) === 'poor';
}

/**
 * Determine if a threshold is AUTO-TUNE optimized or default fallback
 * Default fallback threshold is 0.005 (used when optimization fails)
 * @param {number} threshold - The threshold value
 * @returns {'optimized' | 'default'}
 */
export function getThresholdSource(threshold) {
  // 0.005 or very close to it indicates default fallback
  // Also check for very small thresholds that indicate optimization failed
  if (threshold === 0.005 || threshold < 0.00001) {
    return 'default';
  }
  return 'optimized';
}

/**
 * Get display info for threshold source
 * @param {'optimized' | 'default'} source - The threshold source
 * @returns {{ label: string, color: string, bgColor: string }}
 */
export function getThresholdSourceDisplay(source) {
  const displays = {
    optimized: {
      label: 'AUTO-TUNE',
      color: 'text-blue-700',
      bgColor: 'bg-blue-100',
      borderColor: 'border-blue-300'
    },
    default: {
      label: 'Default',
      color: 'text-gray-600',
      bgColor: 'bg-gray-100',
      borderColor: 'border-gray-300'
    }
  };

  return displays[source] || displays.optimized;
}
