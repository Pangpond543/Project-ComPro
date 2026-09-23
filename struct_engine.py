import struct
import os

# ==============================================================================
# Module 1: struct_engine.py
# Responsibility: คนที่ 1 - Binary File I/O & Struct Engine
# Description: กำหนด Struct Format, Pack/Unpack และ Low-Level Binary File I/O
# ==============================================================================

# --- Format Strings (Little-Endian '<') ---
# 1. Room Record: room_id(I), room_number(15s), room_type(50s), category(20s), price_per_night(f), status(I), is_booked(I)
ROOM_FORMAT = "<I15s50s20sfII"
ROOM_SIZE = struct.calcsize(ROOM_FORMAT)  # 101 Bytes

# 2. Customer Record: customer_id(I), customer_code(15s), name(50s), phone(20s), member_level(20s), status(I)
CUSTOMER_FORMAT = "<I15s50s20s20sI"
CUSTOMER_SIZE = struct.calcsize(CUSTOMER_FORMAT)  # 113 Bytes

# 3. Booking Record: booking_id(I), customer_id(I), room_id(I), check_in_date(20s), check_out_date(20s), total_price(f), status(I)
BOOKING_FORMAT = "<III20s20sfI"
BOOKING_SIZE = struct.calcsize(BOOKING_FORMAT)  # 60 Bytes


# --- Pack / Unpack Functions ---

def pack_room(room_id: int, room_number: str, room_type: str, category: str, price: float, status: int = 1, is_booked: int = 0) -> bytes:
    """แปลงข้อมูล Room เป็น Binary Bytes (Fixed-length)"""
    num_b = room_number.encode('utf-8').ljust(15, b'\x00')[:15]
    type_b = room_type.encode('utf-8').ljust(50, b'\x00')[:50]
    cat_b = category.encode('utf-8').ljust(20, b'\x00')[:20]
    return struct.pack(ROOM_FORMAT, room_id, num_b, type_b, cat_b, price, status, is_booked)

def unpack_room(data_bytes: bytes) -> dict:
    """แปลง Binary Bytes กลับเป็น Dictionary ข้อมูล Room"""
    raw = struct.unpack(ROOM_FORMAT, data_bytes)
    return {
        "room_id": raw[0],
        "room_number": raw[1].decode('utf-8').rstrip('\x00'),
        "room_type": raw[2].decode('utf-8').rstrip('\x00'),
        "category": raw[3].decode('utf-8').rstrip('\x00'),
        "price_per_night": raw[4],
        "status": raw[5],     # 1 = Active, 0 = Deleted
        "is_booked": raw[6]    # 0 = Available, 1 = Booked
    }


def pack_customer(customer_id: int, customer_code: str, name: str, phone: str, member_level: str, status: int = 1) -> bytes:
    """แปลงข้อมูล Customer เป็น Binary Bytes (Fixed-length)"""
    code_b = customer_code.encode('utf-8').ljust(15, b'\x00')[:15]
    name_b = name.encode('utf-8').ljust(50, b'\x00')[:50]
    phone_b = phone.encode('utf-8').ljust(20, b'\x00')[:20]
    level_b = member_level.encode('utf-8').ljust(20, b'\x00')[:20]
    return struct.pack(CUSTOMER_FORMAT, customer_id, code_b, name_b, phone_b, level_b, status)

def unpack_customer(data_bytes: bytes) -> dict:
    """แปลง Binary Bytes กลับเป็น Dictionary ข้อมูล Customer"""
    raw = struct.unpack(CUSTOMER_FORMAT, data_bytes)
    return {
        "customer_id": raw[0],
        "customer_code": raw[1].decode('utf-8').rstrip('\x00'),
        "name": raw[2].decode('utf-8').rstrip('\x00'),
        "phone": raw[3].decode('utf-8').rstrip('\x00'),
        "member_level": raw[4].decode('utf-8').rstrip('\x00'),
        "status": raw[5]      # 1 = Active, 0 = Deleted
    }


def pack_booking(booking_id: int, customer_id: int, room_id: int, check_in: str, check_out: str, total_price: float, status: int = 1) -> bytes:
    """แปลงข้อมูล Booking เป็น Binary Bytes (Fixed-length)"""
    in_b = check_in.encode('utf-8').ljust(20, b'\x00')[:20]
    out_b = check_out.encode('utf-8').ljust(20, b'\x00')[:20]
    return struct.pack(BOOKING_FORMAT, booking_id, customer_id, room_id, in_b, out_b, total_price, status)

def unpack_booking(data_bytes: bytes) -> dict:
    """แปลง Binary Bytes กลับเป็น Dictionary ข้อมูล Booking"""
    raw = struct.unpack(BOOKING_FORMAT, data_bytes)
    return {
        "booking_id": raw[0],
        "customer_id": raw[1],
        "room_id": raw[2],
        "check_in_date": raw[3].decode('utf-8').rstrip('\x00'),
        "check_out_date": raw[4].decode('utf-8').rstrip('\x00'),
        "total_price": raw[5],
        "status": raw[6]      # 1 = Active/Confirmed, 0 = Cancelled
    }


# --- Low-Level File I/O Engine ---

def append_record(filename: str, record_bytes: bytes) -> None:
    """เขียนต่อท้ายไฟล์ไบนารี (Append Mode)"""
    with open(filename, "ab") as f:
        f.write(record_bytes)
        f.flush()
        os.fsync(f.fileno())

def read_all_records(filename: str, record_size: int, unpack_func) -> list:
    """อ่านข้อมูลทั้งหมดจากไฟล์ไบนารี คืนค่าเป็น List ของ Dictionary"""
    records = []
    if not os.path.exists(filename):
        return records
    
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(record_size)
            if len(chunk) < record_size:
                break
            records.append(unpack_func(chunk))
    return records

def update_record_at_index(filename: str, record_index: int, record_size: int, new_bytes: bytes) -> bool:
    """แก้ไขระเบียนในตำแหน่ง index ที่กำหนดด้วย file.seek()"""
    if not os.path.exists(filename):
        return False
    
    offset = record_index * record_size
    with open(filename, "r+b") as f:
        f.seek(offset)
        f.write(new_bytes)
        f.flush()
        os.fsync(f.fileno())
    return True
