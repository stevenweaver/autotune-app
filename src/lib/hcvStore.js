import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// Default values
const defaults = {
  genotype: '1a',
  threshold: '0.2',
  region: 'ns5a'
};

// Create stores with session storage persistence
function createPersistentStore(key, initialValue) {
  // Get initial value from sessionStorage if available
  let storedValue = initialValue;
  if (browser) {
    const stored = sessionStorage.getItem(`hcv_${key}`);
    if (stored !== null) {
      storedValue = stored;
    }
  }

  const store = writable(storedValue);

  // Subscribe to persist changes to sessionStorage
  if (browser) {
    store.subscribe(value => {
      sessionStorage.setItem(`hcv_${key}`, value);
    });
  }

  return store;
}

// Shared stores for HCV page selections
export const selectedGenotype = createPersistentStore('genotype', defaults.genotype);
export const selectedThreshold = createPersistentStore('threshold', defaults.threshold);
export const selectedRegion = createPersistentStore('region', defaults.region);

// Available options (shared across pages)
export const genotypes = ['1a', '1b', '2a', '2b', '3a', '4d'];
export const thresholds = ['0.01', '0.02', '0.05', '0.1', '0.2', '0.25'];
export const regions = ['core', 'e1', 'e2', 'ns2', 'ns3', 'ns4a', 'ns4b', 'ns5a', 'ns5b', 'p7', 'whole'];

// Network viewer state (not persisted - transient)
// Format: { gene: string, genotype: string, threshold: string } | null
export const selectedNetworkRegion = writable(null);
