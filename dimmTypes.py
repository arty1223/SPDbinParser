import json

with open('dimmTypes.json') as json_file:
    dimm1 = json.load(json_file)
dimm2 = {}
for k,v in dimm1.items():
    dimm2[str(int(k,2))] = v

with open('dimmTypes.json','w') as json_file:
    json.dump(dimm2 , json_file, ensure_ascii=False) 
