import bpy
from bpy.props import IntProperty, FloatProperty, FloatVectorProperty, CollectionProperty, PointerProperty
from .Network import NetConnect, NetIsConnected, NetStatusMsg

class T2B_OT_start(bpy.types.Operator):
    bl_idname = 't2b.start'
    bl_label = 'Start'
    
    def execute(self, context):
        NetConnect(context.scene.t2b.port)
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
        r = self.layout.row()
        conn = NetIsConnected()
        r.prop(t2b, 'port', enabled = not conn)
        r.operator('t2b.start', text = 'Stop' if conn else 'Start',
            icon = 'SNAP_FACE' if conn else 'PLAY')
        r = self.layout.row().column()
        r.scale_y = 0.6
        r.label(text=NetStatusMsg())
        r.label(text='(Mouse over to update status)')
        self.layout.row().prop(t2b, 'scale')
        self.layout.row().prop(t2b, 'origin')
        b = self.layout.box().column()
        r = b.row()
        r.label(text='Tracking targets:')
        r.operator('t2b.addobj', text = '', icon = 'ADD')
        for i, o in enumerate(t2b.objs):
            r = b.row()
            r.prop(o, 'obj')
            op = r.operator('t2b.delobj', text = '', icon = 'REMOVE')
            op.objidx = i

class TargetObject(bpy.types.PropertyGroup):
    obj : PointerProperty(type = bpy.types.Object, name = 'Object', description = 
        'Object to follow Tracker data. '
        + 'If an armature, bones follow Tracker objects named ObjName_BoneName. '
        + 'Otherwise, object follows Tracker object named ObjName.')

class TrackerSettings(bpy.types.PropertyGroup):
    port : IntProperty(name = 'Port', description = 'UDP port to listen on for Tracker data',
        min = 0, max = 65535, default = 12345)
    scale : FloatProperty(name = 'Scale', description = 'Scale factor to multiply Tracker data by',
        min = 1e-8, soft_min = 0.01, soft_max = 100.0, default = 1.0)
    origin : FloatVectorProperty(name = 'Origin', description = 'Position of Vicon origin in Blender coords')
    objs : CollectionProperty(type = TargetObject, name = 'Tracked Objects',
        description = 'List of armatures or general objects to track')

classes = [
    TargetObject,
    TrackerSettings,
    
    T2B_OT_start,
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
