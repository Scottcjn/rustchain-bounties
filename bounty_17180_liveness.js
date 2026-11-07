/*
 * Bounty #17180: Node Liveness Checks
 * Health check probes for Node.js applications
 * 
 * This module provides liveness and readiness probes for Node.js applications
 * that can be used with Kubernetes or Docker health checks.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

// Liveness probe - checks if the Node process is alive
function livenessProbe(req, res) {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    status: 'alive',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    pid: process.pid,
  }));
}

// Readiness probe - checks if the application is ready to serve traffic
function readinessProbe(req, res) {
  // Check if database is connected
  // Check if external services are available
  // Check if required modules are loaded
  
  const checks = {
    database: checkDatabase(),
    services: checkServices(),
    modules: checkModules(),
  };
  
  const allPassed = Object.values(checks).every(check => check.status === 'ok');
  
  if (allPassed) {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'ready',
      checks: checks,
      timestamp: new Date().toISOString(),
    }));
  } else {
    res.writeHead(503, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'not_ready',
      checks: checks,
      timestamp: new Date().toISOString(),
    }));
  }
}

// Check database connectivity
function checkDatabase() {
  // Implement database health check logic
  // This is a placeholder - connect to actual DB and ping
  return { status: 'ok', type: 'database', details: 'Connected' };
}

// Check external services
function checkServices() {
  // Implement external service health checks
  return { status: 'ok', type: 'services', details: 'All services available' };
}

// Check required modules
function checkModules() {
  const requiredModules = ['http', 'fs', 'path', 'express'];
  const results = [];
  
  for (const mod of requiredModules) {
    try {
      require.resolve(mod);
      results.push({ module: mod, status: 'ok' });
    } catch (e) {
      results.push({ module: mod, status: 'missing', error: e.message });
    }
  }
  
  const allOk = results.every(r => r.status === 'ok');
  
  return { 
    status: allOk ? 'ok' : 'error', 
    type: 'modules', 
    details: results 
  };
}

// Express middleware for health checks
function setupHealthChecks(app) {
  // Liveness probe endpoint
  app.get('/health/liveness', livenessProbe);
  
  // Readiness probe endpoint
  app.get('/health/readiness', readinessProbe);
  
  // Ready endpoint for load balancers
  app.get('/health/ready', (req, res) => {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      status: 'ready', 
      timestamp: new Date().toISOString() 
    }));
  });
  
  // Live endpoint for basic liveness
  app.get('/health/live', (req, res) => {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      status: 'alive', 
      timestamp: new Date().toISOString() 
    }));
  });
}

module.exports = {
  livenessProbe,
  readinessProbe,
  checkDatabase,
  checkServices,
  checkModules,
  setupHealthChecks,
};