import urllib.request
import importlib.util

# Update the following variables with your GitHub information:
script_url = "https://raw.githubusercontent.com/your_username/your_repository/master/your_script.py"
script_name = "your_script.py"
shelf_file = "path/to/your/shelf.mel"

# Check the Python version
if sys.version_info.major == 2:
    # Python 2
    import urllib2 as url_lib
    import imp as import_module
else:
    # Python 3
    import urllib.request as url_lib
    import importlib.util as import_module

# Download the script from GitHub
response = url_lib.urlopen(script_url)
script_contents = response.read().decode()

# Save the downloaded script locally
with open(script_name, "w") as file:
    file.write(script_contents)

# Load the script in Maya
if sys.version_info.major == 2:
    # Python 2
    script_module = import_module.load_source(script_name, script_name)
else:
    # Python 3
    spec = import_module.spec_from_file_location(script_name, script_name)
    script_module = import_module.module_from_spec(spec)
    spec.loader.exec_module(script_module)

# Update the shelf button command with the new script
with open(shelf_file, "r") as file:
    shelf_contents = file.read()

# Replace "old_script.py" with the name of the previous script in the shelf file
updated_shelf_contents = shelf_contents.replace("old_script.py", script_name)

with open(shelf_file, "w") as file:
    file.write(updated_shelf_contents)
