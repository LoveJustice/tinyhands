from django_webtest import WebTest
from dataentry.models import InterceptionRecord
from fuzzywuzzy import process
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
