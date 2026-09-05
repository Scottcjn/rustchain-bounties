use reqwest::Client as HttpClient;
use std::time::Duration;

use crate::error::{Error, Result};
use crate::models::*;

pub const DEFAULT_NODE_URL: &str = "https://50.28.86.131";

#[derive(Clone, Debug)]
pub struct AgentClient {
    base_url: String,
    wallet: Option<String>,
    http: HttpClient,
}

#[derive(Clone, Debug, Default)]
pub struct JobListOptions {
    pub category: Option<String>,
    pub status: Option<String>,
    pub limit: Option<u32>,
    pub offset: Option<u32>,
    pub min_reward: Option<f64>,
}

impl AgentClient {
    pub fn new(base_url: Option<&str>, wallet: Option<&str>) -> Self {
        let base = base_url.unwrap_or(DEFAULT_NODE_URL).trim_end_matches('/').to_string();
        let http = HttpClient::builder()
            .timeout(Duration::from_secs(30))
            .danger_accept_invalid_certs(true)
            .build()
            .unwrap_or_default();

        Self {
            base_url: base,
            wallet: wallet.map(|s| s.to_string()),
            http,
        }
    }

    pub fn with_http_client(base_url: Option<&str>, wallet: Option<&str>, http: HttpClient) -> Self {
        let base = base_url.unwrap_or(DEFAULT_NODE_URL).trim_end_matches('/').to_string();
        Self {
            base_url: base,
            wallet: wallet.map(|s| s.to_string()),
            http,
        }
    }

    pub fn wallet(&self) -> Option<&str> {
        self.wallet.as_deref()
    }

    pub async fn get_stats(&self) -> Result<StatsResponse> {
        let url = format!("{}/agent/stats", self.base_url);
        let resp = self.http.get(&url).send().await?;
        if !resp.status().is_success() {
            let status = resp.status().as_u16();
            let text = resp.text().await.unwrap_or_default();
            return Err(Error::Api {
                status,
                message: text,
                body: None,
            });
        }
        let data = resp.json::<StatsResponse>().await?;
        Ok(data)
    }

    pub async fn list_jobs(&self, opts: JobListOptions) -> Result<JobListResponse> {
        let url = format!("{}/agent/jobs", self.base_url);
        let mut req = self.http.get(&url);
        if let Some(limit) = opts.limit {
            req = req.query(&[("limit", limit.to_string())]);
        }
        if let Some(offset) = opts.offset {
            req = req.query(&[("offset", offset.to_string())]);
        }
        if let Some(category) = opts.category {
            req = req.query(&[("category", category)]);
        }
        if let Some(status) = opts.status {
            req = req.query(&[("status", status)]);
        }
        if let Some(min_reward) = opts.min_reward {
            req = req.query(&[("min_reward", min_reward.to_string())]);
        }

        let resp = req.send().await?;
        if !resp.status().is_success() {
            let status = resp.status().as_u16();
            let text = resp.text().await.unwrap_or_default();
            return Err(Error::Api {
                status,
                message: text,
                body: None,
            });
        }
        let data = resp.json::<JobListResponse>().await?;
        Ok(data)
    }

    pub async fn get_job(&self, job_id: &str) -> Result<JobDetailResponse> {
        if job_id.trim().is_empty() {
            return Err(Error::Validation("job_id must not be empty".to_string()));
        }
        let url = format!("{}/agent/jobs/{}", self.base_url, job_id.trim());
        let resp = self.http.get(&url).send().await?;
        if !resp.status().is_success() {
            let status = resp.status().as_u16();
            let text = resp.text().await.unwrap_or_default();
            return Err(Error::Api {
                status,
                message: text,
                body: None,
            });
        }
        let data = resp.json::<JobDetailResponse>().await?;
        Ok(data)
    }

    pub async fn post_job(&self, req: PostJobRequest) -> Result<PostJobResponse> {
        if req.title.trim().is_empty() {
            return Err(Error::Validation("title must not be empty".to_string()));
        }
        if req.reward_rtc <= 0.0 {
            return Err(Error::Validation("reward_rtc must be positive".to_string()));
        }
        let url = format!("{}/agent/jobs", self.base_url);
        let resp = self.http.post(&url).json(&req).send().await?;
        if !resp.status().is_success() {
            let status = resp.status().as_u16();
            let text = resp.text().await.unwrap_or_default();
            return Err(Error::Api {
                status,
                message: text,
                body: None,
            });
        }
        let data = resp.json::<PostJobResponse>().await?;
        Ok(data)
    }

    pub async fn claim_job(&self, job_id: &str, req: ClaimJobRequest) -> Result<GenericResponse> {
        if job_id.trim().is_empty() {
            return Err(Error::Validation("job_id must not be empty".to_string()));
        }
        let url = format!("{}/agent/jobs/{}/claim", self.base_url, job_id.trim());
        let resp = self.http.post(&url).json(&req).send().await?;
        if !resp.status().is_success() {
            let status = resp.status().as_u16();
            let text = resp.text().await.unwrap_or_default();
            return Err(Error::Api {
                status,
                message: text,
                body: None,
            });
        }
        let data = resp.json::<GenericResponse>().await?;
        Ok(data)
    }

    pub async fn deliver_job(&self, job_id: &str, req: DeliverJobRequest) -> Result<GenericResponse> {
        if job_id.trim().is_empty() {
            return Err(Error::Validation("job_id must not be empty".to_string()));
        }
        let url = format!("{}/agent/jobs/{}/deliver", self.base_url, job_id.trim());
        let resp = self.http.post(&url).json(&req).send().await?;
        if !resp.status().is_success() {
            let status = resp.status().as_u16();
            let text = resp.text().await.unwrap_or_default();
            return Err(Error::Api {
                status,
                message: text,
                body: None,
            });
        }
        let data = resp.json::<GenericResponse>().await?;
        Ok(data)
    }

    pub async fn accept_job(&self, job_id: &str, req: AcceptJobRequest) -> Result<AcceptJobResponse> {
        if job_id.trim().is_empty() {
            return Err(Error::Validation("job_id must not be empty".to_string()));
        }
        if req.rating < 1 || req.rating > 5 {
            return Err(Error::Validation("rating must be between 1 and 5".to_string()));
        }
        let url = format!("{}/agent/jobs/{}/accept", self.base_url, job_id.trim());
        let resp = self.http.post(&url).json(&req).send().await?;
        if !resp.status().is_success() {
            let status = resp.status().as_u16();
            let text = resp.text().await.unwrap_or_default();
            return Err(Error::Api {
                status,
                message: text,
                body: None,
            });
        }
        let data = resp.json::<AcceptJobResponse>().await?;
        Ok(data)
    }

    pub async fn dispute_job(&self, job_id: &str, req: DisputeJobRequest) -> Result<GenericResponse> {
        if job_id.trim().is_empty() {
            return Err(Error::Validation("job_id must not be empty".to_string()));
        }
        let url = format!("{}/agent/jobs/{}/dispute", self.base_url, job_id.trim());
        let resp = self.http.post(&url).json(&req).send().await?;
        if !resp.status().is_success() {
            let status = resp.status().as_u16();
            let text = resp.text().await.unwrap_or_default();
            return Err(Error::Api {
                status,
                message: text,
                body: None,
            });
        }
        let data = resp.json::<GenericResponse>().await?;
        Ok(data)
    }

    pub async fn cancel_job(&self, job_id: &str, req: CancelJobRequest) -> Result<GenericResponse> {
        if job_id.trim().is_empty() {
            return Err(Error::Validation("job_id must not be empty".to_string()));
        }
        let url = format!("{}/agent/jobs/{}/cancel", self.base_url, job_id.trim());
        let resp = self.http.post(&url).json(&req).send().await?;
        if !resp.status().is_success() {
            let status = resp.status().as_u16();
            let text = resp.text().await.unwrap_or_default();
            return Err(Error::Api {
                status,
                message: text,
                body: None,
            });
        }
        let data = resp.json::<GenericResponse>().await?;
        Ok(data)
    }

    pub async fn get_reputation(&self, wallet: &str) -> Result<ReputationResponse> {
        if wallet.trim().is_empty() {
            return Err(Error::Validation("wallet must not be empty".to_string()));
        }
        let url = format!("{}/agent/reputation/{}", self.base_url, wallet.trim());
        let resp = self.http.get(&url).send().await?;
        if !resp.status().is_success() {
            let status = resp.status().as_u16();
            let text = resp.text().await.unwrap_or_default();
            return Err(Error::Api {
                status,
                message: text,
                body: None,
            });
        }
        let data = resp.json::<ReputationResponse>().await?;
        Ok(data)
    }
}
