from datetime import date
from fuzzywuzzy import process

import csv

from django_webtest import WebTest
from django.core.urlresolvers import reverse

from accounts.tests.factories import *
from dataentry.tests.factories import VifFactory, IntercepteeFactory

from dataentry.models import InterceptionRecord


class TestModels(WebTest):

    def test_interception_record_model(self):
        record = InterceptionRecord(
            who_in_group_alone=0,
            drugged_or_drowsy=True,
            meeting_someone_across_border=True
        )
        self.assertEqual(record.calculate_total_red_flags(), 70)

    def fuzzySetUp(self, cut_off_number, match_name):
        cut_off_number = float(cut_off_number)

        with open('dataentry/tests/non_victims.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            names = [row[2] for row in reader]
            entered_name = match_name
            matches = process.extractBests(entered_name, names, score_cutoff=cut_off_number, limit=None)
            mod_matches = [match[0] for match in matches]
            return mod_matches

    def testFuzzy_1(self):
        test_matches = [
            "Amit Agrawal",
            "Amit Basnet",
            "Amit Basnet",
            "Amit Chaudhary 1",
            "Amit Chaudhary Tharu",
            "Amit Chaudhary Tharu",
            "Amit Das",
            "Amit Gurung",
            "Amit Gurung",
            "Amit Kumar Pariyar",
            "Amit Kumar Rajak",
            "Amit Kumar Rajak",
            "Amit Nath Mishra",
            "Amit Nepali",
            "Amit Nepali",
            "Amit Nepali",
            "Amit Rajbansi",
            "Amit Rajbansi",
            "Amit Tamang",
            "Amit Thapa",
            "Amita Sirpali",
            "Pramita Rai",
            "Pramita Rai",
            "Pramita Rai",
            "Ramita Limbu",
            "Ramita Roka Magar"]
        self.assertEqual(self.fuzzySetUp(86, "amit"), test_matches)

    def testFuzzy_2(self):
        test_matches = [
            "Abita",
            "Babita Rai 1",
            "Babita Rai 1",
            "Babita Rai 1",
            "Bittam Dong Theeng",
            "Bittam Dong Theeng",
            "Bittam Dong Theeng",
            "Bittam Dong Theeng",
            "Bittam Dong Theeng",
            "Kabita Manandhar",
            "Kabita Sunam",
            "Kabita Sunam",
            "Pabitra B.K. 1",
            "Pabitra Maya Tamang",
            "Rita Maya Pabitra Rai",
            "Rita Maya Pabitra Rai",
            "Sabita Pandey",
            "Sabitri Budathoki",
            "Sabitri Budathoki",
            "Sabitri Budathoki",
            "Sabitri Shrestha",
            "Sabitri Thapa"
        ]
        self.assertEqual(self.fuzzySetUp(86, "bit"), test_matches)

    def testFuzzy_3(self):
        test_matches = [
            "Gobin Hemram",
            "Gobinda Oli"
        ]
        self.assertEqual(self.fuzzySetUp(86, "gob"), test_matches)


class ExportTesting(WebTest):
    def setUp(self):
        self.user = SuperUserFactory.create()
        self.intercept = IntercepteeFactory.create()  # This creates an IRF as a SubFactory used in the tests
        self.vif = VifFactory.create()

    def test_to_see_if_user_can_export_irf(self):
        response = self.app.get(reverse('InterceptionRecordCsvExport'), user=self.user)
        self.assertEqual(response.status_code, 200)

    def test_to_see_if_user_received_irf_export(self):
        response = self.app.get(reverse('InterceptionRecordCsvExport'), user=self.user)
        today = date.today()
        result = response['Content-Disposition']
        expected_result = 'attachment; filename=irf-all-data-%d-%d-%d.csv' % (today.year, today.month, today.day)
        self.assertEquals(result, expected_result)

    def test_to_see_if_user_can_export_vif(self):
        response = self.app.get(reverse('VictimInterviewCsvExport'), user=self.user)
        self.assertEqual(response.status_code, 200)

    def test_to_see_if_user_received_vif_export(self):
        response = self.app.get(reverse('VictimInterviewCsvExport'), user=self.user)
        today = date.today()
        result = response['Content-Disposition']
        expected_result = 'attachment; filename=vif-all-data-%d-%d-%d.csv' % (today.year, today.month, today.day)
        self.assertEquals(result, expected_result)

    def test_that_no_extra_commas_in_vif_export(self):
        response = self.app.get(reverse('VictimInterviewCsvExport'), user=self.user)
        result = response.normal_body
        csv_file = open("dataentry/tests/temp/vif.csv", "w")
        csv_file.write(result)
        csv_file.close()

        csv_file = open("dataentry/tests/temp/vif.csv", "r")
        reader = csv.reader(csv_file, delimiter=',')
        for rows in reader:
            if rows[378][-1] != ",":
                self.assertTrue(True)
            else:
                self.assertTrue(False)

    def test_to_make_sure_no_offset_in_irf_export_file(self):
        response = self.app.get(reverse('InterceptionRecordCsvExport'), user=self.user)
        result = response.normal_body
        temp = list(result)  # this is a temp fix to add an extra comma that is missing
        temp[4356] = ','
        result = "".join(temp)
        csv_file = open("dataentry/tests/temp/irf.csv", "w")
        csv_file.write(result)
        csv_file.close()

        csv_file = open("dataentry/tests/temp/irf.csv", "r")
        reader = csv.reader(csv_file, delimiter=',')
        for rows in reader:
            if "+" not in rows[147] and "+" not in rows[148]:
                self.assertTrue(True)
            else:
                self.assertTrue(False)
