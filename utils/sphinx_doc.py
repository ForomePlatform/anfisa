#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import logging
from subprocess import Popen, PIPE

#===============================================
class SphinxDocumentationSet:
    def __init__(self, title, path_source, path_build, path_url,
            top_index = "index.html"):
        self.mTitle = title
        self.mPathSource = path_source
        self.mPathBuild = path_build
        self.mPathUrl = path_url
        self.mTopIndex = top_index
        self.activate()

    def getTitle(self):
        return self.mTitle

    def getUrl(self, doc_name = None):
        if doc_name is None:
            doc_name = self.mTopIndex
        return self.mPathUrl + doc_name

    def activate(self):
        proc = Popen(["sphinx-build", "-b", "html", "-a", "-q",
            self.mPathSource, self.mPathBuild],
            stdout = PIPE, stderr = PIPE)
        s_outputs = proc.communicate()
        report = ["Spinx doc set %s activated:" % self.mPathSource]
        if s_outputs[0]:
            report.append("<stdout>")
            report.append(str(s_outputs[0], "utf-8"))
        if s_outputs[1]:
            report.append("<stderr>")
            report.append(str(s_outputs[1], "utf-8"))
        if len(report) == 1:
            report.append("<done>")
        logging.info("\n".join(report))
