//! Cross-Chain Airdrop Locker - Solana Program
//! 
//! This program locks wRTC tokens on Solana for cross-chain transfers to Base.

use anchor_lang::prelude::*;
use anchor_spl::token::{self, Mint, Token, TokenAccount};

declare_id!("Locker111111111111111111111111111111111111");

#[program]
pub mod cross_chain_locker {
    use super::*;

    /// Initialize a locker account for a user
    pub fn initialize_locker(ctx: Context<InitializeLocker>) -> Result<()> {
        let locker = &mut ctx.accounts.locker;
        locker.user = ctx.accounts.user.key();
        locker.token_mint = ctx.accounts.token_mint.key();
        locker.locked_amount = 0;
        locker.nonce = 0;
        Ok(())
    }

    /// Lock tokens for cross-chain transfer
    pub fn lock_tokens(ctx: Context<LockTokens>, amount: u64, destination: String) -> Result<()> {
        let locker = &mut ctx.accounts.locker;
        
        require!(amount > 0, ErrorCode::InvalidAmount);
        require!(destination.len() <= 42, ErrorCode::InvalidDestination); // Base address length
        
        // Transfer tokens from user to locker
        token::transfer(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                token::Transfer {
                    from: ctx.accounts.user_token_account.to_account_info(),
                    to: ctx.accounts.locker_token_account.to_account_info(),
                    authority: ctx.accounts.user.to_account_info(),
                },
            ),
            amount,
        )?;
        
        locker.locked_amount = locker.locked_amount.checked_add(amount).unwrap();
        locker.nonce = locker.nonce.checked_add(1).unwrap();
        
        // Emit event for cross-chain bridge
        emit!(TokensLocked {
            user: ctx.accounts.user.key(),
            amount,
            destination,
            nonce: locker.nonce,
        });
        
        Ok(())
    }

    /// Unlock tokens after cross-chain transfer is reversed
    pub fn unlock_tokens(ctx: Context<UnlockTokens>, amount: u64) -> Result<()> {
        let locker = &mut ctx.accounts.locker;
        
        require!(locker.locked_amount >= amount, ErrorCode::InsufficientLockedTokens);
        
        // Transfer tokens back to user
        token::transfer(
            CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(),
                token::Transfer {
                    from: ctx.accounts.locker_token_account.to_account_info(),
                    to: ctx.accounts.user_token_account.to_account_info(),
                    authority: ctx.accounts.locker.to_account_info(),
                },
                &[&[
                    b"locker",
                    locker.user.as_ref(),
                    &[locker.nonce],
                ]],
            ),
            amount,
        )?;
        
        locker.locked_amount = locker.locked_amount.checked_sub(amount).unwrap();
        
        emit!(TokensUnlocked {
            user: ctx.accounts.user.key(),
            amount,
        });
        
        Ok(())
    }
}

#[derive(Accounts)]
pub struct InitializeLocker<'info> {
    #[account(mut)]
    pub user: Signer<'info>,
    
    #[account(
        init,
        payer = user,
        space = 8 + Locker::SIZE,
        seeds = [b"locker", user.key().as_ref()],
        bump,
    )]
    pub locker: Account<'info, Locker>,
    
    pub token_mint: Account<'info, Mint>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct LockTokens<'info> {
    #[account(mut)]
    pub user: Signer<'info>,
    
    #[account(
        mut,
        seeds = [b"locker", user.key().as_ref()],
        bump,
    )]
    pub locker: Account<'info, Locker>,
    
    #[account(mut)]
    pub user_token_account: Account<'info, TokenAccount>,
    
    #[account(
        mut,
        associated_token::mint = token_mint,
        associated_token::authority = locker,
    )]
    pub locker_token_account: Account<'info, TokenAccount>,
    
    pub token_mint: Account<'info, Mint>,
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct UnlockTokens<'info> {
    #[account(mut)]
    pub user: Signer<'info>,
    
    #[account(
        mut,
        seeds = [b"locker", user.key().as_ref()],
        bump,
        has_one = user,
    )]
    pub locker: Account<'info, Locker>,
    
    #[account(mut)]
    pub user_token_account: Account<'info, TokenAccount>,
    
    #[account(
        mut,
        associated_token::mint = token_mint,
        associated_token::authority = locker,
    )]
    pub locker_token_account: Account<'info, TokenAccount>,
    
    pub token_mint: Account<'info, Mint>,
    pub token_program: Program<'info, Token>,
}

#[account]
pub struct Locker {
    pub user: Pubkey,
    pub token_mint: Pubkey,
    pub locked_amount: u64,
    pub nonce: u64,
}

impl Locker {
    pub const SIZE: usize = 32 + 32 + 8 + 8; // user + mint + amount + nonce
}

#[event]
pub struct TokensLocked {
    #[index]
    pub user: Pubkey,
    pub amount: u64,
    pub destination: String,
    pub nonce: u64,
}

#[event]
pub struct TokensUnlocked {
    #[index]
    pub user: Pubkey,
    pub amount: u64,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Invalid amount")]
    InvalidAmount,
    #[msg("Invalid destination address")]
    InvalidDestination,
    #[msg("Insufficient locked tokens")]
    InsufficientLockedTokens,
}
