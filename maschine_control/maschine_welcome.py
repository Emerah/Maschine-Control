# MIDI Remote Scripts
# maschine / ableton
#
# maschine_welcome.py
#
# created by Ahmed Emerah - (MaXaR)
# NI user name: Emerah
# NI: Machine MK3, KK S49 MK2, Komplete 12.
# email: ahmed.emerah@icloud.com
#
# developed under macOS 10.15.x and 10.14.6
# python version: python 2.7.17
# live version: 10.1.9
# tools: VS Code (Free)
#

from __future__ import absolute_import, print_function, unicode_literals

from random import choice

from ableton.v2.base import task
from ableton.v2.control_surface.component import Component
from ableton.v2.control_surface.control.button import ButtonControl
from ableton.v2.control_surface.control.control_list import control_list
from explor.maschine_skin import MaschineIndexedColor
# import time
# from functools import partial


class MaschineWelcome(Component):

    """
    this component will accomplish 2 things:
        - run a sequence of colored light through maschine mkiii pads and group buttons
        - display a welcome message on maschine mkiii screens: 'Welcome to Maschine MKiii - Ableton Live (version)'
    """

    pads = control_list(ButtonControl, color='DefaultButton.Off')
    group_buttons = control_list(ButtonControl, color='DefaultButton.Off')
    color_sequence = [MaschineIndexedColor.WARMYELLOW,
                      MaschineIndexedColor.BLUE,
                      MaschineIndexedColor.RED,
                      MaschineIndexedColor.CYAN,
                      MaschineIndexedColor.FUCHSIA,
                      MaschineIndexedColor.PURPLE,
                      MaschineIndexedColor.LIGHTORANGE,
                      MaschineIndexedColor.ORANGE]

    def __init__(self, *a, **k):
        super(MaschineWelcome, self).__init__(*a, **k)
        color_sequence_task = (task.wait(0.050), task.run(self._color_pad_buttons), task.wait(0.1), task.run(self._turn_pads_off),
                               task.wait(0.050), task.run(self._color_pad_buttons), task.wait(0.3), task.run(self._turn_pads_off))

        self._color_task = self._tasks.add(task.sequence(*color_sequence_task))

    def _color_pad_buttons(self):
        color1 = choice(self.color_sequence[:4])
        color2 = choice(self.color_sequence[4:])
        for button in list(self.pads)[:8]:
            button.color = color1
        for button in list(self.pads)[8:]:
            button.color = color2
        for button in list(self.group_buttons)[:4]:
            button.color = color2
        for button in list(self.group_buttons)[4:]:
            button.color = color1

    def _turn_pads_off(self):
        for button in list(self.pads):
            button.color = MaschineIndexedColor.BLACK
        for button in list(self.group_buttons):
            button.color = MaschineIndexedColor.BLACK

    def set_pads(self, buttons):
        self.pads.set_control_element(buttons)

    def set_group_buttons(self, buttons):
        self.group_buttons.set_control_element(buttons)
