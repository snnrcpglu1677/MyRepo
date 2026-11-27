import os
import sys
import time
import sqlite3
from datetime import datetime
from decimal import Decimal, InvalidOperation
from opcua import Client


# =====================================
# SABİT AYARLAR
# =====================================
OPC_READ_SERVER_URL = "opc.tcp://192.168.110.91:4840"
PRODUCT_NAME_NODE_ID = "ns=0;s=Product_ProductName"
STATES_MODES_NODE_ID = "ns=0;s=Machine_StatesModes"

SQLITE_DB_PATH = r"\\192.168.110.91\DT22\SKY22.db"

OPC_WRITE_SERVER_URL = "opc.tcp://192.168.100.250:4840"

BASE_DIR = r"C:\ProgramData\CODESYS\CODESYSControlRTEV3\PlcLogic\PlcLogic"
TRIGGER_FILE = os.path.join(BASE_DIR, "trigger.txt")
OUTPUT_TXT_FILE = os.path.join(BASE_DIR, "PunchReport.txt")
ERROR_TXT_FILE = os.path.join(BASE_DIR, "PunchReport_Error.txt")
LOG_TXT_FILE = os.path.join(BASE_DIR, "ReadDb_Log.txt")

POLL_INTERVAL_SEC = 1


# =====================================
# LOG
# =====================================
def write_log(message):
    try:
        with open(LOG_TXT_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    except Exception:
        pass


# =====================================
# OPC READ
# =====================================
def read_opc_values():
    client = Client(OPC_READ_SERVER_URL)
    try:
        client.connect()

        product_name = client.get_node(PRODUCT_NAME_NODE_ID).get_value()
        states_modes = client.get_node(STATES_MODES_NODE_ID).get_value()

        return str(product_name).strip(), states_modes

    finally:
        try:
            client.disconnect()
        except Exception:
            pass


# =====================================
# DB
# =====================================
def get_product_id(conn, product_name):
    sql = """
        SELECT Id
        FROM Products
        WHERE _Products_ProductName = ?
        LIMIT 1
    """
    cursor = conn.cursor()
    cursor.execute(sql, (product_name,))
    row = cursor.fetchone()
    return None if row is None else row[0]


def get_punch_data(conn, product_id):
    sql = """
        SELECT
            _ProductsSegmentationPunches_ToolDescrip,
            _ProductsSegmentationPunches_ToolOffset,
            _ProductsSegmentationPunches_ToolLength,
            _ProductsSegmentationPunches_ToolIsRotated,
            _ProductsSegmentationPunches_ToolHorn
        FROM ProductsSegmentationPunches
        WHERE _ProductsSegmentationPunches_ProductsId = ?
        ORDER BY Id
    """
    cursor = conn.cursor()
    cursor.execute(sql, (product_id,))
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            "Name": "" if row[0] is None else str(row[0]),
            "Z position": "" if row[1] is None else str(row[1]),
            "Length": "" if row[2] is None else str(row[2]),
            "Rotation": "" if row[3] is None else str(row[3]),
            "Horn": "" if row[4] is None else str(row[4]),
        })
    return result


def get_die_data(conn, product_id):
    sql = """
        SELECT
            _ProductsSegmentationDies_ToolDescrip,
            _ProductsSegmentationDies_ToolOffset,
            _ProductsSegmentationDies_ToolLength
        FROM ProductsSegmentationDies
        WHERE _ProductsSegmentationDies_ProductsId = ?
        ORDER BY Id
    """
    cursor = conn.cursor()
    cursor.execute(sql, (product_id,))
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            "Name": "" if row[0] is None else str(row[0]),
            "Z position": "" if row[1] is None else str(row[1]),
            "Length": "" if row[2] is None else str(row[2]),
        })
    return result


# =====================================
# TXT RAPOR
# =====================================
def build_table(rows, headers):
    widths = {header: len(header) for header in headers}

    for row in rows:
        for header in headers:
            value = str(row.get(header, ""))
            if len(value) > widths[header]:
                widths[header] = len(value)

    def build_line(data):
        return " | ".join(str(data.get(h, "")).ljust(widths[h]) for h in headers)

    header_line = " | ".join(h.ljust(widths[h]) for h in headers)
    separator_line = "-+-".join("-" * widths[h] for h in headers)

    lines = [header_line, separator_line]
    for row in rows:
        lines.append(build_line(row))

    return "\n".join(lines)


def write_report(product_name, states_modes, product_id, punch_rows, die_rows):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("PUNCH / DIE REPORT")
    lines.append("=" * 70)
    lines.append(f"Date Time    : {now}")
    lines.append(f"Product Name : {product_name}")
    lines.append(f"States Modes : {states_modes}")
    lines.append(f"Product Id   : {product_id}")
    lines.append(f"Punch Count  : {len(punch_rows)}")
    lines.append(f"Die Count    : {len(die_rows)}")
    lines.append("")

    lines.append("PUNCH DATA")
    lines.append("-" * 70)
    if punch_rows:
        lines.append(build_table(
            punch_rows,
            ["Name", "Z position", "Length", "Rotation", "Horn"]
        ))
    else:
        lines.append("No punch data found.")

    lines.append("")
    lines.append("DIE DATA")
    lines.append("-" * 70)
    if die_rows:
        lines.append(build_table(
            die_rows,
            ["Name", "Z position", "Length"]
        ))
    else:
        lines.append("No die data found.")

    with open(OUTPUT_TXT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_error(error_message):
    with open(ERROR_TXT_FILE, "w", encoding="utf-8") as f:
        f.write("ERROR REPORT\n")
        f.write("=" * 70 + "\n")
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(str(error_message))


def clear_error_file():
    try:
        if os.path.exists(ERROR_TXT_FILE):
            os.remove(ERROR_TXT_FILE)
    except Exception:
        pass


# =====================================
# OPC WRITE YARDIMCI
# =====================================
def create_empty_matrix(rows=15, cols=12):
    return [["" for _ in range(cols)] for _ in range(rows)]


def center_position(row, tool_type, row_index):
    try:
        position = Decimal(str(row.get("Z position", "")))
        length = Decimal(str(row.get("Length", "")))
    except InvalidOperation as exc:
        raise ValueError(f"{tool_type} satır {row_index}: geçersiz Z pozisyonu veya boy") from exc

    if not position.is_finite() or not length.is_finite() or length <= 0:
        raise ValueError(f"{tool_type} satır {row_index}: geçersiz Z pozisyonu veya boy")

    return format(position + length / 2, "f")


def find_child_by_name(parent, target_name):
    children = parent.get_children()
    for child in children:
        try:
            browse_name = child.get_browse_name()
            display_name = child.get_display_name()

            bn = browse_name.Name if browse_name else ""
            dn = display_name.Text if display_name else ""

            if bn == target_name or dn == target_name:
                return child
        except Exception:
            pass
    return None


def find_child_contains_text(parent, target_text):
    children = parent.get_children()
    target_text_lower = target_text.lower()

    for child in children:
        try:
            browse_name = child.get_browse_name()
            display_name = child.get_display_name()

            bn = browse_name.Name if browse_name else ""
            dn = display_name.Text if display_name else ""

            combined = f"{bn} {dn}".lower()

            if target_text_lower in combined:
                return child
        except Exception:
            pass
    return None


def find_atc_node(client):
    root = client.get_root_node()

    objects = find_child_by_name(root, "Objects")
    if objects is None:
        raise Exception("Objects node bulunamadı.")

    device_set = find_child_by_name(objects, "DeviceSet")
    if device_set is None:
        raise Exception("DeviceSet node bulunamadı.")

    rte_node = find_child_contains_text(device_set, "CODESYS Control RTE x64")
    if rte_node is None:
        raise Exception("CODESYS Control RTE x64 node bulunamadı.")

    resources = find_child_by_name(rte_node, "Resources")
    if resources is None:
        raise Exception("Resources node bulunamadı.")

    atc = find_child_by_name(resources, "ATC")
    if atc is None:
        raise Exception("ATC node bulunamadı.")

    return atc


def write_to_codesys(product_name, punch_rows, die_rows):
    pfields_matrix = create_empty_matrix(15, 12)
    dfields_matrix = create_empty_matrix(15, 12)

    max_punch_count = min(len(punch_rows), 15)
    for i in range(max_punch_count):
        punch = punch_rows[i]
        pfields_matrix[i][2] = str(punch.get("Name", ""))
        pfields_matrix[i][5] = center_position(punch, "Punch", i + 1)
        pfields_matrix[i][6] = str(punch.get("Length", ""))
        pfields_matrix[i][7] = str(punch.get("Rotation", ""))
        pfields_matrix[i][8] = str(punch.get("Horn", ""))

    max_die_count = min(len(die_rows), 15)
    for i in range(max_die_count):
        die = die_rows[i]
        dfields_matrix[i][2] = str(die.get("Name", ""))
        dfields_matrix[i][5] = center_position(die, "Die", i + 1)
        dfields_matrix[i][6] = str(die.get("Length", ""))

    client = Client(OPC_WRITE_SERVER_URL)

    try:
        client.connect()

        atc_node = find_atc_node(client)

        pfields_node = find_child_by_name(atc_node, "PFields")
        if pfields_node is None:
            raise Exception("PFields node bulunamadı.")

        dfields_node = find_child_by_name(atc_node, "DFields")
        if dfields_node is None:
            raise Exception("DFields node bulunamadı.")

        product_name_node = find_child_by_name(atc_node, "Product_Name")
        if product_name_node is None:
            raise Exception("Product_Name node bulunamadı.")

        pfields_node.set_value(pfields_matrix)
        dfields_node.set_value(dfields_matrix)
        product_name_node.set_value(str(product_name))

    finally:
        try:
            client.disconnect()
        except Exception:
            pass


# =====================================
# TRIGGER HELPERS
# =====================================
def trigger_exists():
    return os.path.exists(TRIGGER_FILE)


def delete_trigger():
    try:
        if os.path.exists(TRIGGER_FILE):
            os.remove(TRIGGER_FILE)
            write_log("trigger.txt silindi.")
    except Exception as e:
        write_error(f"trigger.txt silinemedi: {e}")
        write_log(f"trigger.txt silinemedi: {e}")


# =====================================
# ANA İŞ MANTIĞI
# =====================================
def process_once():
    clear_error_file()

    if not os.path.exists(SQLITE_DB_PATH):
        raise FileNotFoundError(f"SQLite dosyası bulunamadı: {SQLITE_DB_PATH}")

    write_log("OPC READ server bağlantısı kuruluyor...")
    product_name, states_modes = read_opc_values()

    if not product_name:
        raise ValueError("OPC'den Product Name boş geldi.")

    write_log(f"Product Name okundu: {product_name}")
    write_log(f"States Modes okundu: {states_modes}")

    write_log("SQLite veritabanına bağlanılıyor...")
    conn = sqlite3.connect(SQLITE_DB_PATH)

    try:
        product_id = get_product_id(conn, product_name)
        if product_id is None:
            raise ValueError(f"Products tablosunda bu ürün bulunamadı: {product_name}")

        write_log(f"Product Id bulundu: {product_id}")

        punch_rows = get_punch_data(conn, product_id)
        write_log(f"Punch sayısı: {len(punch_rows)}")

        die_rows = get_die_data(conn, product_id)
        write_log(f"Die sayısı: {len(die_rows)}")

    finally:
        conn.close()

    write_report(product_name, states_modes, product_id, punch_rows, die_rows)
    write_log(f"TXT çıktı oluşturuldu: {OUTPUT_TXT_FILE}")

    write_log("CODESYS OPC write işlemi başlıyor...")
    write_to_codesys(product_name, punch_rows, die_rows)
    write_log("CODESYS OPC write işlemi tamamlandı.")


# =====================================
# MAIN LOOP
# =====================================
def main():
    write_log("ReadDb arka plan dinleyici başlatıldı.")

    while True:
        try:
            if trigger_exists():
                write_log("trigger.txt algılandı. İşlem başlıyor...")
                try:
                    process_once()
                    write_log("İşlem başarıyla tamamlandı.")
                except Exception as e:
                    write_error(e)
                    write_log(f"Hata oluştu: {e}")
                finally:
                    delete_trigger()
        except Exception as loop_error:
            write_error(loop_error)
            write_log(f"Ana döngü hatası: {loop_error}")

        time.sleep(POLL_INTERVAL_SEC)


if __name__ == "__main__":
    main()

# ReadDb.V2