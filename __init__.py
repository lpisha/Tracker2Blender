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

def register():
    Panel_register()

def unregister():
    Panel_unregister()

if __name__ == '__main__':
    register()
