import argparse
from retro90s_blender import retro_orbit_camera, retro_render_anim

def generate_scene(prompt, output_file):
    # Use LLM approach to generate scene
    # ...

    # Emit retro90s_blender calls to create scene
    retro_orbit_camera()
    retro_render_anim()

    # Save scene to file
    # ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    generate_scene(args.prompt, args.output)