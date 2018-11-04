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
import socket
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
#    - every button requires an operator
#    - an operator contains an execute function that runs on click
# ------------------------------------------------------------------------

# Functionality for the "Output Angles" Button
# Prints the angles of the rig to the System Console
sock = None

class OutputAnglesOperator(bpy.types.Operator):
    global sock
    bl_idname = "wm.output_angles"
    bl_label = "Output Angles"

    def execute(self, context):
        global sock

        #Get references to the armature objects, which contain bones
        arm = context.scene.objects['Arm']
        end_effector = context.scene.objects['End Effector']
        
        #Get references to each bone
        bc_bone = arm.pose.bones["BC"]
        cd_bone = arm.pose.bones["CD"]
        de_bone = arm.pose.bones["DE"]
        end_bone = end_effector.pose.bones["End Effector"]
        
        vertical = bc_bone.head - bc_bone.head #Create a zero vector (probably a better way)
        horizontal = bc_bone.head - bc_bone.head #Create a zero vector (probably a better way
        vertical.z = 1 #Used to determine angle of joint B
        horizontal.x = 1 #Used to determine the angle of joint A
        
        #Calculate all angles
        bc = bc_bone.tail - bc_bone.head
        cd = cd_bone.tail - cd_bone.head
        de = de_bone.tail - de_bone.head
        end = end_bone.tail - end_bone.head

        total_horiz = end_bone.tail - bc_bone.head #Vector from the beginning to end of the arm
        total_horiz.z = 0
        
        # Create a timestamp to print
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


        if sock == None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Connecting...")
            sock.connect(('127.0.0.1', 8019))
            print("Connected!")

        try:
            data = {
                'A': degrees(horizontal.angle(total_horiz)),
                'B': degrees(vertical.angle(bc)),
                'C': degrees(bc.angle(cd)),
                'D': degrees(cd.angle(de)),
                'E': degrees(de.angle(end))
            }
            sock.send(str(data).encode())
            print("Sent!")
        except socket.error as exc:
            print(exc)
            sock = None
        
        # print the values to the console
        print()
        print(st)
        print()
        
        print("A: " + str(degrees(horizontal.angle(total_horiz))))
        print("B: " + str(degrees(vertical.angle(bc))))
        print("C: " + str(degrees(bc.angle(cd))))
        print("D: " + str(degrees(cd.angle(de))))
        print("E: " + str(degrees(de.angle(end))))        
        
        return {'FINISHED'}

# TODO Operator for changing lengths of arm bones
class UpdateLengthsOperator(bpy.types.Operator):
    bl_idname = "wm.update_lengths"
    bl_label = "Update Lengths"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        
        #Set arm lengths based on the values in the menu
        arm = context.scene.objects['Arm']
        end = context.scene.objects['End Effector']
        
        """
        end.data.bones[0].length = 
        arm.data.bones['DE'].length = 
        arm.data.bones['CD'].length = 
        arm.data.bones['BC'].length =

        """ 

        return {'FINISHED'}

# ------------------------------------------------------------------------
#    menus
# ------------------------------------------------------------------------

    # blank because we don't have any menus in our tool

# ------------------------------------------------------------------------
#    Panel in Pose Mode
# ------------------------------------------------------------------------

class OBJECT_PT_my_panel(Panel):

    # Configuration for our tool
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

        # Add the properties and buttons to our layout
        layout.prop(mytool, "bc_length")
        layout.prop(mytool, "cd_length")
        layout.prop(mytool, "de_length")
        layout.prop(mytool, "end_effector_length")
        layout.operator("wm.update_lengths")
        layout.operator("wm.output_angles")


# ------------------------------------------------------------------------
# register and unregister
# - Necessary for our tool to be an "add-on"
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.my_tool = PointerProperty(type=MySettings)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()