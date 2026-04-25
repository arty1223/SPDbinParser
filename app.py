import sys
import json

with open('manufacturers.json') as json_file:
    manufacturers = json.load(json_file)

with open('ddrtypes.json') as json_file:
    ddrtypes = json.load(json_file)

def getManufacturer(lb,hb):
    # производитель
    id = (lb << 8) + hb
    if id > 0x8100:
        id -= 0x8000
    return manufacturers[str(id)]

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
        id = content[2]
        spd_details["ddr_type"] = ddrtypes[str(id)]
        id = spd_details["ddr_type"][spd_details["ddr_type"].find("DDR")+3]
        
        manLb, manHb = 0, 0
        match id:
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
            
        spd_details["manufacturer"] = getManufacturer(manLb, manHb)


        print(f"{filename}\n", spd_details)
            
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден")
    except PermissionError:
        print(f"Ошибка: Нет прав для чтения файла '{filename}'")
    except KeyError:
        print(f"unable to parse manufacturer for {filename}")
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

if __name__ == "__main__":
    main()