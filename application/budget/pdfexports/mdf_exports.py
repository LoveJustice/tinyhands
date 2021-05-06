from budget.pdfexports.pdf_creator import BasePDFCreator
from budget.helpers import MoneyDistributionFormHelper
import zipfile
from io import BytesIO


class MDFExporter(BasePDFCreator):
    template_name = 'budget/MoneyDistributionTemplateV2.rml'

    def __init__(self, mdf_id):
        super(MDFExporter, self).__init__(self.template_name, self.get_mdf_data(mdf_id))

    def get_mdf_data(self, mdf_id):
        mdf_helper = MoneyDistributionFormHelper(mdf_id)
        return {
            'name': mdf_helper.station_name,
            'date': mdf_helper.date_entered,
            'month': mdf_helper.report_month,
            'staff': mdf_helper.staff,
            'sections': mdf_helper.sections,
            'total': mdf_helper.total,
            'notes': mdf_helper.notes,
            'past_money_sent':mdf_helper.past_money_sent_subtotal
        }


class MDFBulkExporter():
    def __init__(self, budgets):
        self.budgets = budgets

    def create(self):
        output = BytesIO()
        mdf_zip = zipfile.ZipFile(output, 'w')

        for budget in self.budgets:
            pdf = MDFExporter(budget).create()
            mdf_zip.writestr(budget.mdf_file_name(), pdf.getvalue())
        mdf_zip.close()
        
        return output
