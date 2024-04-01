import subprocess
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction

import os
import gi
gi.require_version('Wnck', '3.0')
from gi.repository import Gtk

class ZLikeWindowSwitcherExtension(Extension):
    def __init__(self):
        super(ZLikeWindowSwitcherExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        MIN_LEN_TO_SEARCH = 2
        items = []
        pid_list = []

        text = event.get_argument() or ''

        if len(text) >= MIN_LEN_TO_SEARCH:
            windows =  subprocess.Popen(f'wmctrl -lx | sed "s/  */ /g" | grep -i "{text}"',
                shell=True,
                stdout=subprocess.PIPE
            ).stdout.read().decode()

            windows_list = windows.splitlines()

            if len(windows_list) == 0:
                items.append(
                    ExtensionResultItem(
                        icon='images/not_found.png',
                        name='None window found',
                        description='Try searching for something else',
                        on_enter=DoNothingAction()
                    )
                )
                return RenderResultListAction(items)

            for window in windows_list:
                if window:
                    windowsname = " ".join(window.split(" ")[4:])
                    wmclass = window.split(" ")[2]
                    #windowsname = subprocess.Popen(
                    #    'xdotool getwindowname ' + window,
                    #    shell=True,
                    #    stdout=subprocess.PIPE
                    #).stdout.read().decode()
                    icon_name = windowsname
                    icon_theme = Gtk.IconTheme.get_default()

                    icon_info = icon_theme.lookup_icon(icon_name, 48, 0)

                    try:
                        # Some known apps
                        if "brave" in wmclass.lower().split(".")[-1]:
                            icon_path = icon_theme.lookup_icon("brave-desktop", 48, 0).get_filename()
                        else:
                            icon_path = icon_info.get_filename()
                    except AttributeError:
                        icon_theme = Gtk.IconTheme()
                        icon_path = 'images/ios-default-app-icon.png'
                        for icon in icon_theme.list_icons():
                            if wmclass.lower().split(".")[-1] in icon:
                                icon_path = icon_theme.lookup_icon(icon, 48, 0).get_filename()
                                break

                    items.append(ExtensionResultItem(
                        icon=icon_path,
                        name='Open ' + windowsname,
                        on_enter=ExtensionCustomAction(wmclass, keep_app_open=True)
                    ))
            return RenderResultListAction(items)

        items.append(ExtensionResultItem(
            icon='images/icon.png',
            name='Search for a window by name',
            description=f'Try searching for something longer than {MIN_LEN_TO_SEARCH} characters'
        ))

        return RenderResultListAction(items)

class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        pid = event.get_data() or ""

        os.system('wmctrl -x -a  ' + pid)


if __name__ == '__main__':
    ZLikeWindowSwitcherExtension().run()
