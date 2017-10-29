import logging
import datetime

from braces.views import LoginRequiredMixin
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic import View
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from templated_email import send_templated_mail
from rest_framework.decorators import api_view, permission_classes

from accounts.mixins import PermissionsRequiredMixin
from budget.models import BorderStationBudgetCalculation, StaffSalary
from dataentry.models import BorderStation
from rest_api.authentication import HasPermission
from static_border_stations.models import Staff, CommitteeMember
from static_border_stations.serializers import StaffSerializer, CommitteeMemberSerializer
from accounts.models import Account
from accounts.serializers import AccountMDFSerializer

from budget.pdfexports.mdf_exports import MDFExporter, MDFBulkExporter

logger = logging.getLogger(__name__)

class MoneyDistribution(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_budget_view']

    def retrieve(self, request, pk):
        budget = BorderStationBudgetCalculation.objects.get(pk=pk)
        border_station = budget.border_station
        staff = border_station.staff_set.exclude(email__isnull=True)
        committee_members = border_station.committeemember_set.exclude(email__isnull=True)
        national_staff = Account.objects.filter(permission_can_receive_mdf=True)

        staff_serializer = StaffSerializer(staff, many=True)
        committee_members_serializer = CommitteeMemberSerializer(committee_members, many=True)
        national_staff_serializer = AccountMDFSerializer(national_staff, many=True)

        pdf_url = settings.SITE_DOMAIN + reverse('MdfPdf', kwargs={"uuid": budget.mdf_uuid})

        return Response({"staff_members": staff_serializer.data, "committee_members": committee_members_serializer.data, "national_staff_members": national_staff_serializer.data, "pdf_url": pdf_url})

    def send_emails(self, request, pk):
        budget_calc_id = pk
        staff_ids = request.data['staff_ids']
        committee_ids = request.data['committee_ids']
        national_staff_ids = request.data['national_staff_ids']

        budget_calc = BorderStationBudgetCalculation.objects.get(pk=budget_calc_id)
        border_station = BorderStation.objects.get(pk=budget_calc.border_station.id)

        staff = border_station.staff_set.all()
        committee_members = border_station.committeemember_set.all()
        national_staff = Account.objects.filter(permission_can_receive_mdf=True, id__in=national_staff_ids)

        self.save_recipients_and_email(staff, staff_ids, budget_calc)
        self.save_recipients_and_email(committee_members, committee_ids, budget_calc)

        self.email_national_staff(national_staff, budget_calc)
        return Response("Emails Sent!", status=200)

    def save_recipients_and_email(self, person_list, recipient_ids, budget_calc):
        for person in person_list:
            if person.id in recipient_ids:
                if person.receives_money_distribution_form == False:
                    person.receives_money_distribution_form = True
                    person.save()
                self.email_staff_and_committee_members(person, budget_calc, 'money_distribution_form')
            else:
                person.receives_money_distribution_form = False
                person.save()

    def email_national_staff(self, staff_list, budget_calc):
        for staff in staff_list:
            self.email_staff_and_committee_members(staff, budget_calc, 'money_distribution_form')

    def email_staff_and_committee_members(self, person, budget_calc, template, context={}):
        logger.info("Sending MDF - %s for %s to %s", budget_calc.border_station.station_code, budget_calc.month_year.strftime("%B %Y"), person.email)
        context['person'] = person
        context['mdf_uuid'] = budget_calc.mdf_uuid
        context['station_name'] = budget_calc.border_station.station_name
        context['site'] = settings.SITE_DOMAIN
        send_templated_mail(
            template_name=template,
            from_email=settings.BORDER_STATION_EMAIL_SENDER,
            recipient_list=[person.email],
            context=context
        )
        

class MDFExportViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, HasPermission)
    permissions_required = ['permission_budget_view']

    def get_mdf_pdf(self, request, uuid):
        budget = BorderStationBudgetCalculation.objects.get(mdf_uuid=uuid)

        logger.info("Generating MDF PDF %s for %s", budget.mdf_file_name(), request.user)
        pdf_buffer = MDFExporter(budget).create()
        return self.create_response('application/pdf', budget.mdf_file_name(), pdf_buffer)

    def get_mdf_pdf_bulk(self, request, month, year):
        logger.info("Generating MDF Zip for %d %d for %s", month, year, request.user)

        budgets = self.get_budgets(month, year)
        if len(budgets) == 0:
            return Response({'detail' : "No MDFs found for the specific month and year"}, status = status.HTTP_404_NOT_FOUND)

        zip_buffer = MDFBulkExporter(budgets).create()
        return self.create_response('application/zip', "{}-{}-mdfs.zip".format(month, year), zip_buffer)

    def count_mdfs_for_month_year(self, request, month, year):
        return Response({"count": len(self.get_budgets(month, year))})

    def get_budgets(self, month, year):
        startDate = datetime.date(int(year), int(month), 1)
        endDate = datetime.date(int(year), int(month), 28)
        return BorderStationBudgetCalculation.objects.filter(month_year__gte=startDate, month_year__lte=endDate)
        

    def create_response(self, content_type, filename, buffer):
        response = HttpResponse(buffer.getvalue(), content_type=content_type)
        response['Content-Disposition'] = "filename=%s" % filename
        response['X-Frame-Options'] = "*"
        return response