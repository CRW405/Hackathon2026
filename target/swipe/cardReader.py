import re
import requests
import os

from dotenv import load_dotenv

# Build backend URL from environment or defaults
backend_base = os.environ.get("BACKEND_BASE_URL")
if not backend_base:
    backend_host = os.environ.get("BACKEND_HOST", "127.0.0.1")
    backend_port = os.environ.get("BACKEND_PORT", "6000")
    backend_base = f"http://{backend_host}:{backend_port}"

track_path = os.environ.get("TRACK_SWIPE_PATH", "/api/swipe/post/")
url = f"{backend_base}{track_path}"

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
        payload = {
            "first": names[1].capitalize(),
            "last": names[0].capitalize(),
            "bid": "B" + idRaw[0],
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("STUDENT ID RECORDED")
        else:
            print("ERROR RECORDING STUDENT ID")

    else:
        print("NOT A VALID STUDENT ID")
    rawInput = ""
