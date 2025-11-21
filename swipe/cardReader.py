import re

with open("rawInput.txt", "a") as f:
    running = True
    pattern = r"^%B\d{17}\^[A-Z]+/[A-Z]+\^\w+\?\;\d{17}=\d+\?$"

    while (running):
        # cardInfo = input()
        cardInfo = "%B6039500482024337^WIYNINGER/CALEB^2108701B00119458?;6039500482024337=2108701000119458?"
        
        if "close" in cardInfo:
            running = false
            break
        if re.match(pattern, cardInfo):
            name = re.search("^^$", cardInfo)
            f.write(name)
            f.write("\n")
            f.flush()
        else:
            print("NOT A VALID STUDENT ID")
        cardInfo = ""

        

    
