###############
# Guillermo. R. (2020) FBHarfileScraper source code (Version 3.0) [Source code]. https://www.researchgate.net/publication/352350422_FBHarfileScraper

from pathlib import Path

inputharfile = Path("~/Downloads/willem_heinrich 2.har").expanduser()
outputcsvfile = "willem_heinrich 2.csv"

from datetime import datetime

file = open(inputharfile, encoding="latin1")


testfile = open(outputcsvfile, "w")


##testfile.write("Name" + "; " + "Gender" + "; " + "Date" + "; " + "Time" + "; " + "Total Reactions" + "; " + "Likes" + "; " + "Loves" + "; " + "Wows" + "; " + "Hahas" + "; " + "Sads" + "; " + "Angrys" + "; " + "Cares" + "; " + "Labels" + "; " + "Comments" + "\n")
testfile.write(
    "Name"
    + "; "
    + "Gender"
    + "; "
    + "Date"
    + "; "
    + "Time"
    + "; "
    + "Total Reactions"
    + "; "
    + "Comments"
    + "\n"
)

COMNTS = 0
ctr = 0
comment3 = ""
author = "YES"
gender = "YES"

C1 = "0"
C2 = "0"
C3 = "0"
C4 = "0"
C5 = "0"
C6 = "0"
C7 = "0"
C8 = "0"
C9 = "0"
C10 = "0"
C11 = "0"
C12 = "0"

C2a = "0"  # Default or initial value
C2b = "0"  # Default or initial value
for line in file:
    a = line.replace("\\\\\\", "###")
    a1 = a.replace("\\\\", "##")
    z = a1.replace('"', "#")
    y = z.split("\\")

    w = len(y) - 16

    for x in range(w):
        comment3 = ""

        if y[x] + y[x + 4] + y[x + 10] == "#id#name#User":
            author1 = y[x + 6].replace("##", " \\\\")
            author2 = author1.replace("#", "")

            if author == "NO":
                testfile.write(
                    C1
                    + "; "
                    + C2
                    + "; "
                    + C2a
                    + "; "
                    + C2b
                    + "; "
                    + C3
                    + "; "
                    + C4
                    + "; "
                    + C5
                    + "; "
                    + C6
                    + "; "
                    + C7
                    + "; "
                    + C8
                    + "; "
                    + C9
                    + "; "
                    + C10
                    + "; "
                    + C11
                    + "; "
                    + C12
                    + "\n"
                )
                C4 = "0"
                C5 = "0"
                C6 = "0"
                C7 = "0"
                C8 = "0"
                C9 = "0"
                C10 = "0"
                C11 = "0"
                C12 = "0"

                gender = "YES"
                COMNTS = COMNTS + 1

            C1 = author2
            author = "NO"

        if y[x] == "#gender":
            g = 0

            if y[x + 2] == "#NEUTER":
                continue

            if gender == "NO":
                continue

            if author == "YES":
                continue

            if y[x + 2] != "#MALE":
                g = g + 1

            if y[x + 2] != "#FEMALE":
                g = g + 1

            if g == 2:
                continue

            C2 = y[x + 2].replace("#", "")

            gender = "NO"

        if y[x] == "#created_time":
            if author == "YES":
                continue

            timedate1 = y[x + 1].replace("#", "")
            timedate2 = timedate1.replace(":", "")
            timedate3 = timedate2.replace(",", "")
            timedate4 = datetime.fromtimestamp(int(timedate3))
            C2a = timedate4.strftime("%m/%d/%Y")
            C2b = timedate4.strftime("%H:%M:%S")

        if y[x] == "#count_reduced":
            if author == "YES":
                continue

            C3 = y[x + 2].replace("#", "")

        if y[x] == "#LIKE":
            like1 = y[x - 11].replace("#:", "")
            like2 = like1.replace(",", "")

            if author == "YES":
                continue

            C4 = like2

        if y[x] == "#LOVE":
            love1 = y[x - 11].replace("#:", "")
            love2 = love1.replace(",", "")

            if author == "YES":
                continue

            C5 = love2

        if y[x] == "#WOW":
            wow1 = y[x - 11].replace("#:", "")
            wow2 = wow1.replace(",", "")

            if author == "YES":
                continue

            C6 = wow2

        if y[x] == "#HAHA":
            haha1 = y[x - 11].replace("#:", "")
            haha2 = haha1.replace(",", "")

            if author == "YES":
                continue

            C7 = haha2

        if y[x] == "#SORRY":
            sorry1 = y[x - 11].replace("#:", "")
            sorry2 = sorry1.replace(",", "")

            if author == "YES":
                continue

            C8 = sorry2

        if y[x] == "#ANGER":
            angry1 = y[x - 11].replace("#:", "")
            angry2 = angry1.replace(",", "")

            if author == "YES":
                continue

            C9 = angry2

        if y[x] == "#SUPPORT":
            care1 = y[x - 11].replace("#:", "")
            care2 = care1.replace(",", "")

            if author == "YES":
                continue

            C10 = care2

        if y[x] + y[x + 1] == "#label#:":
            if y[x + 2] + y[x + 3] == "##,":
                continue

            C11 = y[x + 2]

        if y[x] == "#text":
            comment1 = y[x + 2].replace("##", " \\\\")
            comment2 = comment1.replace("#", "")
            if comment3 == comment2:
                continue

            if author == "YES":
                continue

            C12 = comment2 + "\n"

            comment3 = comment2

            # testfile.write(C1 + "; " + C2 + "; " + C2a + "; " + C2b + "; " + C3 + "; " + C4 + "; " + C5 + "; " + C6 + "; " + C7 + "; " + C8 + "; " + C9 + "; " + C10 + "; " + C11 + "; "  + C12)

            testfile.write(
                C1 + "; " + C2 + "; " + C2a + "; " + C2b + "; " + C3 + "; " + C12
            )

            C4 = "0"
            C5 = "0"
            C6 = "0"
            C7 = "0"
            C8 = "0"
            C9 = "0"
            C10 = "0"
            C11 = "0"
            C12 = "0"

            author = "YES"
            gender = "YES"
            COMNTS = COMNTS + 1
testfile.close()


#######################################
## Delete Repetitions

testfile = open(outputcsvfile, "r")

COMENTS = [0] * (COMNTS + 1)
x = 0

for line in testfile:
    COMENTS[x] = line
    x = x + 1

for a in range(len(COMENTS)):
    for b in range(len(COMENTS)):
        if COMENTS[a] == COMENTS[b]:
            if a != b:
                COMENTS[b] = "0"

testfile.close()


########################################
# Final list


testfile = open(outputcsvfile, "w")

for a in range(len(COMENTS)):
    if COMENTS[a] == "0":
        continue

    print(COMENTS[a])

    testfile.write(COMENTS[a])

testfile.close()
