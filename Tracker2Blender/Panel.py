import bpy
from bpy.props import BoolProperty, IntProperty, FloatProperty, FloatVectorProperty, \
    CollectionProperty, PointerProperty
from .Network import NetConnect, NetDisconnect, NetIsConnected, NetStatusMsg
from .Anim import SetRecording

class T2B_OT_record(bpy.types.Operator):
    bl_idname = 't2b.record'
    bl_label = 'Record'
    
    def execute(self, context):
        NetConnect(context.scene.t2b.port)
        SetRecording(True)
        bpy.ops.screen.animation_play(reverse = False, sync = True)
        return {'FINISHED'}

class T2B_OT_preview(bpy.types.Operator):
    bl_idname = 't2b.preview'
    bl_label = 'Preview'
    
    def execute(self, context):
        NetConnect(context.scene.t2b.port)
        SetRecording(False)
        bpy.ops.screen.animation_play(reverse = False, sync = True)
        return {'FINISHED'}

class T2B_OT_stop(bpy.types.Operator):
    bl_idname = 't2b.stop'
    bl_label = 'Stop'
    
    def execute(self, context):
        NetDisconnect()
        bpy.ops.screen.animation_cancel(restore_frame = True)
        return {'FINISHED'}

class T2B_OT_addobj(bpy.types.Operator):
    bl_idname = 't2b.addobj'
    bl_label = 'Add Armature / Object'
    
    def execute(self, context):
        t2b = context.scene.t2b
        t2b.objs.add()
        return {'FINISHED'}

class T2B_OT_delobj(bpy.types.Operator):
    bl_idname = 't2b.delobj'
    bl_label = 'Delete'
    
    objidx : IntProperty()
    
    def execute(self, context):
        t2b = context.scene.t2b
        t2b.objs.remove(self.objidx)
        return {'FINISHED'}

class T2B_PT_main_panel(bpy.types.Panel):
    bl_label = 'Tracker2Blender Main Controls'
    bl_idname = 'T2B_PT_main_panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tracker'
    
    def draw(self, context):
        t2b = context.scene.t2b
        conn = NetIsConnected()
        r = self.layout.row()
        r.prop(t2b, 'port')
        r.enabled = not conn
        r = self.layout.row(align = True)
        c = r.column()
        c.operator('t2b.record', icon = 'REC')
        c.enabled = not conn
        c = r.column()
        c.operator('t2b.preview', icon = 'PLAY')
        c.enabled = not conn
        c = r.column()
        c.operator('t2b.stop', icon = 'SNAP_FACE')
        c.enabled = conn
        r = self.layout.row().column()
        r.scale_y = 0.6
        r.label(text=NetStatusMsg())
        r.label(text='(Mouse over btns to update status)')
        self.layout.row().prop(t2b, 'extend')
        self.layout.row().prop(t2b, 'origin')
        r = self.layout.row(align = True)
        r.prop(t2b, 'scale')
        r.prop(t2b, 'zrot')
        b = self.layout.box().column()
        r = b.row()
        r.label(text='Tracking targets:')
        r.operator('t2b.addobj', text = '', icon = 'ADD')
        for i, o in enumerate(t2b.objs):
            r = b.row()
            r.prop(o, 'enab', text = '')
            r.prop(o, 'obj')
            op = r.operator('t2b.delobj', text = '', icon = 'REMOVE')
            op.objidx = i

class TargetObject(bpy.types.PropertyGroup):
    enab : BoolProperty(name = 'Enabled', description = 'Record data to this object', default = True)
    obj : PointerProperty(type = bpy.types.Object, name = 'Object', description = 
        'Object to follow Tracker data. '
        + 'If an armature, bones follow Tracker objects named ObjName_BoneName. '
        + 'Otherwise, object follows Tracker object named ObjName.')

class TrackerSettings(bpy.types.PropertyGroup):
    port : IntProperty(name = 'Port', description = 'UDP port to listen on for Tracker data',
        min = 0, max = 65535, default = 12345)
    extend : BoolProperty(name = 'Extend time while recording',
        description = 'Keep pushing forward the scene end time while recording, so action continues indefinitely without looping',
        default = True)
    scale : FloatProperty(name = 'Scale', description = 'Scale factor to multiply Tracker data by',
        min = 1e-8, soft_min = 0.01, soft_max = 100.0, default = 1.0)
    origin : FloatVectorProperty(name = 'Origin', description = 'Position of Vicon origin in Blender coords',
        size = 2)
    zrot : FloatProperty(name = 'Z Rotation', description = 'Z rotation offset',
        min = 0.0, max = 360.0, default = 0.0)
    objs : CollectionProperty(type = TargetObject, name = 'Tracked Objects',
        description = 'List of armatures or general objects to track')

classes = [
    TargetObject,
    TrackerSettings,
    
    T2B_OT_record,
    T2B_OT_preview,
    T2B_OT_stop,
    T2B_OT_addobj,
    T2B_OT_delobj,
    T2B_PT_main_panel
]

def Panel_register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.t2b = bpy.props.PointerProperty(type=TrackerSettings)

def Panel_unregister():
    del bpy.types.Scene.t2b
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
