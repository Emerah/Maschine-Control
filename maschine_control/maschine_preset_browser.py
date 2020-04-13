#
# native instruments / ableton
# maschine_preset_browser.py
#
# created by Ahmed Emerah - (MaXaR)
#
# NI user name: Emerah
# NI: Machine MK3, KK S49 MK2, Komplete 12.
# email: ahmed.emerah@icloud.com
#
# developed using pythons 2.7.17 on macOS Mojave
# tools: VS Code (Free), PyCharm CE (Free)
#
from __future__ import absolute_import, print_function, unicode_literals


from ableton.v2.control_surface.component import Component


class MaschinePresetBrowser(Component):
    """
    this object enables hotswapping presets for the selected effect or instrument device

    how it will work on the hw controller level:
    in device control mode, user will click the 4-D encoder to enable hotswapping for the selected device.
    the Live browser will open if it were hidden, to the location of the current preset of the selected
    device. if no presets present for the device, a message will display on Maschine MKiii display that
    says 'no presets available'. else when presets are available, user will use the 4-D encoder to navigate
    the device presets. turn the encoder right to scroll down the preset list. turn the encoder left to scroll
    up the preset list.

    selecting a preset will play a preview of the sound when a preview is available.

    when the user found a sound they want to load, user will click the 4-D encoder again to load the preset and
    exit the preset browser mode.

    the preset list can be flattened. easier to implement but user lose access to cataegorized folders
    or the preset list could be displayed and accessed through folders [could also be nested folder].
    this is more complicated to implement and requires the use of extra controls to navigate the folders.

    a decision has to be made about whihc list style to utilize.

    """
    preset_scroller = None
    action_button = None
