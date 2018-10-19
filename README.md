# MRover Inverse Kinematis

## Installing the Blender Add-on

*File -> User Preferences -> Add-ons -> Import from File*

![](https://raw.githubusercontent.com/wolfm/MRover-Inverse-Kinematics/master/images/install_addon_0.png)

Navigate to and select MRoverIK.py, then click *Install Add-on From File*

![](https://raw.githubusercontent.com/wolfm/MRover-Inverse-Kinematics/master/images/install_addon_1.png)

Under *Categories* (on the left), select *User*

Check the box for MRover

![](https://raw.githubusercontent.com/wolfm/MRover-Inverse-Kinematics/master/images/install_addon_2.png)

If you want the Add-on to be enabled every time you start Blender, Click *Save User Settings* in the bottom left


## Using the Blender Add-on

Currently, the add-on only includes the central functionality of IK: determining the angles of each joint based on the position and rotation of the end effector.

Make sure the 3d view is in pose mode. Moving any objects in object mode will cause the output angles to be incorrect.

![](https://raw.githubusercontent.com/wolfm/MRover-Inverse-Kinematics/master/images/using_addon_0.png)

Drag the arm eng effector into desired position using the shown triads. To rotate the end effector, it is recommended that you use the rotation hotkeys. Press `R` to initiate rotation and then `X`, `Y`, or `Z` to limit rotation to the specified axis.

To view the output angles, navigate to the MRover tab of the left toolbar and click *Output Angles*. Note that the MRover tab is only visible in pose mode. If you do not see a toolbar on the left, press `T` to bring it up.

![](https://raw.githubusercontent.com/wolfm/MRover-Inverse-Kinematics/master/images/using_addon_1.png)

To view the output, go to *Window -> Toggle System Console*.

![](https://raw.githubusercontent.com/wolfm/MRover-Inverse-Kinematics/master/images/using_addon_2.png)