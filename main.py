
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

# ================= CONFIG TELEGRAM =================
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
# THÊM CẤU HÌNH CHO RAILWAY
RAILWAY_MODE = True  # Đặt True khi chạy trên Railway
USE_PROXY = False if RAILWAY_MODE else True  # Railway không cần proxy

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

# ================= HUMAN-LIKE TYPING EFFECT =================
def human_type_effect(text, element_name="form"):
    """Hiệu ứng gõ chữ như người thật"""
    if not text:
        return
    
    max_total_time = 15.0
    avg_time_per_char = min(0.2, max_total_time / max(len(text), 1))
    
    typed = ""
    for char in text:
        typed += char
        
        if char.isalpha() or char.isdigit():
            delay = random.uniform(0.05, 0.15)
        elif char in ' .,;:!?':
            delay = random.uniform(0.1, 0.25)
        else:
            delay = random.uniform(0.08, 0.18)
        
        delay = min(delay, avg_time_per_char * 1.5)
        time.sleep(delay)
    
    time.sleep(random.uniform(0.3, 0.8))
    return typed

def is_private_chat(chat_id):
    return chat_id > 0
    
PRIVATE_ONLY_MSG = (
    "<b>⛔ LƯU Ý TỪ BOT!!!</b>\n"
    "━━━━━━━━━━━━━━━━\n"
    "␥ <b><i>Bot chỉ hoạt động trong Tin nhắn riêng (Private), không hỗ trợ sử dụng trong group!.</i></b>\n"
    "␥ Vui lòng nhắn tin riêng cho bot để tiếp tục sử dụng các tính năng!.\n"
    "\n"
 )

COMMAND_ALLOW_GROUP = {
    "/start": True,
    "/regfb": False,
    "/checkif": False,
    "/myinfo": False,
    "/help": False,
    "/symbols": False,
    "/symbols@nuxw_bot": False,
    "/regfb@nuxw_bot": False,
    "/checkif@nuxw_bot": False,
    "/myinfo@nuxw_bot": False,
    "/help@nuxw_bot": False,
    "/start@nuxw_bot": True
}

# ================= TELEGRAM UTILS =================
def block_group_if_needed(chat_id, text, message_id):
    if chat_id < 0:
        cmd = text.split()[0].lower()
        if cmd in COMMAND_ALLOW_GROUP and not COMMAND_ALLOW_GROUP[cmd]:
            tg_send(chat_id, PRIVATE_ONLY_MSG, reply_to_message_id=message_id)
            return True
    return False

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

def tg_delete_message(chat_id, message_id):
    try:
        requests.post(
            f"{API}/deleteMessage",
            data={"chat_id": chat_id, "message_id": message_id},
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

def self_destruct_message(chat_id, sent_msg_id, original_msg_id, delay=120):
    """Tự động xoá tin nhắn sau delay"""
    time.sleep(delay)
    tg_delete_message(chat_id, sent_msg_id)
    tg_delete_message(chat_id, original_msg_id)

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

# ================= SAFE HELPER =================
def safe_int(n):
    """Chuyển đổi sang số nguyên, trả về 0 nếu thất bại."""
    try:
        return int(n)
    except (ValueError, TypeError):
        return 0

def format_number(n):
    """Định dạng số có dấu phẩy."""
    return format(safe_int(n), ",")

def format_created(time_str):
    """Định dạng lại chuỗi thời gian 'dd/mm/yyyy||hh:mm:ss'"""
    try:
        parts = re.split(r'\|\||\s*\|\s*', time_str.strip())
        if len(parts) >= 2:
            d, t = parts[0], parts[1]
            return f"{t} | {d}"
        return time_str.replace("||", " | ")
    except:
        return "Không rõ"
        
def extract_uid_from_input(input_str):
    """Trích xuất UID từ input"""
    input_str = input_str.strip()
    
    if input_str.isdigit():
        return input_str
    
    try:
        url_encoded = quote(input_str)
        res = requests.get(UID_API_URL + url_encoded, timeout=10).json()
        
        if res.get("status") == "success" and "uid" in res:
            return res["uid"]
        else:
            return None
    except Exception as e:
        print(f"Lỗi khi lấy UID từ link: {e}")
        return None

def get_fb_info(uid):
    """Lấy thông tin Facebook từ UID"""
    try:
        url = f"{API_INFO_URL}?uid={uid}&apikey={API_KEY}"
        print(f"{get_time_tag()} 🔗 Gọi API: {url}")
        
        r = requests.get(url, timeout=15)
        
        try:
            res = r.json()
        except requests.exceptions.JSONDecodeError:
            return {"error": f"API lỗi: Phản hồi không phải JSON. Code: {r.status_code}\nNội dung: {r.text[:200]}"}

        if not isinstance(res, dict):
            return {"error": f"Dữ liệu trả về không hợp lệ: {type(res)}"}

        if 'error' in res:
            error_msg = res.get('error', 'Lỗi không xác định từ API')
            return {"error": f"API lỗi: {error_msg}"}
        
        if 'success' in res and not res['success']:
            error_msg = res.get('message', 'Lỗi không xác định từ API')
            return {"error": f"API lỗi: {error_msg}"}

        if not res.get('name') and not res.get('uid'):
            return {"error": "API trả về dữ liệu trống hoặc không hợp lệ"}

        return {"success": True, "data": res}
        
    except requests.exceptions.Timeout:
        return {"error": "Timeout: API không phản hồi sau 15 giây"}
    except requests.exceptions.ConnectionError:
        return {"error": "Lỗi kết nối: Không thể kết nối đến API"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Lỗi kết nối mạng: {e.__class__.__name__}"}
    except Exception as e:
        return {"error": f"Lỗi hệ thống: {e.__class__.__name__}: {str(e)}"}

def create_caption(res):
    """Tạo caption từ dữ liệu API"""
    uid = res.get('uid', 'Không rõ')
    
    caption = (
        "╭─────────────⭓\n"
        f"│ 𝗡𝗮𝗺𝗲: <b>{html_escape(res.get('name','Không rõ'))}</b>\n"
        f"│ 𝗨𝗜𝗗: <code>{html_escape(uid)}</code>\n"
        f"│ 𝗨𝘀𝗲𝗿𝗡𝗮𝗺𝗲: {html_escape(res.get('username','Không rõ'))}\n"
        f"│ 𝗟𝗶𝗻𝗸: <a href=\"{res.get('link_profile', f'https://facebook.com/{uid}')}\">Xem Profile</a>\n"
    )
    
    if 'follower' in res:
        caption += f"│ 𝗙𝗼𝗹𝗹𝗼𝘄𝗲𝗿𝘀: {format_number(res.get('follower'))} Người theo dõi\n"
    
    if 'created_time' in res:
        caption += f"│ 𝗖𝗿𝗲𝗮𝘁𝗲𝗱: {format_created(res.get('created_time',''))}\n"
    
    if 'tichxanh' in res:
        caption += f"│ 𝗩𝗲𝗿𝗶𝗳𝗶𝗲𝗱: {'Đã xác minh ✅' if res.get('tichxanh') else 'Chưa xác minh ❌'}\n"
    
    if 'relationship_status' in res:
        caption += f"│ 𝗦𝘁𝗮𝘁𝘂𝘀: {html_escape(res.get('relationship_status','Không rõ'))}\n"

    love = res.get("love")
    if isinstance(love, dict) and love.get("name"):
        caption += (
            f"│ -> 💍 Đã kết hôn với: {html_escape(love.get('name'))}\n"
            f"│ -> 🔗 Link UID: https://facebook.com/{love.get('id')}\n"
        )

    if 'about' in res:
        bio = res.get('about', 'Không có dữ liệu!')
        caption += f"│ 𝗕𝗶𝗼: {html_escape(bio[:200])}{'...' if len(bio) > 200 else ''}\n"
    
    if 'gender' in res:
        gender = res.get('gender','Không rõ')
        caption += f"│ 𝗚𝗲𝗻𝗱𝗲𝗿: {html_escape(gender.capitalize() if isinstance(gender, str) else gender)}\n"
    
    if 'hometown' in res:
        caption += f"│ 𝗛𝗼𝗺𝗲𝘁𝗼𝘄𝗻: {html_escape(res.get('hometown','Không rõ'))}\n"
    
    if 'location' in res:
        caption += f"│ 𝗟𝗼𝗰𝗮𝘁𝗶𝗼𝗻: {html_escape(res.get('location','Không rõ'))}\n"
    
    work_data = res.get("work", [])
    if work_data:
        caption += f"│ 𝗪𝗼𝗿𝗸:\n"
        work_found = False
        for w in work_data:
            if not isinstance(w, dict):
                continue
            employer = w.get("employer", {}).get("name")
            position = w.get("position", {}).get("name")
            
            if employer:
                work_found = True
                if position:
                    caption += f"│ -> {html_escape(position)}: {html_escape(employer)}\n"
                else:
                    caption += f"│ -> Làm việc tại: {html_escape(employer)}\n"
        
        if not work_found:
             caption += f"│ -> Không có dữ liệu công việc.\n"
    else:
        caption += f"│ 𝗪𝗼𝗿𝗸: Không có dữ liệu\n"

    caption += (
        "├─────────────⭓\n"
        f"│ 𝗧𝗶𝗺𝗲 𝗨𝗽𝗱𝗮𝘁𝗲: <b>{datetime.datetime.now().strftime('%H:%M:%S | %d/%m/%Y')}</b>\n"
        "╰─────────────⭓"
    )
    
    return caption

# ================= REGISTRATION FUNCTIONS =================
def parse_proxy(proxy_str):
    """Parse proxy string"""
    try:
        if not proxy_str:
            return None
            
        if proxy_str.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
            return proxy_str
            
        if proxy_str.startswith('['):
            ipv6_end = proxy_str.find(']')
            if ipv6_end == -1:
                return f"http://{proxy_str}"
            
            ipv6_part = proxy_str[:ipv6_end+1]
            rest = proxy_str[ipv6_end+1:]
            
            if rest.startswith(':'):
                rest = rest[1:]
            
            parts = rest.split(':')
            
            if len(parts) >= 1:
                port = parts[0]
                if len(parts) >= 3:
                    username = parts[1]
                    password = parts[2]
                    parsed = f"http://{username}:{password}@{ipv6_part}:{port}"
                else:
                    parsed = f"http://{ipv6_part}:{port}"
                return parsed
        
        parts = proxy_str.split(':')
        
        if len(parts) == 4:
            host, port, username, password = parts
            parsed = f"http://{username}:{password}@{host}:{port}"
        elif len(parts) == 2:
            host, port = parts
            parsed = f"http://{host}:{port}"
        else:
            parsed = f"http://{proxy_str}"
        
        return parsed
        
    except Exception as e:
        return proxy_str

def get_proxy_for_account():
    """Lấy proxy ngẫu nhiên - FIX CHO RAILWAY"""
    if not USE_PROXY or not proxy_reg:  # Railway không dùng proxy
        return None
        
    proxy_str = random.choice(proxy_reg)
    parsed_proxy = parse_proxy(proxy_str)
    return parsed_proxy

def get_random_user_agent():
    return random.choice(user_agent_reg)

def ten_gha():
    first = ["Bạch","Uyển","Cố","Sở","Trạch","Lam","Thanh","Mặc","Kim","Thiên","Hồng","Kính","Thủy","Kiều","Minh","Nhật","Băng","Hải","Tâm","Phi"]
    mid = ["Vũ","Hạ","Tỉnh","Vân","Khúc","Ảnh","Huyết","Vô","Tuyệt","Mệnh","Ngản","Ngạn","Bi","Lưu","Tĩnh","Lộ","Phong","Tư","Khiết","Vĩ"]
    last = ["Khách","Xuẫn","Nghi","Ninh","Nhạn","Quân","Hiên","Lâm"]
    return f"{random.choice(first)} {random.choice(mid)} {random.choice(last)}"

def birth():
    year = random.randint(1995, 2004)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{day:02d}/{month:02d}/{year}"

def matkhau(length=12):
    fixed_prefix = "@#"
    random_characters = string.ascii_letters + string.digits
    fixed_suffix = "₫1@"
    random_part = ''.join(random.choice(random_characters) for _ in range(15))
    return fixed_prefix + random_part + fixed_suffix

def ten_mail():
    chars = string.ascii_lowercase + string.digits
    username = ''.join(random.choice(chars) for _ in range(8))
    return username

def mail_ao():
    username = ten_mail()
    domains = ["hotmail.com", "gmail.com", "outlook.com", "outlook.com.vn"]
    domain = random.choice(domains)
    return f"{username}@{domain}"

def decode_response_content(response):
    """Decode response content với encoding đúng"""
    try:
        # Thử UTF-8 trước
        try:
            content = response.content.decode('utf-8', errors='ignore')
            return content
        except:
            pass
            
        # Fallback
        return response.text if hasattr(response, 'text') else str(response.content)
    except:
        return str(response.content)

def create_session_with_retry(retries=3):
    # ... (giữ nguyên hàm create_session_with_retry)
    """Tạo session với proxy"""
    proxy_str = get_proxy_for_account()
    
    for attempt in range(retries):
        try:
            session = requests.Session()
            user_agent = get_random_user_agent()
            
            session.headers.update({
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'DNT': '1',
            })
            
            if proxy_str:
                session.proxies.update({
                    'http': proxy_str,
                    'https': proxy_str
                })
                
            response = session.get("https://www.facebook.com/reg/", timeout=15)
            
            if response.status_code == 200:
                content = decode_response_content(response)
                if 'sign up' in content.lower() or 'đăng ký' in content.lower() or 'reg_email__' in content:
                    return session

        except Exception as e:
            time.sleep(3)
    
    for attempt in range(retries):
        try:
            session = requests.Session()
            mobile_agents = [
                'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'
                'Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/549.4 (KHTML, like Gecko) Version/10.5.35 Mobile/FD6B83 Safari/549.4',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/12.5.34 Mobile/Y03Z1S Safari/602.5',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2 like Mac OS X) AppleWebKit/545.27.7 (KHTML, like Gecko) Version/12.2.81 Mobile/Z3XCRI Safari/545.27.7',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/560.18 (KHTML, like Gecko) Version/10.3 Mobile/LQ9VEC Safari/560.18',
                'Mozilla/5.0 (iPhone; U; CPU iPhone OS 11_0_7 like Mac OS X; en-US) AppleWebKit/535.21.31 (KHTML, like Gecko) Version/13.1.2 Mobile/8C3 Safari/6533.18.5',
            ]
            user_agent = random.choice(mobile_agents)
            
            session.headers.update({
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate',
            })

            if proxy_str:
                session.proxies.update({'http': proxy_str, 'https': proxy_str})
                
            response = session.get("https://www.facebook.com/reg/", timeout=15)
            
            if response.status_code == 200:
                content = decode_response_content(response)
                if "facebook" in content.lower():
                    return session
        except Exception as e:
            time.sleep(2)
    
    raise Exception("Không thể tạo session")


def extract_form_fields_with_csrf(soup):
    """Trích xuất form và fields kèm CSRF token"""
    forms = soup.find_all('form')
    if not forms:
        return None, {}
    
    reg_form = None
    for form in forms:
        form_html = str(form).lower()
        if any(keyword in form_html for keyword in ['register', 'sign up', 'đăng ký']):
            reg_form = form
            break
    
    if not reg_form:
        # Lấy form đầu tiên có action
        for form in forms:
            if form.get('action'):
                reg_form = form
                break
        
        if not reg_form:
            reg_form = forms[0]
    
    fields = {}
    
    # Lấy tất cả input fields
    for inp in reg_form.find_all('input'):
        name = inp.get('name')
        value = inp.get('value', '')
        if name and name not in ['', 'submit', 'cancel']:
            fields[name] = value
    
    # Tìm các token quan trọng
    important_fields = ['fb_dtsg', 'jazoest', 'lsd', 'li', '__a', '__req']
    for inp in reg_form.find_all('input'):
        name = inp.get('name', '')
        value = inp.get('value', '')
        if name in important_fields and value:
            fields[name] = value
    
    return reg_form, fields

def register_with_mbasic(session, fullname, email, password, birthday, chat_id, msg_id, update_func):
    """Đăng ký Facebook - OPTIMIZE CHO RAILWAY"""
    try:
        time.sleep(random.uniform(2.0, 3.0))
        
        update_func(chat_id, msg_id, f"{get_time_tag()} 🌐 Đang tải trang đăng ký...")
        
        # Thử www.facebook.com trước
        response = session.get("https://www.facebook.com/reg/", timeout=40)
        
        if response.status_code != 200:
            print(f"{get_time_tag()} ❌ HTTP Error {response.status_code}")
            return False, f"HTTP Error {response.status_code}", None
        
        content = decode_response_content(response)
        
        time.sleep(random.uniform(1.5, 2.5))
        
        soup = BeautifulSoup(content, 'html.parser')
        form, fields = extract_form_fields_with_csrf(soup)
        
        if not form:
            print(f"{get_time_tag()} ❌ No registration form found")
            return False, "Không tìm thấy form đăng ký", None
        
        parts = fullname.split()
        firstname = parts[0]
        lastname = " ".join(parts[1:]) if len(parts) > 1 else parts[0]
        day, month, year = birthday.split("/")

        # Thêm thông tin vào fields
        fields.update({
            'firstname': firstname,
            'lastname': lastname,
            'reg_email__': email,
            'reg_email_confirmation__': email,
            'reg_passwd__': password,
            'birthday_day': day,
            'birthday_month': month,
            'birthday_year': year,
            'sex': str(random.choice([1, 2])),  # 1: female, 2: male
        })
        
        # Lấy action URL
        action = form.get('action', '')
        if not action or action == '#':
            action = '/reg/'
            
        if action.startswith('/'):
            action_url = 'https://www.facebook.com' + action
        else:
            action_url = action
        
        update_func(chat_id, msg_id, f"{get_time_tag()} 📤 Đang gửi đơn đăng ký...")
        
        # Thêm referer
        session.headers.update({'Referer': 'https://www.facebook.com/reg/'})
        
        # Gửi form với timeout dài
        response = session.post(action_url, data=fields, timeout=60, allow_redirects=True)
        
        time.sleep(random.uniform(3.0, 4.0))
        
        # Lấy cookies
        cookies_dict = {}
        for cookie in session.cookies:
            cookies_dict[cookie.name] = cookie.value
        
        uid = cookies_dict.get('c_user', '0')
        
        content = decode_response_content(response)
        
        print(f"{get_time_tag()} 🔍 UID from cookies: {uid}")
        
        # Kiểm tra kết quả
        if uid and uid != '0':
            print(f"{get_time_tag()} ✅ Registration successful, UID: {uid}")
            return True, "Thành công", uid
            
        elif any(keyword in content.lower() for keyword in ['confirm', 'xác nhận', 'mã', 'code', 'email sent']):
            print(f"{get_time_tag()} ⚠️ Need email confirmation")
            return True, "Cần xác nhận email", uid
            
        elif 'checkpoint' in response.url.lower():
            print(f"{get_time_tag()} ⚠️ Checkpoint required")
            return True, "Cần xác minh bảo mật", uid
            
        elif 'error' in content.lower():
            # Tìm thông báo lỗi
            soup2 = BeautifulSoup(content, 'html.parser')
            error_div = soup2.find('div', class_=re.compile(r'error|alert|warning'))
            if error_div:
                error_text = error_div.get_text(strip=True)[:100]
                return False, f"Lỗi: {error_text}", uid
            else:
                return False, "Facebook báo lỗi", uid
        else:
            return False, "Không xác định được kết quả", uid

    except Exception as e:
        print(f"{get_time_tag()} ❌ Registration error: {str(e)}")
        return False, f"Lỗi: {str(e)[:100]}", None

def get_account_cookies(session):
    """Lấy cookies từ session"""
    cookies = {}
    try:
        for cookie in session.cookies:
            cookies[cookie.name] = cookie.value
    except Exception as e:
        pass
    return cookies

def cookies_to_string(cookies_dict):
    """Chuyển cookies dict thành string"""
    if not cookies_dict:
        return "Không có"
    selected_cookies = {}
    if 'c_user' in cookies_dict:
        selected_cookies['c_user'] = cookies_dict['c_user']
    if 'xs' in cookies_dict:
        selected_cookies['xs'] = cookies_dict['xs']
    if 'fr' in cookies_dict:
        selected_cookies['fr'] = cookies_dict['fr']
    if 'datr' in cookies_dict:
        selected_cookies['datr'] = cookies_dict['datr']
    if not selected_cookies:
        return "Không có cookie quan trọng"
    cookie_str = "; ".join([f"{k}={v}" for k, v in selected_cookies.items()])
    return cookie_str

# ================= MAIN REGISTRATION FUNCTION =================
def reg_single_account(chat_id, user_id, user_name, message_id):
    """Hàm chính đăng ký account - OPTIMIZE CHO RAILWAY"""
    if chat_id in RUNNING_CHAT:
        tg_send(chat_id, "⏱️ Đợi lệnh kia chạy xong đã.", reply_to_message_id=message_id)
        return

    now = time.time()
    last = LAST_REG_TIME.get(user_id, 0) 
    if now - last < REG_DELAY:
        wait = int(REG_DELAY - (now - last))
        tg_send(chat_id, f"⏱️ Cỡ {wait}s nữa mới được reg tiếp.", reply_to_message_id=message_id)
        return

    LAST_REG_TIME[user_id] = now
    RUNNING_CHAT.add(chat_id)

    msg_id = tg_send(chat_id, f"{get_time_tag()} 🚀 Bắt đầu reg...", reply_to_message_id=message_id) 
    if not msg_id:
        RUNNING_CHAT.remove(chat_id)
        return

    session = None
    try:
        tg_edit(chat_id, msg_id, f"{get_time_tag()} ⏳ Đang chuẩn bị thông tin...")
        time.sleep(random.uniform(1.0, 2.0))
        
        fullname = ten_gha()
        email = mail_ao()
        password = matkhau()
        birthday = birth()

        tg_edit(chat_id, msg_id, f"{get_time_tag()} 🌐 Đang kết nối...")
        time.sleep(random.uniform(1.5, 2.5))
        session = create_session_with_retry()

        success, message, uid = register_with_mbasic(
            session, fullname, email, password, birthday, 
            chat_id, msg_id, tg_edit
        )

        cookies_dict = get_account_cookies(session)
        cookie_str = cookies_to_string(cookies_dict)
        
        profile_url = f"https://www.facebook.com/profile.php?id={uid}" if uid and uid != '0' else None
        
        # Xác định trạng thái
        if success:
            if uid and uid != '0':
                status = f"✅ Thành công"
                is_live = True
            else:
                status = f"⚠️ {message}"
                is_live = False
        else:
            status = f"❌ {message}"
            is_live = False

        result = {
            "name": fullname,
            "email": email,
            "password": password,
            "status": status,
            "uid": uid or "0",
            "cookies": cookie_str,
            "user_name": user_name,
            "is_live": is_live,
            "message": message
        }

        tg_edit(chat_id, msg_id, format_result(result, success))
        
        # Lưu account nếu có UID thực
        if uid and uid != '0':
            save_account_to_file(fullname, email, password, profile_url, cookies_dict)
            tg_send(chat_id, f"{get_time_tag()} ✅ Đã lưu account!", reply_to_message_id=message_id)

    except Exception as e:
        error_result = {
            "user_name": user_name,
            "status": f"❌ Lỗi hệ thống: {str(e)[:50]}"
        }
        tg_edit(chat_id, msg_id, format_result(error_result, False))
        print(f"{get_time_tag()} ❌ System error: {e}")

    finally:
        RUNNING_CHAT.remove(chat_id)
        if session:
            try:
                session.close()
            except:
                pass

def save_account_to_file(fullname, email, password, profile_url, cookies_dict):
    """Lưu account vào file"""
    try:
        now = datetime.datetime.now()
        date_str = now.strftime("%d-%m-%y")
        file_path = os.path.join(thu_muc_luu, f"acc_nvery_{date_str}.txt")
        
        uid = cookies_dict.get('c_user', '0')
        
        data = f"""╭─────{'-'*25}─────⭓
│ 👤 Tên: {fullname}
│ 📧 Email: {email}
│ 🔑 Pass: {password}
│ 🆔 UID: {uid}
│ 🔗 Profile: {profile_url or "Không có"}
│ 🍪 Cookies: {cookies_to_string(cookies_dict)}
│ ⏰ Time: {now.strftime('%H:%M:%S %d/%m/%Y')}
╰─────{'-'*25}─────⭓

"""
        
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(data)
            
    except Exception as e:
        pass

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

    footer = html_escape(
        """
        ⟡ ⊹₊˚‧︵‿₊୨ᰔ୧₊‿︵‧˚₊⊹ ⟡
           --  MY INFO --
            ─────୨ৎ─────
   𐔌. FB    : /tg.nux — Trung Hiếu
   𐔌. Zalo : 0338316701 — TghieuX
   𐔌. Tele : @tghieuX — Trungg Hieuu
   """
    )

    return (
        f"<b>{status_color} REG {'THÀNH CÔNG' if is_live else 'THẤT BẠI'} {'🎊' if is_live else '❌'}</b>\n"
        "<code><i>Thông tin acc bên dưới:</i></code>      ᓚ₍⑅^..^₎ฅ\n"
        "╭────-_Ი𐑼_-─────────⭓\n"
        f"│ 👤 Tên: ⤷ ゛<code>{html_escape(d['name'])}</code>  ˎˊ˗\n"
        f"│ 📧 Email: <code>{html_escape(d['email'])}</code>\n"
        f"│ 🔑 Mật khẩu: <tg-spoiler><code>{html_escape(d['password'])}</code></tg-spoiler>\n"
        f"│ 📌 Trạng thái: <b>{html_escape(d['status'])}</b>      ୨ৎ⊹ˑ ֗\n"
        f"│ 🆔 UID: <code>{html_escape(d['uid'])}</code>\n"
        f"│ 🔗 Profile: {'https://www.facebook.com/profile.php?id=' + html_escape(d['uid']) if d['uid'] != '0' else 'Không có'}\n"
        f"│ 🍪 Cookies: <code>{html_escape(d['cookies'])}</code>\n"
        f"├───────.────\n"
        f"│ 🌐 IP: <b>▒▒▒▒▒▒▒▒▒▒</b>       ᶻ 𝗓 𐰁 .ᐟ\n"
        f"│ 🌎 Quốc gia: <b>Việt Nam (VN)</b>\n"
        f"│ ⏰ Thời gian: <b>{now}</b>        ◟ ͜ ׁ ˙\n"
        "╰───｡𖦹°‧──────˙⟡────⭓\n"
        f"<b><i>Chúc bạn một buổi tốt lành!</i></b>\n"
        f"<b><i>Người sử dụng bot: {user_name}</i></b>  /ᐠ - ˕-マ⌒\n" 
        f"<b><i>Bot phục vụ bạn: @tghieuX</i></b>\n\n"
        f"<pre>{footer}</pre>"
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

def format_myinfo(chat_id, user_info):
    """Format thông tin user"""
    uid = user_info.get("id")
    full_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
    username = user_info.get("username")
    
    info_text = (
        "<b>✅ DƯỚI ĐÂY LÀ THÔNG TIN CỦA BẠN:</b>\n"
        f"<b><i>🆔 UID:</i></b> <code>{uid}</code>\n"
        f"<b><i>🏷️ Tên:</i></b> <code>{html_escape(full_name)}</code>\n"
    )
    
    if username:
        info_text += f"<b><i>💳 User: @{html_escape(username)}</i></b>\n"
    else:
        info_text += "<b><i>💳 User:</i></b> <code>Không có</code>\n"
        
    info_text += "\n<b><i>⚠️ Tin nhắn sẽ tự xoá sau 1 phút!</i></b>"
    return info_text

def handle_myinfo(chat_id, user_info, message_id):
    """Xử lý lệnh /myinfo"""
    text = format_myinfo(chat_id, user_info)
    sent_msg_id = tg_send(chat_id, text, reply_to_message_id=message_id)
    
    if sent_msg_id:
        threading.Thread(target=self_destruct_message, args=(chat_id, sent_msg_id, message_id, 60), daemon=True).start()

def handle_symbols(chat_id, message_id):
    """Xử lý lệnh /symbols"""
    processing_msg = tg_send(chat_id, "⏱️ Đang lấy...", reply_to_message_id=message_id)
    if not processing_msg:
        return
        
    try:
        symbols_line = "✦ ✧ ★ ☆ ✯ ✰ ⭐ ✨ ⚝ ♕ ♔ ☾ ☽ ☼ ☀ ☁ ⛄ ☔ ♪ ♫ ♬ ♩ ✿ ❀ ❁ ❃ ❄ ❅ ❆ ❇ ❈ ❉ ✢ ✣ ✤ ✥ ❊ ✱ ✲ ✳ ✴ ✵ ✶ ✷ ✸ ✹ ✺ ❋ † ‡ ※ ⁂ ⁑ ☸ ♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓ ☮ ☯ ♨ ❖ ✪ ౿ ๏ ★ ☆"
        
        result_text = (
            "✅ <b>SYMBOLS AESTHETIC:</b>\n"
            f"<code>{html_escape(symbols_line)}</code>\n\n"
            "<b><i>⚠️ Tin nhắn sẽ tự xoá sau 1 phút!</i></b>"
        )

        tg_edit(chat_id, processing_msg, result_text)
        
        threading.Thread(target=self_destruct_message, args=(chat_id, processing_msg, message_id, 60), daemon=True).start()

    except Exception as e:
        error_text = f"❌ Lỗi: {str(e)[:100]}"
        tg_edit(chat_id, processing_msg, error_text)
        print(f"{get_time_tag()} [ERROR] {e}")


def handle_checkif(chat_id, user_input, message_id, user_name):
    """Xử lý lệnh /checkif"""
    processing_msg = tg_send(
        chat_id,
        "⏳ Đang xử lý...",
        reply_to_message_id=message_id
    )
    if not processing_msg:
        return

    try:
        uid = extract_uid_from_input(user_input)
        if not uid:
            tg_edit(chat_id, processing_msg, "❌ Không lấy được UID từ input.")
            return

        api_result = get_fb_info(uid)

        if "error" in api_result:
            tg_edit(chat_id, processing_msg, f"❌ {html_escape(api_result['error'])}")
            return

        caption = create_caption(api_result["data"])
        tg_edit(chat_id, processing_msg, caption)

        threading.Thread(
            target=self_destruct_message,
            args=(chat_id, processing_msg, message_id, 60),
            daemon=True
        ).start()

    except Exception as e:
        tg_edit(
            chat_id,
            processing_msg,
            f"❌ Lỗi hệ thống: {html_escape(str(e)[:100])}"
        )

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
print(f"Group ID: {MANDATORY_GROUP_ID}")
print(f"Railway Mode: {RAILWAY_MODE}")
print(f"Use Proxy: {USE_PROXY}")
print("="*50 + "\n")

while True:
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

        cmd = text.split()[0]
        
        if cmd not in ["/start", f"/start{BOT_USERNAME}", "/help", f"/help{BOT_USERNAME}"]:
            if not check_group_membership(user_id):
                require_join_msg = (
                    "<b>⚠️ YÊU CẦU THAM GIA GROUP!!!</b>\n"
                    "\n"
                    "━━━━━━━━━━━━━━━━\n"
                    "␥ Để sử dụng bot, vui lòng tham gia group:\n"
                    f"• <b>{MANDATORY_GROUP_TITLE}</b>\n"
                    "\n"
                    "␥ Sau khi tham gia, quay lại và sử dụng bot\n"
                )
                
                sent_msg_id = tg_send(chat_id, require_join_msg, reply_to_message_id=message_id)
                
                if sent_msg_id:
                     threading.Thread(target=self_destruct_message, args=(chat_id, sent_msg_id, message_id, 60), daemon=True).start()
                         
                continue
        
        if text.startswith("/"):
               if block_group_if_needed(chat_id, text, message_id):
                continue

        if cmd == "/regfb" or cmd == f"/regfb{BOT_USERNAME}":
            threading.Thread(
                target=reg_single_account,
                args=(chat_id, user_id, user_name, message_id),
                daemon=True
            ).start()
        
        elif cmd == "/checkif" or cmd == f"/checkif{BOT_USERNAME}":
            args = text.split(maxsplit=1)
            if len(args) < 2:
                error_msg = "❌ Dùng: <code>/checkif &lt;uid-hoặc-link&gt;</code>\nVí dụ:\n• <code>/checkif 100000000000001</code>\n• <code>/checkif https://facebook.com/zuck</code>\n\n<b><i>⚠️ Tin nhắn sẽ tự xoá sau 1 phút!</i></b>"
                sent_msg_id = tg_send(chat_id, error_msg, reply_to_message_id=message_id)
                if sent_msg_id:
                    threading.Thread(target=self_destruct_message, args=(chat_id, sent_msg_id, message_id, 60), daemon=True).start()
            else:
                user_input = args[1].strip()
                threading.Thread(
                    target=handle_checkif,
                    args=(chat_id, user_input, message_id, user_name),
                    daemon=True
                ).start()

        elif cmd == "/start" or cmd == f"/start{BOT_USERNAME}":
            handle_start(chat_id, user_name, message_id)
        elif text == "/myinfo" or cmd == f"/myinfo{BOT_USERNAME}":
            handle_myinfo(chat_id, user_info, message_id)
        elif text == "/symbols" or cmd == f"/symbols{BOT_USERNAME}":
            threading.Thread(
                target=handle_symbols,
                args=(chat_id, message_id),
                daemon=True
            ).start()
        elif cmd == "/help" or cmd == f"/help{BOT_USERNAME}":
            handle_help(chat_id, message_id)

    time.sleep(1)
