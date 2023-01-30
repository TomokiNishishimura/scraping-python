import sys
import requests

url = sys.argv[1]
response = requests.get(url)
print(f'encoding: {response.encoding}', file=sys.stderr)
print(response.text)