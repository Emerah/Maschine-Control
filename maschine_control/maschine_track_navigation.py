#
# native instruments / ableton
# maschine_track_navigation.py
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

from itertools import izip

from ableton.v2.base.dependency import depends
from ableton.v2.base.event import EventObject, listens
from ableton.v2.base.live_api_utils import liveobj_changed
from ableton.v2.base.util import forward_property, index_if
from ableton.v2.control_surface.component import Component
from ableton.v2.control_surface.control.button import ButtonControl
from ableton.v2.control_surface.control.control_list import control_list


class MaschineSimpleTrackSlot(EventObject):
    __module__ = __name__
    __events__ = ('name', 'color_index')

    def __init__(self, track=None, name='', *a, **k):
        super(MaschineSimpleTrackSlot, self).__init__(*a, **k)
        self._track = track
        self._name = name
        self.__on_name_changed.subject = self._track if getattr(self._track, 'name_has_listener', None) else None
        self.__on_color_index_changed.subject = self._track if getattr(self._track, 'color_index_has_listener', None) else None

    @property
    def track(self):
        return self._track

    @property
    def name(self):
        return self._name

    @property
    def color_index(self):
        return getattr(self._track, 'color_index', None)

    @listens('name')
    def __on_name_changed(self):
        pass

    @listens('color_index')
    def __on_color_index_changed(self):
        pass


class MaschineTrackSlot(MaschineSimpleTrackSlot):
    __module__ = __name__

    def __init__(self, track=None, **k):
        assert track is not None
        super(MaschineTrackSlot, self).__init__(track=track, name=track.name, **k)

    def __eq__(self, other):
        return id(self) == id(other) or self._track == other

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self._track)

    _live_ptr = forward_property('_track')('_live_ptr')


def collect_all_tracks(song):
    tracks = list(tuple(song.visible_tracks) + tuple(song.return_tracks) + (song.master_track,))
    return tracks


def collect_visible_tracks(song):
    tracks = list(tuple(song.visible_tracks))
    return tracks


def collect_return_tracks(song):
    tracks = list(tuple(song.return_tracks))
    return tracks


class MaschineBasicTrackProvider(EventObject):
    __module__ = __name__
    __events__ = ('tracks', 'selected_track')

    @property
    def tracks(self):
        return []

    @property
    def selected_track(self):
        return


class MaschineTrackProvider(MaschineBasicTrackProvider):

    @depends(song=None)
    def __init__(self, song=None, collect_tracks_func=collect_all_tracks, *a, **k):
        super(MaschineTrackProvider, self).__init__(*a, **k)
        self._song = song
        self._tracks = []
        self._selected_track = None
        self._collect_tracks_func = collect_tracks_func
        self.__on_tracks_changed.subject = self._song
        self.__on_selected_track_changed.subject = self._song.view
        self.__on_tracks_changed()
        self.__on_selected_track_changed()

    @property
    def tracks(self):
        return self._tracks

    @property
    def selected_track(self):
        return self._selected_track

    @selected_track.setter
    def selected_track(self, track):
        if liveobj_changed(self._selected_track, track):
            self._selected_track = track
            self.notify_selected_track()

    def _update_tracks(self):
        self._tracks = self._collect_tracks_func(self._song)
        self.notify_tracks()

    @listens('tracks')
    def __on_tracks_changed(self):
        self._update_tracks()

    @listens('selected_track')
    def __on_selected_track_changed(self):
        pass


class MaschineScrollComponent(Component):
    __module__ = __name__
    __events__ = (u'scroll', )
    button = ButtonControl(color='TrackNavigation.TrackNotSelected', repeat=True)

    @button.pressed
    def button(self, button):
        self.notify_scroll()


class MaschineScrollOverlayComponent(Component):
    __module__ = __name__

    def __init__(self, *a, **k):
        super(MaschineScrollOverlayComponent, self).__init__(*a, **k)
        self._scroll_left_component = MaschineScrollComponent(is_enabled=False)
        self._scroll_right_component = MaschineScrollComponent(is_enabled=False)
        self.add_children(self._scroll_left_component, self._scroll_right_component)
        self.__on_scroll_left.subject = self._scroll_left_component
        self.__on_scroll_right.subject = self._scroll_right_component

    scroll_left_layer = forward_property('_scroll_left_component')('layer')
    scroll_right_layer = forward_property('_scroll_right_component')('layer')

    def can_scroll_left(self):
        raise NotImplementedError

    def can_scroll_right(self):
        raise NotImplementedError

    def scroll_left(self):
        raise NotImplementedError

    def scroll_right(self):
        raise NotImplementedError

    def update_scroll_buttons(self):
        if self.is_enabled():
            self._scroll_left_component.set_enabled(self.can_scroll_left())
            self._scroll_right_component.set_enabled(self.can_scroll_right())

    @listens('scroll')
    def __on_scroll_left(self):
        self.scroll_left()

    @listens('scroll')
    def __on_scroll_right(self):
        self.scroll_right()

    def update(self):
        super(MaschineScrollOverlayComponent, self).update()
        if self.is_enabled():
            self.update_scroll_buttons()


class MaschineBasicTrackLister(Component):
    __module__ = __name__
    __events__ = ('tracks',)

    color_class_name = 'TrackNavigation'
    select_buttons = control_list(ButtonControl, color=color_class_name + '.NoTrack')

    def __init__(self, track_provider=MaschineBasicTrackProvider(), num_visible_tracks=16, *a, **k):
        super(MaschineBasicTrackLister, self).__init__(*a, **k)
        self._track_offset = 0
        self._track_provider = track_provider
        self._tracks = []
        self._num_visible_tracks = num_visible_tracks
        self.__on_tracks_changed.subject = track_provider
        self.update_tracks()

    def reset_offset(self):
        self._track_offset = 0

    @property
    def tracks(self):
        return self._tracks

    @property
    def track_provider(self):
        return self._track_provider

    @property
    def track_offset(self):
        return self._track_offset

    @track_offset.setter
    def track_offset(self, offset):
        self._track_offset = offset
        self.update_tracks()

    @select_buttons.pressed
    def select_buttons(self, button):
        self._on_select_button_pressed(button)

    def _on_select_button_pressed(self, button):
        pass

    def can_scroll_left(self):
        return self.track_offset > 0

    def can_scroll_right(self):
        tracks = self._track_provider.tracks[self.track_offset:]
        return len(tracks) > self._num_visible_tracks

    def scroll_left(self):
        self.track_offset -= 1

    def scroll_right(self):
        self.track_offset += 1

    @listens('tracks')
    def __on_tracks_changed(self):
        self.update_tracks()

    def update_tracks(self):
        for track in self._tracks:
            self.disconnect_disconnectable(track)
        self._adjust_offset()
        self._tracks = map(self.register_disconnectable, self._create_track_slots())
        self.notify_tracks()

    def _adjust_offset(self):
        num_tracks = len(self._track_provider.tracks)
        list_length = self._num_visible_tracks
        if list_length >= num_tracks or self._track_offset >= num_tracks - list_length:
            self._track_offset = max(0, num_tracks - list_length)

    def _create_track_slots(self):
        tracks = self._track_provider.tracks[self.track_offset:]
        num_slots = min(self._num_visible_tracks, len(tracks))
        new_tracks = []
        if num_slots > 0:
            new_tracks = [self._create_slot(index, track) for index, track in enumerate(tracks[:num_slots]) if track is not None]
        return new_tracks

    def _create_slot(self, index, track):
        return MaschineTrackSlot(track=track)


class MaschineTrackListerComponent(MaschineBasicTrackLister):
    __module__ = __name__

    # color_class_name = 'TrackNavigation'
    # select_buttons = control_list(ButtonControl, unavailable_color=color_class_name + '.NoTrack')
    # select_buttons = control_list(ButtonControl, color=color_class_name + '.NoTrack')

    def __init__(self, *a, **k):
        super(MaschineTrackListerComponent, self).__init__(*a, **k)
        self._scroll_overlay = self.add_children(MaschineScrollOverlayComponent(is_enabled=True))
        self._scroll_overlay.can_scroll_left = self.can_scroll_left
        self._scroll_overlay.can_scroll_right = self.can_scroll_right
        self._scroll_overlay.scroll_left = self.scroll_left
        self._scroll_overlay.scroll_right = self.scroll_right
        self.__on_tracks_changed.subject = self
        self.__on_selected_track_changed.subject = self._track_provider
        self.__on_tracks_changed()
        self.__on_selected_track_changed()
        self.select_buttons.control_count = self._num_visible_tracks

    scroll_left_layer = forward_property('_scroll_overlay')('scroll_left_layer')
    scroll_right_layer = forward_property('_scroll_overlay')('scroll_right_layer')

    @listens('tracks')
    def __on_tracks_changed(self):
        # self.select_buttons.control_count = len(self.tracks)
        # for index, button in enumerate(self.select_buttons):
        #     print(index, button)
        self._update_select_buttons()
        self._scroll_overlay.update_scroll_buttons()

    @listens('selected_track')
    def __on_selected_track_changed(self):
        self._update_select_buttons()

    def _update_select_buttons(self):
        selected_track = self._track_provider.selected_track
        # print('selected track: {}'.format(selected_track))
        for button, track in izip(self.select_buttons, self.tracks):
            # print('button: {}, track: {}'.format(button, track))
            button.color = self._color_for_button(button.index, track == selected_track)

    def _color_for_button(self, button_index, is_selected):
        if is_selected:
            return self.color_class_name + '.TrackSelected'
        return self.color_class_name + '.TrackNotSelected'


class MaschineTrackNavigation(MaschineTrackListerComponent):
    __module__ = __name__
    next_track_button = ButtonControl(color='DefaultButton.On', pressed_color='DefaultButton.Off')
    previous_track_button = ButtonControl(color='DefaultButton.On', pressed_color='DefaultButton.Off')
    master_track_button = ButtonControl(color='DefaultButton.On', pressed_color='DefaultButton.Off')
    next_track_page_button = ButtonControl(color='DefaultButton.Off')
    previous_track_page_button = ButtonControl(color='DefaultButton.Off')

    def __init__(self, info_display=None, track_provider=None, *a, **k):
        assert info_display is not None
        self._info_display = info_display
        self._track_list = track_provider
        super(MaschineTrackNavigation, self).__init__(track_provider=self._track_list, *a, **k)
        self._last_pressed_button_index = -1
        self.register_disconnectable(self._track_list)
        self.__on_selected_track_changed.subject = self.song.view
        self.__on_selected_track_changed()
        self._update_select_buttons()
        self.update_track_selection_buttons()

    def set_next_track_button(self, button):
        self.next_track_button.set_control_element(button)

    def set_previous_track_button(self, button):
        self.previous_track_button.set_control_element(button)

    def set_master_track_button(self, button):
        self.master_track_button.set_control_element(button)

    @next_track_button.pressed
    def _on_next_track_button_pressed(self, button):
        self.select_next_track()

    @previous_track_button.pressed
    def _on_previous_track_button_pressed(self, button):
        self.select_previous_track()

    @master_track_button.pressed
    def _on_master_track_button_pressed(self, button):
        self.select_master_track()

    @next_track_page_button.pressed
    def _on_next_track_page_button_pressed(self, button):
        self.select_next_track_page()

    @previous_track_page_button.pressed
    def _on_previous_track_page_button_pressed(self, button):
        self.select_previous_track_page()

    @property
    def selected_track(self):
        return self.track_provider.selected_track

    @listens('tracks')
    def __on_tracks_changed(self):
        self._update_select_buttons()
        self.update_track_selection_buttons()
        self._scroll_overlay.update_scroll_buttons()

    @listens('selected_track')
    def __on_selected_track_changed(self):
        if self.selected_track != self._current_track():
            self.song.view.selected_track = self._current_track()
            self._update_track_provider(self._current_track())
            self._update_select_buttons()
        self.__on_name_changed.subject = self.selected_track
        self._display_track_name(self.selected_track)
        if not self.selected_track.devices:
            self._info_display.clear_display(1)
            self._info_display.clear_display(3)
        self.update_track_selection_buttons()

    @listens('name')
    def __on_name_changed(self):
        track = self.selected_track
        self._display_track_name(track)

    def update_track_selection_buttons(self):
        index = self.tracks.index(self.selected_track)
        self.previous_track_button.enabled = index > 0
        self.next_track_button.enabled = index + 1 < len(self.tracks)
        self.master_track_button.color = 'DefaultButton.On' if self.selected_track == self.song.master_track else 'DefaultButton.Off'

    def select_next_track(self):
        index = self._get_selected_track_index()
        traget_track = None
        if not index == len(self.track_provider.tracks) - 1 and self._is_valid_index(index):
            traget_track = self.track_provider.tracks[index + 1]
            self._select_track(traget_track)

    def select_previous_track(self):
        index = self._get_selected_track_index()
        traget_track = None
        if not index == 0 and self._is_valid_index(index):
            traget_track = self.track_provider.tracks[index - 1]
            self._select_track(traget_track)

    def select_master_track(self):
        master = self.song.master_track
        if self.selected_track != master:
            self._select_track(master)

    def select_next_track_page(self):
        if self.can_scroll_right():
            self.scroll_right()

    def select_previous_track_page(self):
        if self.can_scroll_left():
            self.scroll_left()

    def _select_track(self, track):
        if track and track != self._current_track():
            self.song.view.selected_track = track
            self._update_track_provider(track)

    def _update_selected_track(self):
        self.reset_offset()

    def _current_track(self):
        return self.song.view.selected_track

    def _on_select_button_pressed(self, button):
        self._select_track(self.tracks[button.index].track)

    def _update_track_provider(self, track):
        self._track_list.selected_track = track

    def _get_selected_track_index(self):
        return index_if(lambda track: track == self.selected_track, self.track_provider.tracks)

    def _is_valid_index(self, index):
        return 0 <= index < len(self.track_provider.tracks)

    def _display_track_name(self, track):
        if track in self.song.visible_tracks:
            self._info_display.display_message_on_maschine('Track - {} '.format(track.name), 2)
        elif track in self.song.return_tracks:
            self._info_display.display_message_on_maschine('Return - {}'.format(track.name), 2)
        else:
            self._info_display.display_message_on_maschine('Master Track Selected', 2)
