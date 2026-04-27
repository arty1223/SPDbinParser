import sys
import json

with open('manufacturers.json') as json_file:
    manufacturers = json.load(json_file)

with open('ddrTypes.json') as json_file:
    ddrTypes = json.load(json_file)

with open('dimmTypes.json') as json_file:
    dimmTypes = json.load(json_file)

with open('capacityMap.json') as json_file:
    capacityMap = json.load(json_file)

def main():
    # Проверяем, был ли передан параметр
    if len(sys.argv) < 2:
        print("Ошибка: Не указано имя файла")
        print("Использование: python program.py <имя_файла>")
        sys.exit(1)
    
    # Получаем имя файла из аргументов командной строки
    filename = sys.argv[1]
    spd_details = {}
    try:
        # Пытаемся открыть и прочитать файл
        with open(filename, 'rb') as file:
            content = file.read()
            
        ddr_type = content[2] #тип ддр
        spd_details["ddr_type"] = ddrTypes[str(ddr_type)]
        ddr_type = spd_details["ddr_type"][spd_details["ddr_type"].find("DDR")+3] 
            
        match ddr_type:
            case '3':
                manLb = content[117] # id производителя
                manHb = content[118]
                SDRAM_Capacity = float(capacityMap[str(content[4] & 0b1111)]) # ёмкость в Мб  
                Primary_Bus_Width = 2 ** ((content[8] & 0b111) + 3)
                SDRAM_Width = 2 ** ((content[7] & 0b111) + 2)
                Logical_Ranks_per_DIMM = ((content[7] & 0b111000) >> 3) + 1
                capacity = SDRAM_Capacity / 8 * Primary_Bus_Width / SDRAM_Width * Logical_Ranks_per_DIMM
            case '4':
                manLb = content[320] # id производителя
                manHb = content[321]
                SDRAM_Capacity = float(capacityMap[str(content[4] & 0b1111)]) # ёмкость в Мб  
                Primary_Bus_Width = 2 ** ((content[13] & 0b111) + 3)
                SDRAM_Width = 2 ** ((content[12] & 0b111) + 2)
                Logical_Ranks_per_DIMM = ((content[12] & 0b111000) >> 3) + 1
                if content[6] & 0b11 == 0b10: # 3DS
                    Logical_Ranks_per_DIMM *= ((content[6] & 0b1110000) >> 4) + 1
                capacity = SDRAM_Capacity / 8 * Primary_Bus_Width / SDRAM_Width * Logical_Ranks_per_DIMM
                
            case '5':
                manLb = content[512] # id производителя
                manHb = content[513]
            case _:
                raise("unknown ddr type")
            
        dimm_type = content[3] & 0b1111    
        spd_details["dimm_type"] = dimmTypes[ddr_type+str(dimm_type)]
        spd_details["manufacturer"] = manufacturers[str(((manLb & ~0x80) << 8) + manHb)]
        spd_details["capacity"] = capacity

        print(spd_details)
            
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден")
    except PermissionError:
        print(f"Ошибка: Нет прав для чтения файла '{filename}'")
    except KeyError:
        print(f"unable to parse {filename}")
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

if __name__ == "__main__":
    main()