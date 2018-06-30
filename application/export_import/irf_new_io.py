from dataentry.models import FormType

from .export_form import ExportFormFactory, ExportToGoogleSheetFactory

# assumes all objects in objs list are for the same form
def get_form_export_rows(objs):
    if len(objs) < 1:
        return []
    
    print ("In get_form_export_rows")
    
    export_factory = ExportToGoogleSheetFactory()
    form = ExportFormFactory.find_by_instance(objs[0])
    if form is None:
        # log form not found
        return []
    export_sheet = export_factory.find(form)
    if export_sheet is None:
        # log sheet not found
        return []
    
    for irf in irfs:
        export_sheet.process_object(irf)
        
    return export_sheet.rows
