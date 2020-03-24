#
# native instruments / ableton
# maschine_note_modes.py
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

import Live  # noqa
from ableton.v2.base.event import listens
from ableton.v2.control_surface.mode import ModesComponent
from ableton.v2.control_surface.percussion_instrument_finder import PercussionInstrumentFinder
from ableton.v2.control_surface.components.target_track import ArmedTargetTrackComponent
from ableton.v2.base.live_api_utils import liveobj_valid


class MaschinePlayableModes(ModesComponent):

    def __init__(self, drum_rack=None, keyboard=None, *a, **k):
        super(MaschinePlayableModes, self).__init__(*a, **k)
        self._drum_rack = drum_rack
        self.add_mode('drums_mode', drum_rack)
        self.add_mode('keyboard_mode', keyboard)
        self._target_track = ArmedTargetTrackComponent(name='Target_Track', parent=self)
        self.__on_target_track_changed.subject = self._target_track
        self._drum_rack_finder = self.register_disconnectable(PercussionInstrumentFinder(device_parent=self._target_track.target_track))
        self.__on_drum_group_changed.subject = self._drum_rack_finder
        self.__on_drum_group_changed()

    @listens('selected_mode')
    def __on_selected_mode_changed(self, mode):
        print('selected mode: {}'.format(mode))

    @listens('target_track')
    def __on_target_track_changed(self):
        self._drum_rack_finder.device_parent = self._target_track.target_track
        # self.update()

    @listens('instrument')
    def __on_drum_group_changed(self):
        drum_group = self._drum_rack_finder.drum_group  # or self._drum_rack_finder.sliced_simpler
        self._drum_rack.set_drum_group_device(drum_group)
        self.selected_mode = 'drums_mode' if liveobj_valid(drum_group) else 'keyboard_mode'

    def _track_has_instrument(self, track):
        if track.has_midi_input and track.devices:
            for device in track.devices:
                if device.type == Live.Device.DeviceType.instrument and not device.can_have_drum_pads:
                    return True
        else:
            return False

    def _track_has_drum_rack(self, track):
        if track.has_midi_input and track.devices:
            for device in track.devices:
                if device.can_have_drum_pads:
                    return True
        else:
            return False
