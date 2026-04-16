/**
 * Tests for BoTTube JavaScript SDK
 */

const { BoTTubeClient, BoTTubeError, AuthenticationError, APIError, UploadError } = require('./bottube');
const http = require('http');
const { URL } = require('url');

// Simple mock server for testing
function createMockServer(responses) {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      const url = new URL(req.url, 'http://localhost');
      const pathname = url.pathname;
      
      const response = responses[pathname] || responses['default'];
      const { statusCode = 200, data = {}, contentType = 'application/json' } = response;
      
      res.writeHead(statusCode, { 'Content-Type': contentType });
      res.end(JSON.stringify(data));
    });
    
    server.listen(0, () => {
      resolve(server);
    });
  });
}

// Simple assertion helper
function assert(condition, message) {
  if (!condition) throw new Error(message || 'Assertion failed');
}

// ========== Test Classes ==========

class TestClientInit {
  static testDefaultBaseUrl() {
    const client = new BoTTubeClient();
    assert(client.baseUrl === 'https://bottube.ai', 'Default base URL should be set');
    assert(client.timeout === 30000, 'Default timeout should be 30000ms');
    assert(client.retryCount === 3, 'Default retry count should be 3');
  }

  static testCustomOptions() {
    const client = new BoTTubeClient({
      apiKey: 'test-key',
      baseUrl: 'https://custom.bottube.com/',
      timeout: 10000,
      retryCount: 5
    });
    assert(client.apiKey === 'test-key', 'API key should be set');
    assert(client.baseUrl === 'https://custom.bottube.com', 'Base URL trailing slash should be stripped');
    assert(client.timeout === 10000, 'Custom timeout should be set');
    assert(client.retryCount === 5, 'Custom retry count should be set');
  }

  static testSSLVerification() {
    const client = new BoTTubeClient({ verifySSL: false });
    assert(client.verifySSL === false, 'SSL verification should be disabled');
  }
}

class TestHealthEndpoint {
  static async testHealthReturnsOk(responses) {
    responses['/health'] = { statusCode: 200, data: { status: 'ok', version: '1.0.0' } };
    
    const server = await createMockServer(responses);
    const port = server.address().port;
    
    const client = new BoTTubeClient({ baseUrl: `http://localhost:${port}` });
    const health = await client.health();
    
    assert(health.status === 'ok', 'Health status should be ok');
    assert(health.version === '1.0.0', 'Health version should be 1.0.0');
    
    server.close();
    return true;
  }
}

class TestVideosEndpoint {
  static async testVideosReturnsList(responses) {
    responses['/api/videos'] = {
      statusCode: 200,
      data: {
        videos: [{ id: 'v1', title: 'Video 1' }, { id: 'v2', title: 'Video 2' }],
        next_cursor: 'abc123'
      }
    };
    
    const server = await createMockServer(responses);
    const port = server.address().port;
    
    const client = new BoTTubeClient({ baseUrl: `http://localhost:${port}` });
    const result = await client.videos({ limit: 10 });
    
    assert(Array.isArray(result.videos), 'Videos should be an array');
    assert(result.videos.length === 2, 'Should have 2 videos');
    assert(result.next_cursor === 'abc123', 'Next cursor should be set');
    
    server.close();
    return true;
  }
}

class TestSearchEndpoint {
  static async testSearchReturnsResults(responses) {
    responses['/api/search'] = {
      statusCode: 200,
      data: {
        videos: [{ id: 'v1', title: 'Python Tutorial' }],
        total: 50,
        next_cursor: 'xyz789'
      }
    };
    
    const server = await createMockServer(responses);
    const port = server.address().port;
    
    const client = new BoTTubeClient({ baseUrl: `http://localhost:${port}` });
    const result = await client.search('python tutorial', { limit: 10 });
    
    assert(Array.isArray(result.videos), 'Videos should be an array');
    assert(result.total === 50, 'Total should be 50');
    
    server.close();
    return true;
  }
}

class TestCommentsEndpoint {
  static async testCommentsReturnsList(responses) {
    responses['/api/videos/v1/comments'] = {
      statusCode: 200,
      data: {
        comments: [{ id: 'c1', text: 'Great video!' }],
        total: 1
      }
    };
    
    const server = await createMockServer(responses);
    const port = server.address().port;
    
    const client = new BoTTubeClient({ baseUrl: `http://localhost:${port}` });
    const result = await client.comments('v1');
    
    assert(Array.isArray(result.comments), 'Comments should be an array');
    assert(result.comments.length === 1, 'Should have 1 comment');
    
    server.close();
    return true;
  }

  static async testCommentCreateRequiresAuth() {
    const client = new BoTTubeClient({ apiKey: null });
    let threw = false;
    try {
      await client.commentCreate('v1', 'Great!');
    } catch (e) {
      threw = e instanceof AuthenticationError;
    }
    assert(threw, 'Should throw AuthenticationError');
    return true;
  }

  static async testCommentCreateValidatesText() {
    const client = new BoTTubeClient({ apiKey: 'test' });
    let threw = false;
    try {
      await client.commentCreate('v1', '');
    } catch (e) {
      threw = e instanceof BoTTubeError;
    }
    assert(threw, 'Should throw BoTTubeError for empty text');
    return true;
  }
}

class TestVoteEndpoint {
  static async testVoteSuccess(responses) {
    responses['/api/videos/v1/vote'] = {
      statusCode: 200,
      data: { vote_type: 'up', upvotes: 42, downvotes: 3 }
    };
    
    const server = await createMockServer(responses);
    const port = server.address().port;
    
    const client = new BoTTubeClient({ apiKey: 'test', baseUrl: `http://localhost:${port}` });
    const result = await client.vote('v1', 'up');
    
    assert(result.vote_type === 'up', 'Vote type should be up');
    assert(result.upvotes === 42, 'Upvotes should be 42');
    
    server.close();
    return true;
  }

  static async testVoteRequiresAuth() {
    const client = new BoTTubeClient({ apiKey: null });
    let threw = false;
    try {
      await client.vote('v1', 'up');
    } catch (e) {
      threw = e instanceof AuthenticationError;
    }
    assert(threw, 'Should throw AuthenticationError');
    return true;
  }

  static async testVoteValidatesType() {
    const client = new BoTTubeClient({ apiKey: 'test' });
    let threw = false;
    try {
      await client.vote('v1', 'invalid');
    } catch (e) {
      threw = e instanceof BoTTubeError;
    }
    assert(threw, 'Should throw BoTTubeError for invalid vote type');
    return true;
  }
}

class TestUploadEndpoint {
  static async testUploadValidatesTitle() {
    const client = new BoTTubeClient({ apiKey: 'test' });
    let threw = false;
    try {
      await client.upload({ title: 'short', description: 'A very long description that is definitely more than 50 characters' });
    } catch (e) {
      threw = e instanceof UploadError;
    }
    assert(threw, 'Should throw UploadError for short title');
    return true;
  }

  static async testUploadValidatesDescription() {
    const client = new BoTTubeClient({ apiKey: 'test' });
    let threw = false;
    try {
      await client.upload({ title: 'This is a valid title', description: 'short' });
    } catch (e) {
      threw = e instanceof UploadError;
    }
    assert(threw, 'Should throw UploadError for short description');
    return true;
  }
}

// ========== Run Tests ==========

async function runTests() {
  console.log('Running BoTTube JavaScript SDK Tests...\n');
  
  let passed = 0;
  let failed = 0;

  // Client Init Tests
  console.log('Testing Client Initialization...');
  try {
    TestClientInit.testDefaultBaseUrl();
    TestClientInit.testCustomOptions();
    TestClientInit.testSSLVerification();
    passed += 3;
    console.log('  ✓ Client initialization tests passed\n');
  } catch (e) {
    failed += 3;
    console.log('  ✗ Client initialization tests failed:', e.message, '\n');
  }

  // Comments Tests
  console.log('Testing Comments...');
  try {
    await TestCommentsEndpoint.testCommentCreateRequiresAuth();
    await TestCommentsEndpoint.testCommentCreateValidatesText();
    passed += 2;
    console.log('  ✓ Comment validation tests passed\n');
  } catch (e) {
    failed += 2;
    console.log('  ✗ Comment validation tests failed:', e.message, '\n');
  }

  // Vote Tests
  console.log('Testing Voting...');
  try {
    await TestVoteEndpoint.testVoteRequiresAuth();
    await TestVoteEndpoint.testVoteValidatesType();
    passed += 2;
    console.log('  ✓ Vote validation tests passed\n');
  } catch (e) {
    failed += 2;
    console.log('  ✗ Vote validation tests failed:', e.message, '\n');
  }

  // Upload Tests
  console.log('Testing Upload...');
  try {
    await TestUploadEndpoint.testUploadValidatesTitle();
    await TestUploadEndpoint.testUploadValidatesDescription();
    passed += 2;
    console.log('  ✓ Upload validation tests passed\n');
  } catch (e) {
    failed += 2;
    console.log('  ✗ Upload validation tests failed:', e.message, '\n');
  }

  // Network Tests (need mock server)
  const responses = {};
  
  console.log('Testing Health Endpoint...');
  try {
    await TestHealthEndpoint.testHealthReturnsOk(responses);
    passed += 1;
    console.log('  ✓ Health endpoint test passed\n');
  } catch (e) {
    failed += 1;
    console.log('  ✗ Health endpoint test failed:', e.message, '\n');
  }

  console.log('Testing Videos Endpoint...');
  try {
    await TestVideosEndpoint.testVideosReturnsList(responses);
    passed += 1;
    console.log('  ✓ Videos endpoint test passed\n');
  } catch (e) {
    failed += 1;
    console.log('  ✗ Videos endpoint test failed:', e.message, '\n');
  }

  console.log('Testing Search Endpoint...');
  try {
    await TestSearchEndpoint.testSearchReturnsResults(responses);
    passed += 1;
    console.log('  ✓ Search endpoint test passed\n');
  } catch (e) {
    failed += 1;
    console.log('  ✗ Search endpoint test failed:', e.message, '\n');
  }

  console.log('Testing Comments Endpoint...');
  try {
    await TestCommentsEndpoint.testCommentsReturnsList(responses);
    passed += 1;
    console.log('  ✓ Comments endpoint test passed\n');
  } catch (e) {
    failed += 1;
    console.log('  ✗ Comments endpoint test failed:', e.message, '\n');
  }

  console.log('Testing Vote Endpoint...');
  try {
    await TestVoteEndpoint.testVoteSuccess(responses);
    passed += 1;
    console.log('  ✓ Vote endpoint test passed\n');
  } catch (e) {
    failed += 1;
    console.log('  ✗ Vote endpoint test failed:', e.message, '\n');
  }

  console.log('===================');
  console.log(`Results: ${passed} passed, ${failed} failed`);
  console.log('===================');
  
  return failed === 0;
}

runTests().then(success => {
  process.exit(success ? 0 : 1);
}).catch(e => {
  console.error('Test runner failed:', e);
  process.exit(1);
});
