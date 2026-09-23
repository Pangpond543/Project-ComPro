# ==============================================================================
# Module 3: report_gen.py
# Responsibility: คนที่ 3 - Business Logic & Report Generator
# Description: ลอจิกการทำรายการจอง สถิติสรุป และการสร้างไฟล์รายงาน report.txt
# ==============================================================================

import os
from datetime import datetime
from struct_engine import (
    read_all_records, append_record, update_record_at_index,
    pack_booking, pack_room,
    unpack_room, unpack_customer, unpack_booking,
    ROOM_SIZE, CUSTOMER_SIZE, BOOKING_SIZE
)

ROOMS_FILE = "rooms.dat"
CUSTOMERS_FILE = "customers.dat"
BOOKINGS_FILE = "bookings.dat"

def create_booking_transaction(booking_id: int, customer_id: int, room_id: int, check_in: str, check_out: str, total_price: float) -> bool:
    """ลอจิกการทำรายการจอง: บันทึก Booking + ปรับสถานะห้องพักเป็น Booked (is_booked = 1)"""
    rooms = read_all_records(ROOMS_FILE, ROOM_SIZE, unpack_room)
    target_idx = -1
    target_room = None
    
    for idx, r in enumerate(rooms):
        if r["room_id"] == room_id and r["status"] == 1:
            target_idx = idx
            target_room = r
            break
            
    if target_idx == -1:
        print("❌ ไม่พบห้องพัก หรือห้องพักไม่ได้อยู่ในสถานะ Active")
        return False
        
    if target_room["is_booked"] == 1:
        print("❌ ห้องพักนี้ถูกจองอยู่แล้ว!")
        return False

    # 1. บันทึก Booking Record
    b_bytes = pack_booking(booking_id, customer_id, room_id, check_in, check_out, total_price, status=1)
    append_record(BOOKINGS_FILE, b_bytes)

    # 2. อัปเดตสถานะห้องพักใน rooms.dat ให้เป็น is_booked = 1
    updated_room_bytes = pack_room(
        target_room["room_id"], target_room["room_number"], target_room["room_type"],
        target_room["category"], target_room["price_per_night"], target_room["status"], is_booked=1
    )
    update_record_at_index(ROOMS_FILE, target_idx, ROOM_SIZE, updated_room_bytes)
    print("✅ ทำรายการจองสำเร็จและอัปเดตสถานะห้องเรียบร้อย!")
    return True


def generate_text_report(output_filename: str = "report.txt") -> None:
    """สร้างไฟล์รายงานสรุปผลการทำงานเป็น Text File (.txt) ตามสเปกข้อกำหนดโครงการ"""
    rooms = read_all_records(ROOMS_FILE, ROOM_SIZE, unpack_room)
    customers = read_all_records(CUSTOMERS_FILE, CUSTOMER_SIZE, unpack_customer)
    bookings = read_all_records(BOOKINGS_FILE, BOOKING_SIZE, unpack_booking)

    active_rooms = [r for r in rooms if r["status"] == 1]
    deleted_rooms = [r for r in rooms if r["status"] == 0]
    booked_rooms = [r for r in active_rooms if r["is_booked"] == 1]
    available_rooms = [r for r in active_rooms if r["is_booked"] == 0]

    prices = [r["price_per_night"] for r in active_rooms]
    min_price = min(prices) if prices else 0.0
    max_price = max(prices) if prices else 0.0
    avg_price = sum(prices) / len(prices) if prices else 0.0

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("==========================================================================================")
    lines.append("                  Hotel Room Booking System - Summary Report                              ")
    lines.append("==========================================================================================")
    lines.append(f"Generated At : {now_str}")
    lines.append("App Version  : 1.0 (Python Standard Library - Fixed-Length Binary Struct)")
    lines.append("Endianness   : Little-Endian (<)")
    lines.append("Encoding     : UTF-8")
    lines.append("------------------------------------------------------------------------------------------\n")

    lines.append("[1] ROOMS INVENTORY TABLE")
    lines.append("+---------+---------------+------------------------+-------------------+--------------+--------+--------+")
    lines.append("| Room ID | Room Number   | Room Type              | Category          | Price (THB)  | Status | Booked |")
    lines.append("+---------+---------------+------------------------+-------------------+--------------+--------+--------+")

    for r in rooms:
        st_str = "Active" if r["status"] == 1 else "Deleted"
        bk_str = "Yes" if r["is_booked"] == 1 else "No"
        lines.append(f"| {r['room_id']:<7} | {r['room_number']:<13} | {r['room_type']:<22} | {r['category']:<17} | {r['price_per_night']:<12.2f} | {st_str:<6} | {bk_str:<6} |")
    lines.append("+---------+---------------+------------------------+-------------------+--------------+--------+--------+\n")

    lines.append("[2] SUMMARY STATISTICS (Active Records)")
    lines.append(f"- Total Rooms Registered : {len(rooms)}")
    lines.append(f"- Active Rooms           : {len(active_rooms)}")
    lines.append(f"- Deleted Rooms          : {len(deleted_rooms)}")
    lines.append(f"- Currently Booked       : {len(booked_rooms)}")
    lines.append(f"- Available Now          : {len(available_rooms)}")
    lines.append(f"- Total Customers        : {len(customers)}")
    lines.append(f"- Total Booking Records  : {len(bookings)}\n")

    lines.append("[3] PRICE STATISTICS (Active Rooms)")
    lines.append(f"- Min Price : {min_price:.2f} THB")
    lines.append(f"- Max Price : {max_price:.2f} THB")
    lines.append(f"- Avg Price : {avg_price:.2f} THB\n")

    lines.append("==========================================================================================")
    lines.append("                                END OF REPORT                                             ")
    lines.append("==========================================================================================")

    content = "\n".join(lines)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())

    print(f"✅ สร้างไฟล์รายงาน {output_filename} เรียบร้อยแล้ว!")
