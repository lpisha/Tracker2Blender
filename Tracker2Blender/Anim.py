import bpy
import math
from mathutils import Vector, Quaternion, Euler
from .Network import ReceiveUpdate, vicon_state
from bpy.app.handlers import persistent

recording = False

def ApplyViconState(target, t2b, vo):
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

@persistent
def T2BFrameHandler(scene):
    ReceiveUpdate()
    t2b = scene.t2b
    for to in t2b.objs:
        if not to.enab:
            continue
        o = to.obj
        vo = vicon_state.get(o.name, None)
        if vo is not None:
            ApplyViconState(o, t2b, vo)
        else:
            print('No Vicon state for tracked object ' + o.name)
        if o.type == 'ARMATURE':
            for b in o.pose.bones:
                vo = vicon_state.get(o.name + '_' + b.name, None)
                if vo is not None:
                    ApplyViconState(b, t2b, vo)
    
def Anim_register():
    bpy.app.handlers.frame_change_pre.append(T2BFrameHandler)

def Anim_unregister():
    if T2BFrameHandler in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(T2BFrameHandler)
