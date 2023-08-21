bl_info = {
    "name": "Run Exe Operator",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import os
import subprocess
import tempfile
from bpy.props import StringProperty
from bpy.types import Operator, Panel, AddonPreferences

#创建文件
def make_loader():
    path = "" + tempfile.gettempdir()
    path = '/'.join(path.split('\\'))
    loader = path + "/loader.py"
    return loader

#文件内容
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


# 定义一个名为RunExeOperator的操作类，继承自bpy.types.Operator
class RunExeOperator(Operator):
    # 设置操作的内部名称
    bl_idname = "object.run_exe_operator"
    # 设置操作的显示名称
    bl_label = "Run Exe Operator"

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


class RunExeOperatorPanel(Panel):
    bl_label = "Run Exe Operator"
    bl_idname = "OBJECT_PT_run_exe_operator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Run Exe"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.run_exe_operator")


class RunExeOperatorPreferences(AddonPreferences):
    bl_idname = __name__

    exe_path: StringProperty(
        name="Exe Path",
        subtype='FILE_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "exe_path")


def menu_func(self, context):
    self.layout.operator(RunExeOperator.bl_idname)


def register():
    bpy.utils.register_class(RunExeOperator)
    bpy.utils.register_class(RunExeOperatorPanel)
    bpy.utils.register_class(RunExeOperatorPreferences)


def unregister():
    bpy.utils.unregister_class(RunExeOperator)
    bpy.utils.unregister_class(RunExeOperatorPanel)
    bpy.utils.unregister_class(RunExeOperatorPreferences)


if __name__ == "__main__":
    register()