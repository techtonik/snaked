import os.path
import sys

import rope.base.pyobjects
import rope.base.pynames

from .ropehints import HintProvider, get_attribute_scope_path

def get_path_and_package(module_path, project_root):
    packages = [os.path.basename(module_path).rpartition('.')[0]]
    while True:
        path = os.path.dirname(module_path)
        if path == module_path:
            break
        
        module_path = path
        
        if module_path == project_root:
            break
        
        if os.path.exists(os.path.join(module_path, '__init__.py')):
            packages.append(os.path.basename(module_path))
        else:
            break

    return module_path, '.'.join(reversed(packages))

loaded_django_modules = {}
def load_django_module(pymodule, project_root):
    path = os.path.realpath(pymodule.resource.real_path)
    try:
        return loaded_django_modules[path]
    except KeyError:
        pass

    syspath, module = get_path_and_package(path, project_root)
    if syspath not in sys.path:
        sys.path.append(syspath)
        
    __import__(module)

    loaded_django_modules[path] = sys.modules[module]
    return sys.modules[module]


class DjangoHintProvider(HintProvider):
    def __init__(self, project, settings):
        super(DjangoHintProvider, self).__init__(project)
        
        self.settings = settings
    
    def get_class_attributes(self, scope_path, pyclass, attrs):
        """:type pyclass: rope.base.pyobjectsdef.PyClass"""

        if not any('django.db.models.base.Model' in get_attribute_scope_path(c)
                for c in pyclass.get_superclasses()):
            return

        os.environ['DJANGO_SETTINGS_MODULE'] = self.settings

        module = load_django_module(pyclass.get_module(), self.project.address)
        model = getattr(module, pyclass.get_name())()

        for name in model._meta.get_all_field_names():
            f = model._meta.get_field_by_name(name)[0]
            if name not in attrs:
                attrs[name] = rope.base.pynames.DefinedName(rope.base.pyobjects.PyObject(None))

            if f.__class__.__name__ == 'ForeignKey':
                attrs[f.attname] = rope.base.pynames.DefinedName(rope.base.pyobjects.PyObject(None))

        attrs['objects'] = self.get_type('django.db.models.manager.Manager')

class DjangoObjectsName(rope.base.pynames.PyName):
    def __init__(self, pyobject):
        self.pyobject = pyobject

    def get_object(self):
        return self.pyobject


class DjangoObjectsObject(rope.base.pyobjects.PyObject):
    def __init__(self, pycore, model):
        self.pycore = pycore
        self.model = model

    def get_attributes(self):
        return {}