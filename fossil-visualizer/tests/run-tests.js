/**
 * Test Runner for Fossil Record Visualizer
 * Runs all unit tests with proper module loading
 */

const fs = require('fs');
const path = require('path');

// Load source files
const dataJs = fs.readFileSync(path.join(__dirname, '..', 'data.js'), 'utf8');
const processorJs = fs.readFileSync(path.join(__dirname, '..', 'processor.js'), 'utf8');
const testJs = fs.readFileSync(path.join(__dirname, 'test.js'), 'utf8');

// Combine and execute
const combinedCode = `
${dataJs}
${processorJs}
${testJs}
`;

eval(combinedCode);
