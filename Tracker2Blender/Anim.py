import bpy
import math
from mathutils import Vector, Quaternion, Euler, Matrix
from .Network import ReceiveUpdate, NetIsConnected, vicon_state
from bpy.app.handlers import persistent

recording = False
def SetRecording(r):
    global recording
    recording = r

def TransformViconState(t2b, vo):
    t = vo[0]
    r = vo[1]
    r = Euler((r.x, r.y, r.z), 'ZYX')
    r = r.to_quaternion()
    r = r.to_euler('XYZ')
    zrot = math.radians(t2b.zrot)
    # Fix translation
    t *= t2b.scale
    t.rotate(Euler((0.0, 0.0, zrot), 'XYZ'))
    o = list(t2b.origin)
    t.x += o[0]
    t.y += o[1]
    # Fix rotation
    r.rotate_axis('Z', zrot)
    return t, r

def CheckApplyViconState(o, bone, name, t2b, f):
    vo = vicon_state.get(name, None)
    if vo is None:
        return
    t, r = TransformViconState(t2b, vo)
    # Possibly transform to local space
    if bone is not None and bone.use_local_location:
        world_to_local = Matrix()
        ml = bone.matrix_local
        for i in range(4):
            for j in range(4):
                world_to_local[i][j] = ml[i][j]
        world_to_local.invert_safe()
        t = world_to_local @ t
        r.rotate(world_to_local)
    # Apply
    o.location = t
    o.rotation_mode = 'XYZ'
    o.rotation_euler = r
    if recording:
        o.keyframe_insert(data_path='location', frame=f)
        o.keyframe_insert(data_path='rotation_euler', frame=f)

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
        CheckApplyViconState(o, None, o.name, t2b, f)
        if o.type == 'ARMATURE':
            for b, pb in zip(o.data.bones, o.pose.bones):
                CheckApplyViconState(pb, b, o.name + '_' + b.name, t2b, f)
    
def Anim_register():
    bpy.app.handlers.frame_change_pre.append(T2BFrameHandler)

def Anim_unregister():
    if T2BFrameHandler in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(T2BFrameHandler)
