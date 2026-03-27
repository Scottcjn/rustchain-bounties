// SPDX-License-Identifier: MIT
/**
 * Test runner entry point for the RustChain VS Code extension.
 *
 * This launches a VS Code instance with the extension loaded and
 * runs the Mocha test suite under test/suite/.
 */

import * as path from "path";
import { runTests } from "@vscode/test-electron";

async function main(): Promise<void> {
    const extensionDevelopmentPath = path.resolve(__dirname, "../../");
    const extensionTestsPath = path.resolve(__dirname, "./suite/index");

    await runTests({ extensionDevelopmentPath, extensionTestsPath });
}

main().catch((err) => {
    console.error("Failed to run tests:", err);
    process.exit(1);
});
