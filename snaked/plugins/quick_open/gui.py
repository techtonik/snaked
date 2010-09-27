import os.path
import weakref

from snaked.util import join_to_file_dir, BuilderAware, open_mime
from snaked.core.shortcuts import ShortcutActivator

import settings
import searcher

class QuickOpenDialog(BuilderAware):
    def __init__(self):
        super(QuickOpenDialog, self).__init__(join_to_file_dir(__file__, 'gui.glade'))
        self.shortcuts = ShortcutActivator(self.window)
        self.shortcuts.bind('Escape', self.hide)
        self.shortcuts.bind('<alt>Up', self.project_up)
        self.shortcuts.bind('<alt>Down', self.project_down)
        self.shortcuts.bind('Return', self.open_file)
        self.shortcuts.bind('<ctrl>Return', self.open_mime)
        
    def show(self, editor):
        self.editor = weakref.ref(editor)
        
        root = editor.project_root
        if not root:
            root = os.path.dirname(editor.uri)

        self.update_projects(root)

        self.search_entry.grab_focus()
        
        self.window.set_transient_for(editor.window)
        self.window.show()
    
    def update_projects(self, root):
        self.projects_cbox.set_model(None)
        self.projectlist.clear()
        
        index = -1
        for i, r in enumerate(settings.recent_projects):
            if r == root:
                index = i
            self.projectlist.append((r,))
        
        self.projects_cbox.set_model(self.projectlist)
        self.projects_cbox.set_active(index)
    
    def hide(self):
        self.window.hide()
        
    def on_delete_event(self, *args):
        self.hide()
        return True
    
    def project_up(self):
        pass
        
    def project_down(self):
        pass

    def get_current_root(self):
        return self.projectlist[self.projects_cbox.get_active()][0]
    
    def fill_filelist(self, search):
        self.filelist.clear()
        
        for p in searcher.search(self.get_current_root(), '', search):
            self.filelist.append(p)

    def on_search_entry_changed(self, *args):
        self.fill_filelist(self.search_entry.get_text())
        
    def get_selected_file(self):
        (model, iter) = self.filelist_tree.get_selection().get_selected()
        if iter:
            return os.path.join(self.get_current_root(), *self.filelist.get(iter, 1, 0))
        else:
            return None
    
    def open_file(self):
        fname = self.get_selected_file()
        if fname:
            self.hide()
            print self.editor().request_to_open_file(fname)
        
    def open_mime(self):
        fname = self.get_selected_file()
        if fname:
            self.hide()
            open_mime(fname)
