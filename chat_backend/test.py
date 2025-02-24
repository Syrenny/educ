from openai import OpenAI

# init client and connect to localhost server
client = OpenAI(
    api_key="fake-api-key",
    base_url="http://localhost:8000/v1"  # change the default port if needed
)

stream = client.chat.completions.create(
    model="mock-gpt-model",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True,
)
for chunk in stream:
    print(chunk.choices[0].delta.content)
