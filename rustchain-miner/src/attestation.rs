pub struct SophiaCoreAttestation {
    pub hardware_id: String,
    pub validation_score: u32,
    pub is_valid: bool,
}

impl SophiaCoreAttestation {
    pub fn new(hardware_id: &str, validation_score: u32) -> Self {
        Self {
            hardware_id: hardware_id.to_string(),
            validation_score,
            is_valid: validation_score >= 80,
        }
    }

    pub fn validate(&self) -> Result<(), &'static str> {
        if self.is_valid {
            Ok(())
        } else {
            Err("Sophia Elya validation failed: Hardware requirements not met")
        }
    }
}
