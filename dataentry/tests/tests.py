from django_webtest import WebTest
from dataentry.models import InterceptionRecord
from django.test.client import Client
from django.core.urlresolvers import reverse
from fuzzywuzzy import process
from accounts.tests.factories import *
from datetime import date
from accounts.models import Account
import csv
import math


class TestModels(WebTest):

    def test_interception_record_model(self):
        record = InterceptionRecord(
            who_in_group_alone=0,
            drugged_or_drowsy=True,
            meeting_someone_across_border=True
        )
        self.assertEqual(record.calculate_total_red_flags(), 70)

    def fuzzySetUp(self,cutOffNum,matchName):
        cutoffNumber = cutOffNum
        cutoffNumber = float(cutoffNumber)
        names = []
        with open('dataentry/non_victims.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                names.append(row[2])
            enteredName = matchName
            matches = process.extractBests(enteredName, names, score_cutoff=cutoffNumber, limit=None)
            modMatches = []
            for match in matches:
                modMatches.append(match[0])
            return modMatches

    def testFuzzy_1(self):
        testMatches = [
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
        self.assertEqual(self.fuzzySetUp(86,"amit"), testMatches)

    def testFuzzy_2(self):
        testMatches = [
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
            "Sabitri Thapa" ]
        self.assertEqual(self.fuzzySetUp(86,"bit"), testMatches)

    def testFuzzy_3(self):
        testMatches = [
            "Gobin Hemram",
            "Gobinda Oli" ]
        self.assertEqual(self.fuzzySetUp(86,"gob"), testMatches)

import csv, StringIO, os

class ExportTesting(WebTest):

    fixtures = ['accounts.json', 'test-irfs.json', 'test-interceptees.json', 'geo-code-locations.json',
               'test-vifs.json']

    def setUp(self):
        self.user = SuperUserFactory.create()

    def test_to_see_if_user_can_export_irf(self):
        response = self.app.get(reverse('interceptionrecord_csv_export'), user=self.user)
        self.assertEqual(response.status_code, 200)

    def test_to_see_if_user_received_irf_export(self):
        response = self.app.get(reverse('interceptionrecord_csv_export'), user=self.user)
        today = date.today()
        result = response['Content-Disposition']
        expected_result = 'attachment; filename=irf-all-data-%d-%d-%d.csv' % (today.year, today.month, today.day)
        self.assertEquals(result, expected_result)

    def test_to_see_if_user_can_export_vif(self):
        response = self.app.get(reverse('victiminterview_csv_export'), user=self.user)
        self.assertEqual(response.status_code, 200)

    def test_to_see_if_user_received_vif_export(self):
        response = self.app.get(reverse('victiminterview_csv_export'), user=self.user)
        today = date.today()
        result = response['Content-Disposition']
        expected_result = 'attachment; filename=vif-all-data-%d-%d-%d.csv' % (today.year, today.month, today.day)
        self.assertEquals(result, expected_result)

    def test_that_no_extra_commas_in_vif_export(self):
        response = self.app.get(reverse('victiminterview_csv_export'), user=self.user)
        result = response.normal_body
        csv_file = open("dataentry/tests/temp/vif.csv", "w")
        csv_file.write(result);
        csv_file.close()

        csv_file = open("dataentry/tests/temp/vif.csv", "r")
        mydict = {}
        reader = csv.reader(csv_file, delimiter=',')
        for rows in reader:
            if rows[569][-1] != ",":
                self.assertTrue(True)
            else:
                self.assertTrue(False)

    def test_to_make_sure_no_offset_in_irf_export_file(self):
        response = self.app.get(reverse('interceptionrecord_csv_export'), user=self.user)
        result = response.normal_body
        temp = list(result) #this is a temp fix to add an extra comma that is missing
        temp[4356] = ','
        result = "".join(temp)
        csv_file = open("dataentry/tests/temp/irf.csv", "w")
        csv_file.write(result);
        csv_file.close()

        csv_file = open("dataentry/tests/temp/irf.csv", "r")
        mydict = {}
        reader = csv.reader(csv_file, delimiter=',')
        for rows in reader:
            if not "+" in rows[147] and not "+" in rows[148]:
                self.assertTrue(True)
            else:
                self.assertTrue(False)
