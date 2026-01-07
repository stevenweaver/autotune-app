# AUTO-TUNE

A web application for optimizing HIV-TRACE genetic distance thresholds and visualizing molecular transmission networks.

## Overview

AUTO-TUNE provides interactive visualizations and analysis tools for:

- **Threshold Optimization**: Automatically determine optimal genetic distance thresholds for HIV-TRACE clustering analysis
- **Network Visualization**: Interactive molecular transmission network graphs powered by hivtrace-viz
- **Subsampling Analysis**: Evaluate clustering stability across different sample sizes

## Features

- Interactive D3.js-powered network visualizations
- SVG and PNG export for publication-quality figures
- Cross-region cluster congruence annotations
- Region classification (optimal vs conserved regions for epidemiological clustering)
- Persistent selection controls for genotype and threshold parameters

## Requirements

- Node.js 18+
- npm

## Development

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

## Building for Production

Build the production bundle (requires extra memory for large datasets):

```bash
NODE_OPTIONS="--max-old-space-size=16384" npm run build
```

## Deployment

### Using the Release Tarball

1. Download the latest release tarball from [Releases](https://github.com/stevenweaver/autotune-app/releases)

2. Extract and install:
   ```bash
   tar -xzf autotune-app-vX.X.X-XXXXXXX-XXXXXXXX.tar.gz
   cd build
   npm ci --omit=dev
   ```

3. Run the server:
   ```bash
   PORT=3000 node index.js
   ```

### Using PM2 (Recommended for Production)

```bash
PORT=3000 pm2 start index.js --name autotune-app
```

### With Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Data Files

Network JSON files should follow the HIV-TRACE output format and be placed in the `static/results/` directory.

## License

MIT

## Author

[Steven Weaver](http://stevenweaver.org/)
