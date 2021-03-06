#!/usr/bin/env python
#
# Copyright 2013 Greg Neagle
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path

from autopkglib import Processor, ProcessorError
from DmgMounter import DmgMounter
import FoundationPlist

__all__ = ["Versioner"]


class Versioner(DmgMounter):
    """Returns version information from a plist"""
    input_variables = {
        "input_plist_path": {
            "required": True,
            "description": 
                ("File path to a plist. Can point to a path inside a .dmg "
                 "which will be mounted."),
        },
        "plist_version_key": {
            "required": False,
            "description": 
                ("Which plist key to use; defaults to "
                "CFBundleShortVersionString"),
        },
    }
    output_variables = {
        "version": {
            "description": "Version of the item.",
        },
    }
    description = __doc__


    def main(self):
        # Check if we're trying to read something inside a dmg.
        (dmg_path, dmg, dmg_source_path) = self.env[
            'input_plist_path'].partition(".dmg/")
        dmg_path += ".dmg"
        try:
            if dmg:
                # Mount dmg and copy path inside.
                mount_point = self.mount(dmg_path)
                input_plist_path = os.path.join(mount_point, dmg_source_path)
            else:
                # just use the given path
                input_plist_path = self.env['input_plist_path']
            try:
                plist = FoundationPlist.readPlist(input_plist_path)
                version_key = self.env.get(
                    "plist_version_key", "CFBundleShortVersionString")
                self.env['version'] = plist.get(version_key, "UNKNOWN_VERSION")
                self.output("Found version %s in file %s" 
                            % (self.env['version'], input_plist_path))
            except FoundationPlist.FoundationPlistException, err:
                raise ProcessorError(err)

        finally:
            if dmg:
                self.unmount(dmg_path)


if __name__ == '__main__':
    processor = Versioner()
    processor.execute_shell()

    