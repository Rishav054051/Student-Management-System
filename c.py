import cohere #to check for api key

# Replace this with your actual key
API_KEY = '2cMoENwLIbbF5XNamWZuwWewmehx6VCqvY0oCPyS'

co = cohere.Client(API_KEY)

try:
    response = co.generate(
        model='command-r-plus',
        prompt="Give a motivational quote for students.",
        max_tokens=50
    )
    print("✅ Cohere API is working!")
    print("Generated Output:\n", response.generations[0].text.strip())
except Exception as e:
    print("❌ Error with Cohere API:")
    print(e)
