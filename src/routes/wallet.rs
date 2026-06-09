use actix_web::{web, HttpResponse, HttpRequest};
use serde::{Deserialize, Serialize};
use percent_encoding::{percent_decode, AsciiSet, CONTROLS};

// Define a struct to hold the query parameters
#[derive(Deserialize)]
struct WalletBalanceQuery {
    miner_id: String,
}

// Define a function to handle the wallet balance request
async fn wallet_balance(req: HttpRequest) -> HttpResponse {
    let query: WalletBalanceQuery = web::form::extract(&req).await.unwrap();

    // Check if the miner_id contains any wildcards or whitespace/control characters
    if query.miner_id.contains('*') || query.miner_id.contains(|c: char| !c.is_ascii_graphic()) {
        return HttpResponse::BadRequest().body("Invalid miner_id");
    }

    // Percent decode the miner_id to handle any URL encoded characters
    let decoded_miner_id = percent_decode(query.miner_id.as_bytes())
        .decode_utf8()
        .map_err(|_| HttpResponse::BadRequest().body("Invalid miner_id"))?;

    // Check if the decoded miner_id contains any whitespace/control characters
    if decoded_miner_id.contains(|c: char| !c.is_ascii_graphic()) {
        return HttpResponse::BadRequest().body("Invalid miner_id");
    }

    // Get the wallet balance
    let balance = get_wallet_balance(&decoded_miner_id).await;

    // Return the wallet balance with the original miner_id
    HttpResponse::Ok().json(json!({
        "miner_id": query.miner_id,
        "amount_i64": balance.amount_i64,
        "amount_rtc": balance.amount_rtc,
    }))
}

// Define a function to get the wallet balance
async fn get_wallet_balance(miner_id: &str) -> WalletBalance {
    // Implement the logic to get the wallet balance
    // ...
}

// Define a struct to hold the wallet balance
#[derive(Serialize)]
struct WalletBalance {
    amount_i64: i64,
    amount_rtc: f64,
}