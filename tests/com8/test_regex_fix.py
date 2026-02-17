import re

text = """royalties.</112|65536>

<112|65536:525252,9,Arial|0,0>In addition, there is a risk

<113 |

<113|65536:525252,9,Arial|0,0>1. Increase in allergies</113|65536>"""

print("ORIGINAL:")
print(text)
print()

# My current bad regex
bad_cleaned = re.sub(r'<\s*\d+\s*\|[^>]*$', '', text)
bad_cleaned = re.sub(r'<\s*\d+\s*\|[^>]*(?=\s)', ' ', bad_cleaned)
print("AFTER MY BAD REGEX:")
print(bad_cleaned)
print()

# Better regex - only remove the tag itself, not what follows
better_cleaned = re.sub(r'<\s*\d+\s*\|[^\s>]*', '', text)
print("AFTER BETTER REGEX:")
print(better_cleaned)
print()
