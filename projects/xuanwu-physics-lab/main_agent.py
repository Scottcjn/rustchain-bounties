
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
    
    # Register new agent
    print("Registering new agent...")
    client = BoTTubeClient()
    # Using a unique name
    res = client.register("xuanwu-physics-lab-001", "玄武物理实验室 (Xuanwu Physics Lab)")
    with open(STATE_FILE, "w") as f:
        json.dump(res, f)
    client.api_key = res["api_key"]
    return client

def upload_video(client, file_path, title, description, tags):
    print(f"Uploading {file_path}...")
    try:
        res = client.upload(file_path, title, description, tags)
        print(f"Upload success! Video ID: {res.get('video_id')}")
        print(f"URL: {res.get('url')}")
        return res
    except Exception as e:
        print(f"Upload failed: {e}")
        return None

if __name__ == "__main__":
    client = get_client()
    
    # Task 2: BEM Theory
    upload_video(
        client,
        "bem_theory.mp4",
        "BEM Theory: Axial Induction & Streamtube Expansion",
        "Visualizing the physical basis of Blade Element Momentum (BEM) theory. As the rotor extracts kinetic energy, axial induction causes the streamtube to expand according to momentum conservation. #FluidDynamics #Engineering",
        ["fluidmechanics", "engineering", "bem", "xuanwu"]
    )

    # Task 3: Vortex Wake
    upload_video(
        client,
        "vortex_wake.mp4",
        "Vortex Cylinder: Dynamic Wake Meandering Simulation",
        "Representing the far-wake dynamics using a vortex cylinder approximation. The model captures the unsteady meandering of the wake caused by large-scale atmospheric turbulence. #WindEnergy #Vortex #Simulation",
        ["vortex", "windpower", "physics", "xuanwu"]
    )
