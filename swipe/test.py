import re

# Your test string
# test_string = "%B6039500482024337^WIYNINGER/CALEB^2108701B00119458?;6039500482024337=2108701000119458?"
# test_string = "%B6039500482015763^MORALES/SAMANTHA^2108701B00119615?;6039500482015763=2108701000119615?"
test_string = "%B6039500482017953^WARREN/JONATHAN^2108701B00118334?;6039500482017953=2108701000118334?"

# pattern = r"^%B\d{16}\^[A-Z]+\/[A-+\?\;\Z]+\^\w+\?\;\d{16}=\d+\?$"

# pattern = r"^%B\d{16}\^[A-Z]+\/[A-Z]+\^\w+\?\;\d{16}=\d+\?$"


# namePattern = r"^\^[A-Z]+\/[A-Z]+\^$"
namePattern = r"(?<=\^)[A-Z]+\/[A-Z]+(?=\^)"
idPattern = r"(?<=2108701)B+\d{8}+(?=\?+\;)"

names = re.findall(namePattern, test_string)
print(names)
ids = re.findall(idPattern, test_string)
print(ids)
# Matching
# if re.match(pattern, test_string):
#     print("The string matches the pattern.")
# else:
#     print("The string does not match the pattern.")
