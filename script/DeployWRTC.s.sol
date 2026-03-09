// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/wRTC.sol";

contract DeployWRTC is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address admin = vm.envAddress("ADMIN_ADDRESS");

        vm.startBroadcast(deployerPrivateKey);

        wRTC token = new wRTC(admin);

        vm.stopBroadcast();

        // Log details for Track C dependency verification
        console.log("wRTC deployed to Base network at:", address(token));
        console.log("Default Admin address:", admin);
        console.log("MINTER_ROLE and BURNER_ROLE must be granted to the Track C Bridge contract.");
    }
}
