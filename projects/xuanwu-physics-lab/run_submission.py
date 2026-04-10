
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
