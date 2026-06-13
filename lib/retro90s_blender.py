# lib/retro90s_blender.py
# Existing library with orbit camera and render animation functions

import bpy
import os

def retro_orbit_camera(radius=10, height=5, frames=24):
    """Create a camera that orbits around the origin."""
    # Remove existing cameras
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            bpy.data.objects.remove(obj, do_unlink=True)

    # Add new camera
    bpy.ops.object.camera_add(location=(radius, 0, height))
    cam = bpy.context.object
    cam.name = 'RetroCamera'
    cam.data.lens = 35
    cam.data.clip_end = 1000

    # Add empty for target
    bpy.ops.object.empty_add(location=(0, 0, 0))
    target = bpy.context.object
    target.name = 'CameraTarget'

    # Add Track To constraint
    constraint = cam.constraints.new(type='TRACK_TO')
    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    # Animate camera location
    cam.animation_data_create()
    cam.animation_data.action = bpy.data.actions.new(name='CameraOrbit')
    for frame in range(1, frames + 1):
        angle = frame / frames * 360
        x = radius * bpy.utils.radians(angle).cos()
        y = radius * bpy.utils.radians(angle).sin()
        cam.location = (x, y, height)
        cam.keyframe_insert(data_path='location', index=-1, frame=frame)

def retro_render_anim(output_path='/tmp/frame_', num_frames=24):
    """Render animation to image sequence."""
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.filepath = output_path
    scene.render.image_settings.file_format = 'PNG'
    scene.frame_start = 1
    scene.frame_end = num_frames
    bpy.ops.render.render(animation=True)