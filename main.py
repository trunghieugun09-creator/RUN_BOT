#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import time
import random
import requests
import datetime
import unicodedata
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# ---------------- CONFIG ----------------
DEBUG_LEVEL = 1

# ---------------- UTILITY FUNCTIONS ----------------
def debug(msg, level=1):
    if level <= DEBUG_LEVEL:
        prefixes = {1: "ℹ️", 2: "⚙️", 3: "🌀", 4: "📡", 5: "🔥"}
        prefix = prefixes.get(level, "ℹ️")
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {prefix} {msg}")

def random_vn_name():
    first = ["Nguyễn","Trần","Lê","Phạm","Hoàng","Huỳnh","Phan","Vũ","Đặng","Bùi"]
    mid = ["Văn","Thị","Đức","Thành","Minh","Quốc","Công","Hữu","Trọng","Tấn"]
    last = ["An","Bình","Cường","Dũng","Hùng","Kiệt","Long","Nam","Linh","Quý"]
    return f"{random.choice(first)} {random.choice(mid)} {random.choice(last)}"

def random_birthday():
    start, end = datetime.date(1985,1,1), datetime.date(2003,12,31)
    d = start + datetime.timedelta(days=random.randint(0, (end - start).days))
    return d.strftime("%d/%m/%Y")

def normalize_name_for_email(name):
    """Chuyển tên tiếng Việt thành dạng không dấu, chữ thường"""
    name = unicodedata.normalize('NFKD', name)
    name = ''.join([c for c in name if not unicodedata.combining(c)])
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    name = name.lower()
    name = name.replace(' ', '')
    return name

# ---------------- MAIL.TM ----------------
def create_mailtm_account(base_name):
    """Tạo email tạm từ mail.tm"""
    try:
        # Lấy domain
        r = requests.get("https://api.mail.tm/domains", timeout=10)
        data = r.json()
        domains = [d["domain"] for d in data["hydra:member"]]
        domain = random.choice(domains)
        
        # Tạo email từ tên
        clean_name = normalize_name_for_email(base_name)
        random_suffix = random.randint(10000, 99999)
        username = f"{clean_name}{random_suffix}"
        address = f"{username}@{domain}".lower()
        
        # Tạo mật khẩu theo format
        random_num = random.randint(1000, 9999)
        password = f"tghieu#₫@{clean_name}!{random_num}"

        debug(f"Tạo tài khoản mail.tm: {address}", 3)

        # Tạo session
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (RegBot/1.0)",
            "Accept": "application/json",
        })

        # Tạo account
        url_create = "https://api.mail.tm/accounts"
        payload = {"address": address, "password": password}
        
        r = session.post(url_create, json=payload, timeout=30)
        if r.status_code not in (200, 201):
            raise RuntimeError(f"Tạo account mail.tm thất bại: {r.status_code}")

        debug(f"✅ Đã tạo email: {address}", 3)

        return address, password, clean_name

    except Exception as e:
        debug(f"Lỗi tạo mail.tm: {e}", 5)
        raise

# ---------------- DRIVER SETUP ----------------
def create_driver():
    """Tạo Chrome driver cho Koyeb"""
    chrome_options = Options()
    
    # Các option cho headless Chrome
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless=new')  # Headless mode mới
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Ẩn các dấu hiệu automation
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent giả lập
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Giảm log
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--silent')
    
    # Tạo driver
    try:
        # Dùng ChromeDriver mặc định (đã cài trong Docker)
        driver = webdriver.Chrome(options=chrome_options)
        
        # Ẩn các thuộc tính automation
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    except Exception as e:
        debug(f"Lỗi tạo driver: {e}", 5)
        raise

# ---------------- REGISTER FLOW ----------------
def register_facebook_account(index):
    """Đăng ký Facebook account"""
    fullname = random_vn_name()
    
    try:
        print(f"\n{'='*60}")
        print(f"[{index}] 🚀 BẮT ĐẦU ĐĂNG KÝ: {fullname}")
        print('='*60)
        
        # Tách tên
        parts = fullname.split()
        first = parts[0]
        last = " ".join(parts[1:]) if len(parts) > 1 else "Nguyen"
        day, month, year = random_birthday().split("/")
        
        # 1. Tạo email
        print(f"   📧 Đang tạo email...")
        email, mail_pass, clean_name = create_mailtm_account(fullname)
        
        # 2. Tạo mật khẩu Facebook
        random_num = random.randint(1000, 9999)
        passwd = f"tghieu#₫@{clean_name}!{random_num}"
        
        print(f"   ✅ Email: {email}")
        print(f"   🔐 Pass FB: {passwd}")
        print(f"   🔑 Pass Mail: {mail_pass}")
        
        # 3. Khởi tạo driver
        print(f"   🌐 Đang khởi tạo trình duyệt...")
        driver = create_driver()
        
        # 4. Mở trang đăng ký
        print(f"   📄 Đang mở trang đăng ký Facebook...")
        driver.get("https://www.facebook.com/reg")
        time.sleep(3)
        
        # 5. Điền thông tin
        print(f"   ✍️ Đang điền thông tin...")
        
        # First name
        firstname_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "firstname"))
        )
        firstname_field.send_keys(first)
        
        # Last name
        lastname_field = driver.find_element(By.NAME, "lastname")
        lastname_field.send_keys(last)
        
        # Email
        email_field = driver.find_element(By.NAME, "reg_email__")
        email_field.send_keys(email)
        time.sleep(1)
        
        # Email confirmation (nếu có)
        try:
            confirm_field = driver.find_element(By.NAME, "reg_email_confirmation__")
            confirm_field.send_keys(email)
        except:
            pass
        
        # Password
        pass_field = driver.find_element(By.NAME, "reg_passwd__")
        pass_field.send_keys(passwd)
        
        # Birthday
        Select(driver.find_element(By.NAME, "birthday_day")).select_by_value(str(int(day)))
        Select(driver.find_element(By.NAME, "birthday_month")).select_by_value(str(int(month)))
        Select(driver.find_element(By.NAME, "birthday_year")).select_by_value(year)
        
        # Gender (chọn female - value=2)
        try:
            driver.find_element(By.CSS_SELECTOR, "input[value='2']").click()
        except:
            try:
                driver.find_element(By.XPATH, "//label[contains(text(),'Nữ')]").click()
            except:
                pass
        
        # 6. Submit form
        print(f"   📤 Đang gửi form đăng ký...")
        try:
            submit_btn = driver.find_element(By.NAME, "websubmit")
            submit_btn.click()
        except:
            driver.execute_script("document.querySelector('button[type=\"submit\"]').click()")
        
        # 7. Chờ xử lý
        print(f"   ⏳ Đang chờ xử lý...")
        time.sleep(5)
        
        # 8. Kiểm tra kết quả
        current_url = driver.current_url.lower()
        page_source = driver.page_source.lower()
        
        success = False
        if "checkpoint" in current_url or "confirmemail" in current_url:
            success = True
            print(f"   ✅ THÀNH CÔNG! Đã gửi form, cần xác minh email")
        elif "facebook.com" in current_url and "login" not in current_url:
            success = True
            print(f"   ✅ THÀNH CÔNG! Có thể đã đăng ký thành công")
        elif "sorry" in page_source or "error" in page_source:
            print(f"   ❌ Facebook trả về lỗi")
        else:
            print(f"   ⚠️ Trạng thái không xác định")
        
        # 9. Đóng driver
        driver.quit()
        
        # 10. Trả về kết quả
        result = {
            "index": index,
            "success": success,
            "name": fullname,
            "email": email,
            "password": passwd,
            "mail_pass": mail_pass,
            "time": datetime.datetime.now().strftime("%H:%M:%S")
        }
        
        return result
        
    except Exception as e:
        print(f"   ❌ LỖI: {str(e)[:100]}")
        try:
            if 'driver' in locals():
                driver.quit()
        except:
            pass
        
        return {
            "index": index,
            "success": False,
            "name": fullname,
            "error": str(e),
            "time": datetime.datetime.now().strftime("%H:%M:%S")
        }

# ---------------- MAIN ----------------
def main():
    """Chương trình chính"""
    print("\n" + "="*70)
    print("🤖 BOT ĐĂNG KÝ FACEBOOK - CHẠY TRÊN KOYEB")
    print("="*70)
    
    try:
        # Nhập số lượng account
        try:
            n = int(input("\n👉 Nhập số lượng account cần tạo: "))
            if n <= 0:
                n = 1
                print("   ⚠️ Đã đặt mặc định 1 account")
        except:
            n = 1
            print("   ⚠️ Đã đặt mặc định 1 account")
        
        try:
            delay = float(input("👉 Nhập delay giữa các account (giây): "))
            if delay < 0:
                delay = 5
                print("   ⚠️ Đã đặt mặc định 5 giây")
        except:
            delay = 5
            print("   ⚠️ Đã đặt mặc định 5 giây")
        
        print(f"\n🎯 Bắt đầu tạo {n} account với delay {delay}s")
        print("-" * 60)
        
        accounts = []
        success_count = 0
        
        # Tạo các account
        for i in range(1, n + 1):
            result = register_facebook_account(i)
            accounts.append(result)
            
            if result["success"]:
                success_count += 1
            
            # Delay giữa các account
            if i < n:
                print(f"\n⏳ Chờ {delay} giây trước account tiếp theo...")
                time.sleep(delay)
        
        # HIỂN THỊ KẾT QUẢ
        print("\n" + "="*70)
        print("📊 KẾT QUẢ ĐĂNG KÝ")
        print("="*70)
        
        print(f"\n📈 TỔNG KẾT:")
        print(f"   ✅ Thành công: {success_count}/{n}")
        print(f"   ❌ Thất bại: {n - success_count}/{n}")
        
        print(f"\n📋 DANH SÁCH ACCOUNT:")
        print("-" * 80)
        
        for acc in accounts:
            if acc["success"]:
                print(f"\n[{acc['index']}] ✅ THÀNH CÔNG")
                print(f"   👤 Tên: {acc['name']}")
                print(f"   📧 Email: {acc['email']}")
                print(f"   🔐 Mật khẩu FB: {acc['password']}")
                print(f"   🔑 Mật khẩu Mail: {acc['mail_pass']}")
                print(f"   🕒 Thời gian: {acc['time']}")
            else:
                print(f"\n[{acc['index']}] ❌ THẤT BẠI")
                print(f"   👤 Tên: {acc.get('name', 'N/A')}")
                print(f"   💥 Lỗi: {acc.get('error', 'Không xác định')}")
                print(f"   🕒 Thời gian: {acc['time']}")
            print("-" * 80)
        
        print(f"\n🎉 HOÀN TẤT! Đã xử lý {n} account")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Đã dừng bởi người dùng")
    except Exception as e:
        print(f"\n❌ Lỗi chính: {e}")

# ---------------- RUN ----------------
if __name__ == "__main__":
    main()
