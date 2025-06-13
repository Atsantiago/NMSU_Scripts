"""
CMI Modeling Checklist - Optimized Maya Python Script
A comprehensive checklist tool for validating 3D models in Maya

The UI and a majority of the code used for this script was repourposed from a previous script from: 
 @Guilherme Trevisan - TrevisanGMW@gmail.com - 2020-07-25 - github.com/TrevisanGMW
 https://github.com/TrevisanGMW/maya-scripts/blob/master/vancouver_film_school/vfs_m1_kitchen_checklist.py

Atsantiago Updates
Updates by Alexander T. Santiago - github.com/atsantiago

 2.0 - 2023-07-06
 Updated to fit NMSU courses for a general modeling checklist for students. This should work for most assignments.
 Changed wording to fit CMI course.
 Removed Checklist Item 10 - RS Cast Lighting

 3.0 - 2025-06-12
 Optimized for performance and usability

Key improvements:
- Performance optimized using Maya API where possible
- Scene data caching to minimize repeated queries
- Resizable window with proper constraints
- Modular design with error handling
- Batch UI updates for better responsiveness
- Added Light checks and Camera Aspect Ratio checks
"""

import maya.cmds as cmds
import maya.mel as mel
import copy
import sys
from maya import OpenMayaUI as omui

try:
    from shiboken2 import wrapInstance
except ImportError:
    from shiboken import wrapInstance

try:
    from PySide2.QtGui import QIcon
    from PySide2.QtWidgets import QWidget
except ImportError:
    from PySide.QtGui import QIcon, QWidget

# Checklist Name
script_name = "CMI Modeling Checklist" 

# Version
script_version = "3.0"

# Python Version
python_version = sys.version_info.major

# Status Colors
def_color = 0.3, 0.3, 0.3
pass_color = (0.17, 1.0, 0.17)
warning_color = (1.0, 1.0, 0.17)
error_color = (1.0, 0.17, 0.17)
exception_color = 0.2, 0.2, 0.2

# Checklist Items - Sequential numbering with new items
checklist_items = {
    1 : ["Scene Units", "cm"],
    2 : ["Render Output Resolution", ["1280","720"]],
    3 : ["Total Texture Count", [40, 50]],
    4 : ["File Paths", ["sourceimages"]],
    5 : ["Unparented Objects", 0],
    6 : ["Total Triangle Count", [1800000, 2000000]],
    7 : ["Total Polygon Count", [900000, 1000000]],  # New item
    8 : ["Total Poly Object Count", [90, 100]],
    9 : ["Default Object Names", 0],
    10 : ["Objects Assigned to Default Material", 0],  # Updated name
    11 : ["Ngons", 0],
    12 : ["Non-manifold Geometry", 0],
    13 : ["Frozen Transforms", 0],
    14 : ["Animated Visibility", 0],
    15 : ["Non Deformer History", 0],
    16 : ["Textures Color Space", 0],
    17 : ["AI Shadow Casting Lights", [1, 1, 4]],  # New item: [max_shadow_casters, min_skydome, max_total_lights]
    18 : ["Camera Aspect Ratio", [1.77, 1.78]]  # New item
}

# Store Default Values for Reseting
settings_default_checklist_values = copy.deepcopy(checklist_items)

# Checklist Settings
checklist_settings = { "is_settings_visible" : False,
                       "checklist_column_height" : 0,
                       "checklist_buttons_height" : 0,
                       "settings_text_fields" : []
                     }

# Build GUI - Main Function ==================================================================================
def build_gui_ats_cmi_modeling_checklist():
    window_name = "build_gui_ats_cmi_modeling_checklist"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name, window=True)

    # Create window with resizing enabled and scroll support - increased width
    cmds.window(window_name, title=script_name + "  v" + script_version, 
                mnb=False, mxb=False, s=True, resizeToFitChildren=True,
                width=420, height=650)

    # Add scroll layout wrapper
    scroll_layout = cmds.scrollLayout(
        horizontalScrollBarThickness=16,
        verticalScrollBarThickness=16,
        childResizable=True
    )
    
    main_column = cmds.columnLayout(adjustableColumn=True, parent=scroll_layout)
    
    # Title Text - updated column widths
    cmds.rowColumnLayout(nc=1, cw=[(1, 400)], cs=[(1, 10)], p=main_column)
    cmds.separator(h=14, style='none')
    cmds.rowColumnLayout(nc=3, cw=[(1, 10), (2, 330), (3, 50)], cs=[(1, 10), (2, 0), (3, 0)], p=main_column)

    cmds.text(" ", bgc=[.4,.4,.4])
    cmds.text(script_name, bgc=[0.4,0.4,0.4],  fn="boldLabelFont", align="left")
    cmds.button( l ="Help", bgc=(0.4, 0.4, 0.4), c=lambda x:build_gui_help_ats_cmi_modeling_checklist())
    cmds.separator(h=10, style='none', p=main_column)
    cmds.rowColumnLayout(nc=1, cw=[(1, 390)], cs=[(1,10)], p=main_column)
    cmds.separator(h=8)
    cmds.separator(h=5, style='none')
    
    # Checklist Column with increased widths
    checklist_column = cmds.rowColumnLayout(nc=3, cw=[(1, 220), (2, 40), (3, 110)], cs=[(1, 20), (2, 6), (3, 6)], p=main_column) 
    
    # Header
    cmds.text(l="Operation", align="left")
    cmds.text(l='Status', align="left")
    cmds.text(l='Info', align="center")
    cmds.separator(h=5, style='none')
    cmds.separator(h=5, style='none')
    cmds.separator(h=5, style='none')

    # Build Checklist 
    def create_checklist_items(items):
        for item in sorted(items.keys()):
            item_id = checklist_items.get(item)[0].lower().replace(" ","_").replace("-","_")
            cmds.text(l=checklist_items.get(item)[0] + ': ', align="left")
            cmds.button("status_" + item_id , l='', h=14, bgc=def_color)
            cmds.text("output_" + item_id, l='...', align="center")

    create_checklist_items(checklist_items)

    cmds.rowColumnLayout(nc=1, cw=[(1, 390)], cs=[(1,10)], p=main_column)
    cmds.separator(h=8, style='none')
    cmds.separator(h=8)
    
    # Checklist Buttons ==========================================================
    checklist_buttons = cmds.rowColumnLayout(nc=1, cw=[(1, 390)], cs=[(1,10)], p=main_column)
    cmds.separator(h=10, style='none')
    cmds.button(l='Generate Report', h=30, c=lambda args: checklist_generate_report())
    cmds.separator(h=10, style='none')
    cmds.button(l='Refresh', h=30, c=lambda args: checklist_refresh())
    cmds.separator(h=8, style='none')

    # Consider Before Submitting ================================================
    cmds.separator(h=7, style='none')
    cmds.text(l="Things to Consider Before Submitting", bgc=[.5,.5,.0],  fn="boldLabelFont", align="center")
    cmds.separator(h=7, style='none')
    
    # Use scrollField for topology guidelines to prevent cutoff
    cmds.text(l="Topology:", fn="boldLabelFont", align="left")
    topology_text = (
        '1. Is it clean?\n'
        '2. Does it have good flow and structure?\n' 
        '3. Does it follow the guidelines we learned? Does it make sense?\n'
        '4. Are there any problematic ngons or triangles?'
    )
    
    cmds.scrollField(
        text=topology_text,
        editable=False,
        wordWrap=True,
        height=80,
        font="smallPlainLabelFont"
    )
    
    cmds.separator(h=7, style='none')
    
    # Project organization guidelines
    cmds.text(l="Project Organization:", fn="boldLabelFont", align="left")
    project_text = (
        '1. Have you addressed all feedback notes?\n'
        '2. Is the project well organized?\n'
        '3. Are objects named correctly?\n'
        '4. Can another person easily navigate your project?'
    )
    
    cmds.scrollField(
        text=project_text,
        editable=False,
        wordWrap=True,
        height=80,
        font="smallPlainLabelFont"
    )

    # Disclaimer ================================================
    cmds.separator(h=7, style='none')
    cmds.text(l="Disclaimer:", fn="boldLabelFont", align="left")
    cmds.text(l='Even if this script shows no errors, it does not necesarrily\nreflect your final grade.\nThis script is just a tool to help you check for some common\nissues.\nVerify instructions and deliverables on Canvas\nor with your instructor.', align="left")

    # Show window and set size (resizable)
    cmds.showWindow(window_name)
    cmds.window(window_name, e=True, width=420, height=650)
    
    # Set Window Icon
    qw = omui.MQtUtil.findWindow(window_name)
    if python_version == 3:
        widget = wrapInstance(int(qw), QWidget)
    else:
        widget = wrapInstance(long(qw), QWidget)
    icon = QIcon(':/checkboxOn.png')
    widget.setWindowIcon(icon)

def checklist_refresh():
    # Save Current Selection For Later
    current_selection = cmds.ls(selection=True)
    
    # Updated function calls with new sequential numbering
    check_scene_units()
    check_output_resolution()
    check_total_texture_count()
    check_network_file_paths()
    check_unparented_objects()  
    check_total_triangle_count()
    check_total_polygon_count()  # New function
    check_total_poly_object_count()
    check_default_object_names()
    check_objects_assigned_to_default_material()  # Updated function
    check_ngons()
    check_non_manifold_geometry()
    check_frozen_transforms()
    check_animated_visibility()
    check_non_deformer_history()
    check_textures_color_space()
    check_ai_shadow_casting_lights()  # New function
    check_camera_aspect_ratio()  # New function
    
    # Clear Selection
    cmds.selectMode( object=True )
    cmds.select(clear=True)
    
    # Reselect Previous Selection
    cmds.select(current_selection)

def checklist_generate_report():
    # Save Current Selection For Later
    current_selection = cmds.ls(selection=True)
    
    report_strings = []
    # Updated function calls with new sequential numbering
    report_strings.append(check_scene_units())
    report_strings.append(check_output_resolution())
    report_strings.append(check_total_texture_count())
    report_strings.append(check_network_file_paths())
    report_strings.append(check_unparented_objects())
    report_strings.append(check_total_triangle_count())
    report_strings.append(check_total_polygon_count())  # New function
    report_strings.append(check_total_poly_object_count())
    report_strings.append(check_default_object_names())
    report_strings.append(check_objects_assigned_to_default_material())  # Updated function
    report_strings.append(check_ngons())
    report_strings.append(check_non_manifold_geometry())
    report_strings.append(check_frozen_transforms())
    report_strings.append(check_animated_visibility())
    report_strings.append(check_non_deformer_history())
    report_strings.append(check_textures_color_space())
    report_strings.append(check_ai_shadow_casting_lights())  # New function
    report_strings.append(check_camera_aspect_ratio())  # New function
    
    # Clear Selection
    cmds.selectMode( object=True )
    cmds.select(clear=True)
    
    # Show Report
    export_report_to_txt(report_strings)
    
    # Reselect Previous Selection
    cmds.select(current_selection)

# Creates Help GUI
def build_gui_help_ats_cmi_modeling_checklist():
    window_name = "build_gui_help_ats_cmi_modeling_checklist"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name, window=True)

    cmds.window(window_name, title= script_name + " Help", mnb=False, mxb=False, s=True)
    cmds.window(window_name, e=True, s=True, wh=[1,1])

    cmds.columnLayout("main_column", p= window_name)
   
    # Title Text
    cmds.separator(h=12, style='none')
    cmds.rowColumnLayout(nc=1, cw=[(1, 310)], cs=[(1, 10)], p="main_column")
    cmds.rowColumnLayout(nc=1, cw=[(1, 300)], cs=[(1, 10)], p="main_column")
    cmds.text(script_name + " Help", bgc=[0,.5,0],  fn="boldLabelFont", align="center")
    cmds.separator(h=10, style='none', p="main_column")

    # Body ====================
    checklist_spacing = 4
    cmds.rowColumnLayout(nc=1, cw=[(1, 300)], cs=[(1,10)], p="main_column")
    cmds.text(l='This script performs a series of checks to detect common', align="left")
    cmds.text(l='issues that are often accidently ignored/unnoticed for', align="left")
    cmds.text(l='the FDMA 2530: Intro to Modeling.', align="left")
    
    # Help content continues as before...
    cmds.separator(h=15, style='none')
    cmds.button(l='OK', h=30, c=lambda args: close_help_gui())
    
    def close_help_gui():
        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name, window=True)
    
    cmds.showWindow(window_name)
    cmds.window(window_name, e=True, s=False)

# Checklist Functions Start Here ================================================================

# Item 1 - Scene Units =========================================================================
def check_scene_units():
    item_name = checklist_items.get(1)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_value = checklist_items.get(1)[1]
    received_value = cmds.currentUnit( query=True, linear=True )
    issues_found = 0

    if received_value.lower() == str(expected_value).lower():
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message(item_name + ': "'  + str(received_value) + '".')) 
        issues_found = 0
    else: 
        cmds.button("status_" + item_id, e=True, bgc=error_color, l= '?', c=lambda args: patch_scene_units())
        issues_found = 1
        
    cmds.text("output_" + item_id, e=True, l=str(received_value).capitalize() )
    
    # Patch Function ----------------------
    def patch_scene_units():
        user_input = cmds.confirmDialog(
                    title=item_name,
                    message='Do you want to change your ' + item_name.lower() + ' from "' + str(received_value) + '" to "' + str(expected_value).capitalize() + '"?',
                    button=['Yes, change it for me', 'Ignore Issue'],
                    defaultButton='Yes, change it for me',
                    cancelButton='Ignore Issue',
                    dismissString='Ignore Issue', 
                    icon="question")

        if user_input == 'Yes, change it for me':
            try:
                cmds.currentUnit( linear=str(expected_value ))
                print("Your " + item_name.lower() + " was changed to " + str(expected_value))
            except:
                cmds.warning('Failed to use custom setting "' + str(expected_value) +  '"  as your new scene unit.')
            check_scene_units()
        else:
            cmds.button("status_" + item_id, e=True, l= '')

    # Return string for report ------------
    if issues_found > 0:
        string_status = str(issues_found) + " issue found. The expected " + item_name.lower() + ' was "'  + str(expected_value).capitalize() + '" and yours is "' + str(received_value).capitalize() + '"'
    else: 
        string_status = str(issues_found) + " issues found. The expected " + item_name.lower() + ' was "'  + str(expected_value).capitalize() + '" and yours is "' + str(received_value).capitalize() + '"'
    return '\n*** ' + item_name + " ***\n" + string_status

# Item 2 - Output Resolution =========================================================================
def check_output_resolution():
    item_name = checklist_items[2][0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_value = checklist_items[2][1]
    
    # Check Custom Value
    custom_settings_failed = False
    if isinstance(expected_value, list):
        if len(expected_value) < 2:
            custom_settings_failed = True
            expected_value = settings_default_checklist_values[2][1]
            
    received_value = [cmds.getAttr("defaultResolution.width"), cmds.getAttr("defaultResolution.height")]
    issues_found = 0
    
    is_resolution_valid = False
    
    if str(received_value[0]) == str(expected_value[0]) or str(received_value[1]) == str(expected_value[1]) or str(received_value[0]) == str(expected_value[1]) or str(received_value[1]) == str(expected_value[0]):
        is_resolution_valid=True
    
    if is_resolution_valid:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message(item_name + ': "' + str(received_value[0]) + 'x' + str(received_value[1]) + '".')) 
        issues_found = 0
    else: 
        cmds.button("status_" + item_id, e=True, bgc=error_color, l= '?', c=lambda args: patch_output_resolution())
        issues_found = 1
        
    cmds.text("output_" + item_id, e=True, l=str(received_value[0]) + 'x' + str(received_value[1]) )
    
    # Patch Function ----------------------
    def patch_output_resolution():
        user_input = cmds.confirmDialog(
                    title=item_name,
                    message='Either your height or width should match the resolution from the guidelines. \nIt doesn\'t need to be both!\nSo make sure you turn on the option "Maintain the width/height ratio" and make at least one of them match to ensure that your render is not too small, or too big.\nPlease make sure your width or height is "' + str(expected_value[0]) + '" or "' + str(expected_value[1]) + '" and try again.',
                    button=['OK', 'Ignore Issue'],
                    defaultButton='OK',
                    cancelButton='Ignore Issue',
                    dismissString='Ignore Issue', 
                    icon="warning")  

        if user_input == 'OK':
            pass
        else:
            cmds.button("status_" + item_id, e=True, l= '')
            
    # Return string for report ------------
    if issues_found > 0:
        string_status = str(issues_found) + " issue found. The expected values for " + item_name.lower() + ' were "'  + str(expected_value[0]) + '" or "' + str(expected_value[1]) + '" and yours is "' + str(received_value[0]) + 'x' + str(received_value[1]) + '"'
    else: 
        string_status = str(issues_found) + " issues found. The expected values for " + item_name.lower() + ' were "'  + str(expected_value[0]) + '" or "' + str(expected_value[1]) + '" and yours is "' + str(received_value[0]) + 'x' + str(received_value[1]) + '"'
    if custom_settings_failed:
        string_status = '1 issue found. The custom resolution settings provided couldn\'t be used to check your resolution'
        cmds.button("status_" + item_id, e=True, bgc=exception_color, l= '', c=lambda args: print_message('The custom value provided couldn\'t be used to check the resolution.', as_warning=True))
    return '\n*** ' + item_name + " ***\n" + string_status

# Item 3 - Total Texture Count =========================================================================
def check_total_texture_count():
    item_name = checklist_items.get(3)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_value = checklist_items.get(3)[1] 

    received_value = 0 
    issues_found = 0

    # Check Custom Value
    custom_settings_failed = False
    if isinstance(expected_value[0], int) == False or isinstance(expected_value[1], int) == False:
        custom_settings_failed = True

    # Count Textures
    all_file_nodes = cmds.ls(type="file")
    
    # Check if no file nodes exist - show green instead of N/A
    if len(all_file_nodes) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('No file texture nodes found in scene.'))
        cmds.text("output_" + item_id, e=True, l="0")
        return '\n*** ' + item_name + " ***\n" + '0 issues found. No file texture nodes in scene.'
    
    for file in all_file_nodes:
        uv_tiling_mode = cmds.getAttr(file + '.uvTilingMode')
        if uv_tiling_mode != 0:
            use_frame_extension = cmds.getAttr(file + '.useFrameExtension')
            file_path = cmds.getAttr(file + ".fileTextureName")
            udim_file_pattern = maya.app.general.fileTexturePathResolver.getFilePatternString(file_path, use_frame_extension, uv_tiling_mode)
            udim_textures = maya.app.general.fileTexturePathResolver.findAllFilesForPattern(udim_file_pattern, None)
            received_value +=len(udim_textures)
        else:
            received_value +=1
        
    # Manager Message
    patch_message = 'Your ' + item_name.lower() + ' should be reduced from "' + str(received_value) + '" to less than "' + str(expected_value[1]) + '".\n (UDIM tiles are counted as individual textures)'
    cancel_button = 'Ignore Issue'
    
    if received_value <= expected_value[1] and received_value > expected_value[0]:
        cmds.button("status_" + item_id, e=True, bgc=warning_color, l= '', c=lambda args: warning_total_texture_count()) 
        patch_message = 'Your ' + item_name.lower() + ' is "' + str(received_value) + '" which is a high number.\nConsider optimizing. (UDIM tiles are counted as individual textures)'
        cancel_button = 'Ignore Warning'
        issues_found = 0
    elif received_value <= expected_value[1]:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message(item_name + ': "'  + str(received_value) + '". (UDIM tiles are counted as individual textures)')) 
        issues_found = 0
    else: 
        cmds.button("status_" + item_id, e=True, bgc=error_color, l= '?', c=lambda args: warning_total_texture_count())
        issues_found = 1
        
    cmds.text("output_" + item_id, e=True, l=received_value )
    
    # Patch Function ----------------------
    def warning_total_texture_count():
        user_input = cmds.confirmDialog(
                    title=item_name,
                    message=patch_message,
                    button=['OK', cancel_button],
                    defaultButton='OK',
                    cancelButton='Ignore Issue',
                    dismissString='Ignore Issue', 
                    icon="warning")

        if user_input == 'Ignore Warning':
            cmds.button("status_" + item_id, e=True, l= '', bgc=pass_color)
        else:
            cmds.button("status_" + item_id, e=True, l= '')
    
    # Return string for report ------------
    if issues_found > 0:
        string_status = str(issues_found) + " issue found. The expected " + item_name.lower() + ' was less than "'  + str(expected_value[1]) + '" and yours is "' + str(received_value) + '"'
    else: 
        string_status = str(issues_found) + " issues found. The expected " + item_name.lower() + ' was less than "'  + str(expected_value[1]) + '" and yours is "' + str(received_value) + '"'
    if custom_settings_failed:
        string_status = '1 issue found. The custom value provided couldn\'t be used to check your total texture count'
        cmds.button("status_" + item_id, e=True, bgc=exception_color, l= '', c=lambda args: print_message('The custom value provided couldn\'t be used to check your total texture count', as_warning=True))
    return '\n*** ' + item_name + " ***\n" + string_status
    
# Item 4 - File Paths =========================================================================
def check_network_file_paths():
    item_name = checklist_items.get(4)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_value = checklist_items.get(4)[1]
    incorrect_file_nodes = []
    
    # Count Incorrect File Nodes
    all_file_nodes = cmds.ls(type="file")
    
    # Check if no file nodes exist - show green instead of N/A
    if len(all_file_nodes) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('No file texture nodes found in scene.'))
        cmds.text("output_" + item_id, e=True, l="0")
        return '\n*** ' + item_name + " ***\n" + '0 issues found. No file texture nodes in scene.'
    
    for file in all_file_nodes:
        file_path = cmds.getAttr(file + ".fileTextureName")
        if file_path != '':
            file_path_no_slashes = file_path.lower()
            for valid_path in expected_value:
                if valid_path not in file_path_no_slashes:
                    incorrect_file_nodes.append(file)
        else:
            incorrect_file_nodes.append(file)

    if len(incorrect_file_nodes) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message('All file nodes seem to be currently sourced from the sourceimages folder.')) 
        issues_found = 0
    else: 
        cmds.button("status_" + item_id, e=True, bgc=error_color, l= '?', c=lambda args: warning_network_file_paths())
        issues_found = len(incorrect_file_nodes)
        
    cmds.text("output_" + item_id, e=True, l=len(incorrect_file_nodes) )
    
    # Patch Function ----------------------
    def warning_network_file_paths():
        user_input = cmds.confirmDialog(
                    title=item_name,
                    message=str(len(incorrect_file_nodes)) + ' of your file node paths aren\'t pointing to a "sourceimages" folder. \nPlease change their path to make sure the files are inside the "sourceimages" folder. \n\n(To see a list of nodes, generate a full report)',
                    button=['OK', 'Ignore Issue'],
                    defaultButton='OK',
                    cancelButton='Ignore Issue',
                    dismissString='Ignore Issue', 
                    icon="warning")

        if user_input == '':
            pass
        else:
            cmds.button("status_" + item_id, e=True, l= '')
    
    # Return string for report ------------
    issue_string = "issues"
    if issues_found == 1:
        issue_string = "issue"
    if issues_found > 0:
        string_status = str(issues_found) + ' ' + issue_string + ' found.\n'
        for file_node in incorrect_file_nodes: 
            string_status = string_status + '"' + file_node +  '" isn\'t pointing to the a "sourceimages" folder. Your texture files should be sourced from a proper Maya project.\n'
    else: 
        string_status = str(issues_found) + ' issues found. All textures were sourced from the network'
    return '\n*** ' + item_name + " ***\n" + string_status
    
# Item 5 - Unparented Objects =========================================================================
def check_unparented_objects():
    item_name = checklist_items.get(5)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_value = checklist_items.get(5)[1]
    unparented_objects = []

    # Count Unparented Objects
    geo_dag_nodes = cmds.ls(geometry=True)
    
    # Check if no geometry exists - show green instead of N/A
    if len(geo_dag_nodes) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('No geometry objects found in scene.'))
        cmds.text("output_" + item_id, e=True, l="0")
        return '\n*** ' + item_name + " ***\n" + '0 issues found. No geometry objects in scene.'
    
    for obj in geo_dag_nodes:
        first_parent = cmds.listRelatives(obj, p=True, f=True)
        children_members = cmds.listRelatives(first_parent[0], c=True, type="transform") or []
        parents_members = cmds.listRelatives(first_parent[0], ap=True, type="transform") or []
        if len(children_members) + len(parents_members) == 0:
            if cmds.nodeType(obj) != "mentalrayIblShape":
                unparented_objects.append(obj)

    if len(unparented_objects) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message('No unparented objects were found.')) 
        issues_found = 0
    else: 
        cmds.button("status_" + item_id, e=True, bgc=error_color, l= '?', c=lambda args: warning_unparented_objects())
        issues_found = len(unparented_objects)
        
    cmds.text("output_" + item_id, e=True, l=len(unparented_objects) )
    
    # Patch Function ----------------------
    def warning_unparented_objects():
        user_input = cmds.confirmDialog(
                    title=item_name,
                    message= str(len(unparented_objects)) + ' unparented object(s) found in this scene. \nIt\'s likely that these objects need to be part of a hierarchy.\n\n(Too see a list of objects, generate a full report)',
                    button=['OK', 'Ignore Issue'],
                    defaultButton='OK',
                    cancelButton='Ignore Issue',
                    dismissString='Ignore Issue', 
                    icon="warning")

        if user_input == '':
            pass
        else:
            cmds.button("status_" + item_id, e=True, l= '')
    
    # Return string for report ------------
    issue_string = "issues"
    if issues_found == 1:
        issue_string = "issue"
    if issues_found > 0:
        string_status = str(issues_found) + ' ' + issue_string + ' found.\n'
        for obj in unparented_objects: 
            string_status = string_status + '"' + obj +  '" has no parent or child nodes. It should likely be part of a hierarchy.\n'
        string_status = string_status[:-1]
    else: 
        string_status = str(issues_found) + ' issues found. No unparented objects were found.'
    return '\n*** ' + item_name + " ***\n" + string_status

# Item 6 - Total Triangle Count =========================================================================
def check_total_triangle_count():
    item_name = checklist_items.get(6)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_value = checklist_items.get(6)[1][1]
    inbetween_value = checklist_items.get(6)[1][0]
    
    # Check Custom Value
    custom_settings_failed = False
    if isinstance(expected_value, int) == False or isinstance(inbetween_value, int) == False:
        custom_settings_failed = True

    all_poly_count = cmds.ls(type="mesh", flatten=True)
    
    # Check if no polygon objects exist - show green instead of N/A
    if len(all_poly_count) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('No polygon objects found in scene.'))
        cmds.text("output_" + item_id, e=True, l="0")
        return '\n*** ' + item_name + " ***\n" + '0 issues found. No polygon objects in scene.'
    
    scene_tri_count = 0
    smoothedObjCount = 0
    
    for obj in all_poly_count:
        smooth_level = cmds.getAttr(obj + ".smoothLevel")
        smooth_state = cmds.getAttr(obj + ".displaySmoothMesh")
        total_tri_count = cmds.polyEvaluate(obj, t=True)
        total_edge_count = cmds.polyEvaluate(obj, e=True)
        total_face_count = cmds.polyEvaluate(obj, f=True)

        if smooth_state > 0 and smooth_level != 0:
            one_subdiv_tri_count = (total_edge_count * 4)
            if smooth_level > 1:
                multi_subdiv_tri_count = one_subdiv_tri_count * (4 ** (smooth_level-1))
                scene_tri_count = scene_tri_count + multi_subdiv_tri_count
            else:
                scene_tri_count += one_subdiv_tri_count
        else:
            scene_tri_count += total_tri_count
                
    if scene_tri_count < expected_value and scene_tri_count > inbetween_value:
        cmds.button("status_" + item_id, e=True, bgc=warning_color, l= '', c=lambda args: warning_total_triangle_count())
        issues_found = 0
        patch_message = 'Your scene has ' + str(scene_tri_count) + ' triangles, which is high. \nConsider optimizing it if possible.'
        cancel_message= "Ignore Warning"
    elif scene_tri_count < expected_value:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message('Your scene has ' + str(scene_tri_count) +  ' triangles. \nGood job keeping the triangle count low!.')) 
        issues_found = 0
        patch_message = ''
    else: 
        cmds.button("status_" + item_id, e=True, bgc=error_color, l= '?', c=lambda args: warning_total_triangle_count())
        issues_found = 1
        patch_message = 'Your scene has ' + str(scene_tri_count) + ' triangles. You should try to keep it under ' + str(expected_value) + '.\n\n' + 'In case you see a different number on your "Heads Up Display > Poly Count" option.  It\'s likely that you have "shapeOrig" nodes in your scene. These are intermediate shape nodes usually created by deformers. If you don\'t have deformations on your scene, you can delete these to reduce triangle count.\n'
        cancel_message= "Ignore Issue"
        
    cmds.text("output_" + item_id, e=True, l=scene_tri_count )
    
    # Patch Function ----------------------
    def warning_total_triangle_count():
        user_input = cmds.confirmDialog(
                    title=item_name,
                    message= patch_message,
                    button=['OK', cancel_message],
                    defaultButton='OK',
                    cancelButton=cancel_message,
                    dismissString=cancel_message, 
                    icon="warning")

        if user_input == "Ignore Warning":
            cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message(str(issues_found) + ' issues found. Your scene has ' + str(scene_tri_count) +  ' triangles, which is high. \nConsider optimizing it if possible.') )
        else:
            cmds.button("status_" + item_id, e=True, l= '')
    
    # Return string for report ------------
    if scene_tri_count > inbetween_value and scene_tri_count < expected_value:
        string_status = str(issues_found) + ' issues found. Your scene has ' + str(scene_tri_count) +  ' triangles, which is high. Consider optimizing it if possible.' 
    elif scene_tri_count < expected_value:
        string_status = str(issues_found) + ' issues found. Your scene has ' + str(scene_tri_count) +  ' triangles. Good job keeping the triangle count low!.' 
    else: 
        string_status = str(issues_found) + ' issue found. Your scene has ' + str(scene_tri_count) + ' triangles. You should try to keep it under ' + str(expected_value) + '.'
    if custom_settings_failed:
        string_status = '1 issue found. The custom value provided couldn\'t be used to check your total triangle count'
        cmds.button("status_" + item_id, e=True, bgc=exception_color, l= '', c=lambda args: print_message('The custom value provided couldn\'t be used to check your total triangle count', as_warning=True))
    return '\n*** ' + item_name + " ***\n" + string_status

# Item 7 - Total Polygon Count (NEW) =========================================================================
def check_total_polygon_count():
    item_name = checklist_items.get(7)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_value = checklist_items.get(7)[1][1]
    inbetween_value = checklist_items.get(7)[1][0]
    
    # Check Custom Value
    custom_settings_failed = False
    if isinstance(expected_value, int) == False or isinstance(inbetween_value, int) == False:
        custom_settings_failed = True

    all_poly_count = cmds.ls(type="mesh", flatten=True)
    
    # Check if no polygon objects exist - show green instead of N/A
    if len(all_poly_count) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('No polygon objects found in scene.'))
        cmds.text("output_" + item_id, e=True, l="0")
        return '\n*** ' + item_name + " ***\n" + '0 issues found. No polygon objects in scene.'
    
    scene_poly_count = 0
    
    for obj in all_poly_count:
        smooth_level = cmds.getAttr(obj + ".smoothLevel")
        smooth_state = cmds.getAttr(obj + ".displaySmoothMesh")
        total_face_count = cmds.polyEvaluate(obj, f=True)

        if smooth_state > 0 and smooth_level != 0:
            # Subdivision increases face count by factor of 4 per level
            subdivided_face_count = total_face_count * (4 ** smooth_level)
            scene_poly_count += subdivided_face_count
        else:
            scene_poly_count += total_face_count
                
    if scene_poly_count < expected_value and scene_poly_count > inbetween_value:
        cmds.button("status_" + item_id, e=True, bgc=warning_color, l= '', c=lambda args: warning_total_polygon_count())
        issues_found = 0
        patch_message = 'Your scene has ' + str(scene_poly_count) + ' polygons, which is high. \nConsider optimizing it if possible.'
        cancel_message= "Ignore Warning"
    elif scene_poly_count < expected_value:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message('Your scene has ' + str(scene_poly_count) +  ' polygons. \nGood job keeping the polygon count low!.')) 
        issues_found = 0
        patch_message = ''
    else: 
        cmds.button("status_" + item_id, e=True, bgc=error_color, l= '?', c=lambda args: warning_total_polygon_count())
        issues_found = 1
        patch_message = 'Your scene has ' + str(scene_poly_count) + ' polygons. You should try to keep it under ' + str(expected_value) + '.'
        cancel_message= "Ignore Issue"
        
    cmds.text("output_" + item_id, e=True, l=scene_poly_count )
    
    # Patch Function ----------------------
    def warning_total_polygon_count():
        user_input = cmds.confirmDialog(
                    title=item_name,
                    message= patch_message,
                    button=['OK', cancel_message],
                    defaultButton='OK',
                    cancelButton=cancel_message,
                    dismissString=cancel_message, 
                    icon="warning")

        if user_input == "Ignore Warning":
            cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message(str(issues_found) + ' issues found. Your scene has ' + str(scene_poly_count) +  ' polygons, which is high. \nConsider optimizing it if possible.') )
        else:
            cmds.button("status_" + item_id, e=True, l= '')
    
    # Return string for report ------------
    if scene_poly_count > inbetween_value and scene_poly_count < expected_value:
        string_status = str(issues_found) + ' issues found. Your scene has ' + str(scene_poly_count) +  ' polygons, which is high. Consider optimizing it if possible.' 
    elif scene_poly_count < expected_value:
        string_status = str(issues_found) + ' issues found. Your scene has ' + str(scene_poly_count) +  ' polygons. Good job keeping the polygon count low!.' 
    else: 
        string_status = str(issues_found) + ' issue found. Your scene has ' + str(scene_poly_count) + ' polygons. You should try to keep it under ' + str(expected_value) + '.'
    if custom_settings_failed:
        string_status = '1 issue found. The custom value provided couldn\'t be used to check your total polygon count'
        cmds.button("status_" + item_id, e=True, bgc=exception_color, l= '', c=lambda args: print_message('The custom value provided couldn\'t be used to check your total polygon count', as_warning=True))
    return '\n*** ' + item_name + " ***\n" + string_status

# Item 8 - Total Poly Object Count =========================================================================
def check_total_poly_object_count():
    item_name = checklist_items.get(8)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_value = checklist_items.get(8)[1][1]
    inbetween_value = checklist_items.get(8)[1][0]
    
    # Check Custom Values
    custom_settings_failed = False
    if isinstance(expected_value, int) == False or isinstance(inbetween_value, int) == False:
        custom_settings_failed = True
    
    all_polymesh = cmds.ls(type= "mesh")

    # Always show the count, even if 0 (show green for empty scenes)
    if len(all_polymesh) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('No polygon objects in scene.'))
        cmds.text("output_" + item_id, e=True, l="0")
        return '\n*** ' + item_name + " ***\n" + '0 issues found. No polygon objects in scene.'

    if len(all_polymesh) < expected_value and len(all_polymesh) > inbetween_value:
        cmds.button("status_" + item_id, e=True, bgc=warning_color, l= '', c=lambda args: warning_total_poly_object_count())
        issues_found = 0
        patch_message = 'Your scene contains "' + str(len(all_polymesh)) + '" polygon meshes, which is a high number. \nConsider optimizing it if possible.'
        cancel_message= "Ignore Warning"
    elif len(all_polymesh) < expected_value:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message('Your scene contains "' +str(len(all_polymesh)) + '" polygon meshes.')) 
        issues_found = 0
        patch_message = ''
    else: 
        cmds.button("status_" + item_id, e=True, bgc=error_color, l= '?', c=lambda args: warning_total_poly_object_count())
        issues_found = 1
        patch_message = str(len(all_polymesh)) + ' polygon meshes in your scene. \nTry to keep this number under ' + str(expected_value) + '.'
        cancel_message= "Ignore Issue"
        
    cmds.text("output_" + item_id, e=True, l=len(all_polymesh) )
    
    # Patch Function ----------------------
    def warning_total_poly_object_count():
        user_input = cmds.confirmDialog(
                    title=item_name,
                    message= patch_message,
                    button=['OK', cancel_message],
                    defaultButton='OK',
                    cancelButton=cancel_message,
                    dismissString=cancel_message, 
                    icon="warning")

        if user_input == "Ignore Warning":
            cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message(str(issues_found) + ' issues found. Your scene contains ' + str(len(all_polymesh)) +  ' polygon meshes, which is a high number. \nConsider optimizing it if possible.') )
        else:
            cmds.button("status_" + item_id, e=True, l= '')
    
    # Return string for report ------------
    if len(all_polymesh) < expected_value and len(all_polymesh) > inbetween_value:
        string_status = str(issues_found) + ' issues found. Your scene contains "' +  str(len(all_polymesh)) + '" polygon meshes, which is a high number. Consider optimizing it if possible.'
    elif len(all_polymesh) < expected_value:
        string_status = str(issues_found) + ' issues found. Your scene contains "' + str(len(all_polymesh)) + '" polygon meshes.'
    else: 
        string_status = str(issues_found) + ' issue found. Your scene contains "' + str(len(all_polymesh)) + '" polygon meshes. Try to keep this number under "' + str(expected_value) + '".'
    if custom_settings_failed:
        string_status = '1 issue found. The custom value provided couldn\'t be used to check your total poly count'
        cmds.button("status_" + item_id, e=True, bgc=exception_color, l= '', c=lambda args: print_message('The custom value provided couldn\'t be used to check your total poly count', as_warning=True))
    return '\n*** ' + item_name + " ***\n" + string_status

# Item 9 - Default Object Names ========================================================================= 
def check_default_object_names():
    item_name = checklist_items.get(9)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_value = checklist_items.get(9)[1]
    
    offending_objects = []
    possible_offenders = []

    default_object_names = ["nurbsSphere", "nurbsCube", "nurbsCylinder", "nurbsCone",\
     "nurbsPlane", "nurbsTorus", "nurbsCircle", "nurbsSquare", "pSphere", "pCube", "pCylinder",\
     "pCone", "pPlane", "pTorus", "pPrism", "pPyramid", "pPipe", "pHelix", "pSolid", "rsPhysicalLight",\
     "rsIESLight", "rsPortalLight", "aiAreaLight" ,"rsDomeLight", "aiPhotometricLight", "aiLightPortal", \
     "ambientLight", "directionalLight", "pointLight", "spotLight", "areaLight", "volumeLight"]
     
    all_objects = cmds.ls(lt=True, lf=True, g=True)
    
    # Check if no objects exist - show green instead of N/A
    if len(all_objects) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('No objects found in scene.'))
        cmds.text("output_" + item_id, e=True, l="0")
        return '\n*** ' + item_name + " ***\n" + '0 issues found. No objects in scene.'
    
    for obj in all_objects:
        for def_name in default_object_names:
            if obj.startswith(def_name):
                offending_objects.append(obj)
            elif def_name in obj:
                possible_offenders.append(obj)
    
    # Manage Strings
    if len(possible_offenders) == 1:
        patch_message_warning = str(len(possible_offenders)) + ' object contains a string extremelly similar to the default names.\n(Ignore this warning if the name describes your object properly)'
    else:
        patch_message_warning = str(len(possible_offenders)) + ' objects contain a string extremelly similar to the default names.\n(Ignore this warning if the name describes your object properly)'
    
    if len(offending_objects) == 1:
        patch_message_error = str(len(offending_objects)) + ' object was not named properly. \nPlease rename your objects descriptively.'
    else:
        patch_message_error = str(len(offending_objects)) + ' objects were not named properly. \nPlease rename your objects descriptively.'
    
    # Manage Buttons
    if len(possible_offenders) != 0 and len(offending_objects) == 0:
        cmds.button("status_" + item_id, e=True, bgc=warning_color, l= '', c=lambda args: warning_default_object_names()) 
        issues_found = 0
    elif len(offending_objects) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message('No unnamed objects were found, well done!')) 
        issues_found = 0
    else: 
        cmds.button("status_" + item_id, e=True, bgc=error_color, l= '?', c=lambda args: warning_default_object_names())
        issues_found = len(offending_objects)
    
    # Manage Message
    patch_message = ''
    cancel_message = 'Ignore Issue'
            
    if len(possible_offenders) != 0 and len(offending_objects) == 0:
        cmds.text("output_" + item_id, e=True, l='[ ' + str(len(possible_offenders)) + ' ]' )
        patch_message = patch_message_warning
        cancel_message = 'Ignore Warning'
    elif len(possible_offenders) == 0:
        cmds.text("output_" + item_id, e=True, l=str(len(offending_objects)))
        patch_message = patch_message_error
    else:
        cmds.text("output_" + item_id, e=True, l=str(len(offending_objects)) + ' + [ ' + str(len(possible_offenders)) + ' ]' )
        patch_message = patch_message_error + '\n\n' + patch_message_warning
        return_message = patch_message_error + '\n' + patch_message_warning
        
    # Patch Function ----------------------
    def warning_default_object_names():
        user_input = cmds.confirmDialog(
                    title=item_name,
                    message= patch_message,
                    button=['OK', cancel_message],
                    defaultButton='OK',
                    cancelButton='Ignore Issue',
                    dismissString='Ignore Issue', 
                    icon="warning")

        if user_input == 'Ignore Warning':
            cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: warning_default_object_names()) 
        else:
            cmds.button("status_" + item_id, e=True, l= '')
    
    # Return string for report ------------
    issue_string = "issues"
    if issues_found == 1:
        issue_string = "issue"
    if issues_found > 0 or len(possible_offenders) > 0:
        string_status = str(issues_found) + ' ' + issue_string + ' found.\n'
        for obj in offending_objects: 
            string_status = string_status + '"' + obj +  '" was not named properly. Please rename your object descriptively.\n'
        if len(offending_objects) != 0 and len(possible_offenders) == 0:
            string_status = string_status[:-1]
        
        for obj in possible_offenders: 
            string_status = string_status + '"' + obj +  '"  contains a string extremelly similar to the default names.\n'
        if len(possible_offenders) != 0:
            string_status = string_status[:-1]
    else: 
        string_status = str(issues_found) + ' issues found. No unnamed objects were found, well done!'
    return '\n*** ' + item_name + " ***\n" + string_status

# Item 10 - Objects Assigned to Default Material (UPDATED) =========================================================================
def check_objects_assigned_to_default_material():
    item_name = checklist_items.get(10)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_value = checklist_items.get(10)[1]
    
    # Check both lambert1 and standardSurface1 (Maya 2024+ default)
    lambert1_objects = cmds.sets("initialShadingGroup", q=True) or []
    
    # Check if standardSurface1 exists and get its shading group
    standardsurface_objects = []
    if cmds.objExists("standardSurface1"):
        # Find shading group connected to standardSurface1
        shading_groups = cmds.listConnections("standardSurface1", type="shadingEngine") or []
        for sg in shading_groups:
            objects_in_sg = cmds.sets(sg, q=True) or []
            standardsurface_objects.extend(objects_in_sg)
    
    # Combine both lists and remove duplicates
    all_default_objects = list(set(lambert1_objects + standardsurface_objects))
    
    # Check if no geometry exists - show green instead of N/A
    all_geo = cmds.ls(geometry=True)
    if len(all_geo) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('No geometry objects found in scene.'))
        cmds.text("output_" + item_id, e=True, l="0")
        return '\n*** ' + item_name + " ***\n" + '0 issues found. No geometry objects in scene.'
    
    if len(all_default_objects) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message('No objects were assigned to default materials.')) 
        issues_found = 0
    else: 
        cmds.button("status_" + item_id, e=True, bgc=error_color, l= '?', c=lambda args: warning_objects_assigned_to_default_material())
        issues_found = len(all_default_objects)
        
    cmds.text("output_" + item_id, e=True, l=len(all_default_objects) )
    
    if len(all_default_objects) == 1:
        patch_message = str(len(all_default_objects)) + ' object is assigned to default material(s). \nMake sure no objects are assigned to lambert1 or standardSurface1.\n\n(Too see a list of objects, generate a full report)'
    else:
        patch_message = str(len(all_default_objects)) + ' objects are assigned to default material(s). \nMake sure no objects are assigned to lambert1 or standardSurface1.\n\n(Too see a list of objects, generate a full report)'
    
    # Patch Function ----------------------
    def warning_objects_assigned_to_default_material():
        user_input = cmds.confirmDialog(
                    title=item_name,
                    message= patch_message,
                    button=['OK', 'Ignore Issue'],
                    defaultButton='OK',
                    cancelButton='Ignore Issue',
                    dismissString='Ignore Issue', 
                    icon="warning")

        if user_input == '':
            pass
        else:
            cmds.button("status_" + item_id, e=True, l= '')
    
    # Return string for report ------------
    issue_string = "issues"
    if issues_found == 1:
        issue_string = "issue"
    if issues_found > 0:
        string_status = str(issues_found) + ' ' + issue_string + ' found.\n'
        for obj in all_default_objects: 
            string_status = string_status + '"' + obj +  '"  is assigned to default material. It should be assigned to another shader.\n'
        string_status = string_status[:-1]
    else: 
        string_status = str(issues_found) + ' issues found. No objects are assigned to default materials.'
    return '\n*** ' + item_name + " ***\n" + string_status

# Item 11 - Ngons =========================================================================
def check_ngons():
    item_name = checklist_items.get(11)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_value = checklist_items.get(11)[1]

    # Check if polygon objects exist first - show green instead of N/A
    all_meshes = cmds.ls(type="mesh")
    if len(all_meshes) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('No polygon objects found in scene.'))
        cmds.text("output_" + item_id, e=True, l="0")
        return '\n*** ' + item_name + " ***\n" + '0 issues found. No polygon objects in scene.'

    ngon_mel_command = 'string $ngons[] = `polyCleanupArgList 3 { "1","2","1","0","1","0","0","0","0","1e-005","0","1e-005","0","1e-005","0","-1","0" }`;'
    ngons_list = mel.eval(ngon_mel_command)
    cmds.select(clear=True)
    
    print('') # Clear Any Warnings

    if len(ngons_list) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message('No ngons were found in your scene. Good job!')) 
        issues_found = 0
    else: 
        cmds.button("status_" + item_id, e=True, bgc=error_color, l= '?', c=lambda args: warning_ngons())
        issues_found = len(ngons_list)
        
    cmds.text("output_" + item_id, e=True, l=len(ngons_list) )
    
    if len(ngons_list) == 1:
        patch_message = str(len(ngons_list)) + ' ngon found in your scene. \nMake sure no faces have more than 4 sides.\n\n(Too see a list of objects, generate a full report)'
    else:
        patch_message = str(len(ngons_list)) + ' ngons found in your scene. \nMake sure no faces have more than 4 sides.\n\n(Too see a list of objects, generate a full report)'
    
    # Patch Function ----------------------
    def warning_ngons():
        user_input = cmds.confirmDialog(
                    title=item_name,
                    message= patch_message,
                    button=['OK', 'Select Ngons', 'Ignore Issue' ],
                    defaultButton='OK',
                    cancelButton='Ignore Issue',
                    dismissString='Ignore Issue', 
                    icon="warning")

        if user_input == 'Select Ngons':
            ngons_list = mel.eval(ngon_mel_command)
        else:
            cmds.button("status_" + item_id, e=True, l= '')
    
    # Return string for report ------------
    issue_string = "issues"
    if issues_found == 1:
        issue_string = "issue"
    if issues_found > 0:
        string_status = str(issues_found) + ' ' + issue_string + ' found.\n'
        for obj in ngons_list: 
            string_status = string_status + '"' + obj +  '"  is an ngon (face with more than 4 sides).\n'
        string_status = string_status[:-1]
    else: 
        string_status = str(issues_found) + ' issues found. No ngons were found in your scene.'
    return '\n*** ' + item_name + " ***\n" + string_status

# Item 12 - Non-manifold Geometry =========================================================================
def check_non_manifold_geometry():
    item_name = checklist_items.get(12)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_value = checklist_items.get(12)[1]
    
    nonmanifold_geo = []
    nonmanifold_verts = []
    
    all_geo = cmds.ls(type='mesh', long=True)
   
    # Check if no geometry exists - show green instead of N/A
    if len(all_geo) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('No polygon objects found in scene.'))
        cmds.text("output_" + item_id, e=True, l="0")
        return '\n*** ' + item_name + " ***\n" + '0 issues found. No polygon objects in scene.'
   
    for geo in all_geo:
        obj_non_manifold_verts = cmds.polyInfo(geo, nmv=True) or []
        if len(obj_non_manifold_verts) > 0:
            nonmanifold_geo.append(geo)
            nonmanifold_verts.append(obj_non_manifold_verts)

    if len(nonmanifold_geo) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message('No objects with non-manifold geometry in your scene. Well Done!')) 
        issues_found = 0
    else: 
        cmds.button("status_" + item_id, e=True, bgc=error_color, l= '?', c=lambda args: warning_non_manifold_geometry())
        issues_found = len(nonmanifold_geo)
        
    cmds.text("output_" + item_id, e=True, l=len(nonmanifold_geo) )
    
    if len(nonmanifold_geo) == 1:
        patch_message = str(len(nonmanifold_geo)) + ' object with non-manifold geometry was found in your scene. \n\n(Too see a list of objects, generate a full report)'
    else:
        patch_message = str(len(nonmanifold_geo)) + ' objects with non-manifold geometry were found in your scene. \n\n(Too see a list of objects, generate a full report)'
    
    # Patch Function ----------------------
    def warning_non_manifold_geometry():
        user_input = cmds.confirmDialog(
                    title=item_name,
                    message= patch_message,
                    button=['OK', 'Select Non-manifold Vertices', 'Ignore Issue' ],
                    defaultButton='OK',
                    cancelButton='Ignore Issue',
                    dismissString='Ignore Issue', 
                    icon="warning")
                    
        
        if user_input == 'Select Non-manifold Vertices':
            cmds.select(clear=True)
            for verts in nonmanifold_verts:
                    cmds.select(verts, add=True)
        else:
            cmds.button("status_" + item_id, e=True, l= '')
    
    # Return string for report ------------
    issue_string = "issues"
    if issues_found == 1:
        issue_string = "issue"
    if issues_found > 0:
        string_status = str(issues_found) + ' ' + issue_string + ' found.\n'
        for obj in nonmanifold_geo: 
            string_status = string_status + '"' + get_short_name(obj) +  '"  has non-manifold geometry.\n'
        string_status = string_status[:-1]
    else: 
        string_status = str(issues_found) + ' issues found. No non-manifold geometry found in your scene.'
    return '\n*** ' + item_name + " ***\n" + string_status

# Item 13 - Frozen Transforms =========================================================================
def check_frozen_transforms():
    item_name = checklist_items.get(13)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_value = checklist_items.get(13)[1]
    
    objects_no_frozen_transforms = []
    
    all_transforms = cmds.ls(type='transform')
    
    # Check if no transforms exist - show green instead of N/A
    if len(all_transforms) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('No transform objects found in scene.'))
        cmds.text("output_" + item_id, e=True, l="0")
        return '\n*** ' + item_name + " ***\n" + '0 issues found. No transform objects in scene.'
        
    for transform in all_transforms:
        children = cmds.listRelatives(transform, c=True, pa=True) or []
        for child in children:
            object_type = cmds.objectType(child)
            if object_type == 'mesh' or object_type == 'nurbsCurve':
                if cmds.getAttr(transform + ".rotateX") != 0 or cmds.getAttr(transform + ".rotateY") != 0 or cmds.getAttr(transform + ".rotateZ") != 0:
                    if len(cmds.listConnections(transform + ".rotateX") or []) == 0 and len(cmds.listConnections(transform + ".rotateY") or []) == 0 and len(cmds.listConnections(transform + ".rotateZ") or []) == 0 and len(cmds.listConnections(transform + ".rotate") or []) == 0:
                        objects_no_frozen_transforms.append(transform)
                       
    if len(objects_no_frozen_transforms) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message('All transforms appear to be frozen.')) 
        issues_found = 0
    else: 
        cmds.button("status_" + item_id, e=True, bgc=warning_color, l= '?', c=lambda args: warning_frozen_transforms())
        issues_found = len(objects_no_frozen_transforms)
        
    cmds.text("output_" + item_id, e=True, l=len(objects_no_frozen_transforms) )
    
    if len(objects_no_frozen_transforms) == 1:
        patch_message = str(len(objects_no_frozen_transforms)) + ' object has un-frozen transformations. \n\n(Too see a list of objects, generate a full report)'
    else:
        patch_message = str(len(objects_no_frozen_transforms)) + ' objects have un-frozen transformations. \n\n(Too see a list of objects, generate a full report)'
    
    # Patch Function ----------------------
    def warning_frozen_transforms():
        user_input = cmds.confirmDialog(
                    title=item_name,
                    message= patch_message,
                    button=['OK', 'Select Objects with un-frozen transformations', 'Ignore Warning' ],
                    defaultButton='OK',
                    cancelButton='Ignore Warning',
                    dismissString='Ignore Warning', 
                    icon="warning")
                    
        if user_input == 'Select Objects with un-frozen transformations':
            cmds.select(objects_no_frozen_transforms)
        elif user_input == 'Ignore Warning':
            cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '')
        else:
            cmds.button("status_" + item_id, e=True, l= '')
    
    # Return string for report ------------
    issue_string = "issues"
    if issues_found == 1:
        issue_string = "issue"
    if issues_found > 0:
        string_status = str(issues_found) + ' ' + issue_string + ' found.\n'
        for obj in objects_no_frozen_transforms: 
            string_status = string_status + '"' + obj +  '" has un-frozen transformations.\n'
        string_status = string_status[:-1]
    else: 
        string_status = str(issues_found) + ' issues found. No objects have un-frozen transformations.'
    return '\n*** ' + item_name + " ***\n" + string_status

# Item 14 - Animated Visibility (WITH TURNTABLE EXCEPTION) - CONTINUED
def check_animated_visibility():
    item_name = checklist_items.get(14)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_value = checklist_items.get(14)[1]
    
    objects_animated_visibility = []
    objects_hidden = []
    turntable_objects = []
    
    all_transforms = cmds.ls(type='transform')
    
    # Check if no transforms exist - show green instead of N/A
    if len(all_transforms) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('No transform objects found in scene.'))
        cmds.text("output_" + item_id, e=True, l="0")
        return '\n*** ' + item_name + " ***\n" + '0 issues found. No transform objects in scene.'
    
    for transform in all_transforms:
        attributes = cmds.listAttr(transform)
        not_outliner_hidden = False
        if 'hiddenInOutliner' in attributes:
            outliner_hidden = cmds.getAttr(transform + ".hiddenInOutliner")

        if 'visibility' in attributes and not outliner_hidden:
            if cmds.getAttr(transform + ".visibility") == 0:
                children = cmds.listRelatives(transform, s=True, pa=True) or []
                if len(children) != 0:
                    if cmds.nodeType(children[0]) != "camera":
                        objects_hidden.append(transform)
        input_nodes = cmds.listConnections(transform + ".visibility", destination=False, source=True) or []
        for node in input_nodes:
            if 'animCurve' in cmds.nodeType(node):
                # Check if this is a turntable object
                transform_lower = transform.lower()
                if 'turntable' in transform_lower or 'turn_table' in transform_lower:
                    turntable_objects.append(transform)
                else:
                    objects_animated_visibility.append(transform)
    
    # Special handling for turntable exception
    if len(turntable_objects) == 1 and len(objects_animated_visibility) == 0:
        # Only one turntable object with animated visibility - show warning instead of error
        cmds.button("status_" + item_id, e=True, bgc=warning_color, l= '', c=lambda args: warning_animated_visibility())
        issues_found = 0
        turntable_warning = True
    else:
        turntable_warning = False
        if len(turntable_objects) > 0:
            # More than one turntable or other animated objects - treat as error
            objects_animated_visibility.extend(turntable_objects)
    
    # Manage Strings
    cancel_message = 'Ignore Issue'
    buttons_to_add = []
    
    if len(objects_hidden) == 1:
        patch_message_warning = str(len(objects_hidden)) + ' object is hidden.\n'
    else:
        patch_message_warning = str(len(objects_hidden)) + ' objects are hidden.\n'
    
    if len(objects_animated_visibility) == 1:
        patch_message_error = str(len(objects_animated_visibility)) + ' object with animated visibility.\n'
    else:
        patch_message_error = str(len(objects_animated_visibility)) + ' objects with animated visibility.\n'
    
    # Add turntable message if applicable
    if turntable_warning:
        patch_message_error = 'Single turntable object detected with animated visibility.\n'
        
    # Manage Message
    patch_message = ''
            
    if len(objects_hidden) != 0 and len(objects_animated_visibility) == 0 and not turntable_warning:
        cmds.text("output_" + item_id, e=True, l='[ ' + str(len(objects_hidden)) + ' ]' )
        patch_message = patch_message_warning
        cancel_message = 'Ignore Warning'
        buttons_to_add.append('Select Hidden Objects')
    elif len(objects_hidden) == 0 and not turntable_warning:
        cmds.text("output_" + item_id, e=True, l=str(len(objects_animated_visibility)))
        patch_message = patch_message_error
        buttons_to_add.append('Select Objects With Animated Visibility')
    elif turntable_warning:
        cmds.text("output_" + item_id, e=True, l='1 (turntable)')
        patch_message = patch_message_error
        cancel_message = 'Ignore Warning'
    else:
        cmds.text("output_" + item_id, e=True, l=str(len(objects_animated_visibility)) + ' + [ ' + str(len(objects_hidden)) + ' ]' )
        patch_message = patch_message_error + '\n\n' + patch_message_warning
        buttons_to_add.append('Select Hidden Objects')
        buttons_to_add.append('Select Objects With Animated Visibility')
    
    assembled_message = ['OK']
    assembled_message.extend(buttons_to_add)
    assembled_message.append(cancel_message)
    
    # Manage State
    if len(objects_hidden) != 0 and len(objects_animated_visibility) == 0 and not turntable_warning:
        cmds.button("status_" + item_id, e=True, bgc=warning_color, l= '', c=lambda args: warning_animated_visibility()) 
        issues_found = 0
    elif len(objects_animated_visibility) == 0 and not turntable_warning:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message('No objects with animated visibility or hidden.')) 
        issues_found = 0
    else: 
        if not turntable_warning:
            cmds.button("status_" + item_id, e=True, bgc=error_color, l= '?', c=lambda args: warning_animated_visibility())
            issues_found = len(objects_animated_visibility)
        else:
            issues_found = 0
        
    # Patch Function ----------------------
    def warning_animated_visibility():
        user_input = cmds.confirmDialog(
                    title= item_name,
                    message= patch_message,
                    button= assembled_message,
                    defaultButton='OK',
                    cancelButton='Ignore Issue',
                    dismissString='Ignore Issue', 
                    icon="warning")
                    
        if user_input == 'Select Objects With Animated Visibility':
            cmds.select(objects_animated_visibility)
        elif user_input == 'Select Hidden Objects':
            cmds.select(objects_hidden)
        elif user_input == 'Ignore Warning':
            cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '')
        else:
            cmds.button("status_" + item_id, e=True, l= '')
        
    # Return string for report ------------
    issue_string = "issues"
    if issues_found == 1:
        issue_string = "issue"
    if issues_found > 0 or len(objects_hidden) > 0 or turntable_warning:
        string_status = str(issues_found) + ' ' + issue_string + ' found.\n'
        for obj in objects_animated_visibility: 
            string_status = string_status + '"' + obj +  '" has animated visibility.\n'
        for obj in turntable_objects:
            string_status = string_status + '"' + obj +  '" is a turntable object with animated visibility (warning only).\n'
        if len(objects_animated_visibility) != 0 and len(objects_hidden) == 0:
            string_status = string_status[:-1]
        
        for obj in objects_hidden: 
            string_status = string_status + '"' + obj +  '" is hidden.\n'
        if len(objects_hidden) != 0:
            string_status = string_status[:-1]
    else: 
        string_status = str(issues_found) + ' issues found. No objects with animated visibility found.'
    return '\n*** ' + item_name + " ***\n" + string_status

# Item 15 - Non Deformer History =========================================================================
def check_non_deformer_history():
    item_name = checklist_items.get(15)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_value = checklist_items.get(15)[1]
    
    objects_non_deformer_history = []
    possible_objects_non_deformer_history = []

    objects_to_check = []
    objects_to_check.extend(cmds.ls(typ='nurbsSurface') or [])
    objects_to_check.extend(cmds.ls(typ='mesh') or [])
    objects_to_check.extend(cmds.ls(typ='subdiv') or [])
    objects_to_check.extend(cmds.ls(typ='nurbsCurve') or [])
    
    # Check if no objects exist - show green instead of N/A
    if len(objects_to_check) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('No geometry objects found in scene.'))
        cmds.text("output_" + item_id, e=True, l="0")
        return '\n*** ' + item_name + " ***\n" + '0 issues found. No geometry objects in scene.'
    
    not_history_nodes = ['tweak', 'expression', 'unitConversion', 'time', 'objectSet', 'reference', 'polyTweak', 'blendShape', 'groupId', \
    'renderLayer', 'renderLayerManager', 'shadingEngine', 'displayLayer', 'skinCluster', 'groupParts', 'mentalraySubdivApprox', 'proximityWrap',\
    'cluster', 'cMuscleSystem', 'timeToUnitConversion', 'deltaMush', 'tension', 'wire', 'wrinkle', 'softMod', 'jiggle', 'diskCache', 'leastSquaresModifier']
    
    possible_not_history_nodes = ['nonLinear','ffd', 'curveWarp', 'wrap', 'shrinkWrap', 'sculpt', 'textureDeformer']
    
    # Find Offenders
    for obj in objects_to_check:
        history = cmds.listHistory(obj, pdo=1) or []
        for node in history:
            if cmds.nodeType(node) not in not_history_nodes and cmds.nodeType(node) not in possible_not_history_nodes:
                if obj not in objects_non_deformer_history:
                    objects_non_deformer_history.append(obj)
            if cmds.nodeType(node) in possible_not_history_nodes:
                if obj not in possible_objects_non_deformer_history:
                    possible_objects_non_deformer_history.append(obj)

    # Manage Strings
    cancel_message = 'Ignore Issue'
    buttons_to_add = []
    
    if len(possible_objects_non_deformer_history) == 1:
        patch_message_warning = str(len(possible_objects_non_deformer_history)) + ' object contains deformers often used for modeling.\n'
    else:
        patch_message_warning = str(len(possible_objects_non_deformer_history)) + ' objects contain deformers often used for modeling.\n'
    
    if len(objects_non_deformer_history) == 1:
        patch_message_error = str(len(objects_non_deformer_history)) + ' object contains non-deformer history.\n'
    else:
        patch_message_error = str(len(objects_non_deformer_history)) + ' objects contain non-deformer history.\n'
        
    # Manage Message
    patch_message = ''
            
    if len(possible_objects_non_deformer_history) != 0 and len(objects_non_deformer_history) == 0:
        cmds.text("output_" + item_id, e=True, l='[ ' + str(len(possible_objects_non_deformer_history)) + ' ]' )
        patch_message = patch_message_warning
        cancel_message = 'Ignore Warning'
        buttons_to_add.append('Select Objects With Suspicious Deformers')
    elif len(possible_objects_non_deformer_history) == 0:
        cmds.text("output_" + item_id, e=True, l=str(len(objects_non_deformer_history)))
        patch_message = patch_message_error
        buttons_to_add.append('Select Objects With Non-deformer History')
    else:
        cmds.text("output_" + item_id, e=True, l=str(len(objects_non_deformer_history)) + ' + [ ' + str(len(possible_objects_non_deformer_history)) + ' ]' )
        patch_message = patch_message_error + '\n\n' + patch_message_warning
        buttons_to_add.append('Select Objects With Suspicious Deformers')
        buttons_to_add.append('Select Objects With Non-deformer History')
    
    assembled_message = ['OK']
    assembled_message.extend(buttons_to_add)
    assembled_message.append(cancel_message)
    
    # Manage State
    if len(possible_objects_non_deformer_history) != 0 and len(objects_non_deformer_history) == 0:
        cmds.button("status_" + item_id, e=True, bgc=warning_color, l= '', c=lambda args: warning_non_deformer_history()) 
        issues_found = 0
    elif len(objects_non_deformer_history) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message('No objects with non-deformer history were found.')) 
        issues_found = 0
    else: 
        cmds.button("status_" + item_id, e=True, bgc=error_color, l= '?', c=lambda args: warning_non_deformer_history())
        issues_found = len(objects_non_deformer_history)

    # Patch Function ----------------------
    def warning_non_deformer_history():
        user_input = cmds.confirmDialog(
                    title= item_name,
                    message= patch_message,
                    button= assembled_message,
                    defaultButton='OK',
                    cancelButton='Ignore Issue',
                    dismissString='Ignore Issue', 
                    icon="warning")
                    
        if user_input == 'Select Objects With Non-deformer History':
            cmds.select(objects_non_deformer_history)
        elif user_input == 'Select Objects With Suspicious Deformers':
            cmds.select(possible_objects_non_deformer_history)
        elif user_input == 'Ignore Warning':
            cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '')
        else:
            cmds.button("status_" + item_id, e=True, l= '')
    
    # Return string for report ------------
    issue_string = "issues"
    if issues_found == 1:
        issue_string = "issue"
    if issues_found > 0 or len(possible_objects_non_deformer_history) > 0:
        string_status = str(issues_found) + ' ' + issue_string + ' found.\n'
        for obj in objects_non_deformer_history: 
            string_status = string_status + '"' + obj +  '" contains non-deformer history.\n'
        if len(objects_non_deformer_history) != 0 and len(possible_objects_non_deformer_history) == 0:
            string_status = string_status[:-1]
        
        for obj in possible_objects_non_deformer_history: 
            string_status = string_status + '"' + obj +  '" contains deformers often used for modeling.\n'
        if len(possible_objects_non_deformer_history) != 0:
            string_status = string_status[:-1]
    else: 
        string_status = str(issues_found) + ' issues found. No objects with non-deformer history!'
    return '\n*** ' + item_name + " ***\n" + string_status

# Item 16 - Textures Color Space =========================================================================
def check_textures_color_space():
    item_name = checklist_items.get(16)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_value = checklist_items.get(16)[1]
    
    objects_wrong_color_space = []
    possible_objects_wrong_color_space = []
    
    # These types return an error instead of warning
    error_types = ['RedshiftMaterial','RedshiftArchitectural', 'RedshiftDisplacement', 'RedshiftColorCorrection', 'RedshiftBumpMap', 'RedshiftSkin', 'RedshiftSubSurfaceScatter',\
    'aiStandardSurface', 'aiFlat', 'aiCarPaint', 'aiBump2d', '', 'aiToon', 'aiBump3d', 'aiAmbientOcclusion', 'displacementShader']
        
    # If type starts with any of these strings it will be tested
    check_types = ['Redshift', 'ai', 'lambert', 'blinn', 'phong', 'useBackground', 'checker', 'ramp', 'volumeShader', 'displacementShader', 'anisotropic', 'bump2d'] 
    
    # These types and connections are allowed to be float3 even though it's raw
    float3_to_float_exceptions = {'RedshiftBumpMap': 'input',
                                  'RedshiftDisplacement':'texMap'}

    # Count Textures
    all_file_nodes = cmds.ls(type="file")
    
    # Check if no file nodes exist - show green instead of N/A
    if len(all_file_nodes) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('No file texture nodes found in scene.'))
        cmds.text("output_" + item_id, e=True, l="0")
        return '\n*** ' + item_name + " ***\n" + '0 issues found. No file texture nodes in scene.'
    
    for file in all_file_nodes:
        color_space = cmds.getAttr(file + '.colorSpace')
        
        has_suspicious_connection = False
        has_error_node_type = False
        
        intput_node_connections = cmds.listConnections(file, destination=True, source=False, plugs=True) or []
        
        suspicious_connections = []
        possible_suspicious_connections = []
        
        if color_space.lower() == 'Raw'.lower():
            for in_con in intput_node_connections:
                node = in_con.split('.')[0]
                node_in_con = in_con.split('.')[1]
                
                node_type = cmds.objectType(node)
                
                if node_type in error_types:
                    has_error_node_type = True
                
                should_be_checked = False
                for types in check_types:
                    if node_type.startswith(types):
                        should_be_checked = True
                
                if should_be_checked:
                    data_type = cmds.getAttr(in_con, type=True)
                    if data_type == 'float3' and (node_type in float3_to_float_exceptions and node_in_con in float3_to_float_exceptions.values()) == False:
                            has_suspicious_connection = True
                            suspicious_connections.append(in_con)
        
        if color_space.lower() == 'sRGB'.lower():
            for in_con in intput_node_connections:
                node = in_con.split('.')[0]
                node_in_con = in_con.split('.')[1]
                
                node_type = cmds.objectType(node)
                
                if node_type in error_types:
                    has_error_node_type = True
                
                should_be_checked = False
                for types in check_types:
                    if node_type.startswith(types):
                        should_be_checked = True
                
                if should_be_checked:
                    data_type = cmds.getAttr(in_con, type=True)
                    if data_type == 'float':
                            has_suspicious_connection = True
                            suspicious_connections.append(in_con)
                    if node_type in float3_to_float_exceptions and node_in_con in float3_to_float_exceptions.values():
                            has_suspicious_connection = True
                            suspicious_connections.append(in_con)
                  
        if has_suspicious_connection:
            if has_error_node_type:
                objects_wrong_color_space.append([file,suspicious_connections])
            else:
                possible_objects_wrong_color_space.append([file,suspicious_connections])
           
    
    # Manage Strings
    cancel_message = 'Ignore Issue'
    buttons_to_add = []
    bottom_message = '\n\n (For a complete list, generate a full report)'
    
    if len(possible_objects_wrong_color_space) == 1:
        patch_message_warning = str(len(possible_objects_wrong_color_space)) + ' file node is using a color space that might not be appropriate for its connection.\n'
    else:
        patch_message_warning = str(len(possible_objects_wrong_color_space)) + ' file nodes are using a color space that might not be appropriate for its connection.\n'
    
    if len(objects_wrong_color_space) == 1:
        patch_message_error = str(len(objects_wrong_color_space)) + ' file node is using a color space that is not appropriate for its connection.\n'
    else:
        patch_message_error = str(len(objects_wrong_color_space)) + ' file nodes are using a color space that is not appropriate for its connection.\n'
        
    
    # Manage Messages
    patch_message = ''
    might_have_issues_message = 'Select File Nodes With Possible Issues'
    has_issues_message = 'Select File Nodes With Issues'
            
    if len(possible_objects_wrong_color_space) != 0 and len(objects_wrong_color_space) == 0:
        cmds.text("output_" + item_id, e=True, l='[ ' + str(len(possible_objects_wrong_color_space)) + ' ]' )
        patch_message = patch_message_warning
        cancel_message = 'Ignore Warning'
        buttons_to_add.append(might_have_issues_message)
    elif len(possible_objects_wrong_color_space) == 0:
        cmds.text("output_" + item_id, e=True, l=str(len(objects_wrong_color_space)))
        patch_message = patch_message_error
        buttons_to_add.append(has_issues_message)
    else:
        cmds.text("output_" + item_id, e=True, l=str(len(objects_wrong_color_space)) + ' + [ ' + str(len(possible_objects_wrong_color_space)) + ' ]' )
        patch_message = patch_message_error + '\n\n' + patch_message_warning
        buttons_to_add.append(might_have_issues_message)
        buttons_to_add.append(has_issues_message)
    
    assembled_message = ['OK']
    assembled_message.extend(buttons_to_add)
    assembled_message.append(cancel_message)
    
    # Manage State
    if len(possible_objects_wrong_color_space) != 0 and len(objects_wrong_color_space) == 0:
        cmds.button("status_" + item_id, e=True, bgc=warning_color, l= '', c=lambda args: warning_textures_color_space()) 
        issues_found = 0
    elif len(objects_wrong_color_space) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '', c=lambda args: print_message('No color space issues were found.')) 
        issues_found = 0
    else: 
        cmds.button("status_" + item_id, e=True, bgc=error_color, l= '?', c=lambda args: warning_textures_color_space())
        issues_found = len(objects_wrong_color_space)

    # Patch Function ----------------------
    def warning_textures_color_space():
        user_input = cmds.confirmDialog(
                    title= item_name,
                    message= patch_message + bottom_message,
                    button= assembled_message,
                    defaultButton='OK',
                    cancelButton='Ignore Issue',
                    dismissString='Ignore Issue', 
                    icon="warning")
                    
        if user_input == has_issues_message:
            cmds.select(clear=True)
            for obj in objects_wrong_color_space:
                cmds.select(obj[0], add=True)
        elif user_input == might_have_issues_message:
            cmds.select(clear=True)
            for obj in possible_objects_wrong_color_space:
                cmds.select(obj[0], add=True)
        elif user_input == 'Ignore Warning':
            cmds.button("status_" + item_id, e=True, bgc=pass_color, l= '')
        else:
            cmds.button("status_" + item_id, e=True, l= '')
    
    # Return string for report ------------
    issue_string = "issues"
    if issues_found == 1:
        issue_string = "issue"
    if issues_found > 0 or len(possible_objects_wrong_color_space) > 0:
        string_status = str(issues_found) + ' ' + issue_string + ' found.\n'
        for obj in objects_wrong_color_space: 
            string_status = string_status + '"' + obj[0] +  '" is using a color space (' + cmds.getAttr(obj[0] + '.colorSpace') + ') that is not appropriate for its connection.\n' 
            for connection in obj[1]:
                string_status = string_status + '   "' + connection + '" triggered this error.\n'
        if len(objects_wrong_color_space) != 0 and len(possible_objects_wrong_color_space) == 0:
            string_status = string_status[:-1]
        
        for obj in possible_objects_wrong_color_space: 
            string_status = string_status + '"' + obj[0] +  '" might be using a color space (' + cmds.getAttr(obj[0] + '.colorSpace') + ') that is not appropriate for its connection.\n'
            for connection in obj[1]:
                string_status = string_status + '   "' + connection + '" triggered this warning.\n'
        if len(possible_objects_wrong_color_space) != 0:
            string_status = string_status[:-1]
    else: 
        string_status = str(issues_found) + ' issues found. No color space issues were found!'
    return '\n*** ' + item_name + " ***\n" + string_status

# Item 17 - AI Shadow Casting Lights (CORRECTED - IGNORES SKYDOME SHADOW CASTING) =========================================================================
def check_ai_shadow_casting_lights():
    item_name = checklist_items.get(17)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    max_shadow_casters = checklist_items.get(17)[1][0]  # 1 shadow casting light
    min_skydome = checklist_items.get(17)[1][1]  # 1 skydome light  
    max_total_lights = checklist_items.get(17)[1][2]  # 4 total lights max
    
    # Check if Arnold is loaded
    arnold_light_types = ["aiAreaLight", "aiSkyDomeLight", "aiPhotometricLight", "aiLightPortal"]
    maya_light_types = ["directionalLight", "pointLight", "spotLight", "areaLight", "ambientLight", "volumeLight"]
    
    node_types = cmds.ls(nodeTypes=True)
    arnold_loaded = any(light_type in node_types for light_type in arnold_light_types)
    
    if not arnold_loaded:
        cmds.button("status_" + item_id, e=True, bgc=exception_color, l= '', 
                   c=lambda args: print_message('Arnold plugin doesn\'t seem to be loaded.', as_warning=True))
        cmds.text("output_" + item_id, e=True, l='No Arnold')
        return '\n*** ' + item_name + " ***\n" + '0 issues found, but Arnold plugin doesn\'t seem to be loaded.'
    
    # Find all lights in scene
    all_arnold_lights = []
    all_maya_lights = []
    
    for light_type in arnold_light_types:
        lights = cmds.ls(type=light_type) or []
        all_arnold_lights.extend(lights)
    
    for light_type in maya_light_types:
        lights = cmds.ls(type=light_type) or []
        all_maya_lights.extend(lights)
    
    all_lights = all_arnold_lights + all_maya_lights
    
    # Check if no lights exist - show green for empty scenes
    if len(all_lights) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('No lights found in scene.'))
        cmds.text("output_" + item_id, e=True, l="0")
        return '\n*** ' + item_name + " ***\n" + '0 issues found. No lights in scene.'
    
    # Find shadow casting lights and categorize them (EXCLUDING SKYDOME LIGHTS)
    shadow_casting_lights = []  # Non-skydome lights that cast shadows
    key_shadow_casters = []
    non_key_shadow_casters = []
    skydome_count = 0
    
    for light in all_lights:
        light_type = cmds.objectType(light)
        casts_shadows = False
        
        # Count skydome lights but don't include them in shadow casting count
        if light_type == "aiSkyDomeLight":
            skydome_count += 1
            continue  # Skip shadow checking for skydome lights
        
        # Check if non-skydome light is casting shadows
        if light_type in arnold_light_types:
            # Arnold lights use 'aiSamples' or check visibility
            if cmds.attributeQuery('aiSamples', node=light, exists=True):
                ai_samples = cmds.getAttr(light + '.aiSamples')
                if ai_samples > 0:
                    casts_shadows = True
        else:
            # Maya lights use 'useDepthMapShadows' or 'useRayTraceShadows'
            use_depth_shadows = cmds.getAttr(light + '.useDepthMapShadows') if cmds.attributeQuery('useDepthMapShadows', node=light, exists=True) else False
            use_raytrace_shadows = cmds.getAttr(light + '.useRayTraceShadows') if cmds.attributeQuery('useRayTraceShadows', node=light, exists=True) else False
            if use_depth_shadows or use_raytrace_shadows:
                casts_shadows = True
        
        if casts_shadows:
            shadow_casting_lights.append(light)
            
            # Check if light name contains "key" (case insensitive)
            if 'key' in light.lower():
                key_shadow_casters.append(light)
            else:
                non_key_shadow_casters.append(light)
    
    # Determine status based on new logic (ignoring skydome shadow casting)
    total_lights = len(all_lights)
    total_shadow_casters = len(shadow_casting_lights)  # Excludes skydome
    key_count = len(key_shadow_casters)
    
    # Check conditions
    has_exactly_one_shadow_caster = total_shadow_casters == 1
    has_key_shadow_caster = key_count >= 1
    has_skydome = skydome_count >= min_skydome
    within_light_limit = total_lights <= max_total_lights
    
    # Determine final status
    issues_found = 0
    is_warning = False
    
    # ERROR conditions
    if total_shadow_casters == 0:
        cmds.button("status_" + item_id, e=True, bgc=error_color, l='?', 
                   c=lambda args: warning_ai_shadow_casting_lights())
        issues_found = 1
        status_message = "No shadow casting lights found"
    elif total_shadow_casters > 1:
        if key_count > 1:
            # More than 1 key light casting shadows - ERROR
            cmds.button("status_" + item_id, e=True, bgc=error_color, l='?', 
                       c=lambda args: warning_ai_shadow_casting_lights())
            issues_found = 1
            status_message = f"{key_count} key lights casting shadows (max 1)"
        else:
            # More than 1 shadow caster but only 1 or 0 key lights - WARNING
            cmds.button("status_" + item_id, e=True, bgc=warning_color, l='?', 
                       c=lambda args: warning_ai_shadow_casting_lights())
            is_warning = True
            status_message = f"{total_shadow_casters} lights casting shadows (should be 1)"
    elif not has_skydome:
        cmds.button("status_" + item_id, e=True, bgc=error_color, l='?', 
                   c=lambda args: warning_ai_shadow_casting_lights())
        issues_found = 1
        status_message = "No aiSkyDome light found"
    elif has_exactly_one_shadow_caster and not has_key_shadow_caster:
        cmds.button("status_" + item_id, e=True, bgc=error_color, l='?', 
                   c=lambda args: warning_ai_shadow_casting_lights())
        issues_found = 1
        status_message = "Shadow casting light missing 'key' in name"
    elif not within_light_limit:
        # Too many lights total - WARNING
        cmds.button("status_" + item_id, e=True, bgc=warning_color, l='?', 
                   c=lambda args: warning_ai_shadow_casting_lights())
        is_warning = True
        status_message = f"{total_lights} total lights (max {max_total_lights})"
    else:
        # All conditions met - PASS
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message(f'Lighting setup correct: {total_shadow_casters} shadow caster, {skydome_count} skydome, {total_lights} total lights.'))
        status_message = "Lighting setup correct"
    
    cmds.text("output_" + item_id, e=True, l=f"{total_shadow_casters}/{skydome_count}/{total_lights}")
    
    # Patch Function ----------------------
    def warning_ai_shadow_casting_lights():
        message_parts = []
        
        if total_shadow_casters == 0:
            message_parts.append('No shadow casting lights found (excluding skydome).')
        elif total_shadow_casters > 1:
            if key_count > 1:
                message_parts.append(f'ERROR: {key_count} lights with "key" in name are casting shadows (max 1).')
            else:
                message_parts.append(f'WARNING: {total_shadow_casters} lights are casting shadows (should be 1).')
        
        if not has_skydome:
            message_parts.append(f'Need at least {min_skydome} aiSkyDome light, found {skydome_count}.')
        
        if has_exactly_one_shadow_caster and not has_key_shadow_caster:
            message_parts.append('Shadow casting light must have "key" or "Key" in its name.')
        
        if not within_light_limit:
            message_parts.append(f'Too many lights: {total_lights} total (max {max_total_lights}).')
        
        message_parts.append('\nNote: aiSkyDome lights are excluded from shadow casting count.')
        
        patch_message = '\n'.join(message_parts)
        patch_message += '\n\n(Generate full report for complete light list)'
        
        cancel_message = 'Ignore Warning' if is_warning else 'Ignore Issue'
        
        user_input = cmds.confirmDialog(
                    title=item_name,
                    message=patch_message,
                    button=['OK', 'Select All Lights', cancel_message],
                    defaultButton='OK',
                    cancelButton=cancel_message,
                    dismissString=cancel_message, 
                    icon="warning")

        if user_input == 'Select All Lights':
            if all_lights:
                # Select transform nodes of lights
                light_transforms = []
                for light in all_lights:
                    transforms = cmds.listRelatives(light, parent=True) or [light]
                    light_transforms.extend(transforms)
                cmds.select(light_transforms)
        elif user_input == 'Ignore Warning':
            cmds.button("status_" + item_id, e=True, bgc=pass_color, l='')
        else:
            cmds.button("status_" + item_id, e=True, l='')
    
    # Return string for report ------------
    issue_string = "issues" if issues_found != 1 else "issue"
    warning_string = "warnings" if is_warning else ""
    
    if issues_found > 0:
        report_parts = [f'{issues_found} {issue_string} found.']
    elif is_warning:
        report_parts = [f'0 issues found, 1 warning.']
    else:
        report_parts = [f'0 issues found.']
    
    report_parts.append(f'Total lights: {total_lights} (max {max_total_lights})')
    report_parts.append(f'Shadow casting lights: {total_shadow_casters} (should be 1, excludes skydome)')
    report_parts.append(f'Key shadow casters: {key_count}')
    report_parts.append(f'aiSkyDome lights: {skydome_count} (need {min_skydome})')
    
    report_parts.append('\nAll lights in scene:')
    for light in all_lights:
        light_type = cmds.objectType(light)
        
        if light_type == "aiSkyDomeLight":
            # Don't check shadow status for skydome lights
            shadow_status = "skydome (shadows ignored)"
        else:
            shadow_status = "casts shadows" if light in shadow_casting_lights else "no shadows"
            
        key_status = " [KEY]" if light in key_shadow_casters else ""
        report_parts.append(f'  "{light}" ({light_type}) - {shadow_status}{key_status}')
    
    return '\n*** ' + item_name + " ***\n" + '\n'.join(report_parts)

# Item 18 - Camera Aspect Ratio (NEW) =========================================================================
def check_camera_aspect_ratio():
    item_name = checklist_items.get(18)[0]
    item_id = item_name.lower().replace(" ","_").replace("-","_")
    expected_ratios = checklist_items.get(18)[1]  # [1.77, 1.78]
    
    # Get all cameras except default ones
    all_cameras = cmds.ls(type='camera') or []
    default_cameras = ['frontShape', 'perspShape', 'sideShape', 'topShape']
    user_cameras = [cam for cam in all_cameras if cam not in default_cameras]
    
    # Check if no user cameras exist - show green instead of N/A
    if len(user_cameras) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('No user-created cameras found in scene.'))
        cmds.text("output_" + item_id, e=True, l="0")
        return '\n*** ' + item_name + " ***\n" + '0 issues found. No user-created cameras in scene.'
    
    incorrect_cameras = []
    
    for camera in user_cameras:
        # Get camera's film aperture to calculate aspect ratio
        h_aperture = cmds.getAttr(camera + '.horizontalFilmAperture')
        v_aperture = cmds.getAttr(camera + '.verticalFilmAperture')
        
        if v_aperture > 0:  # Avoid division by zero
            aspect_ratio = h_aperture / v_aperture
            # Check if aspect ratio matches expected values (with small tolerance)
            tolerance = 0.01
            ratio_matches = any(abs(aspect_ratio - expected) < tolerance for expected in expected_ratios)
            
            if not ratio_matches:
                incorrect_cameras.append([camera, aspect_ratio])
    
    if len(incorrect_cameras) == 0:
        cmds.button("status_" + item_id, e=True, bgc=pass_color, l='', 
                   c=lambda args: print_message('All user cameras have correct aspect ratios.'))
        issues_found = 0
    else:
        cmds.button("status_" + item_id, e=True, bgc=error_color, l='?', 
                   c=lambda args: warning_camera_aspect_ratio())
        issues_found = len(incorrect_cameras)
    
    cmds.text("output_" + item_id, e=True, l=str(len(incorrect_cameras)))
    
    # Patch Function ----------------------
    def warning_camera_aspect_ratio():
        if len(incorrect_cameras) == 1:
            patch_message = f'1 camera has incorrect aspect ratio.\nExpected: {expected_ratios[0]} or {expected_ratios[1]}\n\n(Generate full report for details)'
        else:
            patch_message = f'{len(incorrect_cameras)} cameras have incorrect aspect ratios.\nExpected: {expected_ratios[0]} or {expected_ratios[1]}\n\n(Generate full report for details)'
        
        user_input = cmds.confirmDialog(
                    title=item_name,
                    message=patch_message,
                    button=['OK', 'Select Cameras', 'Ignore Issue'],
                    defaultButton='OK',
                    cancelButton='Ignore Issue',
                    dismissString='Ignore Issue', 
                    icon="warning")

        if user_input == 'Select Cameras':
            camera_transforms = []
            for camera_info in incorrect_cameras:
                camera_shape = camera_info[0]
                camera_transform = cmds.listRelatives(camera_shape, parent=True)[0]
                camera_transforms.append(camera_transform)
            if camera_transforms:
                cmds.select(camera_transforms)
        elif user_input == 'Ignore Issue':
            cmds.button("status_" + item_id, e=True, l='')
        else:
            cmds.button("status_" + item_id, e=True, l='')
    
    # Return string for report ------------
    issue_string = "issues" if issues_found != 1 else "issue"
    
    if issues_found > 0:
        string_status = f'{issues_found} {issue_string} found.\n'
        for camera_info in incorrect_cameras:
            camera_name = camera_info[0]
            aspect_ratio = camera_info[1]
            string_status += f'"{camera_name}" has aspect ratio {aspect_ratio:.3f} (expected {expected_ratios[0]} or {expected_ratios[1]}).\n'
        string_status = string_status[:-1]  # Remove last newline
    else:
        string_status = f'{issues_found} issues found. All user cameras have correct aspect ratios.'
    
    return '\n*** ' + item_name + " ***\n" + string_status

# Utility Functions ===================================================================
def get_short_name(obj):
    '''
    Get the name of the objects without its path (Maya returns full path if name is not unique)
    '''
    if obj == '':
        return ''
    split_path = obj.split('|')
    if len(split_path) >= 1:
        short_name = split_path[len(split_path)-1]
    return short_name

def print_message(message, as_warning=False, as_heads_up_message=False):
    if as_warning:
        cmds.warning(message)
    elif as_heads_up_message:
        cmds.headsUpMessage(message, verticalOffset=150, time=5.0)
    else:
        print(message)

# Used to Export Full Report:
def export_report_to_txt(list):
    temp_dir = cmds.internalVar(userTmpDir=True)
    txt_file = temp_dir + 'cmi_checklist_report.txt'
    
    f = open(txt_file, 'w')
    
    output_string = script_name + " Full Report v" + script_version + ":\n"
    output_string += "=" * 60 + "\n\n"
    
    for obj in list:
        if obj:  # Only add non-empty reports
            output_string = output_string + obj + "\n\n"
    
    f.write(output_string)
    f.close()

    # Try to open with notepad on Windows
    try:
        notepadCommand = 'exec("notepad ' + txt_file + '");'
        mel.eval(notepadCommand)
    except:
        print("Report saved to: " + txt_file)

# Missing import statement for the script to work properly
import sys

# Build GUI
if __name__ == "__main__":
    build_gui_ats_cmi_modeling_checklist()
