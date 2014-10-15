# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import tempfile
from build_pack_utils import BuildPack


def preprocess_commands(ctx):
    return ()


def service_commands(ctx):
    release_path = os.path.join(tempfile.gettempdir(), 'release.out')
    with open(release_path) as fp:
        webFound = False
        lines = []
        for line in fp.readlines():
            if line.startswith('  web:'):
                webFound = True
                lines.append(line.replace('  web:', '').strip())
            elif webFound and line.startswith('    '):
                lines.append(line.strip())
        proc = " ".join(lines)
    return {
        'web': [proc]
    }
        

def service_environment(ctx):
    return {}


def download(install, link):
    installer = install._installer
    ctx = install.builder._ctx
    installer.install_binary_direct(
        link,
        'NO HASH',  # skipping hash on purpose
        ctx['BUILD_DIR'])


def compile(install):
    ctx = install.builder._ctx
    # setup logs director for bp
    os.makedirs(os.path.join(ctx['BUILD_DIR'], 'logs'))
    # read links file
    with open(os.path.join(ctx['BUILD_DIR'], 'download-list.txt')) as fp:
        links = [line.strip() for line in fp.readlines()]
    # download links
    for link in links:
        if link.startswith('http'):
            download(install, link)
        else:
            print 'Not sure how to handle [%s], skipping.' % link
    # read build pack
    with open(os.path.join(ctx['BUILD_DIR'], 'build-pack.txt')) as fp:
        bp_link = fp.read().strip()
    if bp_link.find('#') >= 0:
        (bp_link, bp_ver) = bp_link.split('#')
        bp = BuildPack(ctx, bp_link, bp_ver)
    else:
        bp = BuildPack(ctx, bp_link)
    # run build pack
    bp._clone()
    bp._compile()
    # save output from release
    release_path = os.path.join(tempfile.gettempdir(), 'release.out')
    with open(release_path, 'wt') as fp:
        fp.write(bp._release())
    return 0
