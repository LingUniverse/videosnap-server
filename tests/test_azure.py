from litellm import completion

import os

print("test")

## set ENV variables
os.environ["AZURE_API_KEY"] = ""
os.environ["AZURE_API_BASE"] = ""
os.environ["AZURE_API_VERSION"] = ""

print("test")

# azure call
response = completion(
    model = "azure/gpt-4o", 
    messages = [{ "content": "Hello, how are you?","role": "user"}]
)

print(response)

