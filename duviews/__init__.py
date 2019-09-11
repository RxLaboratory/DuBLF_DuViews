# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "DuView",
    "author" : "Nicolas 'Duduf' Dufresne",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "Pie Menu",
    "description" : "Tools to manage views",
    "warning" : "",
    "category" : "Pie Menu"
}

import bpy # pylint: disable=import-error

from . import (
    dublf,
)

class DUVIEW_Preferences( bpy.types.AddonPreferences ):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    resolution_x: bpy.props.IntProperty(
        name="New window width",
        default=1280,
    )
    resolution_y: bpy.props.IntProperty(
        name="New window height",
        default=720,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "resolution_x")
        layout.prop(self, "resolution_y")

class DUVIEW_OT_show_window ( bpy.types.Operator ):
    """Opens a new window with a specific area type"""
    bl_idname = "duview.show_window"
    bl_label = "Swap IK / FK"
    bl_options = {'REGISTER','UNDO'}

    view: bpy.props.StringProperty( default = 'VIEW_3D' )
       
    def execute( self, context ):
        preferences = context.preferences
        prefs = preferences.addons[__package__].preferences

        render = bpy.context.scene.render

        # Keep current settings
        resolution_x = render.resolution_x
        resolution_y = render.resolution_y
        resolution_percentage = render.resolution_percentage
        display_mode = render.display_mode

        # Modify scene settings
        render.resolution_x = prefs.resolution_x
        render.resolution_y = prefs.resolution_y
        render.resolution_percentage = 100
        render.display_mode = "WINDOW"

        # Call image editor window
        bpy.ops.render.view_show("INVOKE_DEFAULT")

        # Change area type
        area = bpy.context.window_manager.windows[-1].screen.areas[0]
        area.type = self.view

        # Restore scene settings
        render.resolution_x = resolution_x
        render.resolution_y = resolution_y
        render.resolution_percentage = resolution_percentage
        render.display_mode = display_mode

        return {'FINISHED'}

class DUVIEW_MT_pie_menu_show_window( bpy.types.Menu ):
    bl_idname = "DUVIEW_MT_pie_menu_show_window"
    bl_label = "Show window"
    bl_description = "Opens a specific new window."

    def draw( self, context ):
        layout = self.layout.menu_pie()
        populateShowWindowMenu(layout)

class DUVIEW_MT_menu_show_window( bpy.types.Menu ):
    bl_idname = "DUVIEW_MT_menu_show_window"
    bl_label = "New Window"
    bl_description = "Opens a specific new window."

    def draw( self, context ):
        layout = self.layout
        populateShowWindowMenu(layout)

def populateShowWindowMenu(layout):
    layout.operator("duview.show_window", text = "3D View", icon='VIEW3D').view = 'VIEW_3D'
    layout.operator("duview.show_window", text = "Image Editor", icon = 'IMAGE').view = 'IMAGE_EDITOR'
    layout.operator("duview.show_window", text = "Shader Editor", icon = 'SHADING_RENDERED').view = 'NODE_EDITOR'
    layout.operator("duview.show_window", text = "Graph Editor", icon = 'GRAPH').view = 'GRAPH_EDITOR'
    layout.operator("duview.show_window", text = "Text Editor", icon = 'TEXT').view = 'TEXT_EDITOR'
    layout.operator("duview.show_window", text = "Preferences", icon = 'PREFERENCES').view = 'PREFERENCES'

def menu_func(self, context):
    self.layout.separator()
    populateShowWindowMenu(self.layout)
    

classes = (
    DUVIEW_Preferences,
    DUVIEW_OT_show_window,
    DUVIEW_MT_menu_show_window,
    DUVIEW_MT_pie_menu_show_window,
)

addon_keymaps = []

def register():
    # register
    for cls in classes:
        bpy.utils.register_class(cls)

    # menus
    bpy.types.TOPBAR_MT_window.append(menu_func)

    # keymaps
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'W', 'PRESS', ctrl=True)
        kmi.properties.name = 'DUVIEW_MT_pie_menu_show_window'
        addon_keymaps.append((km, kmi))

def unregister():
    # unregister
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # menu
    bpy.types.TOPBAR_MT_window.remove(menu_func)

    # keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
