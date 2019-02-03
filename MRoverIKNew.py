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

import time
import datetime
import socket
import asyncio, threading
import json
import math
import mathutils
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
joint_a_zero = 0.0
joint_b_zero = 0.0
joint_c_zero = 0.0
joint_d_zero = 0.0
lastMessageType = "IK"
mysock = None

class OutputAnglesOperator(bpy.types.Operator):
    global sock
    bl_idname = "wm.output_angles"
    bl_label = "Output Angles"

    def execute(self, context):
        send_arm_data()

        return {'FINISHED'}

# TODO Operator for changing lengths of arm bones
class UpdateLengthsOperator(bpy.types.Operator):
    bl_idname = "wm.update_lengths"
    bl_label = "Update Lengths"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        
        #Set arm lengths based on the values in the menu
        arm = context.scene.objects['New Arm']
        end = context.scene.objects['End Effector']
        
        """
        end.data.bones[0].length = 
        arm.data.bones['DE'].length = 
        arm.data.bones['CD'].length = 
        arm.data.bones['BC'].length =

        """ 

        return {'FINISHED'}

# Sets the zero position for joints to the current position (allows for relative rotation)
class SetZeroAngle(bpy.types.Operator):
    bl_idname = "wm.set_zero_angle"
    bl_label = "Set Zero Angles"

    def execute(self, context):
        global joint_a_zero
        global joint_b_zero
        global joint_c_zero
        global joint_d_zero
        
        arm = context.scene.objects['New Arm']
        
        #Get references to each bone
        ab_bone = arm.pose.bones["AB"]
        bc_bone = arm.pose.bones["BC"]
        cd_bone = arm.pose.bones["CD"]
        de_bone = arm.pose.bones["DE"]

        joint_a_zero = ab_bone.rotation_euler[1]
        joint_b_zero = (ab_bone.matrix.inverted() * bc_bone.matrix).to_euler()[0]
        joint_c_zero = (bc_bone.matrix.inverted() * cd_bone.matrix).to_euler()[0]
        joint_d_zero = (cd_bone.matrix.inverted() * de_bone.matrix).to_euler()[0]

        print(joint_a_zero, joint_b_zero, joint_c_zero, joint_d_zero)
        print()

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
        layout.operator("wm.set_zero_angle")


# ------------------------------------------------------------------------
# register and unregister
# - Necessary for our tool to be an "add-on"
# ------------------------------------------------------------------------

def send_arm_data():
    global sock

    #Get references to the armature objects, which contain bones
    arm = bpy.data.objects['New Arm']
    end_effector = bpy.data.objects['End Effector']
    
    #Get references to each bone
    bc_bone = arm.pose.bones["BC"]
    cd_bone = arm.pose.bones["CD"]
    de_bone = arm.pose.bones["DE"]
    end_bone = end_effector.pose.bones["End Effector"]

    
    # Create a timestamp to print
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        if sock == None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Connecting...")
            sock.connect(('127.0.0.1', 8019))
            print("Connected!")

        data = {
            'A': ab_bone.rotation_euler[1] - joint_a_zero,
            'B': bc_bone.rotation_euler[0] - joint_b_zero,
            'C': cd_bone.rotation_euler[0] - joint_c_zero,
            'D': de_bone.rotation_euler[0] - joint_d_zero,
            'E': 0
        }
        sock.sendall(json.dumps(data).encode())
        print("Sent!")
        print(data)
    except socket.error as exc:
        print(exc)
        sock = None

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.my_tool = PointerProperty(type=MySettings)
    bpy.app.handlers.scene_update_pre.append(updateAB)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.my_tool
    bpy.app.handlers.scene_update_pre.remove(updateAB)
    mysock.close()

def updateAB(self):
    if lastMessageType == 'IK':
        arm = bpy.data.objects['New Arm']
        ab_bone = arm.pose.bones["AB"]
        arm_endpoint = bpy.data.objects['End Effector'].pose.bones["End Effector"]
        ab_bone.rotation_euler[1] = math.atan2(arm_endpoint.head[1], arm_endpoint.head[0] - 0.205)

    arm_endpoint = bpy.data.objects['End Effector'].pose.bones["End Effector"]
    vis_endpoint = bpy.data.objects['Visable Effector'].pose.bones["Visable Effector"]
    de_bone = bpy.data.objects['New Arm'].pose.bones["DE"]
    ef_bone = bpy.data.objects['New Arm'].pose.bones["EF"]
    deltaPos = ef_bone.tail - de_bone.tail
    arm_endpoint.location = vis_endpoint.location + mathutils.Vector([-deltaPos.x, -deltaPos.z, deltaPos.y])

def recv_commands():
    global lastMessageType
    global mysock

    print("Starting Thread!")
    mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mysock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mysock.bind(("localhost", 8018))
    mysock.listen(5)
    arm = bpy.data.objects['New Arm']
    arm_endpoint = bpy.data.objects['End Effector'].pose.bones["End Effector"]
    vis_endpoint = bpy.data.objects['Visable Effector'].pose.bones["Visable Effector"]

    ab_bone = arm.pose.bones["AB"]
    bc_bone = arm.pose.bones["BC"]
    cd_bone = arm.pose.bones["CD"]
    de_bone = arm.pose.bones["DE"]
    while True:
        conn, _ = mysock.accept()
        data = conn.recv(1024)
        msg = json.loads(data.decode('utf8'))
        print(msg)
        # print(msg.type)
        lastMessageType = msg['type']
        if msg['type'] == "IK":
            vis_endpoint.location[0] += msg["deltaX"]
            vis_endpoint.location[1] += msg["deltaY"]
            vis_endpoint.location[2] += msg["deltaZ"]

            # ab_bone.rotation_euler[1] = 0
            bc_bone.rotation_euler[0] = 0
            cd_bone.rotation_euler[0] = 0
            de_bone.rotation_euler[0] = 0

            de_bone.constraints[0].mute = False

            if abs( msg["deltaX"] )>0 or abs( msg["deltaY"] )>0 or abs( msg["deltaZ"] )>0:
                send_arm_data()
        elif msg['type'] == "FK":
            de_bone.constraints[0].mute = True
            # end_effector = bpy.data.objects['End Effector']

            ab_bone.rotation_euler[1] = joint_a_zero - math.radians(msg['joint_a'])
            bc_bone.rotation_euler[0] = joint_b_zero -  math.radians(msg['joint_b'])  
            cd_bone.rotation_euler[0] = joint_c_zero -  math.radians(msg['joint_c'])
            de_bone.rotation_euler[0] = joint_d_zero -  math.radians(msg['joint_d'])

            rawLoc = arm.location + de_bone.tail
            _endpoint.location = [rawLoc.x, rawLoc.z, -rawLoc.y]
            print(arm.location, de_bone.tail)

        

thread = threading.Thread(target=recv_commands)
thread.start()


if __name__ == "__main__":
    register()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(recv_commands(), register())