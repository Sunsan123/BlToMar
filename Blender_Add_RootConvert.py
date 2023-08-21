"""
[Blender and Python] Add the root skeleton to a set of specific actions and import & export 
SunSan - April 2023
Email: 1778773436@qq.com
A basic Blender pulgin that lets you add the root skeleton to a set of specific actions and import & export
This code can help you build simple plugin templates in Blender using the Python API.
Thanks Mina Pêcheux and his article "https://medium.com/geekculture/creating-a-custom-panel-with-blenders-python-api-b9602d890663"
--------
MIT License
Copyright (c) 2023 SunSan
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

bl_info = {
    "name": "Add_RootConvert",  # 插件名称
    "description": "A plugin to help my friends process a batch of animation",  # 插件描述
    "author": "SunSan 1778773436@qq.com",  # 插件作者
    "version": (1, 0, 2),  # 插件版本
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


from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )
# 定义属性
PROPS = [
    ('sourcePath', bpy.props.StringProperty(name='文件导入位置', default='',subtype='FILE_PATH')),
    ('exportPath', bpy.props.StringProperty(name='文件输出位置', default='',subtype='DIR_PATH')),

]

# == FUCTION

# 将原点设置为零
def orignToZero():
    bpy.ops.object.mode_set(mode='OBJECT')# 进入对象模式
    # 将光标设置为世界中心的代码
    #-------------Let the cursor to worldCenter code run------------------#
    #If don't go to VIEW_3D, the coordinates back to center won't work!
    bpy.context.area.type = 'VIEW_3D'
    bpy.ops.view3d.snap_cursor_to_center()
    bpy.context.area.type = 'TEXT_EDITOR'# 返回文本编辑器
    #--------------#--------------------#
    bpy.ops.object.select_all(action='SELECT') # 选择所有对象
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')# 将原点设置为光标位置

# 导入FBX文件
def importFBX():
    
    bpy.ops.import_scene.fbx(filepath = bpy.context.scene.sourcePath)

# 骨骼转换
def boneConvert():

    bpy.context.scene.frame_current = 0 # 首先让我们设置动画帧为0
    
    #-----------------#
    #orignToZero()
    #The origin to the center of the world is not available, because the origin has inserted frames, so after the origin is converted to the center of the world, the position of each frame of the skeleton must be changed to the correct position of each frame of the origin
    
    bpy.ops.object.mode_set(mode='EDIT')# 进入编辑模式
    
    ob = bpy.context.object
    if ob.type == 'ARMATURE':
        
        armature = ob.data
        bones = armature.edit_bones
        
        boneList = []
        for bone in armature.bones:
            boneList.append(bone.name)# 获取骨架的所有骨头以检查根
            
        for i in range(len(boneList)):
            #It shouldn't work here, because there's a problem
            #If there are no bones["root"] in the scenario, the system will force an error,so it must be error
            try:
                if bones[boneList[i]] == bones["root"]:
                    raise Exception("You Have Had 'root' Bone!!!!!")
            except:
                pass
            i +=1
        # 创建一个骨头
        bpy.ops.armature.bone_primitive_add(name = 'root')
        # 缩放骨头
        bpy.ops.transform.translate(value=(-0, -0, -0.869407), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)#scale the bone
        # 取消选择所有骨头
        bpy.ops.armature.select_all(action='DESELECT') # dis select
        # 准备选择我们想要的骨头
        boneName = ["Bip001 Pelvis","Bip001 Prop1","Bip001 Prop2"] #preparation for selecting the we want bone
        # 选择骨头
        for i in range(len(boneName)):
            bones[boneName[i]].select = True #select bones
            i += 1
        # 选择活动骨头"root"
        armature.edit_bones.active = bones["root"]
        # 设置父级
        bpy.ops.armature.parent_set(type='OFFSET') #set parent

    # 重命名骨架
    for armature in bpy.data.armatures:
        armature.name = filePathToName(bpy.context.scene.sourcePath)
    
    # 删除root.001...009，以防止生成多个根
    bpy.ops.armature.select_all(action='DESELECT')
    for i in range(9):
        try:
            bones["root.00"+str(i)].select = True
            bpy.ops.armature.delete()
        except:
            pass
        i += 1

    # 切换回对象模式
    bpy.ops.object.mode_set(mode='OBJECT')

# 导出FBX文件
def outputFBX():
    #These are .blend is opening the path to the project file
    #-----------
#    basedir = os.path.dirname(bpy.data.filepath)
#    
#    if not basedir:
#        raise Exception("Blend file is not saved")
#
#    objectName = filePathToName(bpy.context.scene.sourcePath) # the name of the import
#    name = bpy.path.clean_name(objectName) + "_rootConvert"
#    fn = os.path.join(basedir,name)
    #----------
    
#   These are attached path
    # 获取导入文件的名称
    objectName = filePathToName(bpy.context.scene.sourcePath)
    # 设置导出路径
    exportPath = bpy.context.scene.exportPath + objectName + "_rootConvert"

    # 导出FBX文件
    bpy.ops.export_scene.fbx(filepath=exportPath + ".fbx", use_visible=True, object_types={'ARMATURE', 'MESH'},
                             bake_anim_use_all_bones=True)


# 将文件路径转换为名称
def filePathToName(file_path):
    path_contents = file_path.split('.')
    # 获取不带扩展名的文件名
    file_name = path_contents[0].split('\\')[-1]
    return file_name


# 在操作完成后删除对象
def lastDelete():
    # 删除场景中的所有对象
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)

    # 删除不可见的骨架
    for armature in bpy.data.armatures:
        bpy.data.armatures.remove(armature)
    # 删除不可见的动作
    for action in bpy.data.actions:
        bpy.data.actions.remove(action)

    # 删除不可见的材质
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    # 删除不可见的贴图
    for texture in bpy.data.textures:
        bpy.data.textures.remove(texture)

# == OPERATORS
# 导入操作
class ImportOperator(bpy.types.Operator):
    
    bl_idname = 'root.import'
    bl_label = 'Root Convert'
    
    def execute(self, context):
        importFBX()
        
        return {'FINISHED'}

# 根转换操作
class RootConvertOperator(bpy.types.Operator):
    
    bl_idname = 'root.convert'
    bl_label = 'Root Convert'
    
    def execute(self, context):
        boneConvert()
        outputFBX()
        lastDelete()
        
        return {'FINISHED'}
      
    
# == PANELS
# 面板
class RootConvertPanel(bpy.types.Panel):
    
    bl_idname = 'VIEW3D_add_rootBone'
    bl_label = 'Add_RootConvert'
    bl_category = "RootConvert"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
        col = self.layout.column()
        for (prop_name, _) in PROPS:
            row = col.row()
            row.prop(context.scene, prop_name)
            
        col.label(text= "输出路径请勿带有中文、空格、'.'") 
        col.label(text= "我也想进米哈游.jpeg")   
        col.operator('root.import', text='导入') 
        col.operator('root.convert', text='点我转换')
        
#注册类
CLASSES = (
    ImportOperator,
    RootConvertOperator,
    RootConvertPanel,
)


# 注册和反注册函数
def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)  # 将属性添加到Scene类中

    for klass in CLASSES:
        bpy.utils.register_class(klass)  # 注册每个类


def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)  # 从Scene类中删除属性

    for klass in CLASSES:
        bpy.utils.unregister_class(klass)  # 反注册每个类


# 如果是主文件，则注册
if __name__ == "__main__":
    register()