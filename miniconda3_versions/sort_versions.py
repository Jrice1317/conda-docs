from pathlib import Path
from functools import cmp_to_key

def sort_directories_by_version(path_releases: Path) -> list:
    """
    Sort Miniconda version directories from newest to oldest based on version
    """    
    def parse_version_string(version_string):
        version = {
            "major": 0,
            "minor": 0,
            "patch": 0,
            "build": 0
        }

        version_split = version_string.split('.')
        if len(version_split) != 3:
            raise Exception
        
        version["major"] = int(version_split[0])
        version["minor"] = int(version_split[1])
        patch_build = version_split[2].split('-')
        version["patch"] = int(patch_build[0])
        if len(patch_build) == 2:
            version["build"] = int(patch_build[1])
        return version

    def compare_version(x, y):
        if x["major"] != y["major"]:
            return 1 if x["major"] < y["major"] else -1
        if x["minor"] != y["minor"]:
            return 1 if x["minor"] < y["minor"] else -1
        if x["patch"] != y["patch"]:
            return 1 if x["patch"] < y["patch"] else -1
        if x["build"] != y["build"]:
            return 1 if x["build"] < y["build"] else -1
        return 0

    versions = []
    for release in path_releases.iterdir():
        if not release.is_dir():
            continue
        try:
            versions.append({'name': release.name})
            versions[-1].update(parse_version_string(release.name))
        except Exception:
            continue
  
    versions_sorted = sorted(versions, key=cmp_to_key(compare_version))
    return [version["name"] for version in versions_sorted]
    