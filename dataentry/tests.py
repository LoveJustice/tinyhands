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


    def MySetUp(self,cutOffNum,matchName):
        cutoffNumber = cutOffNum #int(input("enter a cutoff number"))                                                                                                                   
        cutoffNumber = float(cutoffNumber)
        names = []
        with open('non_victims.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                names.append(row[2])
            enteredName = matchName #raw_input("Enter name to search: ")                                                                                                                
            matches = process.extractBests(enteredName, names, score_cutoff=cutoffNumber, limit=None)
            modMatches = []
            for match in matches:
                modMatches.append(match[0])
            return modMatches

    def testFuzzyOne(self):
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

        self.assertEqual(MySetUp(86,"amit"), testMatches)
        #self.assertEqual(modeMatches, testMatches)
