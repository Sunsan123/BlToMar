bl_info = {
    "name": "Run Exe Operator",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import os
import subprocess
from bpy.props import StringProperty
from bpy.types import Operator, Panel, AddonPreferences


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
            subprocess.Popen(exe_path)
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