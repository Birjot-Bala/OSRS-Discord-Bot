from osrsbox import items_api
import json

items = items_api.load()
store_data = {}
store_data['items'] = []

for item in items:
    if item.tradeable_on_ge and not item.duplicate:
        store_data['items'].append({
            'id':item.id,
            'name':item.name
        })
        print(f'{item.id},{item.name}')

with open('tradeable_items.json', 'w', encoding='utf-8') as f:
    json.dump(store_data, f, ensure_ascii=False, indent=4)
        