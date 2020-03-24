#
# native instruments / ableton
# maschine_device_organizer.py
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
from ableton.v2.control_surface.control.button import ButtonControl


class MaschineDeviceOrganizer(Component):

    move_backward_button = ButtonControl(color='DefaultButton.Off')
    move_forward_button = ButtonControl(color='DefaultButton.Off')

    # todo: safe guard index range

    def __init__(self, *a, **k):
        super(MaschineDeviceOrganizer, self).__init__(*a, **k)
        self._device = None

    def set_device(self, device):
        self._device = device

    def set_move_backward_button(self, button):
        self.move_backward_button.set_control_element(button)

    def set_move_forward_button(self, button):
        self.move_forward_button.set_control_element(button)

    @move_backward_button.pressed
    def _on_move_backward_button_pressed(self, button):
        self.move_backward()

    @move_forward_button.pressed
    def _on_move_forward_button_pressed(self, button):
        self.move_forward()

    def move_backward(self):
        parent = self._device.canonical_parent
        device_index = list(parent.devices).index(self._device)
        if device_index > 0:
            self.song.move_device(self._device, parent, device_index - 1)

    def move_forward(self):
        parent = self._device.canonical_parent
        device_index = list(parent.devices).index(self._device)
        if device_index < len(parent.devices) - 1:
            self.song.move_device(self._device, parent, device_index + 2)

    def _move_out(self, rack, move_behind=False):
        pass

    def _move_in(self, rack, move_to_end=False):
        pass
