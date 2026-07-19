import bpy

def retro_orbit_camera():
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    camera = bpy.context.object
    camera.data.type = 'PERSP'
    camera.data.lens = 35
    return camera

def retro_render_anim(num_frames):
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = num_frames
    bpy.context.scene.render.filepath = "//frame_"
    bpy.ops.render.render(animation=True)
