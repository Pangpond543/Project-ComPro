# ==============================================================================
# Module 3: report_gen.py
# Responsibility: คนที่ 3 - Business Logic & Report Generator
# Description: ลอจิกการทำรายการจอง สถิติสรุป และการสร้างไฟล์รายงานทั้ง 4 รูปแบบ
# ==============================================================================

import os
from datetime import datetime, timedelta
from struct_engine import (
    read_all_records, append_record, update_record_at_index,
    pack_booking, pack_room,
    unpack_room, unpack_customer, unpack_booking,
    ROOM_SIZE, CUSTOMER_SIZE, BOOKING_SIZE
)

ROOMS_FILE = "rooms.dat"
CUSTOMERS_FILE = "customers.dat"
BOOKINGS_FILE = "bookings.dat"

def get_rooms_dict():
    rooms = read_all_records(ROOMS_FILE, ROOM_SIZE, unpack_room)
    return {r["room_id"]: r for r in rooms}

def get_customers_dict():
    customers = read_all_records(CUSTOMERS_FILE, CUSTOMER_SIZE, unpack_customer)
    return {c["customer_id"]: c for c in customers}

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


# ------------------------------------------------------------------------------
# 1. REPORT 0: Standard Inventory Summary Report
# ------------------------------------------------------------------------------
def generate_text_report(output_filename: str = "report.txt") -> None:
    """สร้างไฟล์รายงานสรุปภาพรวมห้องพักและสถิติ (report_hotel.png style)"""
    rooms = read_all_records(ROOMS_FILE, ROOM_SIZE, unpack_room)
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
    lines.append("Hotel Reservation System - Summary Report (Sample)")
    lines.append(f"Generated At : {now_str}")
    lines.append("App Version  : 1.0")
    lines.append("====================================================================================================")
    lines.append("| RoomID | RoomNum | Room Type            | Category | Price (THB) | Status | Booked Status |")
    lines.append("====================================================================================================")

    for r in rooms:
        st_str = "Active" if r["status"] == 1 else "Deleted"
        bk_str = "Booked" if r["is_booked"] == 1 else "Available"
        lines.append(f"| {r['room_id']:<6} | {r['room_number']:<7} | {r['room_type']:<20} | {r['category']:<8} | {r['price_per_night']:<11,.2f} | {st_str:<6} | {bk_str:<13} |")

    lines.append("====================================================================================================\n")
    lines.append("Summary (นับเฉพาะสถานะ Active)")
    lines.append(f"- Total Rooms (records) : {len(rooms)}")
    lines.append(f"- Active Rooms          : {len(active_rooms)}")
    lines.append(f"- Maintenance/Deleted   : {len(deleted_rooms)}")
    lines.append(f"- Currently Booked      : {len(booked_rooms)}")
    lines.append(f"- Available Now         : {len(available_rooms)}\n")

    lines.append("Room Price Statistics (THB, Active only)")
    lines.append(f"- Min : {min_price:,.2f}")
    lines.append(f"- Max : {max_price:,.2f}")

    # Group by category
    cats = {}
    for r in active_rooms:
        c = r["category"]
        cats[c] = cats.get(c, 0) + 1

    lines.append("Rooms by Category (Active only)")
    for cat_name, count in cats.items():
        lines.append(f"- {cat_name:<8} : {count}")

    content = "\n".join(lines)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())

    print(f"✅ สร้างไฟล์รายงาน {output_filename} เรียบร้อยแล้ว!")


# ------------------------------------------------------------------------------
# 2. REPORT 1: Monthly Overall Revenue & Booking Report
# รายงานประจำเดือน: รายการจองทั้งหมด + รายได้รวมของโรงแรมประจำเดือน
# ------------------------------------------------------------------------------
def generate_monthly_revenue_report(year: int, month: int, output_filename: str = "report_monthly_revenue.txt") -> str:
    rooms_dict = get_rooms_dict()
    cust_dict = get_customers_dict()
    bookings = read_all_records(BOOKINGS_FILE, BOOKING_SIZE, unpack_booking)

    month_bookings = []
    for b in bookings:
        if b["status"] == 1:
            try:
                dt_in = datetime.strptime(b["check_in_date"], "%Y-%m-%d")
                if dt_in.year == year and dt_in.month == month:
                    month_bookings.append(b)
            except ValueError:
                pass

    total_revenue = sum(b["total_price"] for b in month_bookings)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    month_name_str = datetime(year, month, 1).strftime("%B %Y")

    lines = []
    lines.append("====================================================================================================")
    lines.append(f"                 HOTEL MONTHLY REVENUE & BOOKING REPORT ({month_name_str.upper()})")
    lines.append("====================================================================================================")
    lines.append(f"Generated At   : {now_str}")
    lines.append(f"Target Period  : Month {month:02d} / Year {year}")
    lines.append("App Version    : 1.0 (Fixed-Length Binary Struct)")
    lines.append("====================================================================================================\n")

    lines.append("BOOKING DETAILS IN THIS MONTH:")
    lines.append("+------------+------------+----------------------+----------+-------------------+------------+------------+----------------+")
    lines.append("| Booking ID | Cust ID    | Customer Name        | Room No. | Room Type         | Check-In   | Check-Out  | Total Price    |")
    lines.append("+------------+------------+----------------------+----------+-------------------+------------+------------+----------------+")

    if not month_bookings:
        lines.append("|                                NO BOOKINGS FOUND IN THIS MONTH                                    |")
    else:
        for b in month_bookings:
            c = cust_dict.get(b["customer_id"], {"name": "Unknown", "phone": "N/A"})
            r = rooms_dict.get(b["room_id"], {"room_number": "N/A", "room_type": "N/A"})
            c_name = c["name"][:20]
            r_num = r["room_number"][:8]
            r_type = r["room_type"][:17]
            lines.append(f"| {b['booking_id']:<10} | {b['customer_id']:<10} | {c_name:<20} | {r_num:<8} | {r_type:<17} | {b['check_in_date']} | {b['check_out_date']} | {b['total_price']:>12,.2f} THB |")

    lines.append("+------------+------------+----------------------+----------+-------------------+------------+------------+----------------+\n")

    lines.append("MONTHLY SUMMARY STATISTICS:")
    lines.append(f"- Total Bookings Count : {len(month_bookings)} transactions")
    lines.append(f"- Unique Customers     : {len(set(b['customer_id'] for b in month_bookings))} persons")
    lines.append(f"- Total Revenue Earned : {total_revenue:,.2f} THB")
    lines.append("====================================================================================================")
    lines.append("                                        END OF REPORT")
    lines.append("====================================================================================================")

    content = "\n".join(lines)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())

    print(f"✅ สร้างไฟล์รายงาน {output_filename} เรียบร้อยแล้ว!")
    return content


# ------------------------------------------------------------------------------
# 3. REPORT 2: Individual Customer Monthly History & Total Expense Report
# รายงานประวัติของลูกค้าคนๆ หนึ่ง: จองห้องไหนบ้าง ช่วงเวลาไหน ยอดรวมค่าใช้จ่ายทั้งหมด
# ------------------------------------------------------------------------------
def generate_customer_monthly_report(customer_id: int, year: int = None, month: int = None, output_filename: str = "report_customer_monthly.txt") -> str:
    rooms_dict = get_rooms_dict()
    cust_dict = get_customers_dict()
    bookings = read_all_records(BOOKINGS_FILE, BOOKING_SIZE, unpack_booking)

    customer = cust_dict.get(customer_id)
    if not customer:
        print(f"❌ ไม่พบรหัสลูกค้า {customer_id}")
        return ""

    cust_bookings = []
    for b in bookings:
        if b["customer_id"] == customer_id and b["status"] == 1:
            if year and month:
                try:
                    dt_in = datetime.strptime(b["check_in_date"], "%Y-%m-%d")
                    if dt_in.year == year and dt_in.month == month:
                        cust_bookings.append(b)
                except ValueError:
                    pass
            else:
                cust_bookings.append(b)

    total_spent = sum(b["total_price"] for b in cust_bookings)
    total_nights = 0
    for b in cust_bookings:
        try:
            d1 = datetime.strptime(b["check_in_date"], "%Y-%m-%d")
            d2 = datetime.strptime(b["check_out_date"], "%Y-%m-%d")
            total_nights += max(1, (d2 - d1).days)
        except ValueError:
            pass

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    period_str = f"Month {month:02d}/{year}" if (year and month) else "All Time History"

    lines = []
    lines.append("====================================================================================================")
    lines.append("                      INDIVIDUAL CUSTOMER BOOKING & EXPENSE REPORT")
    lines.append("====================================================================================================")
    lines.append(f"Generated At   : {now_str}")
    lines.append(f"Report Period  : {period_str}")
    lines.append("====================================================================================================")
    lines.append("CUSTOMER PROFILE:")
    lines.append(f"- Customer ID   : {customer['customer_id']}")
    lines.append(f"- Customer Code : {customer['customer_code']}")
    lines.append(f"- Full Name     : {customer['name']}")
    lines.append(f"- Phone Number  : {customer['phone']}")
    lines.append(f"- Member Level  : {customer['member_level']}")
    lines.append("====================================================================================================\n")

    lines.append("RESERVATION HISTORY:")
    lines.append("+------------+----------+----------------------+-------------------+------------+------------+----------------+")
    lines.append("| Booking ID | Room No. | Room Type            | Category          | Check-In   | Check-Out  | Amount Paid    |")
    lines.append("+------------+----------+----------------------+-------------------+------------+------------+----------------+")

    if not cust_bookings:
        lines.append("|                           NO RESERVATION RECORD FOUND FOR THIS PERIOD                             |")
    else:
        for b in cust_bookings:
            r = rooms_dict.get(b["room_id"], {"room_number": "N/A", "room_type": "N/A", "category": "N/A"})
            r_num = r["room_number"][:8]
            r_type = r["room_type"][:20]
            r_cat = r["category"][:17]
            lines.append(f"| {b['booking_id']:<10} | {r_num:<8} | {r_type:<20} | {r_cat:<17} | {b['check_in_date']} | {b['check_out_date']} | {b['total_price']:>12,.2f} THB |")

    lines.append("+------------+----------+----------------------+-------------------+------------+------------+----------------+\n")

    lines.append("CUSTOMER EXPENSE & VISITATION SUMMARY:")
    lines.append(f"- Total Visits / Stays  : {len(cust_bookings)} times")
    lines.append(f"- Total Nights Stayed   : {total_nights} nights")
    lines.append(f"- Total Expense Spent   : {total_spent:,.2f} THB")
    lines.append("====================================================================================================")
    lines.append("                                        END OF REPORT")
    lines.append("====================================================================================================")

    content = "\n".join(lines)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())

    print(f"✅ สร้างไฟล์รายงาน {output_filename} เรียบร้อยแล้ว!")
    return content


# ------------------------------------------------------------------------------
# 4. REPORT 3: Next Week Upcoming Bookings Report
# รายงานการจองล่วงหน้าในสัปดาห์หน้า (7 วัน): สำหรับพนักงานจัดเตรียมห้องพัก
# ------------------------------------------------------------------------------
def generate_next_week_upcoming_report(ref_date_str: str = None, output_filename: str = "report_next_week_upcoming.txt") -> str:
    rooms_dict = get_rooms_dict()
    cust_dict = get_customers_dict()
    bookings = read_all_records(BOOKINGS_FILE, BOOKING_SIZE, unpack_booking)

    if not ref_date_str:
        ref_dt = datetime.now()
    else:
        try:
            ref_dt = datetime.strptime(ref_date_str, "%Y-%m-%d")
        except ValueError:
            ref_dt = datetime.now()

    next_week_start = ref_dt.date()
    next_week_end = next_week_start + timedelta(days=7)

    upcoming_list = []
    for b in bookings:
        if b["status"] == 1:
            try:
                dt_in = datetime.strptime(b["check_in_date"], "%Y-%m-%d").date()
                dt_out = datetime.strptime(b["check_out_date"], "%Y-%m-%d").date()
                if next_week_start <= dt_in <= next_week_end or (dt_in <= next_week_start and dt_out >= next_week_start):
                    upcoming_list.append((dt_in, b))
            except ValueError:
                pass

    upcoming_list.sort(key=lambda x: x[0])
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("====================================================================================================")
    lines.append("                   UPCOMING BOOKINGS REPORT (NEXT 7 DAYS ROOM PREPARATION)")
    lines.append("====================================================================================================")
    lines.append(f"Generated At      : {now_str}")
    lines.append(f"Preparation Range : {next_week_start.strftime('%Y-%m-%d')} to {next_week_end.strftime('%Y-%m-%d')}")
    lines.append("Purpose           : Room Cleaning & Hospitality Preparation Schedule")
    lines.append("====================================================================================================\n")

    lines.append("UPCOMING ARRIVALS & RESERVATIONS:")
    lines.append("+------------+----------+----------------------+----------------------+-----------------+------------+------------+")
    lines.append("| Check-In   | Room No. | Room Type            | Customer Name        | Contact Phone   | Check-Out  | Booking ID |")
    lines.append("+------------+----------+----------------------+----------------------+-----------------+------------+------------+")

    if not upcoming_list:
        lines.append("|                        NO UPCOMING BOOKINGS SCHEDULED FOR NEXT WEEK                              |")
    else:
        for dt_in, b in upcoming_list:
            c = cust_dict.get(b["customer_id"], {"name": "Unknown", "phone": "N/A"})
            r = rooms_dict.get(b["room_id"], {"room_number": "N/A", "room_type": "N/A"})
            c_name = c["name"][:20]
            c_phone = c["phone"][:15]
            r_num = r["room_number"][:8]
            r_type = r["room_type"][:20]
            lines.append(f"| {b['check_in_date']} | {r_num:<8} | {r_type:<20} | {c_name:<20} | {c_phone:<15} | {b['check_out_date']} | {b['booking_id']:<10} |")

    lines.append("+------------+----------+----------------------+----------------------+-----------------+------------+------------+\n")

    lines.append("STAFF ACTION SUMMARY:")
    lines.append(f"- Total Rooms to Prepare : {len(upcoming_list)} rooms")
    lines.append(f"- Check-In Period Range  : {next_week_start} ~ {next_week_end}")
    lines.append("====================================================================================================")
    lines.append("                                        END OF REPORT")
    lines.append("====================================================================================================")

    content = "\n".join(lines)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())

    print(f"✅ สร้างไฟล์รายงาน {output_filename} เรียบร้อยแล้ว!")
    return content
