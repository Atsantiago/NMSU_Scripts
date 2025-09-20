"""
CMI Modeling Checklist - Optimized Maya Python Script
A comprehensive checklist tool for validating 3D models in Maya

The UI and a majority of the code used for this script was repourposed 
from a previous script from: 
@Guilherme Trevisan - TrevisanGMW@gmail.com - github.com/TrevisanGMW

Updates and changes by Alexander T. Santiago - github.com/atsantiago
"""

# Standard library imports
import copy
import sys

# Maya imports  
import maya.cmds as cmds
import maya.mel as mel
from maya import OpenMayaUI as omui

# Version imports
from fdma_shelf.utils.version_utils import get_fdma2530_version

# ==============================================================================
# VERSION INFORMATION
# ==============================================================================

# Tool version (independent of package)
__tool_version__ = "2.0.4"

# Package version
__package_version__ = get_fdma2530_version()

# Script information
SCRIPT_NAME = "CMI Modeling Checklist"
SCRIPT_VERSION = __tool_version__
PACKAGE_VERSION = __package_version__
PYTHON_VERSION = sys.version_info.major

# Create comprehensive title for UI with better visual separation
WINDOW_TITLE = f"{SCRIPT_NAME}: {SCRIPT_VERSION}  ——  CMI Tools: {PACKAGE_VERSION}"

# Qt imports with fallback
try:
    from shiboken2 import wrapInstance
    from PySide2.QtGui import QIcon
    from PySide2.QtWidgets import QWidget
except ImportError:
    try:
        from shiboken import wrapInstance
        from PySide.QtGui import QIcon, QWidget
    except ImportError:
        print("Warning: Qt libraries not available for window icons")

# ==============================================================================
# CONSTANTS
# ==============================================================================

# UI Colors
DEFAULT_COLOR = (0.3, 0.3, 0.3)
PASS_COLOR = (0.17, 1.0, 0.17)
WARNING_COLOR = (1.0, 1.0, 0.17)
ERROR_COLOR = (1.0, 0.17, 0.17)
EXCEPTION_COLOR = (0.2, 0.2, 0.2)

# Legacy variable names for compatibility
script_name = SCRIPT_NAME
script_version = SCRIPT_VERSION
python_version = PYTHON_VERSION
def_color = DEFAULT_COLOR
pass_color = PASS_COLOR
warning_color = WARNING_COLOR
error_color = ERROR_COLOR
exception_color = EXCEPTION_COLOR

# Checklist Items - Sequential numbering with new items
CHECKLIST_ITEMS = {
    1: ["Scene Units", "cm"],
    2: ["Render Output Resolution", ["1280", "720"]],
    3: ["Total Texture Count", [40, 50]],
    4: ["File Paths", ["sourceimages"]],
    5: ["Unparented Objects", 0],
    6: ["Total Triangle Count", [180000, 200000]],
    7: ["Total Polygon Count", [90000, 100000]],
    8: ["Total Poly Object Count", [90, 100]],
    9: ["Default Object Names", 0],
    10: ["Objects Assigned to Default Material", 0],
    11: ["Ngons", 0],
    12: ["Non-manifold Geometry", 0],
    13: ["Frozen Transforms", 0],
    14: ["Animated Visibility", 0],
    15: ["Non Deformer History", 0],
    16: ["Textures Color Space", 0],
    17: ["AI Shadow Casting Lights", [1, 1, 4]],
    #18: ["Camera Aspect Ratio", [1.77, 1.78]]
}

# Legacy variable name for compatibility
checklist_items = CHECKLIST_ITEMS

# Store default values for resetting
settings_default_checklist_values = copy.deepcopy(CHECKLIST_ITEMS)

# Checklist Settings
checklist_settings = {
    "is_settings_visible": False,
    "checklist_column_height": 0,
    "checklist_buttons_height": 0,
    "settings_text_fields": []
}

# Default object names for validation
DEFAULT_OBJECT_NAMES = [
    "nurbsSphere", "nurbsCube", "nurbsCylinder", "nurbsCone",
    "nurbsPlane", "nurbsTorus", "nurbsCircle", "nurbsSquare", 
    "pSphere", "pCube", "pCylinder", "pCone", "pPlane", "pTorus",
    "pPrism", "pPyramid", "pPipe", "pHelix", "pSolid", 
    "rsPhysicalLight", "rsIESLight", "rsPortalLight", "aiAreaLight",
    "rsDomeLight", "aiPhotometricLight", "aiLightPortal",
    "ambientLight", "directionalLight", "pointLight", "spotLight",
    "areaLight", "volumeLight"
]


# ==============================================================================
# MAIN GUI FUNCTION
# ==============================================================================

def build_gui_ats_cmi_modeling_checklist():
    """Build the main GUI window with improved layout and resizing."""
    window_name = "build_gui_ats_cmi_modeling_checklist"
    
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name, window=True)

    # Create window with resizing enabled and scroll support
    cmds.window(
        window_name,
        title=WINDOW_TITLE,
        mnb=False,
        mxb=False,
        s=True,
        resizeToFitChildren=True,
        width=420,
        height=810
    )

    # Add scroll layout wrapper
    scroll_layout = cmds.scrollLayout(
        horizontalScrollBarThickness=16,
        verticalScrollBarThickness=16,
        childResizable=True
    )
    
    main_column = cmds.columnLayout(
        adjustableColumn=True,
        parent=scroll_layout
    )
    
    # Title Text - updated column widths
    cmds.rowColumnLayout(
        nc=1,
        cw=[(1, 400)],
        cs=[(1, 10)],
        p=main_column
    )
    cmds.separator(h=14, style='none')
    cmds.rowColumnLayout(
        nc=3,
        cw=[(1, 10), (2, 330), (3, 50)],
        cs=[(1, 10), (2, 0), (3, 0)],
        p=main_column
    )

    cmds.text(" ", bgc=[.4, .4, .4])
    cmds.text(
        script_name,
        bgc=[0.4, 0.4, 0.4],
        fn="boldLabelFont",
        align="left"
    )
    cmds.button(
        l="Help",
        bgc=(0.4, 0.4, 0.4),
        c=lambda x: build_gui_help_ats_cmi_modeling_checklist()
    )
    cmds.separator(h=10, style='none', p=main_column)
    cmds.rowColumnLayout(
        nc=1,
        cw=[(1, 390)],
        cs=[(1, 10)],
        p=main_column
    )
    cmds.separator(h=8)
    cmds.separator(h=5, style='none')
    
    # Checklist Column with increased widths
    checklist_column = cmds.rowColumnLayout(
        nc=3,
        cw=[(1, 220), (2, 40), (3, 110)],
        cs=[(1, 20), (2, 6), (3, 6)],
        p=main_column
    )
    
    # Header
    cmds.text(l="Operation", align="left")
    cmds.text(l='Status', align="left")
    cmds.text(l='Info', align="center")
    cmds.separator(h=5, style='none')
    cmds.separator(h=5, style='none')
    cmds.separator(h=5, style='none')

    # Build Checklist 
    def create_checklist_items(items):
        """Create UI elements for checklist items."""
        for item in sorted(items.keys()):
            item_id = (checklist_items.get(item)[0]
                      .lower()
                      .replace(" ", "_")
                      .replace("-", "_"))
            cmds.text(
                l=checklist_items.get(item)[0] + ': ',
                align="left"
            )
            cmds.button(
                "status_" + item_id,
                l='',
                h=14,
                bgc=def_color
            )
            cmds.text(
                "output_" + item_id,
                l='...',
                align="center"
            )

    create_checklist_items(checklist_items)

    cmds.rowColumnLayout(
        nc=1,
        cw=[(1, 390)],
        cs=[(1, 10)],
        p=main_column
    )
    cmds.separator(h=8, style='none')
    cmds.separator(h=8)
    
    # Checklist Buttons
    checklist_buttons = cmds.rowColumnLayout(
        nc=1,
        cw=[(1, 390)],
        cs=[(1, 10)],
        p=main_column
    )
    cmds.separator(h=10, style='none')
    cmds.button(
        l='Generate Report',
        h=30,
        c=lambda args: checklist_generate_report()
    )
    cmds.separator(h=10, style='none')
    cmds.button(
        l='Refresh',
        h=30,
        c=lambda args: checklist_refresh()
    )
    cmds.separator(h=8, style='none')

    # Consider Before Submitting section with better text wrapping
    cmds.separator(h=7, style='none')
    cmds.text(
        l="Things to Consider Before Submitting",
        bgc=[.5, .5, .0],
        fn="boldLabelFont",
        align="center"
    )
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
    cmds.text(
        l="Project Organization:",
        fn="boldLabelFont",
        align="left"
    )
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

    # Disclaimer
    cmds.separator(h=7, style='none')
    cmds.text(l="Disclaimer:", fn="boldLabelFont", align="left")
    cmds.text(
        l=('Even if this script shows no errors, it does not necessarily\n'
           'reflect your final grade.\nThis script is just a tool to help '
           'you check for some common\nissues.\nVerify instructions and '
           'deliverables on Canvas\nor with your instructor.'),
        align="left"
    )

    # Show window and set size (resizable)
    cmds.showWindow(window_name)
    cmds.window(window_name, e=True, width=420, height=810)
    
    # Set Window Icon
    _set_window_icon(window_name)


def checklist_refresh():
    """Run all validation checks and update UI."""
    # Save Current Selection For Later
    current_selection = cmds.ls(selection=True)
    
    try:
        print("Starting checklist validation...")
        
        # Updated function calls with new sequential numbering
        check_scene_units()
        check_output_resolution()
        check_total_texture_count()
        check_network_file_paths()
        check_unparented_objects()  
        check_total_triangle_count()
        check_total_polygon_count()
        check_total_poly_object_count()
        check_default_object_names()
        check_objects_assigned_to_default_material()
        check_ngons()
        check_non_manifold_geometry()
        check_frozen_transforms()
        check_animated_visibility()
        check_non_deformer_history()
        check_textures_color_space()
        check_ai_shadow_casting_lights()
        # check_camera_aspect_ratio()  # Item 18 - Commented out
        
        print("Checklist validation completed successfully!")
        
    except Exception as e:
        cmds.warning(f"Error during checklist refresh: {e}")
    finally:
        # Clear Selection
        cmds.selectMode(object=True)
        cmds.select(clear=True)
        
        # Reselect Previous Selection
        if current_selection:
            cmds.select(current_selection)


def checklist_generate_report():
    """Generate a comprehensive report of all checklist items."""
    # Save Current Selection For Later
    current_selection = cmds.ls(selection=True)
    
    report_strings = []
    try:
        # Updated function calls with new sequential numbering
        report_strings.append(check_scene_units())
        report_strings.append(check_output_resolution())
        report_strings.append(check_total_texture_count())
        report_strings.append(check_network_file_paths())
        report_strings.append(check_unparented_objects())
        report_strings.append(check_total_triangle_count())
        report_strings.append(check_total_polygon_count())
        report_strings.append(check_total_poly_object_count())
        report_strings.append(check_default_object_names())
        report_strings.append(check_objects_assigned_to_default_material())
        report_strings.append(check_ngons())
        report_strings.append(check_non_manifold_geometry())
        report_strings.append(check_frozen_transforms())
        report_strings.append(check_animated_visibility())
        report_strings.append(check_non_deformer_history())
        report_strings.append(check_textures_color_space())
        report_strings.append(check_ai_shadow_casting_lights())
        # report_strings.append(check_camera_aspect_ratio())  # Item 18 - Commented out
        
        # Show Report
        export_report_to_txt(report_strings)
        
    except Exception as e:
        cmds.warning(f"Error generating report: {e}")
    finally:
        # Clear Selection
        cmds.selectMode(object=True)
        cmds.select(clear=True)
        
        # Reselect Previous Selection
        if current_selection:
            cmds.select(current_selection)


def build_gui_help_ats_cmi_modeling_checklist():
    """
    Create the help window with detailed information about checklist items.
    
    Displays color-coded status meanings and basic usage instructions.
    """
    window_name = "build_gui_help_ats_cmi_modeling_checklist"
    
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name, window=True)

    # Create help window
    cmds.window(
        window_name,
        title=f"{SCRIPT_NAME} Help",
        mnb=False,
        mxb=False,
        s=True
    )
    cmds.window(window_name, e=True, s=True, wh=[1, 1])

    main_column = cmds.columnLayout("main_column", p=window_name)
   
    # Title section
    cmds.separator(h=12, style='none')
    cmds.rowColumnLayout(
        nc=1,
        cw=[(1, 310)],
        cs=[(1, 10)],
        p="main_column"
    )
    cmds.rowColumnLayout(
        nc=1,
        cw=[(1, 300)],
        cs=[(1, 10)],
        p="main_column"
    )
    cmds.text(
        f"{SCRIPT_NAME} Help",
        bgc=[0, .5, 0],
        fn="boldLabelFont",
        align="center"
    )
    cmds.separator(h=10, style='none', p="main_column")

    # Body content
    checklist_spacing = 4
    cmds.rowColumnLayout(
        nc=1,
        cw=[(1, 300)],
        cs=[(1, 10)],
        p="main_column"
    )
    cmds.text(
        l='This script performs checks to detect common issues',
        align="left"
    )
    cmds.text(
        l='that are often accidentally ignored/unnoticed for',
        align="left"
    )
    cmds.text(
        l='the FDMA 2530: Intro to Modeling.',
        align="left"
    )
    
    # Status color explanations
    cmds.separator(h=15, style='none')
    cmds.text(
        l='Checklist Status:',
        align="left",
        fn="boldLabelFont"
    )
    cmds.text(
        l='Click on status buttons for additional functions:',
        align="left",
        fn="smallPlainLabelFont"
    )
    cmds.separator(h=5, style='none')
    
    # Color legend with interactive buttons
    cmds.rowColumnLayout(
        nc=2,
        cw=[(1, 35), (2, 265)],
        cs=[(1, 10), (2, 10)],
        p="main_column"
    )
    
    cmds.button(
        l='',
        h=14,
        bgc=def_color,
        c=lambda args: print_message(
            'Default color - not yet tested.',
            as_heads_up_message=True
        )
    )
    cmds.text(
        l='- Default color, not yet tested.',
        align="left",
        fn="smallPlainLabelFont"
    )
    
    cmds.button(
        l='',
        h=14,
        bgc=pass_color,
        c=lambda args: print_message(
            'Pass color - no issues found.',
            as_heads_up_message=True
        )
    )
    cmds.text(
        l='- Pass color, no issues found.',
        align="left",
        fn="smallPlainLabelFont"
    )
    
    cmds.button(
        l='',
        h=14,
        bgc=warning_color,
        c=lambda args: print_message(
            'Warning color - review recommended.',
            as_heads_up_message=True
        )
    )
    cmds.text(
        l='- Warning color, review recommended.',
        align="left",
        fn="smallPlainLabelFont"
    )
    
    cmds.button(
        l='',
        h=14,
        bgc=error_color,
        c=lambda args: print_message(
            'Error color - issues found.',
            as_heads_up_message=True
        )
    )
    cmds.text(
        l='- Error color, issues found.',
        align="left",
        fn="smallPlainLabelFont"
    )
    
    cmds.button(
        l='',
        h=14,
        bgc=exception_color,
        c=lambda args: print_message(
            'Exception color - check failed to run.',
            as_heads_up_message=True
        )
    )
    cmds.text(
        l='- Exception color, check failed to run.',
        align="left",
        fn="smallPlainLabelFont"
    )

    # Close button
    cmds.rowColumnLayout(
        nc=1,
        cw=[(1, 300)],
        cs=[(1, 10)],
        p="main_column"
    )
    cmds.separator(h=15, style='none')
    cmds.button(
        l='Close',
        h=30,
        c=lambda args: _close_help_gui()
    )
    cmds.separator(h=8, style='none')
    
    # Show and lock window
    cmds.showWindow(window_name)
    cmds.window(window_name, e=True, s=False)
    
    def _close_help_gui():
        """Close the help window."""
        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name, window=True)


# ==============================================================================
# VALIDATION FUNCTIONS (ALL 18 ITEMS)
# ==============================================================================

# Item 1 - Scene Units
def check_scene_units():
    """Validate that scene units are set correctly."""
    item_name = checklist_items.get(1)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items.get(1)[1]
    
    try:
        received_value = cmds.currentUnit(query=True, linear=True)
        issues_found = 0

        if received_value.lower() == str(expected_value).lower():
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    f'{item_name}: "{received_value}".'
                )
            )
            issues_found = 0
        else: 
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=error_color,
                l='?',
                c=lambda args: patch_scene_units()
            )
            issues_found = 1
            
        cmds.text(
            "output_" + item_id,
            e=True,
            l=str(received_value).capitalize()
        )
        
        # Patch Function
        def patch_scene_units():
            """Offer to fix scene units automatically."""
            user_input = cmds.confirmDialog(
                title=item_name,
                message=(f'Do you want to change your {item_name.lower()} '
                        f'from "{received_value}" to '
                        f'"{str(expected_value).capitalize()}"?'),
                button=['Yes, change it for me', 'Ignore Issue'],
                defaultButton='Yes, change it for me',
                cancelButton='Ignore Issue',
                dismissString='Ignore Issue', 
                icon="question"
            )

            if user_input == 'Yes, change it for me':
                try:
                    cmds.currentUnit(linear=str(expected_value))
                    print(f"Your {item_name.lower()} was changed to "
                          f"{expected_value}")
                except Exception:
                    cmds.warning(
                        f'Failed to use custom setting "{expected_value}" '
                        'as your new scene unit.'
                    )
                check_scene_units()
            else:
                cmds.button("status_" + item_id, e=True, l='')

        # Return string for report
        if issues_found > 0:
            string_status = (f"{issues_found} issue found. The expected "
                            f"{item_name.lower()} was "
                            f'"{str(expected_value).capitalize()}" and yours is '
                            f'"{str(received_value).capitalize()}"')
        else: 
            string_status = (f"{issues_found} issues found. The expected "
                            f"{item_name.lower()} was "
                            f'"{str(expected_value).capitalize()}" and yours is '
                            f'"{str(received_value).capitalize()}"')
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 2 - Output Resolution
def check_output_resolution():
    """Validate render output resolution."""
    item_name = checklist_items[2][0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items[2][1]
    
    try:
        # Check Custom Value
        custom_settings_failed = False
        if isinstance(expected_value, list):
            if len(expected_value) < 2:
                custom_settings_failed = True
                expected_value = settings_default_checklist_values[2][1]
                
        received_value = [
            cmds.getAttr("defaultResolution.width"),
            cmds.getAttr("defaultResolution.height")
        ]
        issues_found = 0
        
        is_resolution_valid = False
        
        if (str(received_value[0]) == str(expected_value[0]) or 
            str(received_value[1]) == str(expected_value[1]) or 
            str(received_value[0]) == str(expected_value[1]) or 
            str(received_value[1]) == str(expected_value[0])):
            is_resolution_valid = True
        
        if is_resolution_valid:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    f'{item_name}: "{received_value[0]}x{received_value[1]}".'
                )
            )
            issues_found = 0
        else: 
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=error_color,
                l='?',
                c=lambda args: patch_output_resolution()
            )
            issues_found = 1
            
        cmds.text(
            "output_" + item_id,
            e=True,
            l=f"{received_value[0]}x{received_value[1]}"
        )
        
        # Patch Function
        def patch_output_resolution():
            """Display resolution fix dialog."""
            user_input = cmds.confirmDialog(
                title=item_name,
                message=(
                    'Either your height or width should match the resolution '
                    'from the guidelines. \nIt doesn\'t need to be both!\n'
                    'So make sure you turn on the option "Maintain the '
                    'width/height ratio" and make at least one of them match '
                    'to ensure that your render is not too small, or too big.\n'
                    f'Please make sure your width or height is '
                    f'"{expected_value[0]}" or "{expected_value[1]}" '
                    'and try again.'
                ),
                button=['OK', 'Ignore Issue'],
                defaultButton='OK',
                cancelButton='Ignore Issue',
                dismissString='Ignore Issue', 
                icon="warning"
            )

            if user_input == 'OK':
                pass
            else:
                cmds.button("status_" + item_id, e=True, l='')
                
        # Return string for report
        if issues_found > 0:
            string_status = (
                f"{issues_found} issue found. The expected values for "
                f"{item_name.lower()} were \"{expected_value[0]}\" or "
                f"\"{expected_value[1]}\" and yours is "
                f"\"{received_value[0]}x{received_value[1]}\""
            )
        else: 
            string_status = (
                f"{issues_found} issues found. The expected values for "
                f"{item_name.lower()} were \"{expected_value[0]}\" or "
                f"\"{expected_value[1]}\" and yours is "
                f"\"{received_value[0]}x{received_value[1]}\""
            )
        
        if custom_settings_failed:
            string_status = (
                '1 issue found. The custom resolution settings provided '
                'couldn\'t be used to check your resolution'
            )
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=exception_color,
                l='',
                c=lambda args: print_message(
                    'The custom value provided couldn\'t be used to check '
                    'the resolution.',
                    as_warning=True
                )
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 3 - Total Texture Count
def check_total_texture_count():
    """Validate total texture count in scene."""
    item_name = checklist_items.get(3)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items.get(3)[1] 

    try:
        received_value = 0 
        issues_found = 0

        # Check Custom Value
        custom_settings_failed = False
        if (isinstance(expected_value[0], int) is False or 
            isinstance(expected_value[1], int) is False):
            custom_settings_failed = True

        # Count Textures
        all_file_nodes = cmds.ls(type="file")
        
        # Check if no file nodes exist - show green instead of N/A
        if len(all_file_nodes) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No file texture nodes found in scene.'
                )
            )
            cmds.text("output_" + item_id, e=True, l="0")
            return (f'\n*** {item_name} ***\n'
                    '0 issues found. No file texture nodes in scene.')
        
        for file_node in all_file_nodes:
            try:
                uv_tiling_mode = cmds.getAttr(file_node + '.uvTilingMode')
                if uv_tiling_mode != 0:
                    use_frame_extension = cmds.getAttr(
                        file_node + '.useFrameExtension'
                    )
                    file_path = cmds.getAttr(file_node + ".fileTextureName")
                    udim_file_pattern = (
                        maya.app.general.fileTexturePathResolver
                        .getFilePatternString(
                            file_path, use_frame_extension, uv_tiling_mode
                        )
                    )
                    udim_textures = (
                        maya.app.general.fileTexturePathResolver
                        .findAllFilesForPattern(udim_file_pattern, None)
                    )
                    received_value += len(udim_textures)
                else:
                    received_value += 1
            except Exception:
                received_value += 1  # Fallback count
            
        # Manager Message
        patch_message = (
            f'Your {item_name.lower()} should be reduced from '
            f'"{received_value}" to less than "{expected_value[1]}".\n'
            '(UDIM tiles are counted as individual textures)'
        )
        cancel_button = 'Ignore Issue'
        
        if (received_value <= expected_value[1] and 
            received_value > expected_value[0]):
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=warning_color,
                l='',
                c=lambda args: warning_total_texture_count()
            )
            patch_message = (
                f'Your {item_name.lower()} is "{received_value}" which is '
                'a high number.\nConsider optimizing. (UDIM tiles are '
                'counted as individual textures)'
            )
            cancel_button = 'Ignore Warning'
            issues_found = 0
        elif received_value <= expected_value[0]:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    f'{item_name}: "{received_value}". (UDIM tiles are '
                    'counted as individual textures)'
                )
            )
            issues_found = 0
        else: 
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=error_color,
                l='?',
                c=lambda args: warning_total_texture_count()
            )
            issues_found = 1
            
        cmds.text("output_" + item_id, e=True, l=received_value)
        
        # Patch Function
        def warning_total_texture_count():
            """Display texture count warning dialog."""
            user_input = cmds.confirmDialog(
                title=item_name,
                message=patch_message,
                button=['OK', cancel_button],
                defaultButton='OK',
                cancelButton='Ignore Issue',
                dismissString='Ignore Issue', 
                icon="warning"
            )

            if user_input == 'Ignore Warning':
                cmds.button(
                    "status_" + item_id,
                    e=True,
                    l='',
                    bgc=pass_color
                )
            else:
                cmds.button("status_" + item_id, e=True, l='')
        
        # Return string for report
        if issues_found > 0:
            string_status = (
                f"{issues_found} issue found. The expected "
                f"{item_name.lower()} was less than \"{expected_value[1]}\" "
                f'and yours is "{received_value}"'
            )
        else: 
            string_status = (
                f"{issues_found} issues found. The expected "
                f"{item_name.lower()} was less than \"{expected_value[1]}\" "
                f'and yours is "{received_value}"'
            )
        
        if custom_settings_failed:
            string_status = (
                '1 issue found. The custom value provided couldn\'t be used '
                'to check your total texture count'
            )
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=exception_color,
                l='',
                c=lambda args: print_message(
                    'The custom value provided couldn\'t be used to check '
                    'your total texture count',
                    as_warning=True
                )
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 4 - File Paths
def check_network_file_paths():
    """Validate file texture paths."""
    item_name = checklist_items.get(4)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items.get(4)[1]
    
    try:
        incorrect_file_nodes = []
        
        # Count Incorrect File Nodes
        all_file_nodes = cmds.ls(type="file")
        
        # Check if no file nodes exist - show green instead of N/A
        if len(all_file_nodes) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No file texture nodes found in scene.'
                )
            )
            cmds.text("output_" + item_id, e=True, l="0")
            return (f'\n*** {item_name} ***\n'
                    '0 issues found. No file texture nodes in scene.')
        
        for file_node in all_file_nodes:
            try:
                file_path = cmds.getAttr(file_node + ".fileTextureName")
                if file_path:
                    file_path_lower = file_path.lower()
                    path_valid = any(
                        valid_path in file_path_lower 
                        for valid_path in expected_value
                    )
                    if not path_valid:
                        incorrect_file_nodes.append(file_node)
                else:
                    incorrect_file_nodes.append(file_node)
            except Exception:
                incorrect_file_nodes.append(file_node)

        if len(incorrect_file_nodes) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'All file nodes seem to be currently sourced from the '
                    'sourceimages folder.'
                )
            )
            issues_found = 0
        else: 
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=error_color,
                l='?',
                c=lambda args: warning_network_file_paths()
            )
            issues_found = len(incorrect_file_nodes)
            
        cmds.text("output_" + item_id, e=True, l=len(incorrect_file_nodes))
        
        # Patch Function
        def warning_network_file_paths():
            """Display file path warning dialog."""
            user_input = cmds.confirmDialog(
                title=item_name,
                message=(
                    f'{len(incorrect_file_nodes)} of your file node paths '
                    'aren\'t pointing to a "sourceimages" folder. \nPlease '
                    'change their path to make sure the files are inside the '
                    '"sourceimages" folder. \n\n(To see a list of nodes, '
                    'generate a full report)'
                ),
                button=['OK', 'Ignore Issue'],
                defaultButton='OK',
                cancelButton='Ignore Issue',
                dismissString='Ignore Issue', 
                icon="warning"
            )

            if user_input == 'OK':
                pass
            else:
                cmds.button("status_" + item_id, e=True, l='')
        
        # Return string for report
        issue_string = "issues" if issues_found != 1 else "issue"
        
        if issues_found > 0:
            string_status = f'{issues_found} {issue_string} found.\n'
            for file_node in incorrect_file_nodes:
                string_status += (
                    f'"{file_node}" isn\'t pointing to a "sourceimages" '
                    'folder. Your texture files should be sourced from a '
                    'proper Maya project.\n'
                )
        else: 
            string_status = (
                f'{issues_found} issues found. All textures were sourced '
                'from the network'
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 5 - Unparented Objects
def check_unparented_objects():
    """Validate unparented objects in scene."""
    item_name = checklist_items.get(5)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items.get(5)[1]
    
    try:
        unparented_objects = []

        # Count Unparented Objects
        geo_dag_nodes = cmds.ls(geometry=True)
        
        # Check if no geometry exists - show green instead of N/A
        if len(geo_dag_nodes) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No geometry objects found in scene.'
                )
            )
            cmds.text("output_" + item_id, e=True, l="0")
            return (f'\n*** {item_name} ***\n'
                    '0 issues found. No geometry objects in scene.')
        
        for obj in geo_dag_nodes:
            try:
                first_parent = cmds.listRelatives(obj, p=True, f=True)
                if first_parent:
                    children_members = (
                        cmds.listRelatives(
                            first_parent[0], c=True, type="transform"
                        ) or []
                    )
                    parents_members = (
                        cmds.listRelatives(
                            first_parent[0], ap=True, type="transform"
                        ) or []
                    )
                    
                    if (len(children_members) + len(parents_members) == 0 and
                        cmds.nodeType(obj) != "mentalrayIblShape"):
                        unparented_objects.append(obj)
            except Exception:
                continue

        if len(unparented_objects) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No unparented objects were found.'
                )
            )
            issues_found = 0
        else: 
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=error_color,
                l='?',
                c=lambda args: warning_unparented_objects()
            )
            issues_found = len(unparented_objects)
            
        cmds.text("output_" + item_id, e=True, l=len(unparented_objects))
        
        # Patch Function
        def warning_unparented_objects():
            """Display unparented objects warning dialog."""
            user_input = cmds.confirmDialog(
                title=item_name,
                message=(
                    f'{len(unparented_objects)} unparented object(s) found in '
                    'this scene. \nIt\'s likely that these objects need to be '
                    'part of a hierarchy.\n\n(To see a list of objects, '
                    'generate a full report)'
                ),
                button=['OK', 'Ignore Issue'],
                defaultButton='OK',
                cancelButton='Ignore Issue',
                dismissString='Ignore Issue', 
                icon="warning"
            )

            if user_input == 'OK':
                pass
            else:
                cmds.button("status_" + item_id, e=True, l='')
        
        # Return string for report
        issue_string = "issues" if issues_found != 1 else "issue"
        
        if issues_found > 0:
            string_status = f'{issues_found} {issue_string} found.\n'
            for obj in unparented_objects:
                string_status += (
                    f'"{obj}" has no parent or child nodes. It should likely '
                    'be part of a hierarchy.\n'
                )
            string_status = string_status[:-1]
        else: 
            string_status = (
                f'{issues_found} issues found. No unparented objects '
                'were found.'
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 6 - Total Triangle Count
def check_total_triangle_count():
    """Validate total triangle count in scene."""
    item_name = checklist_items.get(6)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items.get(6)[1][1]
    inbetween_value = checklist_items.get(6)[1][0]
    
    try:
        # Check Custom Value
        custom_settings_failed = False
        if (isinstance(expected_value, int) is False or 
            isinstance(inbetween_value, int) is False):
            custom_settings_failed = True

        all_poly_count = cmds.ls(type="mesh", flatten=True)
        
        # Check if no polygon objects exist - show green instead of N/A
        if len(all_poly_count) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No polygon objects found in scene.'
                )
            )
            cmds.text("output_" + item_id, e=True, l="0")
            return (f'\n*** {item_name} ***\n'
                    '0 issues found. No polygon objects in scene.')
        
        scene_tri_count = 0
        
        for obj in all_poly_count:
            try:
                smooth_level = cmds.getAttr(obj + ".smoothLevel")
                smooth_state = cmds.getAttr(obj + ".displaySmoothMesh")
                total_tri_count = cmds.polyEvaluate(obj, t=True) or 0
                
                if smooth_state > 0 and smooth_level != 0:
                    total_edge_count = cmds.polyEvaluate(obj, e=True) or 0
                    one_subdiv_tri_count = (total_edge_count * 4)
                    if smooth_level > 1:
                        multi_subdiv_tri_count = (
                            one_subdiv_tri_count * (4 ** (smooth_level - 1))
                        )
                        scene_tri_count += multi_subdiv_tri_count
                    else:
                        scene_tri_count += one_subdiv_tri_count
                else:
                    scene_tri_count += total_tri_count
            except Exception:
                continue
                    
        if (scene_tri_count < expected_value and 
            scene_tri_count > inbetween_value):
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=warning_color,
                l='',
                c=lambda args: warning_total_triangle_count()
            )
            issues_found = 0
            patch_message = (
                f'Your scene has {scene_tri_count} triangles, which is high. '
                '\nConsider optimizing it if possible.'
            )
            cancel_message = "Ignore Warning"
        elif scene_tri_count < expected_value:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    f'Your scene has {scene_tri_count} triangles. '
                    '\nGood job keeping the triangle count low!'
                )
            )
            issues_found = 0
            patch_message = ''
        else: 
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=error_color,
                l='?',
                c=lambda args: warning_total_triangle_count()
            )
            issues_found = 1
            patch_message = (
                f'Your scene has {scene_tri_count} triangles. You should '
                f'try to keep it under {expected_value}.\n\n'
                'In case you see a different number on your "Heads Up '
                'Display > Poly Count" option. It\'s likely that you have '
                '"shapeOrig" nodes in your scene. These are intermediate '
                'shape nodes usually created by deformers. If you don\'t '
                'have deformations on your scene, you can delete these to '
                'reduce triangle count.\n'
            )
            cancel_message = "Ignore Issue"
            
        cmds.text("output_" + item_id, e=True, l=scene_tri_count)
        
        # Patch Function
        def warning_total_triangle_count():
            """Display triangle count warning dialog."""
            user_input = cmds.confirmDialog(
                title=item_name,
                message=patch_message,
                button=['OK', cancel_message],
                defaultButton='OK',
                cancelButton=cancel_message,
                dismissString=cancel_message, 
                icon="warning"
            )

            if user_input == "Ignore Warning":
                cmds.button(
                    "status_" + item_id,
                    e=True,
                    bgc=pass_color,
                    l='',
                    c=lambda args: print_message(
                        f'{issues_found} issues found. Your scene has '
                        f'{scene_tri_count} triangles, which is high. '
                        '\nConsider optimizing it if possible.'
                    )
                )
            else:
                cmds.button("status_" + item_id, e=True, l='')
        
        # Return string for report
        if (scene_tri_count > inbetween_value and 
            scene_tri_count < expected_value):
            string_status = (
                f'{issues_found} issues found. Your scene has '
                f'{scene_tri_count} triangles, which is high. Consider '
                'optimizing it if possible.'
            )
        elif scene_tri_count < expected_value:
            string_status = (
                f'{issues_found} issues found. Your scene has '
                f'{scene_tri_count} triangles. Good job keeping the '
                'triangle count low!'
            )
        else: 
            string_status = (
                f'{issues_found} issue found. Your scene has '
                f'{scene_tri_count} triangles. You should try to keep it '
                f'under {expected_value}.'
            )
        
        if custom_settings_failed:
            string_status = (
                '1 issue found. The custom value provided couldn\'t be used '
                'to check your total triangle count'
            )
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=exception_color,
                l='',
                c=lambda args: print_message(
                    'The custom value provided couldn\'t be used to check '
                    'your total triangle count',
                    as_warning=True
                )
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 7 - Total Polygon Count
def check_total_polygon_count():
    """Validate total polygon count in scene."""
    item_name = checklist_items.get(7)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items.get(7)[1][1]
    inbetween_value = checklist_items.get(7)[1][0]
    
    try:
        # Check Custom Value
        custom_settings_failed = False
        if (isinstance(expected_value, int) is False or 
            isinstance(inbetween_value, int) is False):
            custom_settings_failed = True

        all_poly_count = cmds.ls(type="mesh", flatten=True)
        
        # Check if no polygon objects exist - show green instead of N/A
        if len(all_poly_count) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No polygon objects found in scene.'
                )
            )
            cmds.text("output_" + item_id, e=True, l="0")
            return (f'\n*** {item_name} ***\n'
                    '0 issues found. No polygon objects in scene.')
        
        scene_poly_count = 0
        
        for obj in all_poly_count:
            try:
                smooth_level = cmds.getAttr(obj + ".smoothLevel")
                smooth_state = cmds.getAttr(obj + ".displaySmoothMesh")
                total_face_count = cmds.polyEvaluate(obj, f=True) or 0

                if smooth_state > 0 and smooth_level != 0:
                    # Subdivision increases face count by factor of 4 per level
                    subdivided_face_count = (
                        total_face_count * (4 ** smooth_level)
                    )
                    scene_poly_count += subdivided_face_count
                else:
                    scene_poly_count += total_face_count
            except Exception:
                continue
                    
        if (scene_poly_count < expected_value and 
            scene_poly_count > inbetween_value):
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=warning_color,
                l='',
                c=lambda args: warning_total_polygon_count()
            )
            issues_found = 0
            patch_message = (
                f'Your scene has {scene_poly_count} polygons, which is high. '
                '\nConsider optimizing it if possible.'
            )
            cancel_message = "Ignore Warning"
        elif scene_poly_count < expected_value:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    f'Your scene has {scene_poly_count} polygons. '
                    '\nGood job keeping the polygon count low!'
                )
            )
            issues_found = 0
            patch_message = ''
        else: 
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=error_color,
                l='?',
                c=lambda args: warning_total_polygon_count()
            )
            issues_found = 1
            patch_message = (
                f'Your scene has {scene_poly_count} polygons. You should '
                f'try to keep it under {expected_value}.'
            )
            cancel_message = "Ignore Issue"
            
        cmds.text("output_" + item_id, e=True, l=scene_poly_count)
        
        # Patch Function
        def warning_total_polygon_count():
            """Display polygon count warning dialog."""
            user_input = cmds.confirmDialog(
                title=item_name,
                message=patch_message,
                button=['OK', cancel_message],
                defaultButton='OK',
                cancelButton=cancel_message,
                dismissString=cancel_message, 
                icon="warning"
            )

            if user_input == "Ignore Warning":
                cmds.button(
                    "status_" + item_id,
                    e=True,
                    bgc=pass_color,
                    l='',
                    c=lambda args: print_message(
                        f'{issues_found} issues found. Your scene has '
                        f'{scene_poly_count} polygons, which is high. '
                        '\nConsider optimizing it if possible.'
                    )
                )
            else:
                cmds.button("status_" + item_id, e=True, l='')
        
        # Return string for report
        if (scene_poly_count > inbetween_value and 
            scene_poly_count < expected_value):
            string_status = (
                f'{issues_found} issues found. Your scene has '
                f'{scene_poly_count} polygons, which is high. Consider '
                'optimizing it if possible.'
            )
        elif scene_poly_count < expected_value:
            string_status = (
                f'{issues_found} issues found. Your scene has '
                f'{scene_poly_count} polygons. Good job keeping the '
                'polygon count low!'
            )
        else: 
            string_status = (
                f'{issues_found} issue found. Your scene has '
                f'{scene_poly_count} polygons. You should try to keep it '
                f'under {expected_value}.'
            )
        
        if custom_settings_failed:
            string_status = (
                '1 issue found. The custom value provided couldn\'t be used '
                'to check your total polygon count'
            )
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=exception_color,
                l='',
                c=lambda args: print_message(
                    'The custom value provided couldn\'t be used to check '
                    'your total polygon count',
                    as_warning=True
                )
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 8 - Total Poly Object Count
def check_total_poly_object_count():
    """Validate total polygon object count in scene."""
    item_name = checklist_items.get(8)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items.get(8)[1][1]
    inbetween_value = checklist_items.get(8)[1][0]
    
    try:
        # Check Custom Values
        custom_settings_failed = False
        if (isinstance(expected_value, int) is False or 
            isinstance(inbetween_value, int) is False):
            custom_settings_failed = True
        
        all_polymesh = cmds.ls(type="mesh")

        # Always show the count, even if 0 (show green for empty scenes)
        if len(all_polymesh) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No polygon objects in scene.'
                )
            )
            cmds.text("output_" + item_id, e=True, l="0")
            return (f'\n*** {item_name} ***\n'
                    '0 issues found. No polygon objects in scene.')

        if (len(all_polymesh) < expected_value and 
            len(all_polymesh) > inbetween_value):
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=warning_color,
                l='',
                c=lambda args: warning_total_poly_object_count()
            )
            issues_found = 0
            patch_message = (
                f'Your scene contains "{len(all_polymesh)}" polygon meshes, '
                'which is a high number. \nConsider optimizing it if possible.'
            )
            cancel_message = "Ignore Warning"
        elif len(all_polymesh) < expected_value:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    f'Your scene contains "{len(all_polymesh)}" polygon meshes.'
                )
            )
            issues_found = 0
            patch_message = ''
        else: 
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=error_color,
                l='?',
                c=lambda args: warning_total_poly_object_count()
            )
            issues_found = 1
            patch_message = (
                f'{len(all_polymesh)} polygon meshes in your scene. '
                f'\nTry to keep this number under {expected_value}.'
            )
            cancel_message = "Ignore Issue"
            
        cmds.text("output_" + item_id, e=True, l=len(all_polymesh))
        
        # Patch Function
        def warning_total_poly_object_count():
            """Display poly object count warning dialog."""
            user_input = cmds.confirmDialog(
                title=item_name,
                message=patch_message,
                button=['OK', cancel_message],
                defaultButton='OK',
                cancelButton=cancel_message,
                dismissString=cancel_message, 
                icon="warning"
            )

            if user_input == "Ignore Warning":
                cmds.button(
                    "status_" + item_id,
                    e=True,
                    bgc=pass_color,
                    l='',
                    c=lambda args: print_message(
                        f'{issues_found} issues found. Your scene contains '
                        f'{len(all_polymesh)} polygon meshes, which is a high '
                        'number. \nConsider optimizing it if possible.'
                    )
                )
            else:
                cmds.button("status_" + item_id, e=True, l='')
        
        # Return string for report
        if (len(all_polymesh) < expected_value and 
            len(all_polymesh) > inbetween_value):
            string_status = (
                f'{issues_found} issues found. Your scene contains '
                f'"{len(all_polymesh)}" polygon meshes, which is a high '
                'number. Consider optimizing it if possible.'
            )
        elif len(all_polymesh) < expected_value:
            string_status = (
                f'{issues_found} issues found. Your scene contains '
                f'"{len(all_polymesh)}" polygon meshes.'
            )
        else: 
            string_status = (
                f'{issues_found} issue found. Your scene contains '
                f'"{len(all_polymesh)}" polygon meshes. Try to keep this '
                f'number under "{expected_value}".'
            )
        
        if custom_settings_failed:
            string_status = (
                '1 issue found. The custom value provided couldn\'t be used '
                'to check your total poly count'
            )
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=exception_color,
                l='',
                c=lambda args: print_message(
                    'The custom value provided couldn\'t be used to check '
                    'your total poly count',
                    as_warning=True
                )
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 9 - Default Object Names
def check_default_object_names():
    """Validate default object names in scene."""
    item_name = checklist_items.get(9)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items.get(9)[1]
    
    try:
        offending_objects = []
        possible_offenders = []
        
        all_objects = cmds.ls(lt=True, lf=True, g=True)
        
        # Check if no objects exist - show green instead of N/A
        if len(all_objects) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No objects found in scene.'
                )
            )
            cmds.text("output_" + item_id, e=True, l="0")
            return (f'\n*** {item_name} ***\n'
                    '0 issues found. No objects in scene.')
        
        for obj in all_objects:
            for def_name in DEFAULT_OBJECT_NAMES:
                if obj.startswith(def_name):
                    if obj not in offending_objects:
                        offending_objects.append(obj)
                elif def_name in obj:
                    if obj not in possible_offenders:
                        possible_offenders.append(obj)
        
        # Manage Strings
        if len(possible_offenders) == 1:
            patch_message_warning = (
                f'{len(possible_offenders)} object contains a string '
                'extremely similar to the default names.\n(Ignore this '
                'warning if the name describes your object properly)'
            )
        else:
            patch_message_warning = (
                f'{len(possible_offenders)} objects contain a string '
                'extremely similar to the default names.\n(Ignore this '
                'warning if the name describes your object properly)'
            )
        
        if len(offending_objects) == 1:
            patch_message_error = (
                f'{len(offending_objects)} object was not named properly. '
                '\nPlease rename your objects descriptively.'
            )
        else:
            patch_message_error = (
                f'{len(offending_objects)} objects were not named properly. '
                '\nPlease rename your objects descriptively.'
            )
        
        # Manage Buttons
        if len(possible_offenders) != 0 and len(offending_objects) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=warning_color,
                l='',
                c=lambda args: warning_default_object_names()
            )
            issues_found = 0
        elif len(offending_objects) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No unnamed objects were found, well done!'
                )
            )
            issues_found = 0
        else: 
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=error_color,
                l='?',
                c=lambda args: warning_default_object_names()
            )
            issues_found = len(offending_objects)
        
        # Manage Message
        patch_message = ''
        cancel_message = 'Ignore Issue'
                
        if len(possible_offenders) != 0 and len(offending_objects) == 0:
            cmds.text(
                "output_" + item_id,
                e=True,
                l=f'[ {len(possible_offenders)} ]'
            )
            patch_message = patch_message_warning
            cancel_message = 'Ignore Warning'
        elif len(possible_offenders) == 0:
            cmds.text("output_" + item_id, e=True, l=str(len(offending_objects)))
            patch_message = patch_message_error
        else:
            cmds.text(
                "output_" + item_id,
                e=True,
                l=f'{len(offending_objects)} + [ {len(possible_offenders)} ]'
            )
            patch_message = f'{patch_message_error}\n\n{patch_message_warning}'
            
        # Patch Function
        def warning_default_object_names():
            """Display default object names warning dialog."""
            user_input = cmds.confirmDialog(
                title=item_name,
                message=patch_message,
                button=['OK', cancel_message],
                defaultButton='OK',
                cancelButton='Ignore Issue',
                dismissString='Ignore Issue', 
                icon="warning"
            )

            if user_input == 'Ignore Warning':
                cmds.button(
                    "status_" + item_id,
                    e=True,
                    bgc=pass_color,
                    l='',
                    c=lambda args: warning_default_object_names()
                )
            else:
                cmds.button("status_" + item_id, e=True, l='')
        
        # Return string for report
        issue_string = "issues" if issues_found != 1 else "issue"
        
        if issues_found > 0 or len(possible_offenders) > 0:
            string_status = f'{issues_found} {issue_string} found.\n'
            for obj in offending_objects:
                string_status += (
                    f'"{obj}" was not named properly. Please rename your '
                    'object descriptively.\n'
                )
            
            if len(offending_objects) != 0 and len(possible_offenders) == 0:
                string_status = string_status[:-1]
            
            for obj in possible_offenders:
                string_status += (
                    f'"{obj}" contains a string extremely similar to the '
                    'default names.\n'
                )
            
            if len(possible_offenders) != 0:
                string_status = string_status[:-1]
        else: 
            string_status = (
                f'{issues_found} issues found. No unnamed objects were found, '
                'well done!'
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 10 - Objects Assigned to Default Material
def check_objects_assigned_to_default_material():
    """Validate objects assigned to default materials."""
    item_name = checklist_items.get(10)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items.get(10)[1]
    
    try:
        # Check both lambert1 and standardSurface1 (Maya 2024+ default)
        lambert1_objects = cmds.sets("initialShadingGroup", q=True) or []
        
        # Check if standardSurface1 exists and get its shading group
        standardsurface_objects = []
        if cmds.objExists("standardSurface1"):
            # Find shading group connected to standardSurface1
            shading_groups = (
                cmds.listConnections("standardSurface1", type="shadingEngine") 
                or []
            )
            for sg in shading_groups:
                objects_in_sg = cmds.sets(sg, q=True) or []
                standardsurface_objects.extend(objects_in_sg)
        
        # Combine both lists and remove duplicates
        all_default_objects = list(set(lambert1_objects + standardsurface_objects))
        
        # Check if no geometry exists - show green instead of N/A
        all_geo = cmds.ls(geometry=True)
        if len(all_geo) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No geometry objects found in scene.'
                )
            )
            cmds.text("output_" + item_id, e=True, l="0")
            return (f'\n*** {item_name} ***\n'
                    '0 issues found. No geometry objects in scene.')
        
        if len(all_default_objects) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No objects were assigned to default materials.'
                )
            )
            issues_found = 0
        else: 
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=error_color,
                l='?',
                c=lambda args: warning_objects_assigned_to_default_material()
            )
            issues_found = len(all_default_objects)
            
        cmds.text("output_" + item_id, e=True, l=len(all_default_objects))
        
        if len(all_default_objects) == 1:
            patch_message = (
                f'{len(all_default_objects)} object is assigned to default '
                'material(s). \nMake sure no objects are assigned to lambert1 '
                'or standardSurface1.\n\n(To see a list of objects, generate '
                'a full report)'
            )
        else:
            patch_message = (
                f'{len(all_default_objects)} objects are assigned to default '
                'material(s). \nMake sure no objects are assigned to lambert1 '
                'or standardSurface1.\n\n(To see a list of objects, generate '
                'a full report)'
            )
        
        # Patch Function
        def warning_objects_assigned_to_default_material():
            """Display default material assignment warning dialog."""
            user_input = cmds.confirmDialog(
                title=item_name,
                message=patch_message,
                button=['OK', 'Ignore Issue'],
                defaultButton='OK',
                cancelButton='Ignore Issue',
                dismissString='Ignore Issue', 
                icon="warning"
            )

            if user_input == 'OK':
                pass
            else:
                cmds.button("status_" + item_id, e=True, l='')
        
        # Return string for report
        issue_string = "issues" if issues_found != 1 else "issue"
        
        if issues_found > 0:
            string_status = f'{issues_found} {issue_string} found.\n'
            for obj in all_default_objects:
                string_status += (
                    f'"{obj}" is assigned to default material. It should be '
                    'assigned to another shader.\n'
                )
            string_status = string_status[:-1]
        else: 
            string_status = (
                f'{issues_found} issues found. No objects are assigned to '
                'default materials.'
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 11 - Ngons
def check_ngons():
    """Validate ngons in scene."""
    item_name = checklist_items.get(11)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items.get(11)[1]

    try:
        # Check if polygon objects exist first - show green instead of N/A
        all_meshes = cmds.ls(type="mesh")
        if len(all_meshes) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No polygon objects found in scene.'
                )
            )
            cmds.text("output_" + item_id, e=True, l="0")
            return (f'\n*** {item_name} ***\n'
                    '0 issues found. No polygon objects in scene.')

        ngon_mel_command = (
            'string $ngons[] = `polyCleanupArgList 3 { "1","2","1","0","1",'
            '"0","0","0","0","1e-005","0","1e-005","0","1e-005","0","-1",'
            '"0" }`;'
        )
        ngons_list = mel.eval(ngon_mel_command) or []
        cmds.select(clear=True)
        
        print('')  # Clear Any Warnings

        if len(ngons_list) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No ngons were found in your scene. Good job!'
                )
            )
            issues_found = 0
        else: 
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=error_color,
                l='?',
                c=lambda args: warning_ngons()
            )
            issues_found = len(ngons_list)
            
        cmds.text("output_" + item_id, e=True, l=len(ngons_list))
        
        if len(ngons_list) == 1:
            patch_message = (
                f'{len(ngons_list)} ngon found in your scene. \nMake sure no '
                'faces have more than 4 sides.\n\n(To see a list of objects, '
                'generate a full report)'
            )
        else:
            patch_message = (
                f'{len(ngons_list)} ngons found in your scene. \nMake sure no '
                'faces have more than 4 sides.\n\n(To see a list of objects, '
                'generate a full report)'
            )
        
        # Patch Function
        def warning_ngons():
            """Display ngons warning dialog."""
            user_input = cmds.confirmDialog(
                title=item_name,
                message=patch_message,
                button=['OK', 'Select Ngons', 'Ignore Issue'],
                defaultButton='OK',
                cancelButton='Ignore Issue',
                dismissString='Ignore Issue', 
                icon="warning"
            )

            if user_input == 'Select Ngons':
                try:
                    ngons_list_select = mel.eval(ngon_mel_command) or []
                    if ngons_list_select:
                        cmds.select(ngons_list_select)
                except Exception:
                    print("Could not select ngons")
            else:
                cmds.button("status_" + item_id, e=True, l='')
        
        # Return string for report
        issue_string = "issues" if issues_found != 1 else "issue"
        
        if issues_found > 0:
            string_status = f'{issues_found} {issue_string} found.\n'
            for obj in ngons_list:
                string_status += (
                    f'"{obj}" is an ngon (face with more than 4 sides).\n'
                )
            string_status = string_status[:-1]
        else: 
            string_status = (
                f'{issues_found} issues found. No ngons were found in '
                'your scene.'
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 12 - Non-manifold Geometry
def check_non_manifold_geometry():
    """Validate non-manifold geometry in scene."""
    item_name = checklist_items.get(12)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items.get(12)[1]
    
    try:
        nonmanifold_geo = []
        nonmanifold_verts = []
        
        all_geo = cmds.ls(type='mesh', long=True)
       
        # Check if no geometry exists - show green instead of N/A
        if len(all_geo) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No polygon objects found in scene.'
                )
            )
            cmds.text("output_" + item_id, e=True, l="0")
            return (f'\n*** {item_name} ***\n'
                    '0 issues found. No polygon objects in scene.')
       
        for geo in all_geo:
            try:
                obj_non_manifold_verts = cmds.polyInfo(geo, nmv=True) or []
                if len(obj_non_manifold_verts) > 0:
                    nonmanifold_geo.append(geo)
                    nonmanifold_verts.append(obj_non_manifold_verts)
            except Exception:
                continue

        if len(nonmanifold_geo) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No objects with non-manifold geometry in your scene. '
                    'Well Done!'
                )
            )
            issues_found = 0
        else: 
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=error_color,
                l='?',
                c=lambda args: warning_non_manifold_geometry()
            )
            issues_found = len(nonmanifold_geo)
            
        cmds.text("output_" + item_id, e=True, l=len(nonmanifold_geo))
        
        if len(nonmanifold_geo) == 1:
            patch_message = (
                f'{len(nonmanifold_geo)} object with non-manifold geometry '
                'was found in your scene. \n\n(To see a list of objects, '
                'generate a full report)'
            )
        else:
            patch_message = (
                f'{len(nonmanifold_geo)} objects with non-manifold geometry '
                'were found in your scene. \n\n(To see a list of objects, '
                'generate a full report)'
            )
        
        # Patch Function
        def warning_non_manifold_geometry():
            """Display non-manifold geometry warning dialog."""
            user_input = cmds.confirmDialog(
                title=item_name,
                message=patch_message,
                button=['OK', 'Select Non-manifold Vertices', 'Ignore Issue'],
                defaultButton='OK',
                cancelButton='Ignore Issue',
                dismissString='Ignore Issue', 
                icon="warning"
            )
                        
            if user_input == 'Select Non-manifold Vertices':
                try:
                    cmds.select(clear=True)
                    for verts in nonmanifold_verts:
                        cmds.select(verts, add=True)
                except Exception:
                    print("Could not select non-manifold vertices")
            else:
                cmds.button("status_" + item_id, e=True, l='')
        
        # Return string for report
        issue_string = "issues" if issues_found != 1 else "issue"
        
        if issues_found > 0:
            string_status = f'{issues_found} {issue_string} found.\n'
            for obj in nonmanifold_geo:
                string_status += (
                    f'"{get_short_name(obj)}" has non-manifold geometry.\n'
                )
            string_status = string_status[:-1]
        else: 
            string_status = (
                f'{issues_found} issues found. No non-manifold geometry '
                'found in your scene.'
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 13 - Frozen Transforms
def check_frozen_transforms():
    """Validate frozen transforms in scene."""
    item_name = checklist_items.get(13)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items.get(13)[1]
    
    try:
        objects_no_frozen_transforms = []
        
        all_transforms = cmds.ls(type='transform')
        
        # Check if no transforms exist - show green instead of N/A
        if len(all_transforms) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No transform objects found in scene.'
                )
            )
            cmds.text("output_" + item_id, e=True, l="0")
            return (f'\n*** {item_name} ***\n'
                    '0 issues found. No transform objects in scene.')
            
        for transform in all_transforms:
            try:
                children = cmds.listRelatives(transform, c=True, pa=True) or []
                for child in children:
                    object_type = cmds.objectType(child)
                    if object_type in ['mesh', 'nurbsCurve']:
                        # Check if rotation values are not zero
                        rot_x = cmds.getAttr(transform + ".rotateX")
                        rot_y = cmds.getAttr(transform + ".rotateY")
                        rot_z = cmds.getAttr(transform + ".rotateZ")
                        
                        if rot_x != 0 or rot_y != 0 or rot_z != 0:
                            # Check if rotation attributes have no connections
                            connections = []
                            for attr in [".rotateX", ".rotateY", ".rotateZ", 
                                       ".rotate"]:
                                connections.extend(
                                    cmds.listConnections(transform + attr) or []
                                )
                            
                            if len(connections) == 0:
                                if transform not in objects_no_frozen_transforms:
                                    objects_no_frozen_transforms.append(transform)
            except Exception:
                continue
                           
        if len(objects_no_frozen_transforms) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'All transforms appear to be frozen.'
                )
            )
            issues_found = 0
        else: 
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=warning_color,
                l='?',
                c=lambda args: warning_frozen_transforms()
            )
            issues_found = len(objects_no_frozen_transforms)
            
        cmds.text("output_" + item_id, e=True, l=len(objects_no_frozen_transforms))
        
        if len(objects_no_frozen_transforms) == 1:
            patch_message = (
                f'{len(objects_no_frozen_transforms)} object has un-frozen '
                'transformations. \n\n(To see a list of objects, generate a '
                'full report)'
            )
        else:
            patch_message = (
                f'{len(objects_no_frozen_transforms)} objects have un-frozen '
                'transformations. \n\n(To see a list of objects, generate a '
                'full report)'
            )
        
        # Patch Function
        def warning_frozen_transforms():
            """Display frozen transforms warning dialog."""
            user_input = cmds.confirmDialog(
                title=item_name,
                message=patch_message,
                button=['OK', 'Select Objects with un-frozen transformations', 
                       'Ignore Warning'],
                defaultButton='OK',
                cancelButton='Ignore Warning',
                dismissString='Ignore Warning', 
                icon="warning"
            )
                        
            if user_input == 'Select Objects with un-frozen transformations':
                try:
                    cmds.select(objects_no_frozen_transforms)
                except Exception:
                    print("Could not select objects")
            elif user_input == 'Ignore Warning':
                cmds.button("status_" + item_id, e=True, bgc=pass_color, l='')
            else:
                cmds.button("status_" + item_id, e=True, l='')
        
        # Return string for report
        if issues_found > 0:
            string_status = f'{issues_found} {issue_string} found.\n'
            for obj in objects_no_frozen_transforms:
                string_status += f'"{obj}" has un-frozen transformations.\n'
            string_status = string_status[:-1]
        else: 
            string_status = (
                f'{issues_found} issues found. No objects have un-frozen '
                'transformations.'
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 14 - Animated Visibility
def check_animated_visibility():
    """Validate animated visibility with turntable exception."""
    item_name = checklist_items.get(14)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items.get(14)[1]
    
    try:
        objects_animated_visibility = []
        objects_hidden = []
        turntable_objects = []
        
        all_transforms = cmds.ls(type='transform')
        
        # Check if no transforms exist - show green instead of N/A
        if len(all_transforms) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No transform objects found in scene.'
                )
            )
            cmds.text("output_" + item_id, e=True, l="0")
            return (f'\n*** {item_name} ***\n'
                    '0 issues found. No transform objects in scene.')
        
        for transform in all_transforms:
            try:
                attributes = cmds.listAttr(transform)
                outliner_hidden = False
                
                if 'hiddenInOutliner' in attributes:
                    outliner_hidden = cmds.getAttr(transform + ".hiddenInOutliner")

                if 'visibility' in attributes and not outliner_hidden:
                    if cmds.getAttr(transform + ".visibility") == 0:
                        children = (
                            cmds.listRelatives(transform, s=True, pa=True) or []
                        )
                        if len(children) != 0:
                            if cmds.nodeType(children[0]) != "camera":
                                objects_hidden.append(transform)
                
                # Check for animated visibility
                input_nodes = (
                    cmds.listConnections(
                        transform + ".visibility", 
                        destination=False, 
                        source=True
                    ) or []
                )
                
                for node in input_nodes:
                    if 'animCurve' in cmds.nodeType(node):
                        # Check if this is a turntable object
                        transform_lower = transform.lower()
                        if ('turntable' in transform_lower or 
                            'turn_table' in transform_lower):
                            turntable_objects.append(transform)
                        else:
                            objects_animated_visibility.append(transform)
            except Exception:
                continue
        
        # Special handling for turntable exception
        if (len(turntable_objects) == 1 and 
            len(objects_animated_visibility) == 0):
            # Only one turntable object with animated visibility
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=warning_color,
                l='',
                c=lambda args: warning_animated_visibility()
            )
            issues_found = 0
            turntable_warning = True
        else:
            turntable_warning = False
            if len(turntable_objects) > 0:
                # More than one turntable or other animated objects
                objects_animated_visibility.extend(turntable_objects)
        
        # Manage Strings
        cancel_message = 'Ignore Issue'
        buttons_to_add = []
        
        if len(objects_hidden) == 1:
            patch_message_warning = f'{len(objects_hidden)} object is hidden.\n'
        else:
            patch_message_warning = f'{len(objects_hidden)} objects are hidden.\n'
        
        if len(objects_animated_visibility) == 1:
            patch_message_error = (
                f'{len(objects_animated_visibility)} object with animated '
                'visibility.\n'
            )
        else:
            patch_message_error = (
                f'{len(objects_animated_visibility)} objects with animated '
                'visibility.\n'
            )
        
        # Add turntable message if applicable
        if turntable_warning:
            patch_message_error = (
                'Single turntable object detected with animated visibility.\n'
            )
            
        # Manage Message
        patch_message = ''
                
        if (len(objects_hidden) != 0 and 
            len(objects_animated_visibility) == 0 and 
            not turntable_warning):
            cmds.text(
                "output_" + item_id,
                e=True,
                l=f'[ {len(objects_hidden)} ]'
            )
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
            cmds.text(
                "output_" + item_id,
                e=True,
                l=f'{len(objects_animated_visibility)} + [ {len(objects_hidden)} ]'
            )
            patch_message = f'{patch_message_error}\n\n{patch_message_warning}'
            buttons_to_add.append('Select Hidden Objects')
            buttons_to_add.append('Select Objects With Animated Visibility')
        
        assembled_message = ['OK']
        assembled_message.extend(buttons_to_add)
        assembled_message.append(cancel_message)
        
        # Manage State
        if (len(objects_hidden) != 0 and 
            len(objects_animated_visibility) == 0 and 
            not turntable_warning):
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=warning_color,
                l='',
                c=lambda args: warning_animated_visibility()
            )
            issues_found = 0
        elif len(objects_animated_visibility) == 0 and not turntable_warning:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No objects with animated visibility or hidden.'
                )
            )
            issues_found = 0
        else: 
            if not turntable_warning:
                cmds.button(
                    "status_" + item_id,
                    e=True,
                    bgc=error_color,
                    l='?',
                    c=lambda args: warning_animated_visibility()
                )
                issues_found = len(objects_animated_visibility)
            else:
                issues_found = 0
            
        # Patch Function
        def warning_animated_visibility():
            """Display animated visibility warning dialog."""
            user_input = cmds.confirmDialog(
                title=item_name,
                message=patch_message,
                button=assembled_message,
                defaultButton='OK',
                cancelButton='Ignore Issue',
                dismissString='Ignore Issue', 
                icon="warning" if issues_found > 0 else "information"
            )
            
            if user_input == 'Select Objects With Animated Visibility':
                try:
                    cmds.select(objects_animated_visibility)
                except Exception:
                    print("Could not select objects")
            elif user_input == 'Select Hidden Objects':
                try:
                    cmds.select(objects_hidden)
                except Exception:
                    print("Could not select objects")
            elif user_input == 'Ignore Warning':
                cmds.button("status_" + item_id, e=True, bgc=pass_color, l='')
            else:
                cmds.button("status_" + item_id, e=True, l='')
            
        # Return string for report
        issue_string = "issues" if issues_found != 1 else "issue"
        
        if issues_found > 0 or len(objects_hidden) > 0 or turntable_warning:
            string_status = f'{issues_found} {issue_string} found.\n'
            for obj in objects_animated_visibility:
                string_status += f'"{obj}" has animated visibility.\n'
            for obj in turntable_objects:
                string_status += (
                    f'"{obj}" is a turntable object with animated visibility '
                    '(warning only).\n'
                )
            
            if (len(objects_animated_visibility) != 0 and 
                len(objects_hidden) == 0):
                string_status = string_status[:-1]
            
            for obj in objects_hidden:
                string_status += f'"{obj}" is hidden.\n'
            
            if len(objects_hidden) != 0:
                string_status = string_status[:-1]
        else: 
            string_status = (
                f'{issues_found} issues found. No objects with animated '
                'visibility found.'
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 15 - Non Deformer History
def check_non_deformer_history():
    """Validate non-deformer history in scene."""
    item_name = checklist_items.get(15)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items.get(15)[1]
    
    try:
        objects_non_deformer_history = []
        possible_objects_non_deformer_history = []

        objects_to_check = []
        objects_to_check.extend(cmds.ls(typ='nurbsSurface') or [])
        objects_to_check.extend(cmds.ls(typ='mesh') or [])
        objects_to_check.extend(cmds.ls(typ='subdiv') or [])
        objects_to_check.extend(cmds.ls(typ='nurbsCurve') or [])
        
        # Check if no objects exist - show green instead of N/A
        if len(objects_to_check) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No geometry objects found in scene.'
                )
            )
            cmds.text("output_" + item_id, e=True, l="0")
            return (f'\n*** {item_name} ***\n'
                    '0 issues found. No geometry objects in scene.')
        
        not_history_nodes = [
            'tweak', 'expression', 'unitConversion', 'time', 'objectSet', 
            'reference', 'polyTweak', 'blendShape', 'groupId', 'renderLayer', 
            'renderLayerManager', 'shadingEngine', 'displayLayer', 'skinCluster', 
            'groupParts', 'mentalraySubdivApprox', 'proximityWrap', 'cluster', 
            'cMuscleSystem', 'timeToUnitConversion', 'deltaMush', 'tension', 
            'wire', 'wrinkle', 'softMod', 'jiggle', 'diskCache', 'leastSquaresModifier'
        ]
        
        possible_not_history_nodes = [
            'nonLinear', 'ffd', 'curveWarp', 'wrap', 'shrinkWrap', 
            'sculpt', 'textureDeformer'
        ]
        
        # Find Offenders
        for obj in objects_to_check:
            try:
                history = cmds.listHistory(obj, pdo=1) or []
                for node in history:
                    node_type = cmds.nodeType(node)
                    
                    if (node_type not in not_history_nodes and 
                        node_type not in possible_not_history_nodes):
                        if obj not in objects_non_deformer_history:
                            objects_non_deformer_history.append(obj)
                    
                    if node_type in possible_not_history_nodes:
                        if obj not in possible_objects_non_deformer_history:
                            possible_objects_non_deformer_history.append(obj)
            except Exception:
                continue

        # Manage Strings
        cancel_message = 'Ignore Issue'
        buttons_to_add = []
        
        if len(possible_objects_non_deformer_history) == 1:
            patch_message_warning = (
                f'{len(possible_objects_non_deformer_history)} object contains '
                'deformers often used for modeling.\n'
            )
        else:
            patch_message_warning = (
                f'{len(possible_objects_non_deformer_history)} objects contain '
                'deformers often used for modeling.\n'
            )
        
        if len(objects_non_deformer_history) == 1:
            patch_message_error = (
                f'{len(objects_non_deformer_history)} object contains '
                'non-deformer history.\n'
            )
        else:
            patch_message_error = (
                f'{len(objects_non_deformer_history)} objects contain '
                'non-deformer history.\n'
            )
            
        # Manage Message
        patch_message = ''
                
        if (len(possible_objects_non_deformer_history) != 0 and 
            len(objects_non_deformer_history) == 0):
            cmds.text(
                "output_" + item_id,
                e=True,
                l=f'[ {len(possible_objects_non_deformer_history)} ]'
            )
            patch_message = patch_message_warning
            cancel_message = 'Ignore Warning'
            buttons_to_add.append('Select Objects With Suspicious Deformers')
        elif len(objects_non_deformer_history) == 0:
            cmds.text(
                "output_" + item_id,
                e=True,
                l=str(len(possible_objects_non_deformer_history))
            )
            patch_message = patch_message_warning
            cancel_message = 'Ignore Warning'
            buttons_to_add.append('Select Objects With Suspicious Deformers')
        elif len(possible_objects_non_deformer_history) == 0:
            cmds.text(
                "output_" + item_id,
                e=True,
                l=str(len(objects_non_deformer_history))
            )
            patch_message = patch_message_error
            buttons_to_add.append('Select Objects With Non-deformer History')
        else:
            cmds.text(
                "output_" + item_id,
                e=True,
                l=f"{len(objects_non_deformer_history)} + "
                  f"[ {len(possible_objects_non_deformer_history)} ]"
            )
            patch_message = f"{patch_message_error}\n\n{patch_message_warning}"
            buttons_to_add.append('Select Objects With Suspicious Deformers')
            buttons_to_add.append('Select Objects With Non-deformer History')
        
        assembled_message = ['OK']
        assembled_message.extend(buttons_to_add)
        assembled_message.append(cancel_message)
        
        # Manage State
        if (len(possible_objects_non_deformer_history) != 0 and 
            len(objects_non_deformer_history) == 0):
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=warning_color,
                l='',
                c=lambda args: warning_non_deformer_history()
            )
            issues_found = 0
        elif len(objects_non_deformer_history) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No objects with non-deformer history were found.'
                )
            )
            issues_found = 0
        else: 
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=error_color,
                l='?',
                c=lambda args: warning_non_deformer_history()
            )
            issues_found = len(objects_non_deformer_history)

        # Patch Function
        def warning_non_deformer_history():
            """Display non-deformer history warning dialog."""
            user_input = cmds.confirmDialog(
                title=item_name,
                message=patch_message,
                button=assembled_message,
                defaultButton='OK',
                cancelButton='Ignore Issue',
                dismissString='Ignore Issue', 
                icon="warning"
            )
                        
            if user_input == 'Select Objects With Non-deformer History':
                try:
                    cmds.select(objects_non_deformer_history)
                except Exception:
                    print("Could not select objects")
            elif user_input == 'Select Objects With Suspicious Deformers':
                try:
                    cmds.select(possible_objects_non_deformer_history)
                except Exception:
                    print("Could not select objects")
            elif user_input == 'Ignore Warning':
                cmds.button("status_" + item_id, e=True, bgc=pass_color, l='')
            else:
                cmds.button("status_" + item_id, e=True, l='')
        
        # Return string for report
        issue_string = "issues" if issues_found != 1 else "issue"
        
        if issues_found > 0 or len(possible_objects_non_deformer_history) > 0:
            string_status = f'{issues_found} {issue_string} found.\n'
            for obj in objects_non_deformer_history:
                string_status += f'"{obj}" contains non-deformer history.\n'
            
            if (len(objects_non_deformer_history) != 0 and 
                len(possible_objects_non_deformer_history) == 0):
                string_status = string_status[:-1]
            
            for obj in possible_objects_non_deformer_history:
                string_status += (
                    f'"{obj}" contains deformers often used for modeling.\n'
                )
            
            if len(possible_objects_non_deformer_history) != 0:
                string_status = string_status[:-1]
        else: 
            string_status = (
                f'{issues_found} issues found. No objects with non-deformer '
                'history!'
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 16 - Textures Color Space
def check_textures_color_space():
    """Validate texture color space assignments."""
    item_name = checklist_items.get(16)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items.get(16)[1]
    
    try:
        objects_wrong_color_space = []
        possible_objects_wrong_color_space = []
        
        # These types return an error instead of warning
        error_types = [
            'RedshiftMaterial', 'RedshiftArchitectural', 'RedshiftDisplacement',
            'RedshiftColorCorrection', 'RedshiftBumpMap', 'RedshiftSkin',
            'RedshiftSubSurfaceScatter', 'aiStandardSurface', 'aiFlat',
            'aiCarPaint', 'aiBump2d', 'aiToon', 'aiBump3d', 'aiAmbientOcclusion',
            'displacementShader'
        ]
            
        # If type starts with any of these strings it will be tested
        check_types = [
            'Redshift', 'ai', 'lambert', 'blinn', 'phong', 'useBackground',
            'checker', 'ramp', 'volumeShader', 'displacementShader',
            'anisotropic', 'bump2d'
        ]
        
        # These types and connections are allowed to be float3 even though it's raw
        float3_to_float_exceptions = {
            'RedshiftBumpMap': 'input',
            'RedshiftDisplacement': 'texMap'
        }

        # Count Textures
        all_file_nodes = cmds.ls(type="file")
        
        # Check if no file nodes exist - show green instead of N/A
        if len(all_file_nodes) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No file texture nodes found in scene.'
                )
            )
            cmds.text("output_" + item_id, e=True, l="0")
            return (f'\n*** {item_name} ***\n'
                    '0 issues found. No file texture nodes in scene.')
        
        for file_node in all_file_nodes:
            try:
                color_space = cmds.getAttr(file_node + '.colorSpace')
                
                has_suspicious_connection = False
                has_error_node_type = False
                
                input_node_connections = (
                    cmds.listConnections(
                        file_node, destination=True, source=False, plugs=True
                    ) or []
                )
                
                suspicious_connections = []
                
                if color_space.lower() == 'raw':
                    for in_con in input_node_connections:
                        node = in_con.split('.')[0]
                        node_in_con = in_con.split('.')[1]
                        
                        node_type = cmds.objectType(node)
                        
                        if node_type in error_types:
                            has_error_node_type = True
                        
                        should_be_checked = any(
                            node_type.startswith(types) for types in check_types
                        )
                        
                        if should_be_checked:
                            try:
                                data_type = cmds.getAttr(in_con, type=True)
                                if (data_type == 'float3' and 
                                    not (node_type in float3_to_float_exceptions and 
                                         node_in_con in float3_to_float_exceptions.values())):
                                    has_suspicious_connection = True
                                    suspicious_connections.append(in_con)
                            except Exception:
                                continue
                
                elif color_space.lower() == 'srgb':
                    for in_con in input_node_connections:
                        node = in_con.split('.')[0]
                        node_in_con = in_con.split('.')[1]
                        
                        node_type = cmds.objectType(node)
                        
                        if node_type in error_types:
                            has_error_node_type = True
                        
                        should_be_checked = any(
                            node_type.startswith(types) for types in check_types
                        )
                        
                        if should_be_checked:
                            try:
                                data_type = cmds.getAttr(in_con, type=True)
                                if data_type == 'float':
                                    has_suspicious_connection = True
                                    suspicious_connections.append(in_con)
                                
                                if (node_type in float3_to_float_exceptions and 
                                    node_in_con in float3_to_float_exceptions.values()):
                                    has_suspicious_connection = True
                                    suspicious_connections.append(in_con)
                            except Exception:
                                continue
                      
                if has_suspicious_connection:
                    if has_error_node_type:
                        objects_wrong_color_space.append([file_node, suspicious_connections])
                    else:
                        possible_objects_wrong_color_space.append([file_node, suspicious_connections])
            except Exception:
                continue
        
        # Manage UI Status
        if (len(possible_objects_wrong_color_space) != 0 and 
            len(objects_wrong_color_space) == 0):
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=warning_color,
                l='',
                c=lambda args: warning_textures_color_space()
            )
            issues_found = 0
            cmds.text(
                "output_" + item_id,
                e=True,
                l=f'[ {len(possible_objects_wrong_color_space)} ]'
            )
        elif len(objects_wrong_color_space) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    'No color space issues were found.'
                )
            )
            issues_found = 0
            cmds.text("output_" + item_id, e=True, l="0")
        else: 
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=error_color,
                l='?',
                c=lambda args: warning_textures_color_space()
            )
            issues_found = len(objects_wrong_color_space)
            cmds.text(
                "output_" + item_id,
                e=True,
                l=f'{len(objects_wrong_color_space)} + '
                  f'[ {len(possible_objects_wrong_color_space)} ]'
            )

        # Patch Function
        def warning_textures_color_space():
            """Display texture color space warning dialog."""
            message_parts = []
            
            if len(objects_wrong_color_space) > 0:
                if len(objects_wrong_color_space) == 1:
                    message_parts.append(
                        '1 file node is using incorrect color space.'
                    )
                else:
                    message_parts.append(
                        f'{len(objects_wrong_color_space)} file nodes are using '
                        'incorrect color space.'
                    )
            
            if len(possible_objects_wrong_color_space) > 0:
                if len(possible_objects_wrong_color_space) == 1:
                    message_parts.append(
                        '1 file node might be using incorrect color space.'
                    )
                else:
                    message_parts.append(
                        f'{len(possible_objects_wrong_color_space)} file nodes '
                        'might be using incorrect color space.'
                    )
            
            patch_message = '\n'.join(message_parts)
            patch_message += '\n\n(Generate full report for complete details)'
            
            user_input = cmds.confirmDialog(
                title=item_name,
                message=patch_message,
                button=['OK', 'Select File Nodes', 'Ignore Issue'],
                defaultButton='OK',
                cancelButton='Ignore Issue',
                dismissString='Ignore Issue', 
                icon="warning" if issues_found > 0 else "information"
            )
            
            if user_input == 'Select File Nodes':
                try:
                    cmds.select(clear=True)
                    for obj in objects_wrong_color_space:
                        cmds.select(obj[0], add=True)
                    for obj in possible_objects_wrong_color_space:
                        cmds.select(obj[0], add=True)
                except Exception:
                    print("Could not select file nodes")
            elif user_input == 'Ignore Issue':
                cmds.button("status_" + item_id, e=True, l='')
        
        # Return string for report
        issue_string = "issues" if issues_found != 1 else "issue"
        
        if issues_found > 0 or len(possible_objects_wrong_color_space) > 0:
            string_status = f'{issues_found} {issue_string} found.\n'
            
            for obj in objects_wrong_color_space:
                try:
                    color_space = cmds.getAttr(obj[0] + '.colorSpace')
                    string_status += (
                        f'"{obj[0]}" is using color space ({color_space}) '
                        'that is not appropriate for its connection.\n'
                    )
                    for connection in obj[1]:
                        string_status += f'   "{connection}" triggered this error.\n'
                except Exception:
                    string_status += f'"{obj[0]}" has color space issues.\n'
            
            for obj in possible_objects_wrong_color_space:
                try:
                    color_space = cmds.getAttr(obj[0] + '.colorSpace')
                    string_status += (
                        f'"{obj[0]}" might be using color space ({color_space}) '
                        'that is not appropriate for its connection.\n'
                    )
                    for connection in obj[1]:
                        string_status += f'   "{connection}" triggered this warning.\n'
                except Exception:
                    string_status += f'"{obj[0]}" might have color space issues.\n'
            
            if string_status.endswith('\n'):
                string_status = string_status[:-1]
        else: 
            string_status = (
                f'{issues_found} issues found. No color space issues were found!'
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 17 - AI Shadow Casting Lights
def check_ai_shadow_casting_lights():
    """Validate AI shadow casting lights setup."""
    item_name = checklist_items.get(17)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_value = checklist_items.get(17)[1]
    
    try:
        issues_found = 0
        warnings_found = 0
        error_messages = []
        warning_messages = []
        
        # Light types to check
        maya_light_types = ['pointLight', 'directionalLight', 'spotLight', 'areaLight', 'volumeLight', 'ambientLight']
        arnold_light_types = ['aiAreaLight', 'aiSkyDomeLight', 'aiPhotometricLight', 'aiMeshLight', 'aiLightPortal']
        
        all_lights = []
        for light_type in maya_light_types + arnold_light_types:
            all_lights.extend(cmds.ls(type=light_type) or [])
        
        if len(all_lights) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message('No lights found in scene.')
            )
            cmds.text("output_" + item_id, e=True, l="0")
            return f'\n*** {item_name} ***\n0 issues found. No lights in scene.'
        
        # Check total light count (warning if > 4)
        if len(all_lights) > 4:
            warnings_found += 1
            warning_messages.append(f"Scene has {len(all_lights)-4} lights (more than the recommended for 3-point setup)")
        
        # Categorize lights
        skydome_lights = []
        key_lights = []
        shadow_casting_lights = []
        non_key_shadow_casters = []
        
        for light in all_lights:
            light_type = cmds.nodeType(light)
            
            # Check if it's a skydome
            if light_type == 'aiSkyDomeLight':
                skydome_lights.append(light)
            
            # Check if it's a key light (case insensitive)
            is_key_light = 'key' in light.lower()
            if is_key_light:
                key_lights.append(light)
            
            # Check shadow casting (check both castShadows and aiCastShadows for all lights)
            casts_shadows = False
            try:
                # Check aiCastShadows first (for Arnold)
                if cmds.attributeQuery('aiCastShadows', node=light, exists=True):
                    casts_shadows = cmds.getAttr(light + '.aiCastShadows')
                else:
                    # Fallback to regular castShadows
                    casts_shadows = cmds.getAttr(light + '.castShadows')
                
                if casts_shadows:
                    shadow_casting_lights.append(light)
                    # Non-key lights casting shadows should be warned
                    if not is_key_light and light_type != 'aiSkyDomeLight':
                        non_key_shadow_casters.append(light)
            except Exception:
                continue
        
        # Validation checks
        
        # 1. Must have exactly one skydome
        if len(skydome_lights) == 0:
            error_messages.append("No aiSkyDomeLight found in scene")
            issues_found += 1
        elif len(skydome_lights) > 1:
            error_messages.append(f"Multiple aiSkyDomeLights found: {skydome_lights}")
            issues_found += 1
        
        # 2. Should have exactly 1 key light
        if len(key_lights) == 0:
            error_messages.append("No 'key' light found for 3-point light setup")
            issues_found += 1
        elif len(key_lights) > 1:
            error_messages.append(f"There should only be 1 key light for the 3-point light setup (found {len(key_lights)})")
            issues_found += 1
        
        # 3. Only skydome and key lights should cast shadows
        if len(non_key_shadow_casters) > 0:
            warnings_found += 1
            warning_messages.append(f"Non-key lights casting shadows: {non_key_shadow_casters}")
        
        # 4. Check total shadow casters (should be max 2: skydome + 1 key)
        max_allowed_shadow_casters = 2
        if len(shadow_casting_lights) > max_allowed_shadow_casters:
            if len(shadow_casting_lights) == 1:
                error_messages.append("Only one light should be casting shadows")
            else:
                error_messages.append(f"Only {max_allowed_shadow_casters} lights should be casting shadows (found {len(shadow_casting_lights)})")
            issues_found += 1
        
        # Update UI based on results
        if issues_found > 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=error_color,
                l='?',
                c=lambda args: warning_ai_shadow_casting_lights()
            )
        elif warnings_found > 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=warning_color,
                l='!',
                c=lambda args: warning_ai_shadow_casting_lights()
            )
        else:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    f'Light setup is correct. Total lights: {len(all_lights)}, '
                    f'Skydome: {len(skydome_lights)}, Key lights: {len(key_lights)}, '
                    f'Shadow casters: {len(shadow_casting_lights)}'
                )
            )
        
        cmds.text("output_" + item_id, e=True, l=str(issues_found + warnings_found))
        
        # Patch Function
        def warning_ai_shadow_casting_lights():
            """Display AI shadow casting lights warning dialog."""
            all_messages = []
            all_messages.extend(error_messages)
            all_messages.extend(warning_messages)
            
            patch_message = '\n'.join(all_messages) if all_messages else "Light setup issues found."
            patch_message += '\n\n(Generate full report for complete details)'
            
            button_text = 'Select Problem Lights' if non_key_shadow_casters else 'OK'
            buttons = ['OK', button_text, 'Ignore Issue'] if non_key_shadow_casters else ['OK', 'Ignore Issue']
            
            user_input = cmds.confirmDialog(
                title=item_name,
                message=patch_message,
                button=buttons,
                defaultButton='OK',
                cancelButton='Ignore Issue',
                dismissString='Ignore Issue', 
                icon="warning" if issues_found > 0 else "information"
            )
            
            if user_input == 'Select Problem Lights':
                try:
                    if non_key_shadow_casters:
                        cmds.select(non_key_shadow_casters)
                    else:
                        cmds.select(clear=True)
                except Exception:
                    print("Could not select lights")
            elif user_input == 'Ignore Issue':
                cmds.button("status_" + item_id, e=True, l='')
        
        # Return string for report
        total_issues = issues_found + warnings_found
        if total_issues > 0:
            string_status = f'{issues_found} {"issue" if issues_found == 1 else "issues"} found,\n{warnings_found} {"warning" if warnings_found == 1 else "warnings"} found.\n'
            string_status += f'Total lights in scene: {len(all_lights)}\n'
            string_status += f'Skydome lights: {len(skydome_lights)}\n'
            string_status += f'Key lights: {len(key_lights)}\n'
            string_status += f'Shadow casting lights: {len(shadow_casting_lights)}, {shadow_casting_lights}\n'
            
            for msg in error_messages:
                string_status += f'Issues: {msg}\n'
            for msg in warning_messages:
                string_status += f'Warning: {msg}\n'
            
            string_status = string_status.rstrip('\n')
        else:
            string_status = (
                f'0 issues found. Light setup is correct.\n'
                f'Total lights: {len(all_lights)}, Skydome: {len(skydome_lights)}, '
                f'Key lights: {len(key_lights)}, Shadow casters: {len(shadow_casting_lights)}'
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# Item 18 - Camera Aspect Ratio
def check_camera_aspect_ratio():
    """Validate camera aspect ratios."""
    item_name = checklist_items.get(18)[0]
    item_id = item_name.lower().replace(" ", "_").replace("-", "_")
    expected_values = checklist_items.get(18)[1]
    
    try:
        issues_found = 0
        offending_cameras = []
        default_cameras = ['persp', 'top', 'front', 'side']
        
        # Get all cameras excluding defaults
        all_cameras = cmds.ls(type='camera') or []
        user_cameras = []
        
        for cam in all_cameras:
            # Get transform node
            transform = cmds.listRelatives(cam, parent=True)[0] if cmds.listRelatives(cam, parent=True) else cam
            if transform not in default_cameras:
                user_cameras.append(transform)
        
        if len(user_cameras) == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message('No user cameras found in scene.')
            )
            cmds.text("output_" + item_id, e=True, l="0")
            return f'\n*** {item_name} ***\n0 issues found. No user cameras in scene.'
        
        # Get render resolution
        render_width = cmds.getAttr("defaultResolution.width")
        render_height = cmds.getAttr("defaultResolution.height")
        render_aspect = render_width / render_height if render_height > 0 else 0
        
        # Check each user camera
        for cam_transform in user_cameras:
            try:
                # Get camera shape
                cam_shape = cmds.listRelatives(cam_transform, shapes=True, type='camera')[0]
                
                # Get film aperture
                h_aperture = cmds.getAttr(cam_shape + '.horizontalFilmAperture')
                v_aperture = cmds.getAttr(cam_shape + '.verticalFilmAperture')
                
                if v_aperture > 0:
                    film_aspect = h_aperture / v_aperture
                    
                    # Check if film aspect is exactly 1.77 or 1.78
                    film_aspect_rounded = round(film_aspect, 2)
                    if film_aspect_rounded not in [1.77, 1.78]:
                        offending_cameras.append(cam_transform)
                        issues_found += 1
                    
                    # Also check if it matches render aspect (with tolerance)
                    render_aspect_rounded = round(render_aspect, 2)
                    if render_aspect_rounded not in [1.77, 1.78]:
                        if cam_transform not in offending_cameras:
                            offending_cameras.append(cam_transform)
                            issues_found += 1
                else:
                    offending_cameras.append(cam_transform)
                    issues_found += 1
                    
            except Exception:
                offending_cameras.append(cam_transform)
                issues_found += 1
        
        # Update UI
        if issues_found == 0:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=pass_color,
                l='',
                c=lambda args: print_message(
                    f'All {len(user_cameras)} user cameras have correct 16:9 aspect ratio.'
                )
            )
        else:
            cmds.button(
                "status_" + item_id,
                e=True,
                bgc=error_color,
                l='?',
                c=lambda args: warning_camera_aspect_ratio()
            )
        
        cmds.text("output_" + item_id, e=True, l=str(issues_found))
        
        # Patch Function
        def warning_camera_aspect_ratio():
            """Display camera aspect ratio warning dialog."""
            if len(offending_cameras) == 1:
                patch_message = f'1 camera does not have correct 16:9 aspect ratio (1.77 or 1.78).'
            else:
                patch_message = f'{len(offending_cameras)} cameras do not have correct 16:9 aspect ratio (1.77 or 1.78).'
            
            patch_message += f'\nRender resolution: {render_width}x{render_height} (aspect: {render_aspect:.2f})'
            patch_message += '\n\n(Generate full report for complete details)'
            
            user_input = cmds.confirmDialog(
                title=item_name,
                message=patch_message,
                button=['OK', 'Select Cameras', 'Ignore Issue'],
                defaultButton='OK',
                cancelButton='Ignore Issue',
                dismissString='Ignore Issue',
                icon="warning"
            )
            
            if user_input == 'Select Cameras':
                try:
                    if offending_cameras:
                        cmds.select(offending_cameras)
                    else:
                        cmds.select(clear=True)
                except Exception:
                    print("Could not select cameras")
            elif user_input == 'Ignore Issue':
                cmds.button("status_" + item_id, e=True, l='')
        
        # Return string for report
        if issues_found > 0:
            string_status = f'{issues_found} {"issue" if issues_found == 1 else "issues"} found.\n'
            string_status += f'Render resolution: {render_width}x{render_height} (aspect: {render_aspect:.2f})\n'
            for cam in offending_cameras:
                try:
                    cam_shape = cmds.listRelatives(cam, shapes=True, type='camera')[0]
                    h_aperture = cmds.getAttr(cam_shape + '.horizontalFilmAperture')
                    v_aperture = cmds.getAttr(cam_shape + '.verticalFilmAperture')
                    film_aspect = h_aperture / v_aperture if v_aperture > 0 else 0
                    string_status += f'"{cam}" film aspect: {film_aspect:.2f} (should be 1.77 or 1.78)\n'
                except Exception:
                    string_status += f'"{cam}" has aspect ratio issues\n'
            string_status = string_status.rstrip('\n')
        else:
            string_status = (
                f'0 issues found. All {len(user_cameras)} user cameras have correct 16:9 aspect ratio.\n'
                f'Render resolution: {render_width}x{render_height} (aspect: {render_aspect:.2f})'
            )
        
        return f'\n*** {item_name} ***\n{string_status}'
        
    except Exception as e:
        cmds.button(
            "status_" + item_id,
            e=True,
            bgc=exception_color
        )
        return f"Error checking {item_name}: {e}"


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def print_message(message, as_warning=False, as_heads_up_message=False):
    """Print messages in different formats."""
    if as_warning:
        cmds.warning(message)
    elif as_heads_up_message:
        cmds.headsUpMessage(message, verticalOffset=150, time=5.0)
    else:
        print(message)


def export_report_to_txt(report_list):
    """Export the full report to a text file."""
    temp_dir = cmds.internalVar(userTmpDir=True)
    txt_file = temp_dir + 'cmi_checklist_report.txt'
    
    with open(txt_file, 'w') as f:
        output_string = f"{script_name} Full Report v{script_version}:\n"
        output_string += "=" * 60 + "\n\n"
        
        for obj in report_list:
            if obj:  # Only add non-empty reports
                output_string = output_string + obj + "\n\n"
        
        f.write(output_string)

    # Try to open with notepad on Windows
    try:
        notepad_command = f'exec("notepad {txt_file}");'
        mel.eval(notepad_command)
    except Exception:
        print(f"Report saved to: {txt_file}")


def get_short_name(obj):
    """Get the name of objects without path."""
    if obj == '':
        return ''
    split_path = obj.split('|')
    if len(split_path) >= 1:
        short_name = split_path[len(split_path) - 1]
    return short_name


def _set_window_icon(window_name):
    """Set the window icon for the checklist."""
    try:
        qw = omui.MQtUtil.findWindow(window_name)
        if python_version == 3:
            widget = wrapInstance(int(qw), QWidget)
        else:
            widget = wrapInstance(long(qw), QWidget)
        icon = QIcon(':/checkboxOn.png')
        widget.setWindowIcon(icon)
    except Exception as e:
        print(f"Could not set window icon: {e}")


# ==============================================================================
# VERSION UTILITY FUNCTIONS
# ==============================================================================

def get_checklist_version_info():
    """
    Return version information for the checklist tool.
    
    Returns:
        dict: Dictionary containing version information
    """
    return {
        'tool_name': SCRIPT_NAME,
        'tool_version': SCRIPT_VERSION,
        'package_version': PACKAGE_VERSION,
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'window_title': WINDOW_TITLE
    }


# ==============================================================================
# CHECKLIST CONSTANTS
# ==============================================================================

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    """
    Main entry point for the CMI Modeling Checklist tool.
    
    This function serves as the standard entry point when the module is called
    from Maya's script editor or shelf buttons. It launches the main GUI.
    """
    build_gui_ats_cmi_modeling_checklist()


def run():
    """
    Alternative entry point (alias for main).
    Provides compatibility for different calling conventions.
    """
    main()


# Run the tool when called directly
if __name__ == "__main__":
    main()
