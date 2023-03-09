import json
import requests


query_dict = {
    'q': 'Restaurant',
}
serp_url = f'https://serpapi.com/search.json?q={query_dict["q"]}&location=Los+Angeles,+CA,+California,+United+States&hl=en&gl=us&google_domain=google.com&api_key=4184984850056794cfbfea15ff012c639693434be8b767546d6496affe663bb1'
response = requests.get(serp_url)
json_text = response.text
json_dict = json.loads(json_text)
json.dump(json_dict, open('data.json', 'w', encoding='utf-8'), indent=4)