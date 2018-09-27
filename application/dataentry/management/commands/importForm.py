from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('class', nargs='+', type=str)
        parser.add_argument('file_name', nargs='+', type=str)
        parser.add_argument('renum_name', nargs='+', type=str)
    def handle(self, *args, **options):
        class_name = options.get('class')[0]
        file_name = options.get('file_name')[0]
        renum_name = options.get('renum_name')[0]
        
        idx = class_name.rfind('.')
        print (class_name[:idx], class_name[idx+1:])
            
        mod = __import__(class_name[:idx], fromlist=[class_name[idx+1:]])
        if mod is None:
            print('Unable to find module ' + class_name[:idx])
        the_class = getattr(mod, class_name[idx+1:], None)
        if the_class is None:
            print('Unable to find class ' + class_name[idx+1:] + ' in module ' +  class_name[:idx])
            
        import_obj = the_class()
        import_obj.process(file_name, renum_name)