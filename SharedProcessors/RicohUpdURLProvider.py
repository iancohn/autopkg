#!/usr/bin/python
#
# Copyright 2020 Ian Cohn <cohnic@gmail.com>
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

#Factored for Python 3
from __future__ import absolute_import


from autopkglib import Processor, ProcessorError, URLGetter
import json
import re

RICOH_URL = "http://support.ricoh.com/bb/html/dr_ut_e/rc3/model/p_i/p_i.htm"

__all__ = ["RicohUpdURLProvider"]

#Define Options


class RicohUpdURLProvider(URLGetter):
    """Scrape Ricoh's site for the latest version of x32 and x64 version of PCL and PostScript drivers."""
    description = "Provides Download URLs for Ricoh Drivers"
    input_variables = {}
    output_variables = {
        "pcl6_x64_url": {"description": "The URL of the latest released version of the given branch"},
        "raw_html": {"description": "RAW html output from Ricoh's site"}
    }

    __doc__ = description

    def main(self):

        self.output("Retrieving URL Feed from %s." % RICOH_URL)

        #feed_json = json.loads(blob)

        try:
            blob = self.download(RICOH_URL)
        except Exception as e:
            self.output("Unexpected JSON encountered.")
            raise e

        # Return Values
        self.env["raw_html"] = blob

if __name__ == "__main__":
    PROCESSOR = RicohUpdURLProvider()
    PROCESSOR.execute_shell()
