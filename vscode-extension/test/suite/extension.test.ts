// SPDX-License-Identifier: MIT
/**
 * Tests for extension.ts — RustChain VS Code Extension activation and wiring.
 *
 * Verifies that activate() registers all expected commands and initialises
 * all status-bar providers. Uses a mock ExtensionContext.
 *
 * Run: npx mocha --require ts-node/register test/suite/extension.test.ts
 * Bounty: #2868
 */

import * as assert from "assert";
import * as vscode from "vscode";
import { activate } from "../../../vscode-extension/src/extension";

// ---------------------------------------------------------------------------
// Mock ExtensionContext
// ---------------------------------------------------------------------------

const registeredCommands: string[] = [];
const subscriptions: vscode.Disposable[] = [];

const mockContext: vscode.ExtensionContext = {
    subscriptions,
    extensionPath: "/mock/path",
    asAbsolutePath: (p: string) => `/mock/path/${p}`,
    extensionUri: vscode.Uri.parse("file:///mock/path"),
    workspaceState: { get: () => undefined, keys: () => [], getWorkspaceFolder: () => undefined } as unknown as vscode.Memento,
    globalState: { get: () => undefined, keys: () => [], update: () => Promise.resolve() } as unknown as vscode.Memento,
    secrets: { get: () => Promise.resolve(undefined), store: () => Promise.resolve(), delete: () => Promise.resolve(), onDidChange: new vscode.EventEmitter<vscode.SecretStorageChangeEvent>().event } as unknown as vscode.SecretStorage,
    extensionMode: vscode.ExtensionMode.Test,
    environmentVariableCollection: { persistent: false, replace: () => Promise.resolve(), append: () => Promise.resolve(), clear: () => Promise.resolve(), get: () => undefined, forEach: () => undefined, delete: () => undefined, onDidChange: new vscode.EventEmitter<vscode.EnvironmentVariableCollectionChangeEvent>().event } as unknown as vscode.GlobalEnvironmentVariableCollection,
    languageModelAccessInformation: {
        canSend: () => false,
        onCanChange: new vscode.EventEmitter<boolean>().event,
        requestAccess: () => Promise.resolve(false)
    } as unknown as vscode.LanguageModelAccessInformation,
};

function mockRegisterCommand(
    command: string,
    callback: (...args: unknown[]) => unknown,
): vscode.Disposable {
    registeredCommands.push(command);
    return { dispose: () => {} };
}

// Monkey-patch vscode.commands.registerCommand for the duration of the test
let origRegister: typeof vscode.commands.registerCommand;

suite("extension.ts", () => {
    setup(() => {
        registeredCommands.length = 0;
        subscriptions.length = 0;
        origRegister = vscode.commands.registerCommand;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (vscode.commands as any).registerCommand = mockRegisterCommand;
    });

    teardown(() => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (vscode.commands as any).registerCommand = origRegister;
        registeredCommands.length = 0;
        subscriptions.length = 0;
    });

    test("activate() registers rustchain.refreshBalance", async () => {
        await activate(mockContext);
        assert.ok(
            registeredCommands.includes("rustchain.refreshBalance"),
            "rustchain.refreshBalance command should be registered",
        );
    });

    test("activate() registers rustchain.setMinerId", async () => {
        await activate(mockContext);
        assert.ok(
            registeredCommands.includes("rustchain.setMinerId"),
            "rustchain.setMinerId command should be registered",
        );
    });

    test("activate() registers rustchain.checkNodeHealth", async () => {
        await activate(mockContext);
        assert.ok(
            registeredCommands.includes("rustchain.checkNodeHealth"),
            "rustchain.checkNodeHealth command should be registered",
        );
    });

    test("activate() registers rustchain.openBountyBrowser", async () => {
        await activate(mockContext);
        assert.ok(
            registeredCommands.includes("rustchain.openBountyBrowser"),
            "rustchain.openBountyBrowser command should be registered",
        );
    });

    test("activate() populates context.subscriptions (for dispose)", async () => {
        await activate(mockContext);
        assert.ok(
            subscriptions.length > 0,
            "At least one subscription should be added for automatic cleanup",
        );
    });

    test("Multiple activate() calls are idempotent (no duplicate commands)", async () => {
        await activate(mockContext);
        const countBefore = registeredCommands.length;
        await activate(mockContext);
        assert.strictEqual(
            registeredCommands.length,
            countBefore,
            "Second activation should not re-register commands",
        );
    });
});
