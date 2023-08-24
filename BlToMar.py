"""
[Blender and Python]
SunSan - August 2023
Email: 1778773436@qq.com
A blender tool for importing Marmoset Toolbag

--------

"""
bl_info = {
    "name": "BlToMar",
    "description": "A blender tool for importing Marmoset Toolbag",
    "author": "SunSan 1778773436@qq.com",
    "version": (1, 0, 0),
    "blender": (2, 93, 0),
    "location": "3D View > Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}
import bpy
import os
import subprocess
import tempfile

from bpy.props import (StringProperty,
                       CollectionProperty,
                       IntProperty,
                       )

from bpy.types import (Panel,
                       AddonPreferences,
                       Operator,
                       PropertyGroup,
                       )
PROPS = [
]
def rename_suffix(self, context):

    for obj in bpy.context.selected_objects:
        base_name = context.scene.object_custom_name
        if base_name == "":
            name_split = obj.name.split("_")
            if "low" in name_split:
                obj.name = obj.name.replace("_low", "")
            elif "high" in name_split:
                obj.name = obj.name.replace("_high", "")
            base_name = obj.name.split("_" + self.suffix)[0]
        obj.name = base_name + "_" + self.suffix
    return {'FINISHED'}
def active_object_changed(scene, depsgraph):
    active_object_name = bpy.context.view_layer.objects.active.name

    if "_low" in active_object_name:
        base_name = active_object_name.replace("_low", "")
        scene.object_custom_name = base_name
        print("base_name")
    else:
        scene.object_custom_name = ""
def make_loader():
    path = "" + tempfile.gettempdir()
    path = '/'.join(path.split('\\'))
    loader = path + "/loader.py"
    return loader
def py_build_up(exportPath):
    loader = make_loader()
    exportPath = '/'.join(exportPath.split('\\'))
    with open(loader, "w+") as loader:
        loader.write("import mset\n")
        loader.write("import os\n")
        loader.write("fbx_file = " + "'" + str(exportPath) + "'\n")
        loader.write("baker = mset.BakerObject()\n")
        loader.write("baker.importModel(fbx_file)\n")
def outputFBX():
    basedir = os.path.dirname(bpy.data.filepath)
    if not basedir:
       raise Exception("！！！Blend file is not saved！！！\n！！！Blend文件未保存！！！")
    objectName = os.path.basename(bpy.data.filepath).split('.')[0]
    exportPath = os.path.join(basedir, objectName + "_temp" + ".fbx")
    bpy.ops.export_scene.fbx(filepath=(exportPath),
                             check_existing=True,
                             filter_glob="*.fbx",
                             use_selection=True,
                             use_active_collection=True,
                             global_scale=1,
                             apply_unit_scale=True,
                             apply_scale_options='FBX_SCALE_NONE',
                             bake_space_transform=True,
                             object_types={'MESH'},
                             use_mesh_modifiers=True,
                             use_mesh_modifiers_render=True,
                             mesh_smooth_type='OFF',
                             use_mesh_edges=False,
                             use_tspace=False,
                             use_custom_props=False,
                             add_leaf_bones=False,
                             primary_bone_axis='Y',
                             secondary_bone_axis='X',
                             use_armature_deform_only=False,
                             armature_nodetype='NULL',
                             bake_anim=False,
                             bake_anim_use_all_bones=False,
                             bake_anim_use_nla_strips=False,
                             bake_anim_use_all_actions=False,
                             bake_anim_force_startend_keying=False,
                             bake_anim_step=1,
                             bake_anim_simplify_factor=1,
                             path_mode='AUTO',
                             embed_textures=False,
                             batch_mode='OFF',
                             use_batch_own_dir=True,
                             use_metadata=True,
                             axis_forward='-Y',
                             axis_up='Z',
                             )
    return exportPath
class CustomCollectionUIList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name)
class EXEProperties(PropertyGroup):
    exe_path: StringProperty(name="八猴路径", default="", subtype='FILE_PATH')
class ShowObjects(bpy.types.Operator):
    bl_idname = "object.show_objects"
    bl_label = "Show Objects"
    suffix: StringProperty()
    def execute(self, context):
        for obj in bpy.context.view_layer.objects:
            obj.hide_viewport = True
            if self.suffix == "":
                obj.hide_viewport = False
            elif self.suffix == "low":
                if obj.name.endswith("low"):
                    obj.hide_viewport = False
            elif self.suffix == "high":
                if obj.name.endswith("high"):
                    obj.hide_viewport = False
            else:
                obj.hide_viewport = False
        return {'FINISHED'}
class ImportOperator(bpy.types.Operator):
    bl_idname = 'root.import'
    bl_label = 'Root Convert'
    def execute(self, context):
        importFBX()
        return {'FINISHED'}
class StartModalOperator(bpy.types.Operator):
    bl_idname = "object.start_modal_operator"
    bl_label = "Start Modal Operator"
    def execute(self, context):
        bpy.utils.unregister_class(StartModalOperator)
        bpy.ops.object.check_active_object_name('INVOKE_DEFAULT')
        return {'FINISHED'}
class CheckActiveObjectName(bpy.types.Operator):
    bl_idname = "object.check_active_object_name"
    bl_label = "Check Active Object Name"
    _timer = None
    def modal(self, context, event):
        if context.mode == 'OBJECT':
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                selected_objects = bpy.context.selected_objects

                if selected_objects:
                    print("Selected object name:", selected_objects[-1].name)
                    active_object = bpy.context.view_layer.objects.active
                    if "_low" in active_object.name:
                        base_name = active_object.name.replace("_low", "")
                        context.scene.object_custom_name = base_name
                if not selected_objects:
                    context.scene.object_custom_name = ""
                    print("ClickNull")
        if event.type == 'TIMER':
            pass
        return {'PASS_THROUGH'}
    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
class RenameObjectSuffix(bpy.types.Operator):
    bl_idname = "rename.suffix"
    bl_label = "Rename Objects"
    suffix: StringProperty()
    def execute(self, context):
        rename_suffix(self, context)
        return {'FINISHED'}
class ClearSuffix(bpy.types.Operator):
    bl_idname = "object.clear_suffix"
    bl_label = "Clear Suffix"
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if "_low" in obj.name:
                obj.name = obj.name.replace("_low", "")
            elif "_high" in obj.name:
                obj.name = obj.name.replace("_high", "")
        return {'FINISHED'}
class RenameObjectPrefix(bpy.types.Operator):
    bl_idname = "rename.prefix"
    bl_label = "Rename Objects"
    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        prefix = bpy.context.scene.rename_prefix
        for i, obj in enumerate(selected_objects, start=1):
            base_name = obj.name
            if "_low" in base_name:
                base_name = base_name.replace("_low", "")
                suffix = "_low"
            elif "_high" in base_name:
                base_name = base_name.replace("_high", "")
                suffix = "_high"
            else:
                suffix = ""
            new_name = f"{prefix}_{i:03d}{suffix}"
            obj.name = new_name
        return {'FINISHED'}
class list_actions(bpy.types.Operator):
    bl_idname = "list.actions"
    bl_label = "List Actions"
    action: bpy.props.EnumProperty(
        items=(('REMOVE', "Remove", ""), ('ADD', "Add", ""),)
    )
    def invoke(self, context, event):
        scene = context.scene
        collection_index = scene.collection_index
        if self.action == 'REMOVE':
            if scene.collection.children:
                collection = scene.collection.children[collection_index]
                bpy.data.collections.remove(collection)
                scene.collection_index = min(collection_index, len(scene.collection.children) - 1)
        elif self.action == 'ADD':
            new_collection = bpy.data.collections.new("New Collection")
            scene.collection.children.link(new_collection)
            scene.collection_index = len(scene.collection.children) - 1
        return {'FINISHED'}
class AddCollectionWithObjects(bpy.types.Operator):
    bl_idname = "object.add_collection"
    bl_label = "Add Collection with Objects"
    def execute(self, context):
        scene = context.scene
        selected_objects = context.selected_objects
        collection_index = scene.collection_index
        if scene.collection.children and collection_index < len(scene.collection.children):
            parent_collection = scene.collection.children[collection_index]
            for obj in selected_objects:
                base_name = obj.name
                if "_low" in base_name:
                    base_name = base_name.replace("_low", "")
                elif "_high" in base_name:
                    base_name = base_name.replace("_high", "")
                new_collection = bpy.data.collections.new(base_name)
                parent_collection.children.link(new_collection)
                low_collection = bpy.data.collections.new(base_name + "_Low")
                high_collection = bpy.data.collections.new(base_name + "_High")
                new_collection.children.link(low_collection)
                new_collection.children.link(high_collection)
                for obj_iter in scene.objects:
                    if obj_iter.name == base_name + "_low":
                        for col in obj_iter.users_collection:
                            col.objects.unlink(obj_iter)
                        low_collection.objects.link(obj_iter)
                    elif obj_iter.name == base_name + "_high":
                        for col in obj_iter.users_collection:
                            col.objects.unlink(obj_iter)
                        high_collection.objects.link(obj_iter)
        return {'FINISHED'}
class RemoveCollectionWithObjects(bpy.types.Operator):
    bl_idname = "object.remove_collection"
    bl_label = "Remove Collection with Objects"
    def execute(self, context):
        scene = context.scene
        selected_objects = context.selected_objects
        for obj in selected_objects:
            base_name = obj.name
            if "_low" in base_name:
                base_name = base_name.replace("_low", "")
            elif "_high" in base_name:
                base_name = base_name.replace("_high", "")
            for obj_iter in scene.objects:
                if (obj_iter.name == base_name + "_low") or (obj_iter.name == base_name + "_high"):
                    obj_collections = obj_iter.users_collection
                    for collection in obj_collections:
                        parent_collection = None
                        for col in bpy.data.collections:
                            if collection.name in col.children:
                                parent_collection = col
                                break
                        scene.collection.objects.link(obj_iter)
                        collection.objects.unlink(obj_iter)
                        if not collection.objects:
                            bpy.data.collections.remove(collection)
                            if parent_collection and not parent_collection.objects and not parent_collection.children:
                                bpy.data.collections.remove(parent_collection)
        return {'FINISHED'}
class ExportToMarmoset(bpy.types.Operator):
    bl_idname = "object.export_to_marmoset"
    bl_label = "Export to Marmoset Toolbag 4"
    def execute(self, context):
        addon_prefs = context.preferences.addons[__name__].preferences
        exe_path = addon_prefs.exe_path
        if os.path.isfile(exe_path):
            fbxExportPath = outputFBX()
            py_build_up(fbxExportPath)
            loader = make_loader()
            subprocess.Popen([exe_path, loader])
        else:
            self.report({'ERROR'}, f"Invalid exe path: {exe_path}")
        return {'FINISHED'}
class RunExeOperatorPreferences(AddonPreferences):
    bl_idname = __name__
    language = bpy.context.preferences.view.language
    if language == "zh_CN":
        name_text = "八猴路径"
    else:
        name_text = "Marmoset Path"
    exe_path: StringProperty(
        name= name_text,
        subtype='FILE_PATH',
    )
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "exe_path")
class DisplayPanel(bpy.types.Panel):
    bl_label = "Show"
    bl_idname = "OBJECT_PT_display_panel"
    bl_category = "Bl2Mar"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 1
    def draw(self, context):
        layout = self.layout
        language = bpy.context.preferences.view.language
        if language == "zh_CN":
            low_text = "显示 low"
            high_text = "显示 high"
            all_text = "显示全部物体"
        else:
            low_text = "Show low"
            high_text = "Show high"
            all_text = "Show all objects"
        row = layout.row(align=True)
        row.operator("object.show_objects", text=low_text, icon="ZOOM_OUT").suffix = "low"
        row.operator("object.show_objects", text=high_text, icon="ZOOM_OUT").suffix = "high"
        layout.operator("object.show_objects", text=all_text, icon="ZOOM_IN").suffix = ""
class RenamePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_rename_panel"
    bl_label = "Rename"
    bl_category = "Bl2Mar"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 2
    def draw(self, context):
        layout = self.layout
        language = bpy.context.preferences.view.language
        if language == "zh_CN":
            custom_name_text = "自定义名称"
            dynamic_detect_text = "动态检测"
            add_low_suffix_text = "添加 low 后缀"
            add_high_suffix_text = "添加 high 后缀"
            clear_suffix_text = "清除后缀"
            batch_rename_text = "批量命名"
        else:
            custom_name_text = "Custom Name"
            dynamic_detect_text = "Dynamic Detect"
            add_low_suffix_text = "Add low suffix"
            add_high_suffix_text = "Add high suffix"
            clear_suffix_text = "Clear suffix"
            batch_rename_text = "Batch Rename"
        layout.prop(context.scene, "object_custom_name", text=custom_name_text)
        row = layout.row(align=True)
        row.operator("object.start_modal_operator", text=dynamic_detect_text, icon="GHOST_ENABLED")
        row = layout.row(align=True)
        row.operator("rename.suffix", text=add_low_suffix_text, icon="GPBRUSH_CHISEL").suffix = "low"
        row.operator("rename.suffix", text=add_high_suffix_text, icon="GPBRUSH_CHISEL").suffix = "high"
        layout.operator("object.clear_suffix", text=clear_suffix_text, icon="GPBRUSH_ERASE_HARD")
        row = layout.row(align=True)
        row.prop(context.scene, "rename_prefix",text="")
        row.operator("rename.prefix", text=batch_rename_text, icon="GPBRUSH_FILL")
class GroupPanel(bpy.types.Panel):
    bl_label = "Bakery group"
    bl_idname = "OBJECT_PT_group_panel"
    bl_category = "Bl2Mar"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 3
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        language = bpy.context.preferences.view.language
        if language == "zh_CN":
            add_text = "添加"
            remove_text = "移除"
        else:
            add_text = "Add"
            remove_text = "Remove"
        row = layout.row()
        row.template_list("CustomCollectionUIList", "", scene.collection, "children", scene, "collection_index", rows=3)
        col = row.column(align=True)
        col.operator("list.actions", icon='ADD',text="").action = 'ADD'
        col.operator("list.actions", icon='REMOVE',text="").action = 'REMOVE'
        collection = scene.collection.children[scene.collection_index]
        layout.prop(collection, "name")
        row = layout.row()
        row.operator("object.add_collection", text=add_text, icon='COLLECTION_NEW')
        row.operator("object.remove_collection", text=remove_text, icon='TRASH')
class ExportPanel(bpy.types.Panel):
    bl_label = "Export"
    bl_idname = "OBJECT_PT_export_panel"
    bl_category = "Bl2Mar"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 4
    def draw(self, context):
        layout = self.layout
        language = bpy.context.preferences.view.language
        if language == "zh_CN":
            export_text = "导出到 Marmoset Toolbag 4"
        else:
            export_text = "Export to Marmoset Toolbag 4"
        layout.operator("object.export_to_marmoset", text=export_text, icon="MESH_MONKEY")
CLASSES = (
    DisplayPanel,
    RenamePanel,
    GroupPanel,
    ExportPanel,
    ShowObjects,
    RenameObjectSuffix,
    RenameObjectPrefix,
    ClearSuffix,
    StartModalOperator,
    CheckActiveObjectName,
    AddCollectionWithObjects,
    RemoveCollectionWithObjects,
    ExportToMarmoset,
    RunExeOperatorPreferences,
    CustomCollectionUIList,
    list_actions,
)
def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)
    for klass in CLASSES:
        bpy.utils.register_class(klass)
    bpy.types.Scene.object_custom_name = StringProperty(name="Custom Name")
    bpy.types.Scene.rename_prefix = bpy.props.StringProperty(name="Prefix", default="NewName")
    bpy.types.Scene.collection_index = bpy.props.IntProperty()
def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)
    for klass in CLASSES:
        bpy.utils.unregister_class(klass)
    del bpy.types.Scene.object_custom_name
    del bpy.types.Scene.rename_prefix
    del bpy.types.Scene.collection_index
if __name__ == "__main__":
    register()