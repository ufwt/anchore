#!/usr/bin/env python

import sys
import os
import re
import anchore.anchore_utils

gate_name = "SUIDDIFF"

try:
    config = anchore.anchore_utils.init_gate_cmdline(sys.argv, gate_name)
except Exception as err:
    print str(err)
    sys.exit(1)

if not config:
    sys.exit(0)

imgid = config['imgid']
imgdir = config['dirs']['imgdir']

try:
    params = config['params']
except:
    params = None

if config['meta']['usertype'] != 'user':
    sys.exit(0)

outlist = list()

imageId = config['imgid']
baseId = config['baseid']

diffdata = anchore.anchore_utils.diff_images(imageId, baseId)
try:
    isdiff = False
    pkgdiffs = diffdata.pop('file_suids', {}).pop('files.suids', {})
    for module_type in pkgdiffs.keys():
        for pkg in pkgdiffs[module_type].keys():
            isdiff = True
            status = pkgdiffs[module_type][pkg]
            if (status == 'VERSION_DIFF'):
                outlist.append("SUIDMODEDIFF SUID file mode in container is different from baseline for file - " + pkg)
            elif (status == 'INIMG_NOTINBASE'):
                outlist.append("SUIDFILEADD SUID file has been added to image since base - " + pkg)
            elif (status == 'INBASE_NOTINIMG'):
                outlist.append("SUIDFILEDEL SUID file has been removed from image since base - " + pkg)

    if (isdiff):
        outlist.append("SUIDDIFF SUID file manifest is different from image to base")
except Exception as err:
    print "ERROR: running gate " + gate_name + " failed: " + str(err)
    sys.exit(1)

if outlist:
    anchore.anchore_utils.save_gate_output(imageId, gate_name, outlist)

sys.exit(0)
