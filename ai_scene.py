import sys
import retro90s_blender

def main():
    if len(sys.argv) < 5:
        print("Usage: python ai_scene.py --prompt <prompt> --output <output_file>")
        sys.exit(1)

    prompt = sys.argv[2]
    output_file = sys.argv[4]

    # Generate the Blender scene
    scene = retro90s_blender.Scene()
    scene.add_camera(retro90s_blender.retro_orbit_camera())
    scene.add_objects(prompt)
    scene.save(output_file)

if __name__ == "__main__":
    main()
