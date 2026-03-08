import urllib.request
import re

url = "https://www.99acres.com/3-bhk-bedroom-apartment-flat-for-rent-in-total-environment-pursuit-of-a-radical-rhapsody-hoodi-bangalore-east-4303-sq-ft-spid-H89314277"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    print("HTML length:", len(html))
    
    # regex for getting price. Example: "price":45000 or "price": "45000" or similar
    prices = re.findall(r'"price"\s*:\s*"?(\d+)"?', html, re.IGNORECASE)
    print("Found prices JSON:", prices)
    
    # try title
    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    print("Title:", title_match.group(1) if title_match else "None")
    
    # try description
    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
    print("Desc:", desc_match.group(1) if desc_match else "None")
    
except Exception as e:
    print("Failed", e)
