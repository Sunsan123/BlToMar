"""
[Blender and Python]
SunSan - August 2023
Email: 1778773436@qq.com
A blender tool for importing Marmoset Toolbag

--------

"""

bl_info = {
    "name": "BlToMar",  # 插件名称
    "description": "A blender tool for importing Marmoset Toolbag",  # 插件描述
    "author": "SunSan 1778773436@qq.com",  # 插件作者
    "version": (1, 0, 0),  # 插件版本
    "blender": (2, 93, 0),  # Blender版本要求
    "location": "3D View > Tools",  # 插件位置
    "warning": "",  # 警告信息，如果有的话
    "wiki_url": "",  # 插件维基页面URL
    "tracker_url": "",  # 插件跟踪页面URL
    "category": "Development"  # 插件分类
}


# 导入依赖库
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
# 定义属性
PROPS = [
]

# == FUCTION


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
#创建导出临时文件
def make_loader():
    path = "" + tempfile.gettempdir()
    path = '/'.join(path.split('\\'))
    loader = path + "/loader.py"
    return loader

#临时文件内容
def py_build_up(exportPath):
    loader = make_loader()
    exportPath = '/'.join(exportPath.split('\\'))
    with open(loader, "w+") as loader:
        loader.write("import mset\n")
        loader.write("import os\n")
        loader.write("fbx_file = " + "'" + str(exportPath) + "'\n")
        loader.write("baker = mset.BakerObject()\n")
        loader.write("baker.importModel(fbx_file)\n")
#         loader.write("""\
# baker.importModel(fbx_file)
# if os.path.exists(fbx_file):
#     # 删除指定路径的文件
#     os.remove(fbx_file)
#     print(f"文件已删除: {fbx_file}")
# else:
#     print("文件不存在，请检查文件路径。")""")


def outputFBX():

    basedir = os.path.dirname(bpy.data.filepath)

    if not basedir:
       raise Exception("！！！Blend file is not saved！！！\n！！！Blend文件未保存！！！")

    #获取文件名
    objectName = os.path.basename(bpy.data.filepath).split('.')[0]

    # 设置导出路径
    exportPath = os.path.join(basedir, objectName + "_temp" + ".fbx")
    # 导出FBX文件
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



# == OPERATORS
#自定义List属性
# 定义一个名为CustomCollectionUIList的UI列表类，继承自bpy.types.UIList
class CustomCollectionUIList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name)

#自定义路径属性
class EXEProperties(PropertyGroup):
    exe_path: StringProperty(name="八猴路径", default="", subtype='FILE_PATH')
# 显示操作
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
#调用动态检测后删除按钮
class StartModalOperator(bpy.types.Operator):
    bl_idname = "object.start_modal_operator"
    bl_label = "Start Modal Operator"

    def execute(self, context):
        # 注销操作类，从用户界面中删除按钮
        bpy.utils.unregister_class(StartModalOperator)
        # 调用模态操作
        bpy.ops.object.check_active_object_name('INVOKE_DEFAULT')
        return {'FINISHED'}
# 检测鼠标点击物体
class CheckActiveObjectName(bpy.types.Operator):
    bl_idname = "object.check_active_object_name"  # 操作的内部名称
    bl_label = "Check Active Object Name"  # 操作的显示名称

    _timer = None  # 定义一个定时器变量

    def modal(self, context, event):
        if context.mode == 'OBJECT':  # 如果当前模式为对象模式
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':  # 如果检测到鼠标左键点击
                selected_objects = bpy.context.selected_objects  # 获取选中的对象列表

                if selected_objects:  # 如果有选中的对象
                    print("Selected object name:", selected_objects[-1].name)  # 打印选中对象的名称
                    active_object = bpy.context.view_layer.objects.active  # 获取活动对象
                    if "_low" in active_object.name:  # 如果活动对象名称中包含"_low"
                        base_name = active_object.name.replace("_low", "")  # 去除"_low"后缀
                        context.scene.object_custom_name = base_name  # 设置自定义名称属性
                if not selected_objects:  # 如果没有选中的对象
                    context.scene.object_custom_name = ""  # 清空自定义名称属性
                    print("ClickNull")  # 打印空点击信息

        if event.type == 'TIMER':  # 如果事件类型为定时器
            pass

        return {'PASS_THROUGH'}  # 保持模态运行

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)  # 添加定时器
        wm.modal_handler_add(self)  # 添加模态处理器
        return {'RUNNING_MODAL'}  # 返回运行模态状态


#重命名添加后缀
class RenameObjects(bpy.types.Operator):
    bl_idname = "rename.suffix"
    bl_label = "Rename Objects"

    suffix: StringProperty()

    def execute(self, context):
        rename_suffix(self, context)

        return {'FINISHED'}
# 清除后缀操作
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

#集合组
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
#object添加进列表
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

#object移除出列表
class RemoveCollectionWithObjects(bpy.types.Operator):
    bl_idname = "object.remove_collection"
    bl_label = "Remove Collection with Objects"

    def execute(self, context):
        # 获取当前场景
        scene = context.scene
        # 获取当前选定的物体列表
        selected_objects = context.selected_objects

        # 遍历选定的物体列表
        for obj in selected_objects:
            #获取物体名字
            base_name = obj.name
            if "_low" in base_name:
                base_name = base_name.replace("_low", "")
            elif "_high" in base_name:
                base_name = base_name.replace("_high", "")

            for obj_iter in scene.objects:
                if obj_iter == base_name + "_low" or base_name + "_high":
                    # 获取相同besename物体所在的集合列表
                    obj_collections = obj_iter.users_collection
                    # 遍历物体所在的集合列表
                    for collection in obj_collections:
                        # 在删除集合之前获取父集合
                        parent_collection = None  # 初始化变量
                        for col in bpy.data.collections:
                            if collection.name in col.children:
                                parent_collection = col
                                break

                        # 将物体链接回场景集合
                        scene.collection.objects.link(obj_iter)
                        # 从当前集合中取消链接物体
                        collection.objects.unlink(obj_iter)

                        # 检查当前集合是否为空
                        if not collection.objects:
                            # 如果当前集合为空，则将其从场景中删除
                            bpy.data.collections.remove(collection)

                            # 检查父集合是否为空
                            if parent_collection and not parent_collection.objects and not parent_collection.children:
                                # 如果父集合为空，则将其从场景中删除
                                bpy.data.collections.remove(parent_collection)

        # 返回操作已成功完成的状态
        return {'FINISHED'}

# 导出操作
class ExportToMarmoset(bpy.types.Operator):
    bl_idname = "object.export_to_marmoset"
    bl_label = "Export to Marmoset Toolbag 4"


    # 定义操作的执行方法
    def execute(self, context):
        # 从上下文中获取插件的偏好设置
        addon_prefs = context.preferences.addons[__name__].preferences
        # 从插件偏好设置中获取exe文件的路径
        exe_path = addon_prefs.exe_path
        # 检查exe文件路径是否有效
        if os.path.isfile(exe_path):
            # 如果有效，则使用subprocess.Popen()启动exe文件
            fbxExportPath = outputFBX()
            py_build_up(fbxExportPath)
            loader = make_loader()
            subprocess.Popen([exe_path, loader])
        else:
            # 如果无效，则向用户报告错误信息
            self.report({'ERROR'}, f"Invalid exe path: {exe_path}")
        # 返回操作的执行结果
        return {'FINISHED'}

class RunExeOperatorPreferences(AddonPreferences):
    bl_idname = __name__

    exe_path: StringProperty(
        name="八猴路径",
        subtype='FILE_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "exe_path")

# == PANELS
# 面板
# 第一个面板 - 显示
class DisplayPanel(bpy.types.Panel):
    bl_label = "显示"
    bl_idname = "OBJECT_PT_display_panel"
    bl_category = "Bl2Mar"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 1

    def draw(self, context):
        layout = self.layout

        # 添加按钮
        row = layout.row(align=True)
        row.operator("object.show_objects", text="显示 low" ,icon="ZOOM_OUT").suffix = "low"
        row.operator("object.show_objects", text="显示 high",icon="ZOOM_OUT").suffix = "high"
        layout.operator("object.show_objects", text="显示全部物体",icon="ZOOM_IN").suffix = ""

# # 第二个面板 - 重命名
class RenamePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_rename_panel"
    bl_label = "重命名"
    bl_category = "Bl2Mar"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 2

    def draw(self, context):
        layout = self.layout

        # 添加文本框
        layout.prop(context.scene, "object_custom_name", text="自定义名称")
        #动态检测
        row = layout.row(align=True)
        row.operator("object.start_modal_operator", text="动态检测",icon="GHOST_ENABLED")

        # 添加按钮
        row = layout.row(align=True)
        row.operator("rename.suffix", text="添加 low 后缀",icon="GPBRUSH_CHISEL").suffix = "low"
        row.operator("rename.suffix", text="添加 high 后缀",icon="GPBRUSH_CHISEL").suffix = "high"

        layout.operator("object.clear_suffix", text="清除后缀",icon="GPBRUSH_ERASE_HARD")

# 第三个面板 - 分组
class GroupPanel(bpy.types.Panel):
    bl_label = "分组"
    bl_idname = "OBJECT_PT_group_panel"
    bl_category = "Bl2Mar"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # 创建一个新的行
        row = layout.row()
        # 在行中添加一个自定义集合UI列表，用于显示场景中的子集合
        row.template_list("CustomCollectionUIList", "", scene.collection, "children", scene, "collection_index", rows=3)

        # 创建一个新的列，用于放置添加和删除按钮
        col = row.column(align=True)
        col.operator("list.actions", icon='ADD', text="").action = 'ADD'
        col.operator("list.actions", icon='REMOVE', text="").action = 'REMOVE'

        # 获取当前选中的子集合
        collection = scene.collection.children[scene.collection_index]
        # 在面板中显示子集合的名称属性
        layout.prop(collection, "name")

        row = layout.row()
        row.operator("object.add_collection", text="添加", icon='COLLECTION_NEW')
        row.operator("object.remove_collection", text="移除", icon='TRASH')


# 第四个面板 - 导出
class ExportPanel(bpy.types.Panel):
    bl_label = "导出"
    bl_idname = "OBJECT_PT_export_panel"
    bl_category = "Bl2Mar"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 4

    def draw(self, context):
        layout = self.layout

        # 添加按钮
        layout.operator("object.export_to_marmoset", text="导出到 Marmoset Toolbag 4",icon="MESH_MONKEY")

#注册类
CLASSES = (
    DisplayPanel,
    RenamePanel,
    GroupPanel,
    ExportPanel,
    ShowObjects,
    RenameObjects,
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


# 注册和反注册函数

# def menu_func(self, context):
#     self.layout.operator(RunExeOperator.bl_idname)

def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)  # 将属性添加到Scene类中

    for klass in CLASSES:
        bpy.utils.register_class(klass)  # 注册每个类

    #在 Blender 场景数据中创建一个自定义字符串属性 StringProperty 是 Blender 的内置属性，用于创建和管理字符串类型的自定义属性
    bpy.types.Scene.object_custom_name = StringProperty(name="Custom Name")
    # bpy.ops.object.check_active_object_name()
    bpy.types.Scene.collection_index = bpy.props.IntProperty()



def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)  # 从Scene类中删除属性

    for klass in CLASSES:
        bpy.utils.unregister_class(klass)  # 反注册每个类

    del bpy.types.Scene.object_custom_name
    del bpy.types.Scene.collection_index



# 如果是主文件，则注册
if __name__ == "__main__":
    register()