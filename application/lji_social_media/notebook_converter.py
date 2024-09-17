import nbformat
from nbconvert import PythonExporter
import os
from pathlib import Path

# Load the notebook script
notebook_path = Path("~/Downloads/diesel_demand_all_countries.ipynb").expanduser()
script_path = Path("~/Downloads/diesel_demand_all_countries.py").expanduser()
with open(notebook_path) as f:
    notebook = nbformat.read(f, as_version=4)


# Convert to .py
python_exporter = PythonExporter()
python_script, _ = python_exporter.from_notebook_node(notebook)

# Save the python script
with open(script_path, "w") as f:
    f.write(python_script)
