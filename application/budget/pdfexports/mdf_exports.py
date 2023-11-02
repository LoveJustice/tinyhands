from budget.pdfexports.pdf_creator import BasePDFCreator
from budget.helpers import MoneyDistributionFormHelper, Footnote
from budget.helpers_pr import MoneyDistributionFormProjectRequestHelper
from budget.models import BorderStationBudgetCalculation
from dataentry.models import BorderStation
import zipfile
from io import BytesIO


class MDFExporter(BasePDFCreator):
    budget_template_name = 'budget/MoneyDistributionTemplate.rml'
    mdf_pr_template_name = 'budget/MoneyDistributionProjectRequestTemplate.rml'

    def __init__(self, mdf):
        super(MDFExporter, self).__init__(self.budget_template_name if isinstance(mdf, BorderStationBudgetCalculation) else self.mdf_pr_template_name, self.get_mdf_data(mdf))

    def get_mdf_data(self, mdf):
        self.mdf_list = []
        format = "{:,.2f}"
        first_page_footnote = Footnote()
        second_page_footnote = Footnote()
        impact_multiplying_list = list(BorderStation.objects.filter(mdf_project=mdf.border_station))
        if isinstance(mdf, BorderStationBudgetCalculation):
            helper_class = MoneyDistributionFormHelper
        else:
            helper_class = MoneyDistributionFormProjectRequestHelper
            other_requests = mdf.requests.all().exclude(project=mdf.border_station).exclude(project__in=impact_multiplying_list)
            for other_request in other_requests:
                if not (other_request.project in impact_multiplying_list):
                    impact_multiplying_list.append(other_request.project)
            
        main_mdf_helper = helper_class(mdf, mdf.border_station, first_page_footnote, second_page_footnote)
        distribution_subtotal = main_mdf_helper.distribution_total
        distribution_formula = '(' + format.format(main_mdf_helper.distribution_total) + ' (Monthly Distribution Subtotal (' + main_mdf_helper.project.station_code + '))'
        station_subtotal = main_mdf_helper.full_total
        full_formula = '(' + format.format(main_mdf_helper.full_total) + ' (Full Project Cost (' + main_mdf_helper.project.station_code + '))'
        self.mdf_list.append(main_mdf_helper)
        for impact_multiplying in impact_multiplying_list:
            impact_mdf = helper_class(mdf, impact_multiplying, first_page_footnote, second_page_footnote)
            distribution_subtotal += impact_mdf.distribution_total
            distribution_formula += ' + ' + format.format(impact_mdf.distribution_total) + ' (Monthly Distribution Subtotal (' + impact_mdf.project.station_code + '))'
            station_subtotal += impact_mdf.full_total
            full_formula += ' + ' + format.format(impact_mdf.full_total) + ' (Full Project Cost (' + impact_mdf.project.station_code + '))'
            self.mdf_list.append(impact_mdf)
            
        distribution_formula += ' = ' + format.format(distribution_subtotal) + ')'
        full_formula += ' = ' + format.format(station_subtotal) + ')'
            
        return {
            'name': main_mdf_helper.station_name,
            'date': main_mdf_helper.date_entered,
            'month': main_mdf_helper.report_month,
            'mdfs':self.mdf_list,
            'first_footnotes': first_page_footnote,
            'second_footnotes': second_page_footnote,
            'distribution_subtotal': distribution_subtotal,
            'distribution_formula': distribution_formula,
            'station_subtotal': station_subtotal,
            'full_formula': full_formula,
            'other_detail': self.otherDetailPresent()
        }
    
    def otherDetailPresent(self):
        for mdf in self.mdf_list:
            if mdf.money_not_spent_data.has_data():
                return True
            if mdf.past_sent.has_data():
                return True
        
        return False


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
