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
"""Returns a spcified value given a supplied JSON string, schema, and path"""
#Import modules
from __future__ import absolute_import
from autopkglib import Processor, ProcessorError, URLGetter
import json
from platform import mac_ver
import urllib

BASE_URL = ('https://h20614.www2.hp.com/ediags/solutions/software/v3?'
               'os={OS}&'
               'ModelName={MODEL_NAME}&'
               'lc={LANGUAGE_CODE}&'
               'cc={COUNTRY_CODE}')

DEFAULT_OS = 'macOS ' + mac_ver()[0].split('.')[0] + '.' + mac_ver()[0].split('.')[1]

DEFAULT_MODEL = 'HP Color LaserJet M452dw'

__all__ = ["HPPrinterEssentialsURLProvider"]

class HPPrinterEssentialsURLProvider(URLGetter):
    """Scrape HP's feed for the url path to the latest release of HP Printer Essentials."""
    description = "Provides Download URL for HP Printer Essentials software"
    input_variables = {
        "OS": {
            "required": False,
            "default": DEFAULT_OS,
            "description": (
                "Which OS to retrieve the download url for. "
            )
        },
        "MODEL_NAME": {
            "required": False,
            "default": DEFAULT_MODEL,
            "description": (
                "Printer Model to download the software for. "
            )
        },
        "LANGUAGE_CODE": {
            "required": False,
            "default": "en",
            "description": (
                "The language code. "
            )
        },
        "COUNTRY_CODE": {
            "required": False,
            "default": "us",
            "description": (
                "The country code. "
            )
        }
    }
    output_variables = {
        "url": {"description": "The URL of the latest released version of the software"},
        "version": {"description": "The version of the software"},
        "title": {"description": "The software title"},
        "description": {"description": "The HP supplied description for the software"},
        "identifier": {"description": "The identifier of the selected software"}
    }

    __doc__ = description

    def main(self):

        OS = urllib.quote_plus(self.env.get("OS", self.input_variables["OS"]["default"]))
        MODEL_NAME = urllib.quote_plus(self.env.get("MODEL_NAME", self.input_variables["MODEL_NAME"]["default"]))
        LANGUAGE_CODE = self.env.get("LANGUAGE_CODE", self.input_variables["LANGUAGE_CODE"]["default"])
        COUNTRY_CODE = self.env.get("COUNTRY_CODE", self.input_variables["COUNTRY_CODE"]["default"])

        feed_url = BASE_URL.format(OS=OS, MODEL_NAME=MODEL_NAME,LANGUAGE_CODE=LANGUAGE_CODE,COUNTRY_CODE=COUNTRY_CODE)

        self.output("Retrieving URL Feed from %s." % feed_url)

        blob = self.download(feed_url)
        feed_json = json.loads(blob)

        self.output("Extracting JSON Values for %s - %s" % (OS, MODEL_NAME))

        try:
            item = None
            #select only the first result that returns with the correct Title
            for i in feed_json:
                if i["Title"] == "Essential Software":
                    item = i
                    break
            if item == None:
                raise ValueError("Software package with correct title not found")
            url = item["FtpURL"]
            version = item["Version"]
            title = item["Title"]
            description = item["Description"]
            identifier = item["Identifier"]

        except ValueError as v:
            raise v
        except Exception as e:
            raise e

        # Return Values
        self.env["url"] = url
        self.env["version"] = version
        self.env["title"] = title
        self.env["description"] = description
        self.env["identifier"] = identifier

if __name__ == "__main__":
    PROCESSOR = HPPrinterEssentialsURLProvider()
    PROCESSOR.execute_shell()
