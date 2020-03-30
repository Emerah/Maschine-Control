#
# native instruments / ableton
# maschine_device_navigation.py
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

from ableton.v2.base.event import listens
from ableton.v2.base.util import index_if
from ableton.v2.control_surface.components.device_navigation import DeviceNavigationComponent
from ableton.v2.control_surface.control.button import ButtonControl

from .maschine_device_organizer import MaschineDeviceOrganizer


class MaschineDeviceNavigation(DeviceNavigationComponent):
    """
    this object will observe the device chain on the selected track. it enables the users to:
        - select devices from the device chain for control
        - move devices backward and forward in the device chain
        - move devices in and out of a rack (when one exists in the device chain)
        - remove the selected device from the device chain.
    """

    # todo: paging buttons should page through by 8 and not 1
    # todo: add device resetting to default state
    # todo: may be add parameter randomizer too?

    next_device_button = ButtonControl(color='ItemNavigation.ItemNotSelected', pressed_color='ItemNavigation.ItemSelected')
    previous_device_button = ButtonControl(color='ItemNavigation.ItemNotSelected', pressed_color='ItemNavigation.ItemSelected')
    remove_device_button = ButtonControl(color='DefaultButton.Off', pressed_color='DefaultButton.On')

    def __init__(self, info_display=None, device_component=None, item_provider=None, *a, **k):
        assert info_display is not None
        self._info_display = info_display
        super(MaschineDeviceNavigation, self).__init__(device_component=device_component, item_provider=item_provider, *a, **k)
        self.__on_appointed_device_changed.subject = self.song
        self._device_organizer = MaschineDeviceOrganizer(parent=self, name='Device_Organizer')

    @property
    def first_device(self):
        index = self._get_selected_device_index()
        return index == 0

    @property
    def last_device(self):
        index = self._get_selected_device_index()
        return index == len(self.item_provider.items) - 1

    @listens(u'appointed_device')
    def __on_appointed_device_changed(self):
        device = self.song.appointed_device
        self._device_organizer.set_device(device)
        self._info_display.clear_display(3)

    def set_next_device_button(self, button):
        self.next_device_button.set_control_element(button)

    def set_previous_device_button(self, button):
        self.previous_device_button.set_control_element(button)

    def set_remove_device_button(self, button):
        self.remove_device_button.set_control_element(button)

    def set_move_backward_button(self, button):
        self._device_organizer.set_move_backward_button(button)

    def set_move_forward_button(self, button):
        self._device_organizer.set_move_forward_button(button)

    @previous_device_button.pressed
    def _on_previous_device_button_pressed(self, _):
        self.select_previous_device()

    @next_device_button.pressed
    def _on_next_device_button_pressed(self, _):
        self.select_next_device()

    @remove_device_button.pressed
    def _on_remove_device_button_pressed(self, _):
        self.remove_selected_device()

    def select_next_device(self):
        index = self._get_selected_device_index()
        target_device = None
        if not self.last_device and self._is_valid_index(index):
            target_device = self.item_provider.items[index + 1][0]
            self._select_item(target_device)
            self._show_selected_item()

    def select_previous_device(self):
        index = self._get_selected_device_index()
        target_device = None
        if not self.first_device and self._is_valid_index(index):
            target_device = self.item_provider.items[index - 1][0]
            self._select_item(target_device)
            self._show_selected_item()

    def remove_selected_device(self):
        if self.selected_item is not None:
            parent = self.selected_item.canonical_parent
            index = list(parent.devices).index(self.selected_item)
            parent.delete_device(index)
            self.update_items()

    def _is_valid_index(self, index):
        return 0 <= index < len(self.item_provider.items)

    def _get_selected_device_index(self):
        return index_if(lambda i: i[0] == self.selected_item, self.item_provider.items)
