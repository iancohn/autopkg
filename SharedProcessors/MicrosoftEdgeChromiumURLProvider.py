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

from autopkglib import Processor, ProcessorError
import urllib2 as urllib
import json

MSEDGE_URL_FEED = "https://edgeupdates.microsoft.com/api/products?view=enterprise"

__all__ = ["MicrosoftEdgeChromiumURLProvider"]

#Define Options
PLATFORM_OPT = [
    "Windows",
    "MacOS"#,
    # Commenting out 'Any' as it should not be needed in production
    #"Any"
    ]
ARCHITECTURE_OPT = ["x86","x64"]
PRODUCT_OPT = [
    "Dev",
    "Beta",
    "Stable"#,
    # Commenting out 'EdgeUpdate' and 'Policy' as they should not be needed in production
    #"EdgeUpdate",
    # "Policy"
    ]

class MicrosoftEdgeChromiumURLProvider(Processor):
    ("Scrap Microsoft's feed for the url path to the latest release of Microsoft Edge (Chromium).")
    description = __doc__
    input_variables = {
        "PLATFORM": {
            "required": True,
            "default": "Windows",
            "description": (
                "Which Product / Branch to download. "
                "Options: {}".format(PLATFORM_OPT)
            )
        },
        "ARCHITECTURE": {
            "required": False,
            "default": "x64",
            "description": (
                "Which Architecture to download. "
                "Options: {}".format(ARCHITECTURE_OPT)
            )
        },
        "PRODUCT": {
            "required": False,
            "default": "Stable",
            "description": (
                "Which Product / Branch to download. "
                "Options: {}".format(PRODUCT_OPT)
            )
        }
    }
    output_variables = {
        "url": {"description": "The URL of the latest released version of the given branch"},
        "installer_version": {"description": "Platform and version details as a concatenated string."},
        "Hash": {"description": "The value of the installer hash"},
        "HashAlgorithm": {"description": "The algorithm type of the hash"},
        "SizeInBytes": {"description": "The size in bytes of the installer"},
        "installer_type": {"description": "The file type of the installer"},
        "PublishedTime": {"description": "The time when the installer was published"}
    }

    def main(self):
        self.output("Available Platforms: {}".format(PLATFORM_OPT))
        platform = self.env.get("PLATFORM")

        self.output("Available Architectures: {}".format(ARCHITECTURE_OPT))
        architecture = self.env.get("ARCHITECTURE") or self.input_variables["ARCHITECTURE"]["default"]

        self.output("Available Product Branches: {}".format(PRODUCT_OPT))
        product = self.env.get("PRODUCT") or self.input_variables["PRODUCT"]["default"]

        #installer_platform = platform + "-" + architecture + "-" + product

        blob = urllib.urlopen(MSEDGE_URL_FEED)
        feed_json = json.loads(blob)
        blob.close()

        # Select array item by product name
        for item in feed_json:
            if item["Product"] == product:
                selected_product = item

        # Select Architecture and and Platform
        releases = []
        for release in selected_product:
            if ((release["Platform"] == platform ) and (release["Architecture"] == architecture)):
                releases.add(release)

        # Sort releases, and select latest released
        latest_release = sorted(releases, key=lambda x: x["ProductVersion"], reverse=True )[0]

        # Return Values
        self.env["url"] = latest_release["Artifacts"][0]["Location"]
        self.env["installer_version"] = str(platform + "-" + architecture + "-v" + latest_release["ProductVersion"] + "-"+ product)
        self.env["Hash"] = latest_release["Artifacts"][0]["Hash"]
        self.env["HashAlgorithm"] = latest_release["Artifacts"][0]["HashAlgorithm"]
        self.env["SizeInBytes"] = latest_release["Artifacts"][0]["SizeInBytes"]
        self.env["installer_type"] = latest_release["Artifacts"][0]["ArtifactName"]
        self.env["PublishedTime"] = latest_release["PublishedTime"]

        self.output(
            "Got URL %s from Microsoft for package '%s':" % (self.env["url"], self.env["installer_version"])
        )

if __name__ == "__main__":
    PROCESSOR = MicrosoftEdgeChromiumURLProvider()
    PROCESSOR.execute_shell()
