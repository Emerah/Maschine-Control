#
# maschine / ableton
# maschine_control_surface.py
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

from contextlib import contextmanager

import Live  # noqa
from ableton.v2.base.dependency import inject
# from ableton.v2.base.event import listens
# from .maschine_note_modes import MaschineNoteModes
# from ableton.v2.base.live_api_utils import liveobj_valid
from ableton.v2.base.util import const
from ableton.v2.control_surface.components.auto_arm import AutoArmComponent
# from ableton.v2.control_surface.components.target_track import ArmedTargetTrackComponent
from ableton.v2.control_surface.control_surface import ControlSurface
from ableton.v2.control_surface.layer import Layer
from ableton.v2.control_surface.mode import Mode, ModesComponent  # , NullModes
# from ableton.v2.control_surface.percussion_instrument_finder import PercussionInstrumentFinder

from .maschine_drums import MaschineDrumRack
from .maschine_elements import MaschineElements
from .maschine_info_display import MaschineInfoDisplay
from .maschine_keyboard import MaschineKeyboard
from .maschine_note_repeat import MaschineNoteRepeatEnabler
from .maschine_playable_modes import MaschinePlayableModes
from .maschine_recording import MaschineRecording
from .maschine_skin import maschine_skin
from .maschine_transport import MaschineTransport

KEYBOARD_CHANNEL = 2
DRUMS_CHANNEL = 1
FEEDBACK_CHANNELS = [KEYBOARD_CHANNEL, DRUMS_CHANNEL]


class MaschineControlSurface(ControlSurface):

    def __init__(self, *a, **k):
        super(MaschineControlSurface, self).__init__(*a, **k)
        self._maschine_injector = inject(element_container=const(None)).everywhere()
        with self.component_guard():
            self._info_display = MaschineInfoDisplay()
            with inject(skin=const(maschine_skin)).everywhere():
                self._elements = MaschineElements()
        self._maschine_injector = inject(element_container=const(self._elements)).everywhere()
        with self.component_guard():
            self.create_auto_arm_component()
            self.create_transport_component()
            self.create_recording_component()
            self.create_note_repeat_component()
            self.create_keyboard_component()
            self.create_drum_rack_component()
            self.create_playable_mode()
            self.create_main_modes()
        self.set_feedback_channels(FEEDBACK_CHANNELS)
        self.show_message('Maschine MKiii - ' + str(self.live_version))

    def disconnect(self):
        self._info_display.clear_all_displays()
        self._autoarm.set_enabled(False)
        super(MaschineControlSurface, self).disconnect()

    @contextmanager
    def _component_guard(self):
        with super(MaschineControlSurface, self)._component_guard():
            with self._maschine_injector:
                yield

    @property
    def live_version(self):
        bugfix = self.application.get_bugfix_version()
        minor = self.application.get_minor_version()
        major = self.application.get_major_version()
        current_version = u'Ableton Live {}.{}.{}'.format(major, minor, bugfix)
        return current_version

    def create_auto_arm_component(self):
        self._autoarm = AutoArmComponent(name='AutoArm')

    def create_transport_component(self):
        self._transport = MaschineTransport(name='Transport', is_enabled=False)
        layer = Layer(play_button='play_button', stop_button='stop_button', tap_tempo_button='tap_button', metronome_button='metro_button')
        self._transport.layer = layer
        self._transport.set_enabled(True)

    def create_recording_component(self):
        self._recording = MaschineRecording(name='Recording', is_enabled=False)
        layer = Layer(record_button='record_button', session_automation_button='auto_button')
        self._recording.layer = layer
        self._recording.set_enabled(True)

    def create_note_repeat_component(self):
        self._note_repeat = MaschineNoteRepeatEnabler(note_repeat=self._c_instance.note_repeat, name='Note_Repeat_Enabler', is_enabled=False)
        self._note_repeat.layer = Layer(note_repeat_button='note_repeat_button')
        self._note_repeat.note_repeat_component.layer = Layer(select_buttons='group_matrix')
        self._note_repeat.set_enabled(True)

    def create_drum_rack_component(self):
        self._drum_rack = MaschineDrumRack(translation_channel=DRUMS_CHANNEL, name='Drum_Rack', is_enabled=False)
        self._drum_rack.layer = Layer(matrix='pad_matrix', scroll_page_down_button='chords_button', scroll_page_up_button='step_button')

    def create_keyboard_component(self):
        self._keyboard = MaschineKeyboard(translation_channel=KEYBOARD_CHANNEL, name='Keyboard', is_enabled=False)
        self._keyboard.layer = Layer(matrix='pad_matrix', scroll_down_button='chords_button', scroll_up_button='step_button')

    def create_playable_mode(self):
        self._playable_modes = MaschinePlayableModes(drum_rack=self._drum_rack, keyboard=self._keyboard, name='Playable_Modes', is_enabled=False)
        self._playable_modes.set_enabled(True)

    def create_main_modes(self):
        self._main_modes = ModesComponent(name='Main_Modes')
        self._main_modes.add_mode('device_mode', Mode())
        self._main_modes.add_mode('mixer_mode', Mode())
        self._main_modes.add_mode('browser_mode', Mode())
        self._main_modes.layer = Layer(device_mode_button='plugin_button', mixer_mode_button='mixer_button', browser_mode_button='browser_button')
        self._main_modes.selected_mode = 'device_mode'
