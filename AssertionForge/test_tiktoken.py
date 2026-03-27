import tiktoken
print("Imported tiktoken.")
try:
    print("Getting encoding for o200k_base...")
    encoding = tiktoken.get_encoding("o200k_base")
    print("Got encoding.")
    print(encoding.encode("test"))
except Exception as e:
    print(f"Error: {e}")

try:
    print("Getting encoding for cl100k_base...")
    encoding = tiktoken.get_encoding("cl100k_base")
    print("Got encoding.")
    print(encoding.encode("test"))
except Exception as e:
    print(f"Error: {e}")
