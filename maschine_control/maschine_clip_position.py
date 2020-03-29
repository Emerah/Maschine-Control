#
# maschine / ableton
# maschine_clip_position.py
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

from ableton.v2.base.event import listens
from ableton.v2.control_surface.component import Component
from ableton.v2.control_surface.control.encoder import SendValueEncoderControl


class MaschineClipPositionIndicator(Component):

    touch_strip_display = SendValueEncoderControl()

    def __init__(self, *a, **k):
        super(MaschineClipPositionIndicator, self).__init__(*a, **k)
        self._clip = None
        self.register_slot(self.song.view, self.__on_detail_clip_changed, 'detail_clip')
        if self._clip is None:
            self._clip = self._get_detail_clip()
        self.__on_playing_position_changed.subject = self._clip

    def __on_detail_clip_changed(self):
        clip = self.song.view.detail_clip
        self._clip = clip
        self.__on_playing_position_changed.subject = self._clip
        if clip is None:
            self.touch_strip_display.value = 0.0

    @listens('playing_position')
    def __on_playing_position_changed(self):
        if not self._clip.is_recording:
            position = self._clip.playing_position
            length = self._clip.length
            self.touch_strip_display.value = position / length * 127

    def _get_detail_clip(self):
        return self.song.view.detail_clip
