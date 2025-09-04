#!/usr/bin/env node

/**
 * Validation script for WebApp integrity and deployment readiness
 */

const fs = require('fs');
const path = require('path');

class WebAppValidator {
    constructor() {
        this.errors = [];
        this.warnings = [];
        this.webappDir = path.join(__dirname, '..');
    }

    log(message, type = 'info') {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] ${type.toUpperCase()}: ${message}`);
    }

    error(message) {
        this.errors.push(message);
        this.log(message, 'error');
    }

    warning(message) {
        this.warnings.push(message);
        this.log(message, 'warning');
    }

    info(message) {
        this.log(message, 'info');
    }

    /**
     * Check if required files exist
     */
    validateFileStructure() {
        this.info('Validating file structure...');

        const requiredFiles = [
            'index.html',
            'css/styles.css',
            'js/app.js',
            'js/pyodide-bridge.js',
            'js/visualization.js',
            'package.json'
        ];

        const optionalFiles = [
            'tests/app.test.js',
            'tests/pyodide-bridge.test.js',
            'tests/visualization.test.js'
        ];

        // Check required files
        requiredFiles.forEach(file => {
            const filePath = path.join(this.webappDir, file);
            if (!fs.existsSync(filePath)) {
                this.error(`Required file missing: ${file}`);
            } else {
                const stats = fs.statSync(filePath);
                if (stats.size === 0) {
                    this.error(`Required file is empty: ${file}`);
                }
            }
        });

        // Check optional files
        optionalFiles.forEach(file => {
            const filePath = path.join(this.webappDir, file);
            if (!fs.existsSync(filePath)) {
                this.warning(`Optional file missing: ${file}`);
            }
        });
    }

    /**
     * Validate HTML structure
     */
    validateHTML() {
        this.info('Validating HTML structure...');

        const htmlPath = path.join(this.webappDir, 'index.html');
        if (!fs.existsSync(htmlPath)) {
            this.error('index.html not found');
            return;
        }

        const html = fs.readFileSync(htmlPath, 'utf8');

        // Check for required elements
        const requiredIds = [
            'segmentation-upload',
            'probability-upload',
            'parameters-section',
            'visualization-section',
            'results-section',
            'axial-canvas',
            'coronal-canvas',
            'sagittal-canvas',
            'process-btn',
            'download-btn'
        ];

        requiredIds.forEach(id => {
            if (!html.includes(`id="${id}"`)) {
                this.error(`HTML element with id="${id}" not found`);
            }
        });

        // Check for required script includes
        const requiredScripts = [
            'pyodide.js',
            'js/pyodide-bridge.js',
            'js/visualization.js',
            'js/app.js'
        ];

        requiredScripts.forEach(script => {
            if (!html.includes(script)) {
                this.error(`Script not included: ${script}`);
            }
        });

        // Check for CSS
        if (!html.includes('css/styles.css')) {
            this.error('CSS stylesheet not linked');
        }

        // Check for responsive viewport meta tag
        if (!html.includes('viewport')) {
            this.warning('Viewport meta tag missing (affects mobile experience)');
        }
    }

    /**
     * Validate JavaScript files
     */
    validateJavaScript() {
        this.info('Validating JavaScript files...');

        const jsFiles = [
            'js/app.js',
            'js/pyodide-bridge.js',
            'js/visualization.js'
        ];

        jsFiles.forEach(file => {
            const filePath = path.join(this.webappDir, file);
            if (!fs.existsSync(filePath)) {
                this.error(`JavaScript file missing: ${file}`);
                return;
            }

            const content = fs.readFileSync(filePath, 'utf8');

            // Basic syntax validation (very simple)
            const braceCount = (content.match(/\{/g) || []).length - (content.match(/\}/g) || []).length;
            if (braceCount !== 0) {
                this.warning(`Possible syntax error in ${file}: unmatched braces`);
            }

            const parenCount = (content.match(/\(/g) || []).length - (content.match(/\)/g) || []).length;
            if (parenCount !== 0) {
                this.warning(`Possible syntax error in ${file}: unmatched parentheses`);
            }

            // Check for required classes
            if (file === 'js/app.js' && !content.includes('class PETRefRegionApp')) {
                this.error('PETRefRegionApp class not found in app.js');
            }

            if (file === 'js/pyodide-bridge.js' && !content.includes('class PyodideBridge')) {
                this.error('PyodideBridge class not found in pyodide-bridge.js');
            }

            if (file === 'js/visualization.js' && !content.includes('class NiftiVisualization')) {
                this.error('NiftiVisualization class not found in visualization.js');
            }
        });
    }

    /**
     * Validate CSS
     */
    validateCSS() {
        this.info('Validating CSS...');

        const cssPath = path.join(this.webappDir, 'css/styles.css');
        if (!fs.existsSync(cssPath)) {
            this.error('CSS file missing: css/styles.css');
            return;
        }

        const css = fs.readFileSync(cssPath, 'utf8');

        // Check for responsive design
        if (!css.includes('@media')) {
            this.warning('No responsive media queries found in CSS');
        }

        // Check for canvas styling
        if (!css.includes('canvas')) {
            this.warning('No canvas styling found in CSS');
        }

        // Basic CSS syntax check
        const braceCount = (css.match(/\{/g) || []).length - (css.match(/\}/g) || []).length;
        if (braceCount !== 0) {
            this.warning('Possible CSS syntax error: unmatched braces');
        }
    }

    /**
     * Validate package.json
     */
    validatePackageJson() {
        this.info('Validating package.json...');

        const packagePath = path.join(this.webappDir, 'package.json');
        if (!fs.existsSync(packagePath)) {
            this.warning('package.json missing (optional for static webapp)');
            return;
        }

        try {
            const packageData = JSON.parse(fs.readFileSync(packagePath, 'utf8'));

            // Check required fields
            const requiredFields = ['name', 'version', 'description'];
            requiredFields.forEach(field => {
                if (!packageData[field]) {
                    this.warning(`package.json missing field: ${field}`);
                }
            });

            // Check for test script
            if (!packageData.scripts?.test) {
                this.warning('No test script defined in package.json');
            }

            // Check for development dependencies
            if (!packageData.devDependencies?.jest) {
                this.warning('Jest not found in devDependencies (testing framework)');
            }

        } catch (error) {
            this.error(`Invalid package.json: ${error.message}`);
        }
    }

    /**
     * Check for security issues
     */
    validateSecurity() {
        this.info('Validating security...');

        const jsFiles = [
            'js/app.js',
            'js/pyodide-bridge.js',
            'js/visualization.js'
        ];

        jsFiles.forEach(file => {
            const filePath = path.join(this.webappDir, file);
            if (!fs.existsSync(filePath)) return;

            const content = fs.readFileSync(filePath, 'utf8');

            // Check for eval usage
            if (content.includes('eval(')) {
                this.warning(`Potential security risk: eval() found in ${file}`);
            }

            // Check for innerHTML with user input
            if (content.includes('innerHTML') && content.includes('user')) {
                this.warning(`Potential XSS risk: innerHTML with user input in ${file}`);
            }

            // Check for external script loading
            if (content.includes('document.createElement("script")')) {
                this.warning(`Dynamic script loading found in ${file}`);
            }
        });

        // Check HTML for inline scripts
        const htmlPath = path.join(this.webappDir, 'index.html');
        if (fs.existsSync(htmlPath)) {
            const html = fs.readFileSync(htmlPath, 'utf8');
            
            if (html.includes('<script>') && !html.includes('</script>')) {
                this.warning('Inline scripts found in HTML (consider moving to separate files)');
            }
        }
    }

    /**
     * Validate deployment readiness
     */
    validateDeployment() {
        this.info('Validating deployment readiness...');

        // Check for .nojekyll file (GitHub Pages)
        const nojekyllPath = path.join(this.webappDir, '.nojekyll');
        if (!fs.existsSync(nojekyllPath)) {
            this.info('Creating .nojekyll file for GitHub Pages deployment...');
            fs.writeFileSync(nojekyllPath, '');
        }

        // Check total directory size
        const getTotalSize = (dirPath) => {
            let totalSize = 0;
            const files = fs.readdirSync(dirPath);
            
            files.forEach(file => {
                const fullPath = path.join(dirPath, file);
                const stats = fs.statSync(fullPath);
                
                if (stats.isDirectory()) {
                    totalSize += getTotalSize(fullPath);
                } else {
                    totalSize += stats.size;
                }
            });
            
            return totalSize;
        };

        const totalSize = getTotalSize(this.webappDir);
        const sizeMB = totalSize / (1024 * 1024);
        
        if (sizeMB > 100) {
            this.warning(`WebApp size is ${sizeMB.toFixed(1)}MB (consider optimization)`);
        } else {
            this.info(`WebApp size: ${sizeMB.toFixed(1)}MB`);
        }
    }

    /**
     * Run all validations
     */
    async validate() {
        this.info('Starting WebApp validation...');

        this.validateFileStructure();
        this.validateHTML();
        this.validateJavaScript();
        this.validateCSS();
        this.validatePackageJson();
        this.validateSecurity();
        this.validateDeployment();

        // Summary
        this.info('\n=== Validation Summary ===');
        this.info(`Errors: ${this.errors.length}`);
        this.info(`Warnings: ${this.warnings.length}`);

        if (this.errors.length > 0) {
            this.log('\nErrors found:', 'error');
            this.errors.forEach((error, i) => {
                this.log(`  ${i + 1}. ${error}`, 'error');
            });
        }

        if (this.warnings.length > 0) {
            this.log('\nWarnings:', 'warning');
            this.warnings.forEach((warning, i) => {
                this.log(`  ${i + 1}. ${warning}`, 'warning');
            });
        }

        if (this.errors.length === 0) {
            this.info('\n✅ WebApp validation passed! Ready for deployment.');
            return true;
        } else {
            this.log('\n❌ WebApp validation failed. Please fix errors before deployment.', 'error');
            return false;
        }
    }
}

// Run validation if called directly
if (require.main === module) {
    const validator = new WebAppValidator();
    validator.validate().then(success => {
        process.exit(success ? 0 : 1);
    }).catch(error => {
        console.error('Validation failed:', error);
        process.exit(1);
    });
}

module.exports = WebAppValidator;