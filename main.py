# ==============================================================================
# Module 4: main.py
# Responsibility: คนที่ 4 / Main Application Integration
# Description: ไฟล์หลักสำหรับรันโปรแกรม เชื่อมโยงโมดูลและควบคุม CLI Menu
# ==============================================================================

import os
import sys
from struct_engine import (
    pack_room, pack_customer, unpack_room, unpack_customer, unpack_booking,
    read_all_records, append_record, update_record_at_index,
    ROOM_SIZE, CUSTOMER_SIZE, BOOKING_SIZE
)
from cli_menu import (
    get_valid_int, get_valid_float, get_valid_string, display_header
)
from report_gen import (
    create_booking_transaction, generate_text_report
)

ROOMS_FILE = "rooms.dat"
CUSTOMERS_FILE = "customers.dat"
BOOKINGS_FILE = "bookings.dat"

def init_sample_data():
    """สร้างข้อมูลตัวอย่างตั้งต้นหากยังไม่มีไฟล์ไบนารี"""
    if not os.path.exists(ROOMS_FILE):
        samples = [
            (1001, "A101", "Deluxe Ocean View", "VIP", 2500.0, 1, 0),
            (1002, "A102", "Superior Room", "Standard", 1500.0, 1, 0),
            (1003, "B201", "Suite Pool Villa", "VIP", 4500.0, 1, 0),
            (1004, "B202", "Family Suite", "Family", 3200.0, 1, 0),
            (1005, "C301", "Standard Room", "Standard", 900.0, 0, 0) # Deleted sample
        ]
        for s in samples:
            append_record(ROOMS_FILE, pack_room(*s))

    if not os.path.exists(CUSTOMERS_FILE):
        c_samples = [
            (5001, "CUS-001", "Somchai Jaidee", "0812345678", "Gold", 1),
            (5002, "CUS-002", "Somsri Meesuk", "0898765432", "Platinum", 1)
        ]
        for cs in c_samples:
            append_record(CUSTOMERS_FILE, pack_customer(*cs))


def menu_add_room():
    display_header("1.1 เพิ่มข้อมูลห้องพักใหม่ (Add Room)")
    rooms = read_all_records(ROOMS_FILE, ROOM_SIZE, unpack_room)
    existing_ids = [r["room_id"] for r in rooms]

    while True:
        room_id = get_valid_int("ป้อนรหัสห้องพัก (Room ID): ", min_val=1)
        if room_id in existing_ids:
            print("⚠️ รหัสห้องพักนี้มีอยู่ในระบบแล้ว! กรุณาใช้รหัสอื่น")
        else:
            break

    room_num = get_valid_string("ป้อนหมายเลขห้อง (เช่น A101): ", max_len=15)
    room_type = get_valid_string("ป้อนประเภทห้อง (เช่น Deluxe Ocean View): ", max_len=50)
    category = get_valid_string("ป้อนหมวดหมู่ (เช่น VIP, Standard): ", max_len=20)
    price = get_valid_float("ป้อนราคาต่อคืน (บาท): ", min_val=0.0)

    record_bytes = pack_room(room_id, room_num, room_type, category, price, status=1, is_booked=0)
    append_record(ROOMS_FILE, record_bytes)
    print("✅ เพิ่มข้อมูลห้องพักสำเร็จ!")


def menu_update_room():
    display_header("2. แก้ไขข้อมูลห้องพัก (Update Room)")
    rooms = read_all_records(ROOMS_FILE, ROOM_SIZE, unpack_room)
    if not rooms:
        print("❌ ไม่มีข้อมูลห้องพักในระบบ")
        return

    room_id = get_valid_int("ป้อนรหัสห้องพักที่ต้องการแก้ไข: ")
    target_idx = -1
    target_room = None

    for idx, r in enumerate(rooms):
        if r["room_id"] == room_id:
            target_idx = idx
            target_room = r
            break

    if target_idx == -1:
        print("❌ ไม่พบรหัสห้องพักนี้")
        return

    print(f"ข้อมูลปัจจุบัน: {target_room['room_number']} | {target_room['room_type']} | ราคา {target_room['price_per_night']} บาท")
    new_type = get_valid_string("ป้อนประเภทห้องใหม่: ", max_len=50)
    new_cat = get_valid_string("ป้อนหมวดหมู่ใหม่: ", max_len=20)
    new_price = get_valid_float("ป้อนราคาใหม่ (บาท): ", min_val=0.0)

    updated_bytes = pack_room(
        target_room["room_id"], target_room["room_number"], new_type, new_cat, new_price,
        target_room["status"], target_room["is_booked"]
    )
    update_record_at_index(ROOMS_FILE, target_idx, ROOM_SIZE, updated_bytes)
    print("✅ แก้ไขข้อมูลห้องพักเรียบร้อย!")


def menu_delete_room():
    display_header("3. ลบข้อมูลห้องพัก (Soft Delete Room)")
    rooms = read_all_records(ROOMS_FILE, ROOM_SIZE, unpack_room)
    room_id = get_valid_int("ป้อนรหัสห้องพักที่ต้องการลบ: ")

    for idx, r in enumerate(rooms):
        if r["room_id"] == room_id:
            if r["status"] == 0:
                print("⚠️ ห้องพักนี้ถูกลบไปแล้ว")
                return
            
            confirm = input(f"ยืนยันลบห้อง {r['room_number']}? (y/n): ").strip().lower()
            if confirm == 'y':
                updated_bytes = pack_room(
                    r["room_id"], r["room_number"], r["room_type"], r["category"],
                    r["price_per_night"], status=0, is_booked=r["is_booked"] # Soft delete (status = 0)
                )
                update_record_at_index(ROOMS_FILE, idx, ROOM_SIZE, updated_bytes)
                print("✅ ลบข้อมูลห้องพักเรียบร้อย (Soft Delete)")
            return

    print("❌ ไม่พบรหัสห้องพักนี้")


def menu_view_rooms():
    display_header("4. ดูข้อมูลห้องพัก (View Rooms)")
    rooms = read_all_records(ROOMS_FILE, ROOM_SIZE, unpack_room)
    active_rooms = [r for r in rooms if r["status"] == 1]

    if not active_rooms:
        print("❌ ไม่มีห้องพักที่ใช้งานอยู่")
        return

    print(f"{'Room ID':<8} | {'Room No.':<10} | {'Room Type':<22} | {'Category':<12} | {'Price':<10} | {'Status':<8}")
    print("-" * 80)
    for r in active_rooms:
        b_str = "Booked" if r["is_booked"] == 1 else "Available"
        print(f"{r['room_id']:<8} | {r['room_number']:<10} | {r['room_type']:<22} | {r['category']:<12} | {r['price_per_night']:<10.2f} | {b_str:<8}")


def main():
    init_sample_data()
    
    while True:
        display_header("ระบบจัดการจองห้องพักโรงแรม (Hotel Booking Management)")
        print("1. Add (เพิ่มข้อมูลห้องพัก)")
        print("2. Update (แก้ไขข้อมูลห้องพัก)")
        print("3. Delete (ลบข้อมูลห้องพัก - Soft Delete)")
        print("4. View (ดูข้อมูลห้องพัก)")
        print("5. Booking (ทำรายการจองห้องพัก)")
        print("6. Generate Report (.txt)")
        print("0. Exit (ออกจากโปรแกรมอย่างปลอดภัย)")
        
        choice = input("\nเลือกเมนู (0-6): ").strip()
        
        if choice == '1':
            menu_add_room()
        elif choice == '2':
            menu_update_room()
        elif choice == '3':
            menu_delete_room()
        elif choice == '4':
            menu_view_rooms()
        elif choice == '5':
            display_header("5. ทำรายการจองห้องพัก (Booking)")
            b_id = get_valid_int("ป้อนรหัสการจอง (Booking ID): ")
            c_id = get_valid_int("ป้อนรหัสลูกค้า (Customer ID): ")
            r_id = get_valid_int("ป้อนรหัสห้องพัก (Room ID): ")
            in_date = get_valid_string("ป้อนวัน Check-in (YYYY-MM-DD): ", max_len=20)
            out_date = get_valid_string("ป้อนวัน Check-out (YYYY-MM-DD): ", max_len=20)
            total = get_valid_float("ป้อน ราคารวม (บาท): ", min_val=0.0)
            create_booking_transaction(b_id, c_id, r_id, in_date, out_date, total)
        elif choice == '6':
            generate_text_report("report.txt")
        elif choice == '0':
            print("\n🔒 ปิดโปรแกรมและ flush/sync ข้อมูลไบนารีลงดิสก์เรียบร้อยแล้ว!")
            sys.exit(0)
        else:
            print("⚠️ เลือกเมนูไม่ถูกต้อง กรุณาลองใหม่")

if __name__ == "__main__":
    main()
