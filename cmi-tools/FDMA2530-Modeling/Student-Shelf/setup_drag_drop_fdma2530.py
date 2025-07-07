"""
CMI Tools Shelf Installer v2.0.1 - OPTIMIZED ZIP DOWNLOAD
=========================================================
Drag-and-drop installer for CMI Tools student shelf system.
Fast ZIP-based installation following GT Tools architecture.

Cross-platform compatible: Windows, macOS, Linux
Maya versions: 2016-2025+ | Python 2/3 compatible

Created by: Alexander T. Santiago
Contact: asanti89@nmsu.edu
"""

import os
import sys
import shutil
import tempfile
import zipfile

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

import maya.cmds as cmds

__version__ = "2.0.1"

# Configuration - GitHub repository ZIP download
REPO_ZIP_URL = "https://github.com/Atsantiago/NMSU_Scripts/archive/refs/heads/master.zip"

def get_cmi_tools_root():
    """Get the cmi-tools root directory path"""
    maya_app_dir = cmds.internalVar(userAppDir=True)
    return os.path.join(maya_app_dir, "cmi-tools").replace('\\', '/')

def get_modules_dir():
    """Get Maya modules directory path"""
    maya_app_dir = cmds.internalVar(userAppDir=True)
    modules_dir = os.path.join(maya_app_dir, "modules")
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir)
    return modules_dir

def safe_download(url, timeout=30):
    """Download content from URL with error handling"""
    try:
        response = urlopen(url, timeout=timeout)
        content = response.read()
        return content
    except Exception as e:
        print("Download failed: {0}".format(e))
        return None

def download_and_extract_package(target_dir):
    """Download repo ZIP and extract to cmi-tools structure"""
    print("Downloading CMI Tools shelf package...")
    
    try:
        zip_data = safe_download(REPO_ZIP_URL)
        if not zip_data:
            return False
        
        # Create temp ZIP file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
            temp_zip.write(zip_data)
            temp_zip_path = temp_zip.name
        
        try:
            # Extract ZIP
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                temp_extract_dir = tempfile.mkdtemp(prefix="cmi_extract_")
                zip_ref.extractall(temp_extract_dir)
                
                # Find extracted repo
                extracted_repo = None
                for item in os.listdir(temp_extract_dir):
                    if item.startswith("NMSU_Scripts-"):
                        extracted_repo = os.path.join(temp_extract_dir, item)
                        break
                
                if not extracted_repo:
                    print("Could not find extracted repository")
                    return False
                
                # ----------------------------------------------------------
                # Source paths
                # ----------------------------------------------------------
                student_shelf_path = os.path.join(
                    extracted_repo, "cmi-tools", "FDMA2530-Modeling", "Student-Shelf"
                )
                source_package  = os.path.join(student_shelf_path, "fdma_shelf")
                source_config   = os.path.join(student_shelf_path, "shelf_config.json")
                source_manifest = os.path.join(
                    extracted_repo, "cmi-tools", "FDMA2530-Modeling", "releases.json"
                )  # ← NEW: manifest file
                # ----------------------------------------------------------
                
                # Create cmi-tools directory structure
                scripts_dir  = os.path.join(target_dir, "scripts")
                icons_dir    = os.path.join(target_dir, "icons") 
                shelves_dir  = os.path.join(target_dir, "shelves")
                
                for dir_path in [scripts_dir, icons_dir, shelves_dir]:
                    if not os.path.exists(dir_path):
                        os.makedirs(dir_path)
                
                # Copy package to scripts directory
                target_package = os.path.join(scripts_dir, "fdma_shelf")
                if os.path.exists(source_package):
                    if os.path.exists(target_package):
                        shutil.rmtree(target_package)
                    shutil.copytree(source_package, target_package)
                    print("Copied fdma_shelf package to scripts/")
                else:
                    print("Warning: fdma_shelf package not found in repository")
                    return False
                
                # Copy config to scripts directory
                if os.path.exists(source_config):
                    shutil.copy2(source_config, scripts_dir)
                    print("Copied shelf_config.json to scripts/")
                else:
                    print("Warning: shelf_config.json not found in repository")
                
                # ------------------------ NEW ----------------------------
                # Copy releases.json so version_utils can locate it
                if os.path.exists(source_manifest):
                    shutil.copy2(source_manifest, scripts_dir)
                    print("Copied releases.json to scripts/")
                else:
                    print("Warning: releases.json not found in repository")
                # ---------------------------------------------------------
                
                # Clean up temp extraction
                shutil.rmtree(temp_extract_dir)
            
            return True
            
        finally:
            os.unlink(temp_zip_path)
        
    except Exception as e:
        print("Package extraction failed: {0}".format(e))
        import traceback
        print(traceback.format_exc())
        return False
