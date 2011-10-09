dialog = [None]
recent_editors = {}

def init(injector):
    from ..prefs import add_option

    add_option('EDITOR_LIST_SWITCH_ON_SELECT', True,
        'Activates editor on item select (i.e cursor move) in editor list dialog')

    injector.bind_accel('window', 'show-editor-list', '_Window/_Editor list',
        '<alt>e', show_editor_list)

    injector.on_done('last-buffer-editor', editor_closed)

def editor_closed(editor):
    recent_editors[editor.uri] = editor.get_title.emit()

def show_editor_list(window):
    if not dialog[0]:
        from .gui import EditorListDialog
        dialog[0] = EditorListDialog()

    dialog[0].show(window, recent_editors)
