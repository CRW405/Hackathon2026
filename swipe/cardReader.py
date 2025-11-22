import re
import requests

# send to localhost:6000/api/trackSwipe/<card_info>

url = "http://127.0.0.1:6000/api/trackSwipe/"

# RegEx patterns to parse raw input data

pattern = r"^%B\d{16}\^[A-Z]+\/[A-Z]+\^\w+\?\;\d{16}=\d+\?$"  # checks if input is a valid student id
namePattern = r"(?<=\^)[A-Z]+\/[A-Z]+(?=\^)"  # grabs name
idPattern = r"(?<=2108701)B+\d{8}+(?=\?+\;)"  # grabs B-Number

running = True
while running:
    # rawInput = "%B6039500482024337^WIYNINGER/CALEB^2108701B00119458?;6039500482024337=2108701000119458?"
    rawInput = input()

    if "close" in rawInput:  # closes application if close typed into input
        running = False
        break
    if re.match(pattern, rawInput):  # only runs if valid student ID input
        cardInfo = rawInput
        nameRaw = re.findall(namePattern, cardInfo)
        names = nameRaw[0].split("/")
        idRaw = re.findall(idPattern, cardInfo)

        # FIRSTNAME, LASTNAME, B00XXXXXX
        infoString = names[0] + ", " + names[1] + ", " + idRaw[0]

        response = requests.post(url + infoString, verify=False)
        print(response.text)
    else:
        print("NOT A VALID STUDENT ID")
    rawInput = ""
