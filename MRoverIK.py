#Custom UI info and template file: https://blender.stackexchange.com/questions/57306/how-to-create-a-custom-ui

bl_info = {
    "name": "MRover Inverse Kinematics",
    "description": "The Michigan Mars Rover Team's inverse kinematics tool for controlling a robotic arm",
    "author": "Michael Wolf",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "3D View > MRover",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "", #make this a link to the  Github page for this project (once it has one)
    "tracker_url": "",
    "category": "Development"
}

import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       )
from math import degrees

import time
import datetime

# ------------------------------------------------------------------------
#    store properties in the active scene
# ------------------------------------------------------------------------

class MySettings(PropertyGroup):

    bc_length = FloatProperty(
        name = "BC Length",
        description = "Length of the First Segment",
        default = 1,
        min = 0.01,
        max = 30.0
        )

    cd_length = FloatProperty(
        name = "CD Length",
        description = "Length of the Second Segment",
        default = 1,
        min = 0.01,
        max = 30.0
        )

    de_length = FloatProperty(
        name = "DE Length",
        description = "Length of the Third Segment",
        default = 1,
        min = 0.01,
        max = 30.0
        )

    end_effector_length = FloatProperty(
        name = "End Effector Length",
        description = "Length of the End Effector",
        default = 1,
        min = 0.01,
        max = 30.0
        )

# ------------------------------------------------------------------------
#    operators
# ------------------------------------------------------------------------

class OutputAnglesOperator(bpy.types.Operator):
    bl_idname = "wm.output_angles"
    bl_label = "Output Angles"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        #Get angles to send
        arm = context.scene.objects['Arm']
        end_effector = context.scene.objects['End Effector']
        
        bc_bone = arm.pose.bones["BC"]
        cd_bone = arm.pose.bones["CD"]
        de_bone = arm.pose.bones["DE"]
        end_bone = end_effector.pose.bones["End Effector"]
        
        vertical = bc_bone.head - bc_bone.head #A zero vector that is the same type as the bone vectors
        horizontal = bc_bone.head - bc_bone.head
        vertical.z = 1
        horizontal.x = 1
        
        bc = bc_bone.tail - bc_bone.head
        cd = cd_bone.tail - cd_bone.head
        de = de_bone.tail - de_bone.head
        end = end_bone.tail - end_bone.head
        total = end_bone.tail - bc_bone.head
        
        print("vertical: " + str(vertical))
        print("horizontal: " + str(horizontal))
        print("bc: " + str(bc))
        print("cd: " + str(cd))
        print("de: " + str(de))
        print("end: " + str(end))
        print("total: " + str(total))
        
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        
        # print the values to the console
        print()
        print(st)
        print()
        
        print("A: " + str(degrees(horizontal.angle(total))))
        print("B: " + str(degrees(vertical.angle(bc))))
        print("C: " + str(degrees(bc.angle(cd))))
        print("D: " + str(degrees(cd.angle(de))))
        print("E: " + str(degrees(de.angle(end))))        
        
        #TODO output all the joint angles

        return {'FINISHED'}
    
class UpdateLengthsOperator(bpy.types.Operator):
    bl_idname = "wm.update_lengths"
    bl_label = "Update Lengths"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        
        #Set arm lengths based on the values in the menu
        arm = context.scene.objects['Arm']
        end = context.scene.objects['End Effector']
        
        end.data.bones[0].length = end_effector_length.value
        arm.data.bones['DE'].length = de_length
        arm.data.bones['CD'].length = cd_length
        arm.data.bones['BC'].length = bc_length

        return {'FINISHED'}

# ------------------------------------------------------------------------
#    menus
# ------------------------------------------------------------------------

    #blank because we don't have any menus in our tool

# ------------------------------------------------------------------------
#    my tool in posemode
# ------------------------------------------------------------------------

class OBJECT_PT_my_panel(Panel):
    bl_idname = "OBJECT_PT_my_panel"
    bl_label = "MRover Arm IK"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "TOOLS"    
    bl_category = "MRover"
    bl_context = "posemode"   

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.prop(mytool, "bc_length")
        layout.prop(mytool, "cd_length")
        layout.prop(mytool, "de_length")
        layout.prop(mytool, "end_effector_length")
        layout.operator("wm.update_lengths")
        layout.operator("wm.output_angles")


# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.my_tool = PointerProperty(type=MySettings)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()