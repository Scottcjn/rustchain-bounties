//! RustChain RIP-302 Agent Economy Client Crate.
//!
//! Provides an asynchronous, strongly-typed interface for autonomous agents
//! to interact with the RustChain Agent-to-Agent marketplace.

pub mod client;
pub mod error;
pub mod models;

pub use client::{AgentClient, JobListOptions, DEFAULT_NODE_URL};
pub use error::{Error, Result};
pub use models::*;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_escrow_calculation() {
        let calc = EscrowCalculation::new(100.0);
        assert_eq!(calc.reward_rtc, 100.0);
        assert_eq!(calc.fee_rtc, 5.0);
        assert_eq!(calc.total_escrow_rtc, 105.0);
    }

    #[test]
    fn test_categories() {
        assert!(CATEGORIES.contains(&"code"));
        assert!(CATEGORIES.contains(&"research"));
        assert_eq!(CATEGORIES.len(), 10);
    }

    #[test]
    fn test_client_initialization() {
        let client = AgentClient::new(None, Some("agent_test_wallet"));
        assert_eq!(client.wallet(), Some("agent_test_wallet"));
    }
}
