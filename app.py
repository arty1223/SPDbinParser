import sys
import json

with open('manufacturers.json') as json_file:
    manufacturers = json.load(json_file)

with open('ddrTypes.json') as json_file:
    ddrTypes = json.load(json_file)

with open('dimmTypes.json') as json_file:
    dimmTypes = json.load(json_file)

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
            #тип
        ddr_type = content[2]
        spd_details["ddr_type"] = ddrTypes[str(ddr_type)]
        ddr_type = spd_details["ddr_type"][spd_details["ddr_type"].find("DDR")+3]
        dimm_type = content[3] & 0b1111
        
        match ddr_type:
            case '3':
                manLb = content[117] # id производителя
                manHb = content[118]
            case '4':
                manLb = content[320] # id производителя
                manHb = content[321]
            case '5':
                manLb = content[512] # id производителя
                manHb = content[513]
            case _:
                raise("unknown ddr type")
            
        spd_details["dimm_type"] = dimmTypes[ddr_type+str(dimm_type)]
        spd_details["manufacturer"] = manufacturers[str(((manLb & ~0x80) << 8) + manHb)]

        print(f"{filename}\n", spd_details)
            
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