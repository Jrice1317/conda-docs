#! /usr/bin/env python
"""
Create rst file with size, date and sha256 for miniconda installers.

"""

import urllib.request
import json
import datetime
import math
import os
import time
from packaging.version import Version
from pathlib import Path
from jinja2 import Template

HERE = Path(__file__).parent
OUT_FILENAME = HERE / "miniconda-hashes.rst"
TEMPLATE_FILENAME = HERE / "miniconda-hashes.rst.jinja2"


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi"]:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, "Yi", suffix)


def main():
    # =================================================================
    # The main hosting server is central time, so pretend we are too
    # in order for anyone to be able to run this on Unix platforms.
    os.environ['TZ'] = 'US/Central'
    time.tzset()
    # =================================================================

    FILES_URL = "https://repo.anaconda.com/miniconda/.files.json"
    with urllib.request.urlopen(urllib.request.Request(url=FILES_URL)) as f:
        data = json.loads(f.read().decode("utf-8"))
    # remove index.json and 'latest' entries
    data.pop("index.json")
    data = {k: v for k, v in data.items() if "latest" not in k and "uninstaller" not in k}

    # Load the Jinja template
    with open(TEMPLATE_FILENAME, "r") as template_file:
        template_content = template_file.read()
        template = Template(template_content)

    # Generate data for the template
    template_data = {
        "title": "Miniconda hash information",
        # "title_len": len(template_data["title"]),
        # "filename_len": FILENAME_LEN,
        # "size_len": SIZE_LEN,
        # "timemod_len": TIMEMOD_LEN,
        # "hash_len": HASH_LEN,
        "items": []
    }


    def sorting_key(filename):
        """
        Sort by:
          conda_version_platform_ext (e.g. "23.1.0-1-Linux-x86_64.sh")
          miniconda_prefix (e.g. "Miniconda3")
          py_version (e.g. the "310" from "py310")
        """
        # 1. conda_version_platform_ext
        version_str = filename.split("-")[1]
        # Starting with v4.8.2 in 2020, we release Miniconda variants for each 
        # python version we support: Miniconda3-py3XX_<version>-<platform>.<ext>
        # So we need to split that off.
        if "_" in version_str:
            version_str = version_str.split("_")[1]
        conda_version_platform_ext = version_str

        # 2. miniconda_prefix
        miniconda_prefix = filename.split("-")[0]

        # 3. py_version
        if "py" in filename:
            py_intermediate = filename.split("py")[1]
            py_version = int(py_intermediate.split("_")[0])
        else:
            py_version = ""

        return (Version(conda_version_platform_ext), miniconda_prefix, py_version)


    # We sort the 'data' dict by our special sorting_key() function,
    # which accounts for all the ways our Miniconda installers have
    # changed their naming format over the years.

    # Populate template_data["items"] list
    for filename in sorted(data, reverse=True, key=sorting_key):
        last_modified = datetime.datetime.fromtimestamp(
            math.floor(data[filename]["mtime"])
        )
        last_mod_str = (
            last_modified.date().isoformat() + " " + last_modified.time().isoformat()
        )
        if "sha256" not in data[filename]:
            print("WARNING: no sha256 information for:", filename)
            continue
        template_data["items"].append(
            {
                "filename": filename,
                "size": sizeof_fmt(data[filename]["size"]),
                "last_modified": last_mod_str,
                "sha256": data[filename]["sha256"]
            }
        )


    # Render the template with the data
    rst_text = template.render(template_data=template_data, items=template_data["items"])

    # Write the rendered content to the output RST file
    with open(OUT_FILENAME, "w") as rst_file:
        rst_file.write(rst_text) 


if __name__ == "__main__":
    main()
