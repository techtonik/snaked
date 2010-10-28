import gtk

from snaked.core.shortcuts import ContextShortcutActivator, register_shortcut
import snaked.core.editor

class TabbedEditorManager(snaked.core.editor.EditorManager):
    def __init__(self, show_tabs=True):
        super(TabbedEditorManager, self).__init__()

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('delete-event', self.on_delete_event)

        self.window.set_property('default-width', 800)
        self.window.set_property('default-height', 500)
    
        self.activator = ContextShortcutActivator(self.window, self.get_context)
        
        self.note = gtk.Notebook()
        self.note.set_show_tabs(show_tabs)
        self.note.set_scrollable(True)
        self.note.set_property('tab-hborder', 10)
        self.note.set_property('homogeneous', False)
        self.note.connect_after('switch-page', self.on_switch_page)
        self.window.add(self.note)

        register_shortcut('toggle-tabs-visibility', '<alt>F11', 'Window', 'Toggles tabs visibility')
        register_shortcut('next-editor', '<alt>Right', 'Window', 'Switches to next editor')
        register_shortcut('prev-editor', '<alt>Left', 'Window', 'Switches to previous editor')
        register_shortcut('next-editor-alt', '<ctrl>Page_Down', 'Window', 'Switches to next editor')
        register_shortcut('prev-editor-alt', '<ctrl>Page_Up', 'Window', 'Switches to previous editor')
        register_shortcut('fullscreen', 'F11', 'Window', 'Toggles fullscreen mode')
        
        self.window.show_all()
    
    def get_context(self):
        widget = self.note.get_nth_page(self.note.get_current_page())
        for e in self.editors:
            if e.widget is widget:
                return (e,)

        return (None,)

    def manage_editor(self, editor):
        label = gtk.Label('Unknown')
        self.note.append_page(editor.widget, label)
        self.focus_editor(editor)
        editor.view.grab_focus()
       
    def focus_editor(self, editor):
        idx = self.note.page_num(editor.widget)
        self.note.set_current_page(idx)

    def update_top_level_title(self):
        idx = self.note.get_current_page()
        if idx < 0:
            return
        
        title = self.note.get_tab_label_text(self.note.get_nth_page(idx))
        if title is not None:
            self.window.set_title(title)        
                
    def set_editor_title(self, editor, title):
        self.note.set_tab_label_text(editor.widget, title)
        if self.note.get_current_page() == self.note.page_num(editor.widget):
            self.update_top_level_title()

    def on_delete_event(self, *args):
        self.quit(None)

    def close_editor(self, editor):
        idx = self.note.page_num(editor.widget)
        self.note.remove_page(idx)
        editor.editor_closed.emit()

    def set_editor_shortcuts(self, editor):
        self.plugin_manager.bind_shortcuts(self.activator, editor)

        if hasattr(self, 'editor_shortcuts_binded'):
            return
        
        self.editor_shortcuts_binded = True

        self.activator.bind_to_name('quit', self.quit)
        self.activator.bind_to_name('close-window', self.close_editor)
        self.activator.bind_to_name('save', self.save)
        self.activator.bind_to_name('next-editor', self.switch_to, 1)
        self.activator.bind_to_name('prev-editor', self.switch_to, -1)
        self.activator.bind_to_name('next-editor-alt', self.switch_to, 1)
        self.activator.bind_to_name('prev-editor-alt', self.switch_to, -1)
        self.activator.bind_to_name('new-file', self.new_file_action)
        self.activator.bind_to_name('show-preferences', self.show_preferences)
        self.activator.bind_to_name('fullscreen', self.fullscreen, [True])
        self.activator.bind_to_name('toggle-tabs-visibility', self.toggle_tabs)

        self.activator.bind('Escape', self.process_escape)

    def quit(self, editor):
        self.window.hide()
        super(TabbedEditorManager, self).quit(editor)

    def save(self, editor):
        editor.save()

    def set_transient_for(self, editor, window):
        window.set_transient_for(self.window)

    def on_switch_page(self, *args):
        self.update_top_level_title()
        
    def switch_to(self, editor, dir):
        idx = ( self.note.get_current_page() + dir ) % self.note.get_n_pages()
        self.note.set_current_page(idx)

    def fullscreen(self, editor, state):
        if state[0]:
            self.window.fullscreen()
        else:
            self.window.unfullscreen()
            
        state[0] = not state[0]
        
    def toggle_tabs(self, editor):
        self.note.set_show_tabs(not self.note.get_show_tabs())