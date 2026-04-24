import sys
import json

with open('manufacturers.json') as json_file:
    manufacturers = json.load(json_file)

def main():
    # Проверяем, был ли передан параметр
    if len(sys.argv) < 2:
        print("Ошибка: Не указано имя файла")
        print("Использование: python program.py <имя_файла>")
        sys.exit(1)
    
    # Получаем имя файла из аргументов командной строки
    filename = sys.argv[1]
    
    try:
        # Пытаемся открыть и прочитать файл
        with open(filename, 'rb') as file:
            content = file.read()
            print(f"Содержимое файла '{filename}':")
            id = (content[320] << 8) + content[321]
            if id > 0x8100:
                id -= 0x8000
            print(manufacturers[str(id)])
            
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден")
    except PermissionError:
        print(f"Ошибка: Нет прав для чтения файла '{filename}'")
    except KeyError:
        print("unable to parse manufacturer")
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

if __name__ == "__main__":
    main()