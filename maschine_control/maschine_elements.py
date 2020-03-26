#
# maschine / ableton
# maschine_elements.py
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

import Live  # noqa
from ableton.v2.base.dependency import depends
from ableton.v2.control_surface.elements.button import ButtonElement
from ableton.v2.control_surface.elements.button_matrix import ButtonMatrixElement
from ableton.v2.control_surface.elements.combo import ComboElement
from ableton.v2.control_surface.elements.encoder import EncoderElement
from ableton.v2.control_surface.input_control_element import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from ableton.v2.control_surface.resource import PrioritizedResource
from ableton.v2.control_surface.elements.full_velocity_element import FullVelocityElement

DEFAULT_CHANNEL = 15
RELATIVE_SMOOTH = Live.MidiMap.MapMode.relative_smooth_two_compliment
ABSOLUTE = Live.MidiMap.MapMode.absolute


@depends(skin=None)
def create_button(name, identifier, skin=None, **k):
    button = ButtonElement(is_momentary=True, msg_type=MIDI_CC_TYPE, channel=DEFAULT_CHANNEL, identifier=identifier, skin=skin, name=name, **k)
    return button


@depends(skin=None)
def create_pad(name, identifier, skin=None, **k):
    button = ButtonElement(is_momentary=True, msg_type=MIDI_NOTE_TYPE, channel=DEFAULT_CHANNEL, identifier=identifier, skin=skin, name=name, **k)
    return button


def create_encoder(name, identifier, **k):
    encoder = EncoderElement(msg_type=MIDI_CC_TYPE, channel=DEFAULT_CHANNEL, identifier=identifier, map_mode=RELATIVE_SMOOTH, encoder_sensitivity=1.0, name=name, **k)
    encoder.set_feedback_delay(-1)
    encoder.mapping_sensitivity = 0.1
    return encoder


def create_knob(name, identifier, **k):
    encoder = EncoderElement(msg_type=MIDI_CC_TYPE, channel=DEFAULT_CHANNEL, identifier=identifier, map_mode=ABSOLUTE, encoder_sensitivity=1.0, name=name, **k)
    encoder.set_feedback_delay(-1)
    encoder.mapping_sensitivity = 0.1
    return encoder


def create_matrix(name, controls, **k):
    rows = controls if isinstance(controls[0], list) else [controls]
    matrix = ButtonMatrixElement(rows=rows, name=name)
    return matrix


class MaschineElements(object):

    def __init__(self, *a, **k):
        super(MaschineElements, self).__init__(*a, **k)

        # shift button
        self.restart_button = create_button('Restart', 53, resource_type=PrioritizedResource)

        def with_shift(name, control):
            return ComboElement(control=control, modifier=self.restart_button, name=name)

        # mode buttons
        self.plugin_button = create_button('Plugin', 35)
        self.mixer_button = create_button('Mixer', 37)
        self.browser_button = create_button('Browser', 38)
        self.arranger_button = create_button('Arranger', 36)
        # transport buttons
        self.play_button = create_button('Play', 57)
        self.stop_button = create_button('Stop', 59)
        self.tap_button = create_button('Tap', 55)
        self.metro_button = with_shift('Metro', self.tap_button)

        # recording buttons
        self.record_button = create_button('Record', 58)
        self.auto_button = create_button('Auto', 42)
        self.re_enable_auto_button = with_shift('Re_Enable_Auto', self.auto_button)

        # note repeat
        self.note_repeat_button = create_button('Note_Repeat', 46)

        self.group_buttons = [create_button('Group_{}'.format(index + 1), index + 100) for index in xrange(8)]
        self.group_matrix = create_matrix('Group_Matrix', self.group_buttons)

        # drum rack matrix
        self.pads = [[create_pad(('{}_Pad_{}').format(col_index + 1, row_index + 1), offset + col_index) for col_index in xrange(4)] for row_index, offset in enumerate(xrange(48, 32, -4))]
        self.pad_matrix = create_matrix(name='Pad_Matrix', controls=self.pads)
        self.chords_button = create_button('Chords', 83)
        self.step_button = create_button('Step', 84)

        self.fixed_vel_button = create_button('Accent', 80)
        self.keyboard_button = create_button('Keyboard', 82)
        self.duplicate_button = create_button('Mute', 89)
        self.select_button = create_button('Mute', 90)
        self.solo_button = create_button('Mute', 91)
        self.mute_button = create_button('Mute', 92)

        # console section controls
        self.console_buttons = [create_button('Console_{}'.format(index + 1), index + 22) for index in xrange(8)]
        self.console_matrix = create_matrix(name='Console_Matrix', controls=self.console_buttons)

        self.remove_device_button = with_shift('Remove', self.console_buttons[4])
        self.return_track_button = with_shift('New_Return', self.console_buttons[0])
        self.audio_track_button = with_shift('New_Audio', self.console_buttons[1])
        self.midi_track_button = with_shift('New_Midi', self.console_buttons[2])

        self.console_knobs = [create_knob('Knob_{}'.format(index + 1), index + 70) for index in xrange(8)]
        self.knob_matrix = create_matrix(name='Knob_Matrix', controls=self.console_knobs)

        # main encoder section controls
        self.right_button = create_button('right', 31)
        self.left_button = create_button('Left', 33)
        self.move_backward_button = with_shift('Move_Backward', self.left_button)
        self.move_forward_button = with_shift('Move_Forward', self.right_button)
        # self.up_button = create_button('Up', 30)
        # self.down_button = create_button('Down', 32)
        # self.click_button = create_button('Click', 119)
        # self.encoder = create_encoder('Encoder', 118)

        # touch strip control
        self.touch_strip = create_knob('Touch_Strip', 12)
