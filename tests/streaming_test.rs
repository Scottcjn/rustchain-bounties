use rustchain_mcp::server;
use rustchain_mcp::mcp::CapabilityFlags;

#[test]
fn test_streaming_and_long_running_tools() {
    // Start the server
    let server = server::start_server();

    // Check the advertised capabilities
    let capabilities = server.get_capabilities();
    assert!(!capabilities.contains(CapabilityFlags::STREAMING_RESULTS));
    assert!(!capabilities.contains(CapabilityFlags::PROGRESS_NOTIFICATIONS));

    // Mock a slow tool call
    let result = server.handle_tool_call("slow_tool", vec![]);
    assert!(result.is_ok(), "Tool call should complete successfully");

    // Stop the server
    server.stop();
}