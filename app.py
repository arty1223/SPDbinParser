import sys
from ctypes import c_byte, c_ubyte
from crc import Calculator, Crc32

from jedecSpeeds import jedecSpeeds
from manufacturers import manufacturers
from ddrTypes import ddrTypes
from capacityMap import capacityMap
from capacityMapD5 import capacityMapD5
from dimmTypes import dimmTypes

def crc16(a:list):
    crc = 0
    for i in list(a):
        crc = crc ^ i << 8;
        for i in range(8):
            if (crc & 0x8000):
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF

def to_signed_byte(value):
    return c_byte(c_ubyte(value).value).value

def calc_tCKavg(mtb: int,ftb: int) -> float:
    ftb = to_signed_byte(ftb)
    return mtb * 0.125 + ftb * 0.001

def correct_speed(speed_mts: float) -> int:
    """
    Округляет вычисленную скорость до ближайшего стандартного JEDEC значения.
    Если скорость превышает максимальную в списке, возвращает её с округлением до целых.
    """
    # Находим ближайшее стандартное значение
    closest = min(jedecSpeeds, key=lambda x: abs(x - speed_mts))
    # Если разница больше 5% — возможно, это не JEDEC скорость, возвращаем округлённое целое
    if abs(closest - speed_mts) / speed_mts > 0.05:
        return int(round(speed_mts))
    return closest

def main():
    # Проверяем, был ли передан параметр
    if len(sys.argv) < 2:
        print("Ошибка: Не указано имя файла")
        print("Использование: python3 app.py <имя_файла>")
        sys.exit(1)

    # Получаем имя файла из аргументов командной строки
    crcCalc = Calculator(Crc32.CRC32)
    filename = sys.argv[1]
    spd_details = {}
    try:
        # Пытаемся открыть и прочитать файл
        with open(filename, "rb") as file:
            content = file.read()

        ddr_type = content[2]  # тип ддр
        spd_details["ddr_type"] = ddrTypes[str(ddr_type)]
        ddr_type = spd_details["ddr_type"][spd_details["ddr_type"].find("DDR") + 3]
        speed_grade = [0,0,0]
        
        match ddr_type:
            case "3":
                if (content[0] & 0x80) == 0:
                    crc = crc16(content[:126]) == ((content[127] << 8) + content[126])
                else:
                    crc = crc16(content[:117]) == ((content[127] << 8) + content[126])
                
                manLb = content[117]  # id производителя
                manHb = content[118]
                part_number = content[128 : 128 + 18]
                SDRAM_Capacity = float(
                    capacityMap[str(content[4] & 0b1111)]
                )  # ёмкость в Мб
                Primary_Bus_Width = 2 ** ((content[8] & 0b111) + 3)
                SDRAM_Width = 2 ** ((content[7] & 0b111) + 2)
                Logical_Ranks_per_DIMM = ((content[7] & 0b111000) >> 3) + 1
                capacity = (
                    SDRAM_Capacity
                    / 8
                    * Primary_Bus_Width
                    / SDRAM_Width
                    * Logical_Ranks_per_DIMM
                )
                tCKavg = calc_tCKavg(content[12], content[34])
                speed_grade[0] = correct_speed(2000 / tCKavg)

            case "4":
                crc = crc16(content[:126]) == ((content[127] << 8) + content[126])
                                
                manLb = content[320]  # id производителя
                manHb = content[321]
                part_number = content[329 : 329 + 20]
                SDRAM_Capacity = float(
                    capacityMap[str(content[4] & 0b1111)]
                )  # ёмкость в Мб
                Primary_Bus_Width = 2 ** ((content[13] & 0b111) + 3)
                SDRAM_Width = 2 ** ((content[12] & 0b111) + 2)
                Logical_Ranks_per_DIMM = ((content[12] & 0b111000) >> 3) + 1
                if content[6] & 0b11 == 0b10:  # 3DS
                    Logical_Ranks_per_DIMM *= ((content[6] & 0b1110000) >> 4) + 1
                capacity = (
                    SDRAM_Capacity
                    / 8
                    * Primary_Bus_Width
                    / SDRAM_Width
                    * Logical_Ranks_per_DIMM
                )
                tCKavg = calc_tCKavg(content[18], content[125])
                speed_grade[0] = correct_speed(2000 / tCKavg)
                tCKavg = calc_tCKavg(content[0x18C], content[0x1AF])
                if tCKavg != 0:
                    speed_grade[1] = correct_speed(2000 / tCKavg)
                tCKavg = calc_tCKavg(content[0x1BB], content[0x1DE])
                if tCKavg != 0:
                    speed_grade[2] = correct_speed(2000 / tCKavg)

            case "5":
                crc = crc16(content[:510]) == ((content[511] << 8) + content[510])                
            
                manLb = content[512]  # id производителя
                manHb = content[513]
                part_number = content[521 : 521 + 30]

                # print(f"content[234] {bin(content[234])}, content[235] {bin(content[235])}, content[6] {bin(content[6])}, content[4] {bin(content[4])}")

                symmetry = content[234] & 0b100_0000
                Number_of_sub_channels_per_DIMM = 2 ** (
                    (content[235] & 0b1110_0000) >> 5
                )
                Primary_bus_width_per_sub_channel = 2 ** ((content[235] & 0b111) + 3)
                SDRAM_IO_Width = 2 ** (((content[6] & 0b1110_0000) >> 5) + 2)
                SDRAM_Density_per_die = int(capacityMapD5[str(content[4] & 0b11111)])
                Package_ranks_per_sub_channel = ((content[234] & 0b111000) >> 3) + 1
                Die_per_package = ((content[4] & 0b1110_0000) >> 5) + 1
                if ((content[4] & 0b1110_0000) >> 5) > 0b01:
                    Die_per_package = (Die_per_package - 1) ** 2

                capacity = (
                    Number_of_sub_channels_per_DIMM
                    * Primary_bus_width_per_sub_channel
                    / SDRAM_IO_Width
                    * Die_per_package
                    * SDRAM_Density_per_die
                    / 8
                    * Package_ranks_per_sub_channel
                )

                if symmetry:
                    even_ranks = capacity / 2
                    SDRAM_IO_Width = 2 ** (((content[6] & 0b1110_0000) >> 5) + 2)
                    SDRAM_Density_per_die = int(
                        capacityMapD5[str(content[4] & 0b11111)]
                    )
                    Die_per_package = ((content[4] & 0b1110_0000) >> 5) + 1
                    Package_ranks_per_sub_channel //= 2
                    odd_ranks = (
                        Number_of_sub_channels_per_DIMM
                        * Primary_bus_width_per_sub_channel
                        / SDRAM_IO_Width
                        * Die_per_package
                        * SDRAM_Density_per_die
                        / 8
                        * Package_ranks_per_sub_channel
                    )
                    capacity = even_ranks + odd_ranks

                tCKmin = ((content[21] << 8) + content[20]) / 1000
                speed_grade[0] = 2_000 / tCKmin // 100 * 100

                tCKmin = ((content[0x2C6] << 8) + content[0x2C5]) / 1000
                if tCKmin != 0:
                    speed_grade[1] = 2_000 / tCKmin // 100 * 100

                tCKmin = ((content[0x306] << 8) + content[0x305]) / 1000
                if tCKmin != 0:
                    speed_grade[2] = 2_000 / tCKmin // 100 * 100 
                
            case _:
                raise ("unknown ddr type")

        dimm_type = content[3] & 0b1111
        spd_details["dimm_type"] = dimmTypes[ddr_type + str(dimm_type)]
        spd_details["manufacturer"] = manufacturers[str(((manLb & ~0x80) << 8) + manHb)]
        spd_details["capacity"] = capacity  # В ГБ
        part_number = part_number.replace(b'\x00', b'')
        spd_details["part_number"] = part_number.decode("utf-8", errors="ignore").rstrip()
        spd_details["base_speed_grade"] = speed_grade[0]
        spd_details["max_speed_grade"] = max(speed_grade)
        spd_details["CRC32"] = crcCalc.checksum(content)
        spd_details["crc"] = crc
        spd_details["filename"] = f"{spd_details["ddr_type"].replace(' ','_')}_{spd_details["dimm_type"]}_{spd_details["manufacturer"]}_{spd_details['part_number']}_{hex(spd_details["CRC32"])}.bin"
        
        print(spd_details)

    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден")
    except PermissionError:
        print(f"Ошибка: Нет прав для чтения файла '{filename}'")
    except KeyError:
        print(f"unable to parse {filename}")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
