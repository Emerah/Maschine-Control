#
# maschine / ableton
# __init__.py
#
# created by Ahmed Emerah - (MaXaR)
#
# NI user name: Emerah
# NI: Machine MK3, KK S49 MK2, Komplete 12.
# email: ahmed.emerah@icloud.com
#
# developed using python 2.7.17 on macOS Catalina
# tools: VS Code (Free)
#
from __future__ import absolute_import, print_function, unicode_literals

import os
import sys

from .maschine_control_surface import MaschineControlSurface

# ===============================================================================
#  create path
# ===============================================================================
outfilepath = (os.path.join(os.path.expanduser('~/Desktop')))
if not os.path.exists(outfilepath):
    os.mkdir(outfilepath)

# ===============================================================================
# set log files
# ===============================================================================
errorLog = open(os.path.join(outfilepath, "stderr.log"), "w")
errorLog.write("Starting Error Log\n")
sys.stderr = errorLog
stdoutLog = open(os.path.join(outfilepath, "stdout.log"), "w")
stdoutLog.write("Starting Standard Out Log\n")
sys.stdout = stdoutLog
# ===============================================================================


def create_instance(c_instance):
    return MaschineControlSurface(c_instance)
