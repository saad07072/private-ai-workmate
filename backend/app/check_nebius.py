import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("NEBIUS_API_KEY")

if not api_key:
    raise RuntimeError("NEBIUS_API_KEY was not found in .env")

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=api_key,
)

print("Connected to Nebius Token Factory.")
print("Available models:\n")

models = client.models.list()

for model in models.data:
    print(model.id)