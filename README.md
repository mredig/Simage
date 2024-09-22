# Simage

SIMilarIMAGEs.

run `python3 -m venv .` in the checked out directory. Activate the virtual environment with `source bin/activate`, then run `pip-sync`. This installs only in the current directory, keeping this environment localized.

1. Organize all photos you want to sort into a single directory
2. run `hasher.py` pointing at said directory and create a json file.
3. run `sorter.py` pointing at the directory and the json file. optionally sort images via mv/ln.

use `-h` with both scripts to get specifics of each.