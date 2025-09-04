# Deployment Guide 🚀

This guide covers deploying the PET Reference Regions WebApp to various platforms.

## GitHub Pages (Recommended)

### Automatic Deployment

The webapp automatically deploys to GitHub Pages via GitHub Actions when:
- Changes are pushed to `main` or `dev/webapp` branches
- Changes are made to `webapp/` directory or deployment workflow

**Live URL**: `https://[username].github.io/pet_reference_regions/`

### Manual Deployment

1. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: "GitHub Actions"

2. **Trigger Deployment**:
   ```bash
   git add webapp/
   git commit -m "Deploy webapp updates"
   git push origin main
   ```

3. **Monitor Deployment**:
   - Check Actions tab for deployment status
   - Typical deployment time: 2-5 minutes

### Configuration

The deployment workflow (`.github/workflows/deploy-webapp.yml`) handles:
- ✅ Automated testing (optional, continues on failure)
- ✅ File validation and integrity checks
- ✅ Static site optimization
- ✅ GitHub Pages deployment

## Alternative Deployment Options

### 1. Netlify

**Benefits**: Custom domains, form handling, serverless functions

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy from webapp directory
cd webapp
netlify deploy --prod --dir .
```

**Configuration** (`netlify.toml`):
```toml
[build]
  publish = "webapp"
  
[[headers]]
  for = "/*"
  [headers.values]
    Cross-Origin-Embedder-Policy = "require-corp"
    Cross-Origin-Opener-Policy = "same-origin"
```

### 2. Vercel

**Benefits**: Edge deployment, analytics, preview deployments

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from project root
vercel --prod
```

**Configuration** (`vercel.json`):
```json
{
  "version": 2,
  "builds": [
    {
      "src": "webapp/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/webapp/$1"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Cross-Origin-Embedder-Policy",
          "value": "require-corp"
        },
        {
          "key": "Cross-Origin-Opener-Policy", 
          "value": "same-origin"
        }
      ]
    }
  ]
}
```

### 3. Firebase Hosting

**Benefits**: Google infrastructure, real-time database integration

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Initialize project
firebase init hosting

# Deploy
firebase deploy
```

**Configuration** (`firebase.json`):
```json
{
  "hosting": {
    "public": "webapp",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "headers": [
      {
        "source": "**",
        "headers": [
          {
            "key": "Cross-Origin-Embedder-Policy",
            "value": "require-corp"
          },
          {
            "key": "Cross-Origin-Opener-Policy",
            "value": "same-origin"
          }
        ]
      }
    ]
  }
}
```

### 4. AWS S3 + CloudFront

**Benefits**: Scalable, CDN integration, advanced security

```bash
# Create S3 bucket
aws s3 mb s3://pet-reference-regions-webapp

# Sync webapp files
aws s3 sync webapp/ s3://pet-reference-regions-webapp --delete

# Configure static website hosting
aws s3 website s3://pet-reference-regions-webapp --index-document index.html
```

## Pre-Deployment Checklist

### 🔍 Validation

```bash
cd webapp
npm run validate    # Run integrity checks
npm test           # Run test suite (optional)
npm run lint       # Check code quality
```

### 📋 Required Files

- ✅ `index.html` - Main application entry
- ✅ `css/styles.css` - Styling
- ✅ `js/app.js` - Application logic
- ✅ `js/pyodide-bridge.js` - Python integration
- ✅ `js/visualization.js` - 3D viewer
- ✅ `.nojekyll` - Prevent Jekyll processing (GitHub Pages)

### 🌐 Cross-Origin Headers

**Important**: For Pyodide WebAssembly to work properly, ensure these headers are set:

```
Cross-Origin-Embedder-Policy: require-corp
Cross-Origin-Opener-Policy: same-origin
```

Most static hosting platforms handle this automatically, but verify if you encounter WebAssembly loading issues.

## Performance Optimization

### 1. CDN Configuration

Ensure static assets are served via CDN:
- **HTML/CSS/JS**: Cache for 1 hour (frequent updates)
- **Images**: Cache for 1 week  
- **Pyodide packages**: Cache for 1 month (rarely change)

### 2. Compression

Enable gzip/brotli compression:
- **HTML/CSS/JS**: ~70% size reduction
- **Large packages**: Significant load time improvement

### 3. Preloading

Consider preloading critical resources:
```html
<link rel="preload" href="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js" as="script">
```

## Monitoring & Analytics

### Error Tracking

Add error tracking to monitor WebApp issues:

```javascript
// In app.js
window.addEventListener('error', (event) => {
    // Log to analytics service
    console.error('WebApp Error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled Promise Rejection:', event.reason);
});
```

### Usage Analytics

Consider adding privacy-respecting analytics:
- **Plausible**: GDPR-compliant, no personal data
- **Google Analytics 4**: With privacy settings
- **Self-hosted**: Umami, Matomo

### Performance Monitoring

Track key metrics:
- **Initial load time**: Pyodide + packages download
- **File processing time**: Per image size
- **Memory usage**: Browser performance
- **Error rates**: WebAssembly failures

## Security Considerations

### Content Security Policy (CSP)

Recommended CSP headers:
```
Content-Security-Policy: 
  default-src 'self' 
  'unsafe-eval' 'unsafe-inline' 
  https://cdn.jsdelivr.net 
  data: blob:
```

**Note**: `unsafe-eval` required for Pyodide WebAssembly execution.

### HTTPS Only

Always deploy over HTTPS:
- Required for modern browser features
- Essential for WebAssembly security
- Standard for medical data applications

## Troubleshooting

### Common Issues

**1. Pyodide Loading Fails**
- Check CORS headers
- Verify CDN accessibility
- Test in different browsers

**2. Large Files Timeout**
- Increase server timeout limits
- Consider chunked upload for very large files
- Add progress indicators

**3. Memory Issues**
- Monitor browser memory usage
- Implement garbage collection
- Add memory usage warnings

### Browser Compatibility

Test deployment across browsers:
- **Chrome 57+**: Primary target
- **Firefox 52+**: Good support
- **Safari 11+**: WebAssembly support
- **Edge 79+**: Modern Edge versions

### Support Resources

- **GitHub Issues**: Report deployment problems
- **Documentation**: Check main README
- **Community**: GitHub Discussions for help

---

**🚀 Ready to deploy your privacy-first neuroimaging webapp!**