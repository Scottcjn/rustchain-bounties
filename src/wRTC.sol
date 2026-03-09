// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title Wrapped RTC (wRTC)
 * @dev Base-side ERC-20 implementation for RIP-305 Airdrop.
 * Phase 1 bridge control uses AccessControl for explicit permission boundaries.
 */
contract wRTC is ERC20, AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BURNER_ROLE = keccak256("BURNER_ROLE");

    /**
     * @dev Sets up the token with a default admin role.
     */
    constructor(address defaultAdmin) ERC20("Wrapped RTC", "wRTC") {
        require(defaultAdmin != address(0), "Admin cannot be zero address");
        _grantRole(DEFAULT_ADMIN_ROLE, defaultAdmin);
    }

    /**
     * @dev Explicit decimals definition (18 by default in OZ, explicit here for specification).
     */
    function decimals() public view virtual override returns (uint8) {
        return 18;
    }

    /**
     * @dev Mints tokens to a specified address. Callable only by MINTER_ROLE (Bridge).
     */
    function mint(address to, uint256 amount) public onlyRole(MINTER_ROLE) {
        _mint(to, amount);
    }

    /**
     * @dev Burns tokens from a specified address. Callable only by BURNER_ROLE (Bridge).
     */
    function burn(address from, uint256 amount) public onlyRole(BURNER_ROLE) {
        _burn(from, amount);
    }
}
