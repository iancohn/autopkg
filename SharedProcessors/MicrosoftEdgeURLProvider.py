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

MSEDGE_URL_FEED = "https://edgeupdates.microsoft.com/api/products?view=enterprise"

__all__ = ["MicrosoftEdgeURLProvider"]

#Define Options
PLATFORM_OPT = [
    "Windows",
    "MacOS"#,
    # Commenting out 'Any' as it should not be needed in production
    #"Any"
    ]
ARCHITECTURE_OPT = [
    "x86",
    "x64"
]
PRODUCT_OPT = [
    "Dev",
    "Beta",
    "Stable"#,
    # Commenting out 'EdgeUpdate' and 'Policy' as they should not be needed in production
    #"EdgeUpdate",
    # "Policy"
    ]

class MicrosoftEdgeURLProvider(URLGetter):
    """Scrap Microsoft's feed for the url path to the latest release of Microsoft Edge (Chromium)."""
    description = "Provides Download URL for Microsoft Edge"
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
        "version": {"description": "The version of the installer"},
        "installer_version": {"description": "Platform and version details as a concatenated string."},
        "Hash": {"description": "The value of the installer hash"},
        "HashAlgorithm": {"description": "The algorithm type of the hash"},
        "SizeInBytes": {"description": "The size in bytes of the installer"},
        "installer_type": {"description": "The file type of the installer"},
        "PublishedTime": {"description": "The time when the installer was published"},
        "bes_installer_name": {"description": "BES Installer file name"}
    }

    __doc__ = description

    def main(self):

        platform = self.env.get("PLATFORM")
        architecture = self.env.get("ARCHITECTURE", self.input_variables["ARCHITECTURE"]["default"])
        product = self.env.get("PRODUCT", self.input_variables["PRODUCT"]["default"])

        self.output("Retrieving URL Feed from %s.") % MSEDGE_URL_FEED

        blob = self.download(MSEDGE_URL_FEED)
        feed_json = json.loads(blob)

        self.output("Extracting JSON Values for %s - %s - %s") % (platform, architecture, product)

        try:
        # Select array item by product name
            for item in feed_json:
                if item["Product"] == product:
                    selected_product = item["Releases"]
            self.output("Selected product")
        # Select Architecture and and Platform
            releases = []
            for release in selected_product:
                if ((release["Platform"] == platform ) and (release["Architecture"] == architecture)):
                    releases.append(release)
        # Sort releases, and select latest released
            latest_release = sorted(releases, key=lambda x: x["ProductVersion"], reverse=True )[0]
            url = latest_release["Artifacts"][0]["Location"]
            version = latest_release["ProductVersion"]
            installer_version = platform + "-" + architecture + "-v" + latest_release["ProductVersion"] + "-"+ product
            installer_type = latest_release["Artifacts"][0]["ArtifactName"]
            Hash = latest_release["Artifacts"][0]["Hash"]
            HashAlgorithm = latest_release["Artifacts"][0]["HashAlgorithm"]
            SizeInBytes = latest_release["Artifacts"][0]["SizeInBytes"]
            PublishedTime = latest_release["PublishedTime"]
        except Exception as e:
            self.output("Unexpected JSON encountered.")
            raise e

        # Return Values
        self.env["url"] = url
        self.env["version"] = version
        self.env["installer_version"] = installer_version
        self.env["Hash"] = Hash
        self.env["HashAlgorithm"] = HashAlgorithm
        self.env["SizeInBytes"] = SizeInBytes
        self.env["installer_type"] = installer_type
        self.env["PublishedTime"] = PublishedTime
        self.env["bes_installer_name"] = "PLACEHOLDER"

if __name__ == "__main__":
    PROCESSOR = MicrosoftEdgeURLProvider()
    PROCESSOR.execute_shell()
