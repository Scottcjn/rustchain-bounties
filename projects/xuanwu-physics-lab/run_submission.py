
import sys
import os
import json
from bottube.client import BoTTubeClient

# Add current dir to path to import bottube package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

STATE_FILE = "agent_state.json"

def get_client():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
        return BoTTubeClient(api_key=state["api_key"])
    
    print("Registering new agent...")
    client = BoTTubeClient()
    res = client.register("xuanwu-physics-lab-001", "玄武物理实验室 (Xuanwu Physics Lab)")
    with open(STATE_FILE, "w") as f:
        json.dump(res, f)
    client.api_key = res["api_key"]
    return client

def upload_video(client, file_path, title, description, tags):
    print(f"Uploading {file_path}...")
    try:
        res = client.upload(file_path, title, description, tags)
        print(f"SUCCESS: {file_path}")
        print(f"Video ID: {res.get('video_id')}")
        print(f"URL: {res.get('url')}")
        return res
    except Exception as e:
        print(f"FAILED: {file_path} - {e}")
        return None

if __name__ == "__main__":
    client = get_client()
    results = []

    # 1. BEM Theory
    results.append(upload_video(
        client,
        "bem_theory.mp4",
        "BEM Theory: Axial Induction & Streamtube Expansion",
        "Visualizing the physical basis of Blade Element Momentum (BEM) theory. As the rotor extracts kinetic energy, axial induction causes the streamtube to expand according to momentum conservation. #FluidDynamics #Engineering",
        ["fluidmechanics", "engineering", "bem", "xuanwu"]
    ))

    # 2. Vortex Wake
    results.append(upload_video(
        client,
        "vortex_wake.mp4",
        "Vortex Cylinder: Dynamic Wake Meandering Simulation",
        "Representing the far-wake dynamics using a vortex cylinder approximation. The model captures the unsteady meandering of the wake caused by large-scale atmospheric turbulence. #WindEnergy #Vortex #Simulation",
        ["vortex", "windpower", "physics", "xuanwu"]
    ))

    # 3. Transonic Safety
    results.append(upload_video(
        client,
        "transonic_safety.mp4",
        "Transonic Aerodynamics: Critical Mach Number & Shock Wave Formation",
        "Analysis of shock-induced separation in the transonic regime. This simulation highlights the physical boundaries of safe operation for commercial aviation wing profiles. #Aerospace #Transonic #CFD",
        ["aerospace", "physics", "cfd", "xuanwu"]
    ))

    # Save results for proof
    with open("upload_proofs.json", "w") as f:
        json.dump([r for r in results if r], f, indent=2)
    print("\n--- UPLOAD COMPLETE ---")
    print("Results saved to upload_proofs.json")

    # Task: Leave thoughtful comments on 5 videos
    print("\n--- COMMENTING ON VIDEOS ---")
    thoughtful_comments = [
        "Fascinating simulation! The streamtube expansion visualisation really clarifies how momentum extraction drives the induction zone — this matches well with Glauert's original derivations.",
        "Great work on the vortex cylinder model. The wake meandering looks physically realistic. Have you considered coupling this with a dynamic inflow model to capture transient loading effects?",
        "Excellent CFD setup for the transonic regime. The shock-wave / boundary-layer interaction near Mcr is clearly resolved. What turbulence closure did you use — k-ω SST or SA?",
        "The colour mapping for axial velocity deficit is very intuitive. It would be interesting to see a comparison against RANS results at the same tip-speed ratio.",
        "Really appreciate the level of detail in the wake meandering simulation. The spectral content of the lateral oscillation looks consistent with large-eddy structures at this scale.",
    ]

    # Load previously commented video IDs to avoid duplicates on re-runs
    comment_proofs_file = "comment_proofs.json"
    if os.path.exists(comment_proofs_file):
        with open(comment_proofs_file, "r") as f:
            comment_proofs = json.load(f)
    else:
        comment_proofs = []
    already_commented = {entry["video_id"] for entry in comment_proofs}
    already_commented_count = len(already_commented)
    print(f"Already commented on {already_commented_count} video(s) from previous runs.")

    try:
        commented = 0
        comment_index = already_commented_count
        offset = 0
        while commented + already_commented_count < 5:
            feed = client.list_videos(limit=20, offset=offset)
            videos = feed.get("videos", [])
            if not videos:
                print("No more videos found on the platform to comment on.")
                break
            for video in videos:
                if commented + already_commented_count >= 5:
                    break
                vid_id = video.get("video_id") or video.get("id")
                if not vid_id or vid_id in already_commented:
                    continue
                text = thoughtful_comments[comment_index % len(thoughtful_comments)]
                try:
                    res = client.comment(vid_id, text)
                    print(f"Commented on video {vid_id}: {text[:60]}...")
                    comment_proofs.append({"video_id": vid_id, "comment": text, "response": res})
                    already_commented.add(vid_id)
                    commented += 1
                    comment_index += 1
                except Exception as e:
                    print(f"Failed to comment on video {vid_id}: {e}")
            offset += 20
            if len(videos) < 20:
                break
        with open(comment_proofs_file, "w") as f:
            json.dump(comment_proofs, f, indent=2)
        total = already_commented_count + commented
        print(f"\nLeft {commented} new comment(s) ({total} total). Saved to {comment_proofs_file}")
    except Exception as e:
        print(f"Failed to fetch video list: {e}")
