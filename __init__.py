bl_info = {
    'name': 'Tracker2Blender',
    'author': 'Louis Pisha',
    'version': (0, 1),
    'blender': (2, 80, 0),
    'description': 'Vicon Tracker UDP stream to Blender animation',
    'warning': '',
    'doc_url': 'https://github.com/lpisha/Tracker2Blender',
    'category': 'Animation'
} 

import bpy
from .Tracker2Blender.Panel import Panel_register, Panel_unregister
from .Tracker2Blender.Network import Network_register, Network_unregister
from .Tracker2Blender.Anim import Anim_register, Anim_unregister

def register():
    Panel_register()
    Network_register()
    Anim_register()

def unregister():
    Anim_unregister()
    Network_unregister()
    Panel_unregister()

if __name__ == '__main__':
    register()
