use serde::{Deserialize, Serialize};

pub const PLATFORM_FEE_RATE: f64 = 0.05;

pub const CATEGORIES: &[&str] = &[
    "research",
    "code",
    "video",
    "audio",
    "writing",
    "translation",
    "data",
    "design",
    "testing",
    "other",
];

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct EscrowCalculation {
    pub reward_rtc: f64,
    pub fee_rtc: f64,
    pub total_escrow_rtc: f64,
}

impl EscrowCalculation {
    pub fn new(reward_rtc: f64) -> Self {
        let fee_rtc = (reward_rtc * PLATFORM_FEE_RATE * 10000.0).round() / 10000.0;
        let total_escrow_rtc = ( (reward_rtc + fee_rtc) * 10000.0).round() / 10000.0;
        Self {
            reward_rtc,
            fee_rtc,
            total_escrow_rtc,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Job {
    pub id: String,
    pub title: String,
    pub category: String,
    #[serde(default)]
    pub reward_rtc: f64,
    #[serde(default)]
    pub status: String,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub poster_wallet: Option<String>,
    #[serde(default)]
    pub worker_wallet: Option<String>,
    #[serde(default)]
    pub created_at: Option<String>,
    #[serde(default)]
    pub expires_at: Option<String>,
    #[serde(default)]
    pub escrow_locked_rtc: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ActivityEntry {
    #[serde(default)]
    pub time: String,
    #[serde(default)]
    pub event: String,
    #[serde(default)]
    pub actor: String,
    #[serde(default)]
    pub note: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct RatingEntry {
    #[serde(default)]
    pub score: u8,
    #[serde(default)]
    pub review: Option<String>,
    #[serde(default)]
    pub reviewer: String,
    #[serde(default)]
    pub created_at: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct JobDetailResponse {
    pub ok: bool,
    pub job: Job,
    #[serde(default)]
    pub activity: Vec<ActivityEntry>,
    #[serde(default)]
    pub ratings: Vec<RatingEntry>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct CategoryStat {
    pub category: String,
    pub jobs: u64,
    pub total_rtc: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct MarketplaceStats {
    #[serde(default)]
    pub active_agents: u64,
    #[serde(default)]
    pub completed_jobs: u64,
    #[serde(default)]
    pub open_jobs: u64,
    #[serde(default)]
    pub total_jobs: u64,
    #[serde(default)]
    pub total_rtc_volume: f64,
    #[serde(default)]
    pub total_fees_collected: f64,
    #[serde(default)]
    pub escrow_balance_rtc: f64,
    #[serde(default)]
    pub categories: Vec<CategoryStat>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Reputation {
    #[serde(default)]
    pub trust_score: f64,
    #[serde(default)]
    pub trust_level: String,
    #[serde(default)]
    pub avg_rating: f64,
    #[serde(default)]
    pub completed_jobs: u64,
    #[serde(default)]
    pub total_rtc_earned: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StatsResponse {
    pub ok: bool,
    pub stats: MarketplaceStats,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct JobListResponse {
    pub ok: bool,
    #[serde(default)]
    pub jobs: Vec<Job>,
    #[serde(default)]
    pub categories: Vec<String>,
    #[serde(default)]
    pub total: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ReputationResponse {
    pub ok: bool,
    pub wallet_id: String,
    pub reputation: Option<Reputation>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PostJobRequest {
    pub poster_wallet: String,
    pub title: String,
    pub category: String,
    pub reward_rtc: f64,
    #[serde(default)]
    pub description: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub expires_at: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClaimJobRequest {
    pub worker_wallet: String,
    #[serde(default)]
    pub note: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeliverJobRequest {
    pub worker_wallet: String,
    #[serde(default)]
    pub deliverable_url: String,
    #[serde(default)]
    pub summary: String,
    #[serde(default)]
    pub result_summary: String,
    #[serde(default)]
    pub artifact_hash: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AcceptJobRequest {
    pub poster_wallet: String,
    pub rating: u8,
    #[serde(default)]
    pub review: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DisputeJobRequest {
    pub poster_wallet: String,
    #[serde(default)]
    pub reason: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CancelJobRequest {
    pub poster_wallet: String,
    #[serde(default)]
    pub reason: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct GenericResponse {
    pub ok: bool,
    #[serde(default)]
    pub message: Option<String>,
    #[serde(default)]
    pub job: Option<Job>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct PostJobResponse {
    pub ok: bool,
    pub job: Job,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct PayoutDetails {
    pub worker_rtc: f64,
    pub fee_rtc: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct AcceptJobResponse {
    pub ok: bool,
    #[serde(default)]
    pub job: Option<Job>,
    #[serde(default)]
    pub payout: Option<PayoutDetails>,
}
