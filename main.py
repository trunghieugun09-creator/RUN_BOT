import keep_alive 
import os
import time
import random
import string
import datetime
import requests
import re
import json
import platform
import sys
import threading
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote
keep_alive.keep_alive()

# ================= CONFIG TEALWAY =================
RAILWAY_MODE = True  # Luôn bật cho Railway
BOT_TOKEN = "8251269112:AAEuO_mDQ8wcivcMDjXwc_srXcTHgvTjQI8"
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
UID_FILE = "tele_uid.txt"
OFFSET = 0
REG_DELAY = 10
LAST_REG_TIME = {}
RUNNING_CHAT = set()

# THÊM CẤU HÌNH NHÓM BẮT BUỘC THAM GIA
MANDATORY_GROUP_ID = -1003444341292 
MANDATORY_GROUP_TITLE = "𝗣𝗮𝗿𝗮𝗴𝗼𝗻 𝗦𝗲𝗹 ᵎ!ᵎ 𝐟𝐫𝐬 𝐜𝐨𝐝𝐞"

# ================= CONFIG REGISTRATION =================
# RAILWAY CONFIG - KHÔNG DÙNG PROXY TRÊN RAILWAY
USE_PROXY = False  # Railway không cần proxy

proxy_reg = [
    "sp06v4-01.proxymmo.me:20393:sp06v405-20393:PDQLU"
]

user_agent_reg = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
]

window = platform.system().lower().startswith("win")
thu_muc_luu = "accounts_output"
os.makedirs(thu_muc_luu, exist_ok=True)

# ================= CONFIG CHECK INFO =================
API_KEY = "apikeysumi"
API_INFO_URL = "https://adidaphat.site/facebook/getinfo"
UID_API_URL = "https://keyherlyswar.x10.mx/Apidocs/getuidfb.php?link="

# ================= HÀM TẠO EMAIL VÀ MẬT KHẨU THEO YÊU CẦU =================
def remove_accents(text):
    """Chuyển tên thành không dấu và viết thường"""
    accents = {
        'á': 'a', 'à': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'đ': 'd',
        'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'í': 'i', 'ì': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
        'Á': 'a', 'À': 'a', 'Ả': 'a', 'Ã': 'a', 'Ạ': 'a',
        'Ă': 'a', 'Ắ': 'a', 'Ằ': 'a', 'Ẳ': 'a', 'Ẵ': 'a', 'Ặ': 'a',
        'Â': 'a', 'Ấ': 'a', 'Ầ': 'a', 'Ẩ': 'a', 'Ẫ': 'a', 'Ậ': 'a',
        'Đ': 'd',
        'É': 'e', 'È': 'e', 'Ẻ': 'e', 'Ẽ': 'e', 'Ẹ': 'e',
        'Ê': 'e', 'Ế': 'e', 'Ề': 'e', 'Ể': 'e', 'Ễ': 'e', 'Ệ': 'e',
        'Í': 'i', 'Ì': 'i', 'Ỉ': 'i', 'Ĩ': 'i', 'Ị': 'i',
        'Ó': 'o', 'Ò': 'o', 'Ỏ': 'o', 'Õ': 'o', 'Ọ': 'o',
        'Ô': 'o', 'Ố': 'o', 'Ồ': 'o', 'Ổ': 'o', 'Ỗ': 'o', 'Ộ': 'o',
        'Ơ': 'o', 'Ớ': 'o', 'Ờ': 'o', 'Ở': 'o', 'Ỡ': 'o', 'Ợ': 'o',
        'Ú': 'u', 'Ù': 'u', 'Ủ': 'u', 'Ũ': 'u', 'Ụ': 'u',
        'Ư': 'u', 'Ứ': 'u', 'Ừ': 'u', 'Ử': 'u', 'Ữ': 'u', 'Ự': 'u',
        'Ý': 'y', 'Ỳ': 'y', 'Ỷ': 'y', 'Ỹ': 'y', 'Ỵ': 'y',
    }
    
    result = ""
    for char in text:
        result += accents.get(char, char)
    return result

def generate_account_from_name(full_name):
    """
    Tạo tài khoản từ tên đầy đủ theo định dạng:
    - Email: tên không dấu + số random 4-6 ký tự + @domain
    - Mật khẩu: tên không dấu + 3-5 số random + 2 ký tự đặc biệt + "tghieux" + 3 số random
    """
    # 1. Chuyển tên thành không dấu và viết thường liền nhau
    name_no_accents = remove_accents(full_name)
    name_clean = re.sub(r'[^a-zA-Z]', '', name_no_accents).lower()
    
    # 2. Tạo email: truongminhkhanh(số random 4-6)@hotmail.com
    email_random_length = random.randint(4, 6)
    email_random_number = ''.join(random.choices(string.digits, k=email_random_length))
    email = f"{name_clean}{email_random_number}@hotmail.com"
    
    # 3. Tạo mật khẩu: tên + 3-5 số + 2 ký tự đặc biệt + tghieux + 3 số
    special_chars = "!@#$&"
    
    password_random_length = random.randint(3, 5)
    password_random_part1 = ''.join(random.choices(string.digits, k=password_random_length))
    
    special_chars_part = ''.join(random.choices(special_chars, k=2))
    
    password_random_part2 = ''.join(random.choices(string.digits, k=3))
    
    password = f"{name_clean}{password_random_part1}{special_chars_part}tghieux{password_random_part2}"
    
    return {"email": email, "password": password}

# ================= DEBUG UTILS =================
def debug_save_html(filename, html_content):
    """Lưu HTML để debug trên Railway"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content[:5000])
        print(f"{get_time_tag()} [DEBUG] Đã lưu {filename}")
    except:
        pass

# ================= TELEGRAM UTILS =================
def get_time_tag():
    return datetime.datetime.now().strftime("[%H:%M:%S]")

def html_escape(s):
    if s is None:
        s = "None"
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def tg_send(chat_id, text, parse_mode="HTML", reply_to_message_id=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_to_message_id:
        data["reply_to_message_id"] = reply_to_message_id

    try:
        r = requests.post(
            f"{API}/sendMessage",
            data=data,
            timeout=15
        ).json()
        return r.get("result", {}).get("message_id")
    except:
        return None

def tg_edit(chat_id, msg_id, text, parse_mode="HTML"):
    try:
        requests.post(
            f"{API}/editMessageText",
            data={"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": parse_mode},
            timeout=10
        )
    except:
        pass

def get_updates():
    global OFFSET
    try:
        r = requests.get(f"{API}/getUpdates", params={"offset": OFFSET, "timeout": 30}, timeout=35).json()
        if r.get("result"):
            OFFSET = r["result"][-1]["update_id"] + 1
            return r["result"]
    except:
        pass
    return []

def check_group_membership(user_id):
    """Kiểm tra xem người dùng có phải là thành viên của MANDATORY_GROUP_ID không."""
    global MANDATORY_GROUP_ID, API
    if not MANDATORY_GROUP_ID:
        return True
        
    try:
        url = f"{API}/getChatMember"
        params = {
            "chat_id": MANDATORY_GROUP_ID,
            "user_id": user_id
        }
        r = requests.get(url, params=params, timeout=15).json()
        
        status = r.get("result", {}).get("status")
        
        if status in ["creator", "administrator", "member", "restricted"]: 
            return True
        else:
            return False
            
    except Exception as e:
        return False

# ================= REGISTRATION FUNCTIONS =================
def get_random_user_agent():
    return random.choice(user_agent_reg)

def ten_gha():
    """Tạo tên giả - Cập nhật để phù hợp với định dạng mới"""
    first = ["Trương", "Nguyễn", "Lê", "Phạm", "Hoàng", "Phan", "Vũ", "Đặng", "Bùi", "Đỗ", 
             "Hồ", "Ngô", "Dương", "Lý", "Trần", "Đoàn", "Vương", "Trịnh", "Đinh", "Lâm"]
    mid = ["Minh", "Thanh", "Quốc", "Hữu", "Đức", "Văn", "Thị", "Công", "Xuân", "Hồng",
           "Thu", "Hải", "Tuấn", "Kim", "Ngọc", "Bảo", "Gia", "Thế", "Việt", "Nam"]
    last = ["Khánh", "Anh", "Phương", "Huy", "Duy", "Long", "Khang", "Thịnh", "Nhật", "Linh",
            "My", "Ngân", "Thy", "Trang", "Nhi", "Vy", "Uyên", "Lam", "Tú", "Hằng"]
    
    return f"{random.choice(first)} {random.choice(mid)} {random.choice(last)}"

def birth():
    year = random.randint(1995, 2004)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{day:02d}/{month:02d}/{year}"

def create_session_with_retry():
    """Tạo session cho Railway (không dùng proxy)"""
    try:
        session = requests.Session()
        
        # Railway không cần proxy
        print(f"{get_time_tag()} 🌐 Railway mode - Không dùng proxy")
        
        # Tắt warnings SSL
        import warnings
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        
        # Cấu hình session
        session.verify = False
        session.trust_env = False
        
        # Header Facebook
        headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        session.headers.update(headers)
        
        # Khởi tạo session
        print(f"{get_time_tag()} 🌐 Khởi tạo session...")
        try:
            response = session.get("https://www.facebook.com/", timeout=20, allow_redirects=True)
            print(f"{get_time_tag()} ✅ Session OK - Status: {response.status_code}")
            return session
        except Exception as e:
            print(f"{get_time_tag()} ⚠️ Session init error: {str(e)[:50]}")
            return session
        
    except Exception as e:
        print(f"{get_time_tag()} ❌ Lỗi tạo session: {e}")
        return None

# ================= SIMPLE MOBILE REGISTRATION =================
def mobile_facebook_registration(session, fullname, email, password, birthday):
    """Đăng ký Facebook qua mobile site - Đơn giản nhất"""
    try:
        print(f"{get_time_tag()} [1/3] Đang lấy trang đăng ký mobile...")
        
        # Dùng mbasic.facebook.com (ổn định nhất)
        mobile_url = "https://mbasic.facebook.com/reg/"
        
        # Headers mobile đơn giản
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })
        
        response = session.get(mobile_url, timeout=30, allow_redirects=True)
        
        if response.status_code != 200:
            print(f"{get_time_tag()} ❌ Mobile page status: {response.status_code}")
            return False, f"Mobile page status: {response.status_code}"
        
        # Lưu HTML để debug
        debug_save_html("mobile_form.html", response.text)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm tất cả form
        forms = soup.find_all('form')
        print(f"{get_time_tag()} [DEBUG] Tìm thấy {len(forms)} forms")
        
        form = None
        # Tìm form có chứa các field đăng ký
        for f in forms:
            form_text = str(f).lower()
            # Kiểm tra các từ khóa đăng ký
            if any(keyword in form_text for keyword in ['firstname', 'lastname', 'reg_email', 'reg_passwd']):
                form = f
                print(f"{get_time_tag()} [✅] Tìm thấy form đăng ký")
                break
        
        if not form and forms:
            form = forms[0]  # Lấy form đầu tiên
            print(f"{get_time_tag()} [⚠️] Lấy form đầu tiên")
        
        if not form:
            print(f"{get_time_tag()} [❌] Không tìm thấy form nào")
            return False, "Không tìm thấy form đăng ký trên mobile"
        
        # Thu thập các field
        form_data = {}
        for inp in form.find_all('input'):
            name = inp.get('name')
            value = inp.get('value', '')
            if name:
                form_data[name] = value
        
        print(f"{get_time_tag()} [DEBUG] Found {len(form_data)} form fields")
        
        # Thêm thông tin đăng ký
        parts = fullname.split()
        firstname = parts[0]
        lastname = " ".join(parts[1:]) if len(parts) > 1 else firstname
        day, month, year = birthday.split("/")
        
        # Cập nhật form data với các field cơ bản
        base_fields = {
            'firstname': firstname,
            'lastname': lastname,
            'birthday_day': day,
            'birthday_month': month,
            'birthday_year': year,
            'sex': str(random.choice([1, 2])),  # 1=Nữ, 2=Nam
        }
        
        # Thêm các field cơ bản
        form_data.update(base_fields)
        
        # Tìm và cập nhật email và password fields
        email_field = None
        pass_field = None
        
        for field in form_data.keys():
            field_lower = field.lower()
            if 'email' in field_lower:
                email_field = field
            elif 'pass' in field_lower:
                pass_field = field
        
        # Thêm email
        if email_field:
            form_data[email_field] = email
            # Tìm field xác nhận email
            confirm_field = email_field.replace('__', '_confirmation__')
            if confirm_field in form_data:
                form_data[confirm_field] = email
        else:
            # Thử các field mặc định
            form_data['reg_email__'] = email
            form_data['reg_email_confirmation__'] = email
        
        # Thêm password
        if pass_field:
            form_data[pass_field] = password
        else:
            form_data['reg_passwd__'] = password
        
        # Xử lý action URL
        action = form.get('action', '')
        if action.startswith('/'):
            submit_url = f"https://mbasic.facebook.com{action}"
        elif action.startswith('http'):
            submit_url = action
        else:
            submit_url = mobile_url
        
        print(f"{get_time_tag()} [2/3] Đang submit form...")
        time.sleep(2)
        
        # Gửi request đăng ký
        submit_response = session.post(
            submit_url,
            data=form_data,
            timeout=30,
            allow_redirects=True,
            headers={
                'Referer': mobile_url,
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        )
        
        print(f"{get_time_tag()} [3/3] Kiểm tra kết quả...")
        
        # Kiểm tra cookies
        if 'c_user' in session.cookies:
            uid = session.cookies.get('c_user')
            print(f"{get_time_tag()} [🎉] Tìm thấy c_user: {uid}")
            return True, f"Thành công - UID: {uid}"
        
        # Kiểm tra URL và nội dung
        final_url = submit_response.url.lower()
        content = submit_response.text.lower()
        
        # Kiểm tra thành công
        success_indicators = ['home', 'welcome', 'feed', 'confirm', 'checkpoint', 'verification']
        for indicator in success_indicators:
            if indicator in final_url or indicator in content:
                print(f"{get_time_tag()} [✅] Found indicator: {indicator}")
                return True, f"Thành công - {indicator}"
        
        # Kiểm tra lỗi
        error_indicators = ['sorry', 'error', 'invalid', 'incorrect', 'temporarily']
        for indicator in error_indicators:
            if indicator in content:
                print(f"{get_time_tag()} [❌] Found error: {indicator}")
                return False, f"Lỗi: {indicator}"
        
        # Kiểm tra lại cookies sau 3 giây
        time.sleep(3)
        if 'c_user' in session.cookies:
            uid = session.cookies.get('c_user')
            return True, f"Thành công (delayed) - UID: {uid}"
        
        return False, "Không xác định kết quả"
            
    except Exception as e:
        print(f"{get_time_tag()} ❌ Lỗi mobile: {str(e)[:200]}")
        import traceback
        traceback.print_exc()
        return False, f"Lỗi hệ thống: {str(e)[:100]}"

def check_live_status(session):
    """Kiểm tra account có live không"""
    try:
        # Kiểm tra cookie c_user
        if 'c_user' in session.cookies:
            uid = session.cookies.get('c_user')
            if uid and len(uid) > 5:
                return True, "LIVE", f"https://www.facebook.com/profile.php?id={uid}", uid
        
        return False, "DIE", None, None
        
    except Exception as e:
        return False, f"ERROR: {str(e)[:50]}", None, None

def get_account_cookies(session):
    cookies = {}
    for cookie in session.cookies:
        cookies[cookie.name] = cookie.value
    return cookies

def cookies_to_string(cookies_dict):
    important = ['c_user', 'xs', 'fr', 'datr']
    selected = {k: v for k, v in cookies_dict.items() if k in important}
    if not selected:
        return "Không có"
    return "; ".join([f"{k}={v}" for k, v in selected.items()])

# ================= MAIN REGISTRATION FUNCTION =================
def reg_single_account(chat_id, user_id, user_name, message_id):
    """Hàm đăng ký account chính"""
    RUNNING_CHAT.add(chat_id)
    msg_id = tg_send(chat_id, f"{get_time_tag()} 🚀 Bắt đầu reg...", reply_to_message_id=message_id) 
    if not msg_id:
        RUNNING_CHAT.remove(chat_id)
        return

    session = None
    try:
        tg_edit(chat_id, msg_id, f"{get_time_tag()} ⏳ Đang chuẩn bị thông tin...")
        time.sleep(1)
        
        # Tạo thông tin account
        fullname = ten_gha()
        birthday = birth()
        
        # Sử dụng hàm mới để tạo email và password
        account_info = generate_account_from_name(fullname)
        email = account_info["email"]
        password = account_info["password"]
        
        print(f"{get_time_tag()} [INFO] Tên: {fullname}")
        print(f"{get_time_tag()} [INFO] Email: {email}")
        print(f"{get_time_tag()} [INFO] Password: {password}")

        # Tạo session
        tg_edit(chat_id, msg_id, f"{get_time_tag()} 🌐 Đang tạo session...")
        session = create_session_with_retry()
        if not session:
            tg_edit(chat_id, msg_id, f"{get_time_tag()} ❌ Không tạo được session")
            RUNNING_CHAT.remove(chat_id)
            return
        
        # Ưu tiên mobile trên Railway
        tg_edit(chat_id, msg_id, f"{get_time_tag()} 📱 Đang đăng ký qua mobile...")
        success, message = mobile_facebook_registration(session, fullname, email, password, birthday)
        
        if not success:
            tg_edit(chat_id, msg_id, f"{get_time_tag()} ❌ Đăng ký thất bại: {message}")
            
            # Thử lại lần 2
            time.sleep(3)
            tg_edit(chat_id, msg_id, f"{get_time_tag()} 🔄 Thử lại lần 2...")
            session = create_session_with_retry()
            if session:
                success, message = mobile_facebook_registration(session, fullname, email, password, birthday)
            
            if not success:
                # Kiểm tra xem có live không
                is_live, live_msg, profile_url, uid = check_live_status(session)
                if is_live:
                    tg_edit(chat_id, msg_id, f"{get_time_tag()} ⚠️ Lỗi reg nhưng acc vẫn LIVE!")
                else:
                    if session:
                        session.close()
                    RUNNING_CHAT.remove(chat_id)
                    return
        else:
            # Xử lý kết quả thành công
            time.sleep(3)
            is_live, live_msg, profile_url, uid = check_live_status(session)
            
            if not is_live:
                tg_edit(chat_id, msg_id, f"{get_time_tag()} 💀 ACC DIE")
                if session:
                    session.close()
                RUNNING_CHAT.remove(chat_id)
                return
        
        # Lấy cookies và thông tin
        cookies_dict = get_account_cookies(session)
        cookie_str = cookies_to_string(cookies_dict)
        
        uid = uid or cookies_dict.get('c_user', '0')
        profile_url = profile_url or f"https://www.facebook.com/profile.php?id={uid}"
        
        # Chuẩn bị kết quả
        result = {
            "name": fullname,
            "email": email,
            "password": password,
            "status": "✅ Thành công" if is_live else f"❌ {live_msg}",
            "uid": uid,
            "cookies": cookie_str,
            "user_name": user_name,
            "is_live": is_live,
            "message": message if not is_live else "Thành công"
        }

        # Hiển thị kết quả
        tg_edit(chat_id, msg_id, format_result(result, is_live))
        
        # Lưu account
        if uid and uid != '0':
            save_account_to_file(fullname, email, password, profile_url, cookies_dict)

    except Exception as e:
        error_result = {
            "user_name": user_name,
            "status": f"❌ Lỗi hệ thống: {str(e)[:50]}"
        }
        tg_edit(chat_id, msg_id, format_result(error_result, False))
        print(f"{get_time_tag()} ❌ System error: {e}")
        import traceback
        traceback.print_exc()

        if session:
            try:
                session.close()
            except:
                pass
        RUNNING_CHAT.remove(chat_id)

def save_account_to_file(fullname, email, password, profile_url, cookies_dict):
    """Lưu account vào file"""
    try:
        now = datetime.datetime.now()
        date_str = now.strftime("%d-%m-%y")
        file_path = os.path.join(thu_muc_luu, f"acc_nvery_{date_str}.txt")
        
        uid = cookies_dict.get('c_user', '0')
        
        data = f"""
╭──────────⭓
│ 👤 Tên: {fullname}
│ 📧 Email: {email}
│ 🔑 Pass: {password}
│ 🆔 UID: {uid}
│ 🔗 Profile: {profile_url or "Không có"}
│ 🍪 Cookies: {cookies_to_string(cookies_dict)}
│ ⏰ Time: {now.strftime('%H:%M:%S %d/%m/%Y')}
╰──────────⭓

"""
        
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(data)
        print(f"{get_time_tag()} ✅ Đã lưu account {uid}")
            
    except Exception as e:
        print(f"{get_time_tag()} ❌ Lỗi lưu file: {e}")

# ================= RESULT FORMATTING =================
def format_result(d, success):
    """Format kết quả để gửi Telegram"""
    now = datetime.datetime.now().strftime("%H:%M:%S | %d/%m/%y")
    user_name = html_escape(d.get('user_name', 'Unknown User'))
    
    if not success:
        return (
            f"👤 Người sử dụng bot: <b>{user_name}</b>\n"
            f"❌ Reg thất bại\n"
            f"⏰ {now}\n"
            f"Lỗi: {html_escape(d.get('status', 'Không xác định'))}"
        )

    is_live = d.get('is_live', False)
    status_color = "🟢" if is_live else "🔴"
    
    for k in ["name", "email", "password", "status", "uid", "cookies"]:
        if k not in d or d[k] is None:
            d[k] = "None"

    return (
        f"<b>{status_color} REG {'THÀNH CÔNG' if is_live else 'THẤT BẠI'} {'🎊' if is_live else '❌'}</b>\n"
        f"<code><i>Thông tin acc bên dưới:</i></code>      ᓚ₍⑅^..^₎ฅ\n"
        f"╭────-_Ი𐑼_-─────────⭓\n"
        f"│ 👤 Tên: ⤷ ゛<code>{html_escape(d['name'])}</code>  ˎˊ˗\n"
        f"│ 📧 Email: <code>{html_escape(d['email'])}</code>\n"
        f"│ 🔑 Mật khẩu: <tg-spoiler>{html_escape(d['password'])}</tg-spoiler>\n"
        f"│ 📌 Trạng thái: <b>🟢Live!</b>      ୨ৎ⊹ˑ ֗\n"
        f"│ 🆔 UID: <code>{html_escape(d['uid'])}</code>\n"
        f"│ 🔗 Profile: https://www.facebook.com/profile.php?id={html_escape(d['uid'])}\n"
        f"│ 🍪 Cookies: <code>{html_escape(d['cookies'])}</code>\n"
        f"├───────.────\n"
        f"│ ⏰ Thời gian: <b>{now}</b>        ◟ ͜ ׁ ˙\n"
        "╰───｡𖦹°‧──────˙⟡────⭓\n"
        f"<b><i>Chúc bạn một buổi tốt lành!</i></b>\n"
        f"<b><i>Người sử dụng bot: {user_name}</i></b>  /ᐠ - ˕-マ⌒\n" 
        f"<b><i>Bot phục vụ bạn: @nuxw_bot</i></b>    ᶻ 𝗓 𐰁 .ᐟ\n\n"
    )

# ================= BOT HANDLERS =================
def handle_start(chat_id, user_name, message_id):
    """Xử lý lệnh /start"""
    text = (
        f"<b><i>🎉 Chào mừng {html_escape(user_name)} đã đến!👋</i></b>\n"
        f"<b><i>💌 Hãy sử dụng lệnh /help để xem hướng dẫn!</i></b>"
    )
    tg_send(chat_id, text, reply_to_message_id=message_id)

def handle_help(chat_id, message_id):
    """Xử lý lệnh /help"""
    text = (
        "<b><i> 🧸 ┊‌ NUX BOT XIN CHÀO! ┊‌ 🍰\n"
        "                 ˚༺☆༻</i></b>\n"
        "\n"
        "␥ 🫧 TỚ XIN HỖ TRỢ BẠN BẰNG CÁC LỆNH NHƯ SAU:\n"
        "\n"
        "━━━━━━━━━━━━━━━━\n"
        "␥ 「 🚀 LỆNH REG: 」\n"
        "𖥻𓂃  <b>/regfb</b> — Tạo một tài khoản Facebook (no verify)\n"
        " ₎₎ ๑\n"
        "━━━━━━━━━━━━━━━━\n"
        "␥ 「 🔎 LỆNH CHECK INFO: 」\n"
        "𖥻𓂃  <b>/checkif &lt;UID | Link&gt;</b> — Check info Facebook\n"
        " ₎₎ ๑\n"
        "━━━━━━━━━━━━━━━━\n"
        "␥ 「 👤 LỆNH XEM THÔNG TIN TELEGRAM: 」\n"
        "𖥻𓂃  <b>/myinfo</b> — Xem thông tin của bạn\n"
        " ₎₎ ๑\n"
        "━━━━━━━━━━━━━━━━\n"
        "␥ 「 ✨ LỆNH KÍ TỰ AESTHETIC: 」\n"
        "𖥻𓂃  <b>/symbols</b> — Lấy 150 kí tự symbols aesthetic\n"
        " ₎₎ ๑\n"
        "━━━━━━━━━━━━━━━━\n"
        "␥ 「 ⏱ LƯU Ý: 」 Một số lệnh sẽ tự xoá sau 60 giây\n"
    )
    tg_send(chat_id, text, reply_to_message_id=message_id)

# ================= BOT MAIN LOOP =================
def get_bot_username():
    """Lấy username của bot"""
    try:
        r = requests.get(f"{API}/getMe", timeout=10).json()
        if r.get("ok") and r.get("result"):
            return "@" + r["result"]["username"]
    except:
        pass
    return "Không xác định"

BOT_USERNAME = get_bot_username()

print("\n" + "="*50)
print("🤖 NOVERY TELEGRAM BOT - BY TGHIEUX")
print(f"Bot: {BOT_USERNAME}")
print(f"Railway Mode: {RAILWAY_MODE}")
print(f"Use Proxy: {USE_PROXY}")
print("="*50 + "\n")

# Main loop
while True:
    try:
        for u in get_updates():
            msg = u.get("message")
            if not msg or "text" not in msg or "from" not in msg:
                continue

            chat_id = msg["chat"]["id"]
            user_info = msg["from"]
            user_id = user_info.get("id")
            text = msg["text"].strip()
            message_id = msg.get("message_id")

            username_str = user_info.get("username")
            first_name_str = user_info.get("first_name", "Unknown")
            user_name = "@" + username_str if username_str else first_name_str

            print(f"{get_time_tag()} | USER: {user_name} | ID: {user_id} | CMD: {text}")

            # Kiểm tra nhóm bắt buộc
            if text.startswith("/regfb") and not check_group_membership(user_id):
                require_join_msg = (
                    "<b>⚠️ YÊU CẦU THAM GIA GROUP!!!</b>\n"
                    "\n"
                    "━━━━━━━━━━━━━━━━\n"
                    "␥ Để sử dụng bot, vui lòng tham gia group:\n"
                    f"• <b>{MANDATORY_GROUP_TITLE}</b>\n"
                    "\n"
                    "␥ Sau khi tham gia, quay lại và sử dụng bot\n"
                )
                tg_send(chat_id, require_join_msg, reply_to_message_id=message_id)
                continue

            # Xử lý commands
            if text.startswith("/regfb"):
                if chat_id in RUNNING_CHAT:
                    tg_send(chat_id, "⏳ Đang xử lý reg trước đó, vui lòng chờ...", reply_to_message_id=message_id)
                else:
                    threading.Thread(
                        target=reg_single_account,
                        args=(chat_id, user_id, user_name, message_id),
                        daemon=True
                    ).start()
            
            elif text.startswith("/start"):
                handle_start(chat_id, user_name, message_id)
            
            elif text.startswith("/help"):
                handle_help(chat_id, message_id)

    except Exception as e:
        print(f"{get_time_tag()} ❌ Lỗi main loop: {e}")
        import traceback
        traceback.print_exc()
    
    time.sleep(1)
