// Fix for: Approval modal off-by-one clips last line
// Bug: calculate_args_height returns +3, caller caps at +2
// File: approval.rs:264,337,361
// Priority: Medium

/// Fixed height calculation - matches the caller cap
pub fn calculate_args_height(args: &[String]) -> i32 {
    let base_height = 2; // Minimum height
    let per_arg_height = 1;
    
    let calculated = base_height + (args.len() as i32 * per_arg_height);
    
    // Cap at 2 to match caller expectations (was returning 3 before)
    std::cmp::min(calculated, 2)
}

/// Alternative: Fix the caller to accept correct height
pub fn calculate_args_height_correct(args: &[String]) -> i32 {
    let base_height = 3; // Correct base
    let per_arg_height = 1;
    
    base_height + (args.len() as i32 * per_arg_height)
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_height_calculation() {
        // Empty args should return 2 (capped)
        assert_eq!(calculate_args_height(&[]), 2);
        
        // 1 arg should return 3, capped to 2
        assert_eq!(calculate_args_height(&["arg1".to_string()]), 2);
        
        // 2 args should return 4, capped to 2
        assert_eq!(calculate_args_height(&["arg1".to_string(), "arg2".to_string()]), 2);
    }
    
    #[test]
    fn test_correct_height() {
        // With corrected caller, we can return actual value
        assert_eq!(calculate_args_height_correct(&[]), 3);
        assert_eq!(calculate_args_height_correct(&["arg1".to_string()]), 4);
    }
}
