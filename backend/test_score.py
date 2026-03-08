import asyncio
import json
import logging
import sys
sys.path.insert(0, '.')

from ai_layer.pipeline import ArgusAIPipeline

logging.basicConfig(level=logging.WARNING)

async def main():
    p = ArgusAIPipeline()
    
    url1 = "https://www.99acres.com/4-bhk-bedroom-independent-house-villa-for-rent-in-dodsworth-layout-bangalore-east-6500-sq-ft-spid-R88345030"
    url2 = "https://www.99acres.com/3-bhk-bedroom-apartment-flat-for-rent-in-total-environment-pursuit-of-a-radical-rhapsody-hoodi-bangalore-east-4303-sq-ft-spid-H89314277"
    
    out = {}
    out['url1'] = await p.analyze_url(url1)
    out['url2'] = await p.analyze_url(url2)
    
    with open('test_res.json', 'w') as f:
        json.dump(out, f, indent=2)
        
    print("Done")

if __name__ == "__main__":
    asyncio.run(main())
