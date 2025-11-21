import re

with open("rawInput.txt", "a") as f:
    running = True

    pattern = r"^%B\d{16}\^[A-Z]+\/[A-Z]+\^\w+\?\;\d{16}=\d+\?$"
    namePattern = r"(?<=\^)[A-Z]+\/[A-Z]+(?=\^)"
    idPattern = r"(?<=2108701)B+\d{8}+(?=\?+\;)"

    while (running):
        rawInput = input()
        # rawInput = "%B6039500482024337^WIYNINGER/CALEB^2108701B00119458?;6039500482024337=2108701000119458?"
        
        if "close" in rawInput:
            running = false
            break
        if re.match(pattern, rawInput):
            cardInfo = rawInput
            name = re.findall(namePattern, cardInfo)
            print(name)
            f.write("\n")
        else:
            print("NOT A VALID STUDENT ID")
        rawInput = ""

        

    
