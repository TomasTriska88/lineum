import json
import codecs

try:
    with open('.scratch/report2.json', 'r', encoding='utf-8') as f:
        # Check for BOM and skip if present
        content = f.read()
        if content.startswith(codecs.BOM_UTF8.decode('utf-8')):
            content = content[1:]
        data = json.loads(content)
        
    for suit in data.get('errors', []):
        print("====== ERROR ======")
        print(suit.get('message', 'No message'))
        
except Exception as e:
    print(f"Failed: {e}")
