# ==============================================================================
# Module 4: main.py
# Responsibility: คนที่ 4 / Main Application Integration
# Description: ไฟล์หลักสำหรับรันโปรแกรม เชื่อมโยงโมดูลและควบคุม CLI Menu
# ==============================================================================

import os
import sys
from struct_engine import (
    pack_room, pack_customer, pack_booking,
    unpack_room, unpack_customer, unpack_booking,
    read_all_records, append_record, update_record_at_index,
    ROOM_SIZE, CUSTOMER_SIZE, BOOKING_SIZE
)
from cli_menu import (
    get_valid_int, get_valid_float, get_valid_string, display_header
)
from report_gen import (
    create_booking_transaction, generate_text_report,
    generate_monthly_revenue_report, generate_customer_monthly_report,
    generate_next_week_upcoming_report
)

ROOMS_FILE = "rooms.dat"
CUSTOMERS_FILE = "customers.dat"
BOOKINGS_FILE = "bookings.dat"

def init_sample_data():
    """สร้างข้อมูลตัวอย่างตั้งต้น 20 ห้อง, 5 ลูกค้า และรายการจองหากยังไม่มีไฟล์ไบนารี"""
    if not os.path.exists(ROOMS_FILE):
        rooms_data = [
            # Building A - Tower 1
            (1001, "A101", "Superior Single", "Standard", 1200.0, 1, 1),
            (1002, "A102", "Superior Double", "Standard", 1500.0, 1, 0),
            (1003, "A103", "Superior Twin", "Standard", 1500.0, 1, 1),
            (1004, "A104", "Deluxe Ocean View", "VIP", 2500.0, 1, 0),
            (1005, "A105", "Deluxe Corner", "VIP", 2800.0, 1, 1),
            (1006, "A201", "Superior Single", "Standard", 1200.0, 1, 0),
            (1007, "A202", "Superior Double", "Standard", 1500.0, 1, 1),
            (1008, "A203", "Executive Suite", "VIP", 3800.0, 1, 0),
            (1009, "A204", "Executive Suite", "VIP", 3800.0, 1, 1),
            (1010, "A205", "Presidential Suite", "Luxury", 8500.0, 1, 0),

            # Building B - Ocean Wing
            (2001, "B101", "Standard King", "Standard", 900.0, 1, 0),
            (2002, "B102", "Standard Twin", "Standard", 900.0, 1, 0),
            (2003, "B103", "Family Suite", "Family", 3200.0, 1, 1),
            (2004, "B104", "Family Suite Pool", "Family", 4200.0, 1, 0),
            (2005, "B105", "Standard King", "Standard", 900.0, 0, 0), # Deleted/Maintenance

            # Building V - Villa Zone
            (3001, "V001", "Beachfront Villa", "Luxury", 5500.0, 1, 1),
            (3002, "V002", "Beachfront Villa", "Luxury", 5500.0, 1, 0),
            (3003, "V003", "Pool Villa Deluxe", "Luxury", 6500.0, 1, 1),
            (3004, "V004", "Garden Villa", "VIP", 4000.0, 1, 0),
            (3005, "V005", "Garden Villa", "VIP", 4000.0, 0, 0)  # Deleted/Maintenance
        ]
        for r in rooms_data:
            append_record(ROOMS_FILE, pack_room(*r))

    if not os.path.exists(CUSTOMERS_FILE):
        customers_data = [
            (5001, "CUS-001", "Somchai Jaidee", "0812345678", "Platinum", 1),
            (5002, "CUS-002", "Somsri Meesuk", "0898765432", "Gold", 1),
            (5003, "CUS-003", "Anan Sukjai", "0861112233", "Standard", 1),
            (5004, "CUS-004", "Wichai Rakthai", "0829998877", "Gold", 1),
            (5005, "CUS-005", "Kanya Ploysai", "0835554433", "Platinum", 1)
        ]
        for cs in customers_data:
            append_record(CUSTOMERS_FILE, pack_customer(*cs))

    if not os.path.exists(BOOKINGS_FILE):
        bookings_data = [
            (9001, 5001, 1001, "2026-09-02", "2026-09-04", 2400.0, 1),
            (9002, 5001, 1004, "2026-09-12", "2026-09-15", 7500.0, 1),
            (9003, 5001, 3001, "2026-09-25", "2026-09-28", 16500.0, 1),
            (9004, 5002, 2003, "2026-09-10", "2026-09-12", 6400.0, 1),
            (9005, 5002, 1005, "2026-09-28", "2026-10-01", 8400.0, 1),
            (9006, 5003, 1003, "2026-09-29", "2026-10-02", 4500.0, 1),
            (9007, 5004, 1009, "2026-09-30", "2026-10-03", 11400.0, 1),
            (9008, 5005, 3003, "2026-10-01", "2026-10-05", 26000.0, 1)
        ]
        for b in bookings_data:
            append_record(BOOKINGS_FILE, pack_booking(*b))


def menu_add_room():
    display_header("1. เพิ่มข้อมูลห้องพักใหม่ (Add Room)")
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
    category = get_valid_string("ป้อนหมวดหมู่ (เช่น VIP, Standard, Luxury): ", max_len=20)
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
                    r["price_per_night"], status=0, is_booked=r["is_booked"]
                )
                update_record_at_index(ROOMS_FILE, idx, ROOM_SIZE, updated_bytes)
                print("✅ ลบข้อมูลห้องพักเรียบร้อย (Soft Delete)")
            return

    print("❌ ไม่พบรหัสห้องพักนี้")


def menu_view_rooms():
    display_header("4. ดูข้อมูลห้องพักทั้งหมด (View Rooms)")
    rooms = read_all_records(ROOMS_FILE, ROOM_SIZE, unpack_room)
    active_rooms = [r for r in rooms if r["status"] == 1]

    if not active_rooms:
        print("❌ ไม่มีห้องพักที่ใช้งานอยู่")
        return

    print(f"{'Room ID':<8} | {'Room No.':<10} | {'Room Type':<22} | {'Category':<12} | {'Price':<10} | {'Status':<10}")
    print("-" * 85)
    for r in active_rooms:
        b_str = "Booked" if r["is_booked"] == 1 else "Available"
        print(f"{r['room_id']:<8} | {r['room_number']:<10} | {r['room_type']:<22} | {r['category']:<12} | {r['price_per_night']:<10.2f} | {b_str:<10}")
    print("-" * 85)
    print(f"รวมห้องพักในระบบทั้งหมด {len(active_rooms)} ห้อง")


def menu_reports():
    while True:
        display_header("6. ระบบออกรายงานสรุปผล (Reports Menu)")
        print("1. รายงานสรุปภาพรวมระบบห้องพัก (Standard Inventory Report)")
        print("2. รายงานสรุปรายได้และการจองประจำเดือน (Monthly Revenue Report)")
        print("3. รายงานประวัติการจองและค่าใช้จ่ายของลูกค้าเฉพาะบุคคล (Individual Customer Monthly Report)")
        print("4. รายงานการจองล่วงหน้าสำหรับเตรียมห้องพักในสัปดาห์หน้า (Next Week Upcoming Report)")
        print("0. ย้อนกลับเมนูหลัก")

        sub_choice = input("\nเลือกรายงาน (0-4): ").strip()
        if sub_choice == '1':
            generate_text_report("report.txt")
        elif sub_choice == '2':
            year = get_valid_int("ป้อนปี ค.ศ. (เช่น 2026): ", min_val=2000, max_val=2100)
            month = get_valid_int("ป้อนเดือน (1-12): ", min_val=1, max_val=12)
            generate_monthly_revenue_report(year, month, "report_monthly_revenue.txt")
        elif sub_choice == '3':
            c_id = get_valid_int("ป้อนรหัสลูกค้า (Customer ID): ", min_val=1)
            year = get_valid_int("ป้อนปี ค.ศ. (เช่น 2026, หรือป้อน 0 หากต้องการดูทั้งหมด): ")
            if year > 0:
                month = get_valid_int("ป้อนเดือน (1-12): ", min_val=1, max_val=12)
            else:
                year, month = None, None
            generate_customer_monthly_report(c_id, year, month, "report_customer_monthly.txt")
        elif sub_choice == '4':
            ref_date = input("ป้อนวันที่อ้างอิงเริ่มต้น (YYYY-MM-DD) หรือกด Enter เพื่อใช้วันนี้: ").strip()
            if not ref_date:
                ref_date = None
            generate_next_week_upcoming_report(ref_date, "report_next_week_upcoming.txt")
        elif sub_choice == '0':
            break
        else:
            print("⚠️ เลือกเมนูไม่ถูกต้อง กรุณาลองใหม่")


def main():
    init_sample_data()
    
    while True:
        display_header("ระบบจัดการจองห้องพักโรงแรม (Hotel Booking Management)")
        print("1. Add (เพิ่มข้อมูลห้องพัก)")
        print("2. Update (แก้ไขข้อมูลห้องพัก)")
        print("3. Delete (ลบข้อมูลห้องพัก - Soft Delete)")
        print("4. View (ดูข้อมูลห้องพัก)")
        print("5. Booking (ทำรายการจองห้องพัก)")
        print("6. Reports Menu (ระบบสร้างรายงาน 4 รูปแบบ)")
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
            total = get_valid_float("ป้อนราคารวมสุทธิ (บาท): ", min_val=0.0)
            create_booking_transaction(b_id, c_id, r_id, in_date, out_date, total)
        elif choice == '6':
            menu_reports()
        elif choice == '0':
            print("\n🔒 ปิดโปรแกรมและ flush/sync ข้อมูลไบนารีลงดิสก์เรียบร้อยแล้ว!")
            sys.exit(0)
        else:
            print("⚠️ เลือกเมนูไม่ถูกต้อง กรุณาลองใหม่")

if __name__ == "__main__":
    main()
