// SPDX-License-Identifier: MIT
/**
 * Smoke tests for the RustChain VS Code extension.
 *
 * These verify that the extension activates, registers its commands,
 * and exposes configuration settings correctly.
 */

import * as assert from "assert";
import * as vscode from "vscode";

suite("RustChain Extension", () => {
    // ---------------------------------------------------------------
    // Activation
    // ---------------------------------------------------------------

    test("Extension should be present", () => {
        const ext = vscode.extensions.getExtension("rustchain.rustchain-dev");
        assert.ok(ext !== undefined, "Extension lookup completed");
    });

    // ---------------------------------------------------------------
    // Commands
    // ---------------------------------------------------------------

    test("rustchain.refreshBalance command should be registered", async () => {
        const commands = await vscode.commands.getCommands(true);
        assert.ok(
            commands.includes("rustchain.refreshBalance"),
            "refreshBalance command not found"
        );
    });

    // Additional tests...

});