// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title  wRTC — Wrapped RTC on Base (RIP-305 Track B)
 * @notice ERC-20 with 6 decimals, burnable, pausable, EIP-2612 permit,
 *         role-based minting, and a hard cumulative mint cap of 20,000 wRTC.
 *
 * @dev    Roles:
 *         - DEFAULT_ADMIN_ROLE → multisig; can grant/revoke all roles.
 *         - MINTER_ROLE        → bridge relayer or minter contract.
 *         - PAUSER_ROLE        → ops key that can freeze transfers in emergencies.
 *
 *         totalMinted is cumulative; burns do NOT reduce it (allocation ceiling).
 */
contract wRTC is ERC20, ERC20Burnable, ERC20Permit, Pausable, AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    uint8   private constant DECIMALS = 6;

    /// @notice RIP-305 Base allocation: 20,000 wRTC (6 decimals)
    uint256 public constant MINT_CAP = 20_000 * 10 ** DECIMALS;

    /// @notice Running total of tokens ever minted (never decreases)
    uint256 public totalMinted;

    event TokensMinted(address indexed to, uint256 amount);
    event TokensBurned(address indexed from, uint256 amount);

    /// @param admin Receives DEFAULT_ADMIN_ROLE, MINTER_ROLE, and PAUSER_ROLE
    ///              (rotate roles in deploy / handover script)
    constructor(address admin)
        ERC20("Wrapped RTC", "wRTC")
        ERC20Permit("Wrapped RTC")
    {
        if (admin == address(0)) revert("wRTC: zero admin");
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(MINTER_ROLE, admin);
        _grantRole(PAUSER_ROLE, admin);
    }

    // ── Token metadata ──────────────────────────────────────────────────

    function decimals() public pure override returns (uint8) {
        return DECIMALS;
    }

    // ── Minting (capped) ────────────────────────────────────────────────

    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
        if (totalMinted + amount > MINT_CAP) revert("wRTC: cap exceeded");
        totalMinted += amount;
        _mint(to, amount);
        emit TokensMinted(to, amount);
    }

    // ── Burning ─────────────────────────────────────────────────────────

    function burn(uint256 amount) public override {
        super.burn(amount);
        emit TokensBurned(msg.sender, amount);
    }

    function burnFrom(address account, uint256 amount) public override {
        super.burnFrom(account, amount);
        emit TokensBurned(account, amount);
    }

    // ── Pausable ────────────────────────────────────────────────────────

    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    // ── Internal overrides (Pausable + ERC20 linearization) ─────────────

    /**
     * @dev Hook that enforces pause on every transfer, mint, and burn.
     *      Required override because both ERC20 and Pausable touch _update.
     */
    function _update(
        address from,
        address to,
        uint256 value
    ) internal override(ERC20) whenNotPaused {
        super._update(from, to, value);
    }

    // ── ERC-165 supportsInterface ───────────────────────────────────────

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    /**
     * @dev Override nonces from ERC20Permit (required for Solidity linearization
     *      when both ERC20Permit and the base contract expose nonces).
     */
    function nonces(address owner)
        public
        view
        override(ERC20Permit)
        returns (uint256)
    {
        return super.nonces(owner);
    }
}
