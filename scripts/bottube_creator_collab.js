/**
 * BoTTube Creator Collaboration Features
 * Implements collab requests, co-creator linking, and shared revenue tracking.
 *
 * Bounty: #2161 (25 RTC)
 * PoA-Signature: poa_8BsByR6rPqxDPku6dYtdoiSk6bdgE9YETbLQF2RGSw1C
 */

class CreatorCollabSystem {
  constructor(apiBase = "https://api.bottube.io") {
    this.apiBase = apiBase;
    this.pendingCollabs = new Map();
  }

  /**
   * Send a collaboration request to another creator.
   */
  async requestCollab(fromCreatorId, toCreatorId, videoId, splitPercent = 50) {
    if (splitPercent < 1 || splitPercent > 99) throw new Error("Split must be 1–99%");
    const collabId = `collab_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    const request = {
      id: collabId,
      from: fromCreatorId,
      to: toCreatorId,
      videoId,
      split: { fromPercent: splitPercent, toPercent: 100 - splitPercent },
      status: "pending",
      createdAt: new Date().toISOString()
    };
    this.pendingCollabs.set(collabId, request);
    console.log(`[Collab] Request sent: ${fromCreatorId} → ${toCreatorId} (${splitPercent}/${100 - splitPercent})`);
    return request;
  }

  /**
   * Accept a pending collaboration request.
   */
  async acceptCollab(collabId, toCreatorId) {
    const collab = this.pendingCollabs.get(collabId);
    if (!collab) throw new Error(`Collab ${collabId} not found`);
    if (collab.to !== toCreatorId) throw new Error("Not authorized to accept this collab");
    collab.status = "accepted";
    collab.acceptedAt = new Date().toISOString();
    this.pendingCollabs.set(collabId, collab);
    console.log(`[Collab] Accepted: ${collabId}`);
    return collab;
  }

  /**
   * Get all active collabs for a creator.
   */
  getCollabsFor(creatorId) {
    return [...this.pendingCollabs.values()].filter(
      c => c.from === creatorId || c.to === creatorId
    );
  }

  /**
   * Calculate revenue splits for a video.
   */
  calculateRevenueSplit(totalRTC, collabId) {
    const collab = this.pendingCollabs.get(collabId);
    if (!collab || collab.status !== "accepted") return null;
    return {
      [collab.from]: (totalRTC * collab.split.fromPercent) / 100,
      [collab.to]:   (totalRTC * collab.split.toPercent)   / 100,
    };
  }

  /**
   * List pending invites for a creator (notification feed).
   */
  getPendingInvites(creatorId) {
    return [...this.pendingCollabs.values()].filter(
      c => c.to === creatorId && c.status === "pending"
    );
  }
}

// ──────────────────────────────────────────────
// Export for BoTTube SDK integration
// ──────────────────────────────────────────────
if (typeof module !== "undefined") {
  module.exports = { CreatorCollabSystem };
}

// Demo
const collab = new CreatorCollabSystem();
collab.requestCollab("creator_alice", "creator_bob", "vid_001", 60).then(req => {
  console.log("Collab request:", req);
  collab.acceptCollab(req.id, "creator_bob").then(accepted => {
    console.log("Revenue split:", collab.calculateRevenueSplit(100, req.id));
  });
});
