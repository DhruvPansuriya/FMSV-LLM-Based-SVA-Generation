import re

source = "AssertionForge/entity_extraction.txt"
with open(source, "r") as f:
    text = f.read()

# Pattern for { that is NOT followed by a known placeholder
# Known placeholders: {entity_types}, {input_text}, {tuple_delimiter}, {record_delimiter}, {completion_delimiter}
pattern = r"\{(?!entity_types|input_text|tuple_delimiter|record_delimiter|completion_delimiter)"

matches = re.finditer(pattern, text)
print(f"Checking {source} for invalid braces...")
for match in matches:
    start = match.start()
    end = match.end()
    # Print context
    context_start = max(0, start - 20)
    context_end = min(len(text), end + 20)
    print(f"Found invalid brace at {start}: '{text[start:end]}'")
    print(f"Context: ...{text[context_start:context_end]}...")
