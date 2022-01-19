import bpy
import math
from mathutils import Vector, Quaternion, Euler
from .Network import ReceiveUpdate, NetIsConnected, vicon_state
from bpy.app.handlers import persistent

recording = False
def SetRecording(r):
    global recording
    recording = r

def ApplyViconState(target, t2b, vo, f):
    t = vo[0]
    r = vo[1]
    zrot = math.radians(t2b.zrot)
    # Fix translation
    t *= t2b.scale
    t.rotate(Euler((0.0, 0.0, zrot), 'XYZ'))
    o = list(t2b.origin)
    t.x += o[0]
    t.y += o[1]
    # Fix rotation
    r.rotate_axis('Z', zrot)
    # Apply
    target.location = t
    target.rotation_mode = 'XYZ'
    target.rotation_euler = r
    if recording:
        target.keyframe_insert(data_path='location', frame=f)
        target.keyframe_insert(data_path='rotation_euler', frame=f)

@persistent
def T2BFrameHandler(scene):
    if not NetIsConnected():
        return
    ReceiveUpdate()
    t2b = scene.t2b
    f = scene.frame_current
    maxf = scene.frame_end
    if t2b.extend and recording and f >= maxf - 1:
        scene.frame_end = f + 1
    for to in t2b.objs:
        if not to.enab:
            continue
        o = to.obj
        vo = vicon_state.get(o.name, None)
        if vo is not None:
            ApplyViconState(o, t2b, vo, f)
        if o.type == 'ARMATURE':
            for b in o.pose.bones:
                vo = vicon_state.get(o.name + '_' + b.name, None)
                if vo is not None:
                    ApplyViconState(b, t2b, vo, f)
    
def Anim_register():
    bpy.app.handlers.frame_change_pre.append(T2BFrameHandler)

def Anim_unregister():
    if T2BFrameHandler in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(T2BFrameHandler)
