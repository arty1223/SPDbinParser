import json
with open ("manufacturers.txt", "r") as f:
    table = f.readlines()
K = -1
manufacturers = {}
for i in table:
    if i == "COMPANY 8 7 6 5 4 3 2 1 HEX\n":
        K+=1
        continue
    elif i == "Continuation Code 0 1 1 1 1 1 1 1 7F\n":
        continue
    t = ' '.join(i[:-19].split()[1:])
    if K == 0:
        manufacturers[int('80' + i[-3:-1],16)] = t
    else:
        manufacturers[int(hex(K)[2:].capitalize() + i[-3:-1],16)] = t
    

with open("./manufacturers.json", "w") as fp:
        json.dump(manufacturers , fp, ensure_ascii=False) 