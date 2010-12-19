import weakref

import pango, gtk

from snaked.util import idle, join_to_file_dir, BuilderAware, set_activate_the_one_item
from snaked.core.shortcuts import ShortcutActivator

class EditorListDialog(BuilderAware):
    """glade-file: gui.glade"""

    def __init__(self):
        super(EditorListDialog, self).__init__(join_to_file_dir(__file__, 'gui.glade'))
        self.shortcuts = ShortcutActivator(self.window)
        self.shortcuts.bind('Escape', self.hide)
        self.shortcuts.bind('Delete', self.close_editor)
        self.shortcuts.bind('<alt>s', self.focus_search)

        set_activate_the_one_item(self.search_entry, self.editors_view)

        self.editors_view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.path2editor = weakref.WeakValueDictionary()


    def show(self, editor, editors):
        self.editor = weakref.ref(editor)
        self.editor_list = editors
        self.fill()
        editor.request_transient_for.emit(self.window)

        self.search_entry.set_text('')
        self.search_entry.grab_focus()

        self.window.present()

    def fill(self, search=None):
        self.editors.clear()
        self.path2editor.clear()

        active_editor = self.editor()
        titles = [(e.get_title.emit(), e) for e in self.editor_list]
        for t, e in sorted(titles, key=lambda r: r[0]):
            if not search or search in t:
                weight = pango.WEIGHT_BOLD if e is active_editor else pango.WEIGHT_NORMAL
                iter = self.editors.append(None, (t, weight))
                path = self.editors.get_path(iter)
                self.path2editor[path] = e

        self.editors_view.get_selection().select_path((0,))
        self.editors_view.columns_autosize()

    def hide(self):
        self.window.hide()

    def on_delete_event(self, *args):
        self.escape()
        return True

    def on_search_entry_changed(self, *args):
        search = self.search_entry.get_text().strip()
        idle(self.fill, search)

    def focus_search(self):
        self.search_entry.grab_focus()

    def close_editor(self, *args):
        model, pathes = self.editors_view.get_selection().get_selected_rows()
        for p in pathes:
            idle(self.path2editor[p].request_close.emit)

        idle(self.on_search_entry_changed)

    def on_editors_view_row_activated(self, view, path, *args):
        idle(self.editor().open_file, self.path2editor[path].uri)
        idle(self.hide)

    def on_editors_view_cursor_changed(self, *args):
        path, _ = self.editors_view.get_cursor()
        idle(self.editor().open_file, self.path2editor[path].uri)
