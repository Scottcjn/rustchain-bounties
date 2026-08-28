use std::fs;
use std::path::Path;

#[cfg(test)]
mod tests {
    use super::*;
    
    const ARTICLE_PATH: &str = "articles/comparisons/rustchain-vs-monero.md";
    
    #[test]
    fn test_article_exists() {
        assert!(Path::new(ARTICLE_PATH).exists(), "Article file should exist");
    }
    
    #[test]
    fn test_article_not_empty() {
        let content = fs::read_to_string(ARTICLE_PATH)
            .expect("Should be able to read article");
        assert!(!content.is_empty(), "Article should not be empty");
    }
    
    #[test]
    fn test_article_has_required_sections() {
        let content = fs::read_to_string(ARTICLE_PATH)
            .expect("Should be able to read article");
        
        let required_sections = [
            "# RustChain vs Monero",
            "## Overview",
            "## Core Technology Comparison",
            "## Mining: CPU-First Philosophy",
            "## Privacy Features",
            "## Community & Governance",
            "## Use Case Scenarios",
            "## Performance Benchmarks",
            "## Conclusion",
            "## References",
        ];
        
        for section in &required_sections {
            assert!(
                content.contains(section),
                "Article should contain section: {}", section
            );
        }
    }
    
    #[test]
    fn test_article_has_code_blocks() {
        let content = fs::read_to_string(ARTICLE_PATH)
            .expect("Should be able to read article");
        
        let code_blocks = content.matches("```").count();
        assert!(code_blocks >= 6, "Article should have at least 3 code blocks (6 ``` markers)");
    }
    
    #[test]
    fn test_article_has_table() {
        let content = fs::read_to_string(ARTICLE_PATH)
            .expect("Should be able to read article");
        
        assert!(content.contains("|"), "Article should contain markdown tables");
    }
    
    #[test]
    fn test_article_word_count() {
        let content = fs::read_to_string(ARTICLE_PATH)
            .expect("Should be able to read article");
        
        let word_count = content.split_whitespace().count();
        assert!(
            word_count >= 500,
            "Article should have at least 500 words, got {}", word_count
        );
    }
    
    #[test]
    fn test_article_has_bounty_header() {
        let content = fs::read_to_string(ARTICLE_PATH)
            .expect("Should be able to read article");
        
        assert!(
            content.contains("**Bounty**: 5 RTC"),
            "Article should mention the bounty amount"
        );
    }
    
    #[test]
    fn test_article_has_comparison_metrics() {
        let content = fs::read_to_string(ARTICLE_PATH)
            .expect("Should be able to read article");
        
        let metrics = ["TPS", "Energy", "Storage", "Sync Time"];
        for metric in &metrics {
            assert!(
                content.contains(metric),
                "Article should mention metric: {}", metric
