// SPDX-License-Identifier: MIT
//
// Artillery custom processor – generates unique miner identities and
// attestation payloads for each virtual user.

"use strict";

const crypto = require("crypto");

const ARCH_KEYS = ["g4", "g5", "apple_silicon", "modern_x86"];
const PROFILES = {
  g4:            { model: "PowerPC G4 (7447A)", family: "PowerPC" },
  g5:            { model: "PowerPC G5 (970MP)", family: "PowerPC" },
  apple_silicon: { model: "Apple M2 Max",       family: "ARM64"   },
  modern_x86:    { model: "AMD Ryzen 9 7950X",  family: "x86_64"  },
};

function randomHex(len) {
  return crypto.randomBytes(Math.ceil(len / 2)).toString("hex").slice(0, len);
}

function randomMac() {
  return Array.from({ length: 6 }, () =>
    Math.floor(Math.random() * 256).toString(16).padStart(2, "0")
  ).join(":");
}

/**
 * Sets {{ minerId }}, {{ wallet }}, {{ serial }}, {{ mac }},
 * {{ deviceFamily }}, {{ deviceArch }}, {{ deviceModel }} on the
 * virtual-user context.
 */
function generateMinerId(userContext, _events, done) {
  const arch   = ARCH_KEYS[Math.floor(Math.random() * ARCH_KEYS.length)];
  const prof   = PROFILES[arch];
  const uid    = randomHex(8);

  userContext.vars.minerId     = `art-${arch}-${uid}`;
  userContext.vars.wallet      = randomHex(38) + "RTC";
  userContext.vars.serial      = "SN-" + randomHex(12).toUpperCase();
  userContext.vars.mac         = randomMac();
  userContext.vars.deviceFamily = prof.family;
  userContext.vars.deviceArch   = arch;
  userContext.vars.deviceModel  = prof.model;

  return done();
}

/**
 * Builds a pseudo-commitment hash and sets {{ commitment }} on the
 * virtual-user context (requires {{ nonce }} and {{ wallet }} to exist).
 */
function buildAttestPayload(userContext, _events, done) {
  const nonce  = userContext.vars.nonce  || "";
  const wallet = userContext.vars.wallet || "";

  const commitment = crypto
    .createHash("sha256")
    .update(nonce + wallet + Date.now().toString())
    .digest("hex");

  userContext.vars.commitment = commitment;

  return done();
}

module.exports = {
  generateMinerId,
  buildAttestPayload,
};
