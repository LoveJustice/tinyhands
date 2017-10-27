from budget.pdfexports.pdf_creator import BasePDFCreator
from budget.helpers import MoneyDistributionFormHelper
import zipfile
from StringIO import StringIO


class MDFExporter(BasePDFCreator):
    template_name = 'budget/MoneyDistributionTemplateV2.rml'

    def __init__(self, mdf_id):
        super(MDFExporter, self).__init__(self.template_name, self.get_mdf_data(mdf_id))

    def get_mdf_data(self, mdf_id):
        mdf_helper = MoneyDistributionFormHelper(mdf_id)
        return {
            'name': mdf_helper.station_name,
            'date': mdf_helper.date_entered,
            'sections': mdf_helper.sections,
            'total': mdf_helper.total
        }


class MDFBulkExporter():
    def __init__(self, mdf_id_list):
        self.mdf_id_list = mdf_id_list

    def create(self):
        output = StringIO()
        mdf_zip = zipfile.ZipFile(output, 'w')

        for mdf_id in self.mdf_id_list:
            pdf = MDFExporter(mdf_id).create()
            mdf_zip.writestr(str(mdf_id) + '.pdf', pdf.getvalue())
        mdf_zip.close()
        
        return output