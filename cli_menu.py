# ==============================================================================
# Module 2: cli_menu.py
# Responsibility: คนที่ 2 - CLI Menu & Input Validation
# Description: ระบบรับและตรวจสอบอินพุต (Input Validation) และการจัดหน้าจอเมนู
# ==============================================================================

def get_valid_int(prompt: str, min_val: int = None, max_val: int = None) -> int:
    """รับค่าจำนวนเต็ม และตรวจสอบความถูกต้อง"""
    while True:
        try:
            val = int(input(prompt).strip())
            if min_val is not None and val < min_val:
                print(f"⚠️ ค่าต้องไม่น้อยกว่า {min_val}")
                continue
            if max_val is not None and val > max_val:
                print(f"⚠️ ค่าต้องไม่เกิน {max_val}")
                continue
            return val
        except ValueError:
            print("⚠️ กรุณาป้อนตัวเลขจำนวนเต็มเท่านั้น!")

def get_valid_float(prompt: str, min_val: float = None) -> float:
    """รับค่าตัวเลขทศนิยม (เช่น ราคา) และตรวจสอบความถูกต้อง"""
    while True:
        try:
            val = float(input(prompt).strip())
            if min_val is not None and val < min_val:
                print(f"⚠️ ค่าต้องไม่น้อยกว่า {min_val}")
                continue
            return val
        except ValueError:
            print("⚠️ กรุณาป้อนตัวเลขทศนิยมที่ถูกต้อง!")

def get_valid_string(prompt: str, max_len: int, allow_empty: bool = False) -> str:
    """รับข้อความ สตริง และตรวจสอบความยาวไบต์ไม่ให้เกินกำหนด"""
    while True:
        val = input(prompt).strip()
        if not val and not allow_empty:
            print("⚠️ ห้ามป้อนค่าว่าง!")
            continue
        byte_len = len(val.encode('utf-8'))
        if byte_len > max_len:
            print(f"⚠️ ข้อความยาวเกินไป! (ปัจจุบัน {byte_len} ไบต์, สูงสุด {max_len} ไบต์)")
            continue
        return val

def display_header(title: str):
    """แสดงส่วนหัวเมนูสวยงาม"""
    print("\n" + "=" * 55)
    print(f"   {title}")
    print("=" * 55)
