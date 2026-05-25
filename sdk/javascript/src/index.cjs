// CommonJS entry — re-exports the ESM build via a dynamic import wrapper.
//
// Most consumers will use `import { RustChainClient } from "rustchain-sdk"`.
// This shim exists so `require("rustchain-sdk")` returns a Promise of the
// module, matching Node's documented CJS/ESM interop guidance.
//
// Usage:
//   const { RustChainClient } = await require("rustchain-sdk");

module.exports = import("./index.js");
