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
from urllib.parse import urlparse, quote, urljoin
keep_alive.keep_alive()

# ================= CONFIG TEALWAY =================
RAILWAY_MODE = os.getenv('RAILWAY_ENVIRONMENT', 'False').lower() == 'true'
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
# RAILWAY CONFIG
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

# ================= DEBUG UTILS =================
def debug_save_html(filename, html_content):
    """Lưu HTML để debug trên Railway"""
    if RAILWAY_MODE:
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html_content[:5000])
            print(f"{get_time_tag()} [DEBUG] Đã lưu {filename}")
        except:
            pass

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

def block_group_if_needed(chat_id, text, message_id):
    if chat_id < 0:
        cmd = text.split()[0].lower()
        if cmd in COMMAND_ALLOW_GROUP and not COMMAND_ALLOW_GROUP[cmd]:
            tg_send(chat_id, PRIVATE_ONLY_MSG, reply_to_message_id=message_id)
            return True
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
        if not isinstance(proxy_str, str):
            return None
            
        if ":" not in proxy_str:
            return None
        
        parts = proxy_str.split(":")
        
        # Format: host:port:username:password
        if len(parts) == 4:
            host, port, username, password = parts
            if not port.isdigit():
                return None
            return f"http://{username}:{password}@{host}:{port}"
        else:
            return None
            
    except Exception as e:
        return None

def check_proxy_live(proxy_str):
    """Kiểm tra proxy có hoạt động không"""
    try:
        test_url = "http://httpbin.org/ip"
        proxies = {'http': proxy_str, 'https': proxy_str}
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(test_url, proxies=proxies, headers=headers, timeout=15, verify=False)
        return response.status_code == 200
    except:
        return False

def get_proxy_for_account():
    """Lấy proxy cho account"""
    if not proxy_reg or not USE_PROXY:
        return None
        
    proxy_str = proxy_reg[0]  # Lấy proxy đầu tiên
    parsed_proxy = parse_proxy(proxy_str)
    
    if not parsed_proxy:
        return None
    
    # Kiểm tra proxy
    if check_proxy_live(parsed_proxy):
        return parsed_proxy
    else:
        # Thử parse và test các proxy khác
        for p in proxy_reg[1:]:
            parsed = parse_proxy(p)
            if parsed and check_proxy_live(parsed):
                return parsed
    
    return None

def get_random_user_agent():
    return random.choice(user_agent_reg)

def ten_gha():
    first = ["Bạch","Uyển","Cố","Sở","Trạch","Lam","Thanh","Mặc","Kim","Thiên","Hồng","Kính","Thủy","Kiều","Minh","Nhật","Băng","Hải","Tâm","Phi"]
    mid = ["Vũ","Hạ","Tỉnh","Vân","Khúc","Ảnh","Huyết","Vô","Tuyệt","Mệnh","Ngản","Ngạn","Bi","Lưu","Tĩnh","Lộ","Phong","Tư","Khiết","Vĩ"]
    last = ["Khách","Xuẫn","Nghi","Ninh","Nhạn","Quân","Hiên","Lâm","歌","琴","郎","箫","楼","塔","叶","燕","府","徒","豪"]
    return f"{random.choice(first)} {random.choice(mid)} {random.choice(last)}"

def birth():
    year = random.randint(1995, 2004)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{day:02d}/{month:02d}/{year}"

def matkhau(length=15):
    chars = string.ascii_letters + string.digits + "!@#"
    return ''.join(random.choice(chars) for _ in range(length))

def ten_mail():
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(8))

def mail_ao():
    domains = [
        "gmail.com",
        "outlook.com",
        "hotmail.com",
        "outlook.com.vn",
    ]
    domain = random.choice(domains)
    return f"{ten_mail()}@{domain}"

def create_session_with_retry():
    """Tạo session với proxy"""
    try:
        session = requests.Session()
        
        # Lấy proxy
        proxy_str = get_proxy_for_account()
        if proxy_str:
            session.proxies = {'http': proxy_str, 'https': proxy_str}
            print(f"{get_time_tag()} 🌐 Đang dùng proxy")
        
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
            if response.status_code in [200, 302]:
                print(f"{get_time_tag()} ✅ Session OK")
            else:
                print(f"{get_time_tag()} ⚠️ Session status: {response.status_code}")
        except Exception as e:
            print(f"{get_time_tag()} ⚠️ Session init: {str(e)[:50]}")
        
        return session
        
    except Exception as e:
        print(f"{get_time_tag()} ❌ Lỗi tạo session: {e}")
        return None

# ================= MOBILE FACEBOOK REGISTRATION (UPDATED FIX) =================
def mobile_facebook_registration(session, fullname, email, password, birthday):
    """Đăng ký Facebook qua mobile site - Phương pháp mới tìm form"""
    try:
        print(f"{get_time_tag()} [1/3] Đang lấy trang đăng ký mobile...")
        
        # URL ĐĂNG KÝ MỚI - TRỰC TIẾP TỚI TRANG TẠO TÀI KHOẢN
        mobile_urls = [
            "https://mbasic.facebook.com/reg/",
            "https://m.facebook.com/reg/",
            "https://mbasic.facebook.com/r.php?next=https%3A%2F%2Fmbasic.facebook.com%2F",
            "https://m.facebook.com/r.php",
            "https://mbasic.facebook.com/reg/?cid=103",
            "https://m.facebook.com/reg/?cid=103"
        ]
        
        response = None
        html_content = ""
        
        for url in mobile_urls:
            try:
                print(f"{get_time_tag()}     Thử URL: {url}")
                time.sleep(random.uniform(1, 2))
                
                # Header mobile mới nhất
                mobile_headers = {
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                }
                session.headers.update(mobile_headers)
                
                response = session.get(url, timeout=25, allow_redirects=True)
                
                if response.status_code == 200:
                    html_content = response.text
                    print(f"{get_time_tag()}     [✅] Truy cập thành công: {len(html_content)} chars")
                    
                    # KIỂM TRA CÓ PHẢI TRANG ĐĂNG KÝ
                    content_lower = html_content.lower()
                    is_reg_page = any(keyword in content_lower for keyword in [
                        'sign up', 'create account', 'tạo tài khoản', 
                        'first name', 'last name', 'email', 'password',
                        'birthday', 'giới tính', 'gender'
                    ])
                    
                    if is_reg_page:
                        print(f"{get_time_tag()}     [✅] Đây là trang đăng ký")
                        break
                    else:
                        print(f"{get_time_tag()}     [⚠️] Không phải trang đăng ký, kiểm tra nhanh...")
                        
                        # Debug: Lưu HTML để phân tích
                        debug_save_html(f"debug_mobile_{len(html_content)}.html", html_content)
                        
                else:
                    print(f"{get_time_tag()}     [❌] Status: {response.status_code}")
                    
            except Exception as e:
                print(f"{get_time_tag()}     [❌] Lỗi với URL {url}: {str(e)[:50]}")
                continue
        
        if not response or response.status_code != 200:
            return False, f"Không thể truy cập trang mobile"
        
        # PHÂN TÍCH HTML - PHƯƠNG PHÁP MỚI
        print(f"{get_time_tag()}     Phân tích HTML...")
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # PHƯƠNG PHÁP 1: TÌM FORM BẰNG ID HOẶC CLASS ĐẶC BIỆT
        form = None
        
        # Các selector có thể có của form đăng ký mobile
        possible_selectors = [
            "form[action*='/reg/']",
            "form[action*='/r.php']",
            "form[method='post']",
            "form",
            "#reg_form",
            ".registration_form",
            "#signup_form",
            "form#reg"
        ]
        
        for selector in possible_selectors:
            try:
                found_form = soup.select_one(selector)
                if found_form:
                    form = found_form
                    print(f"{get_time_tag()}     [✅] Tìm thấy form bằng selector: {selector}")
                    break
            except:
                continue
        
        # PHƯƠNG PHÁP 2: TÌM FORM CÓ INPUT ĐẶC BIỆT
        if not form:
            print(f"{get_time_tag()}     [🔍] Tìm form bằng input đặc biệt...")
            
            # Tìm tất cả form
            all_forms = soup.find_all('form')
            print(f"{get_time_tag()}     Tìm thấy {len(all_forms)} form trong trang")
            
            for f in all_forms:
                # Kiểm tra form có input đăng ký không
                inputs = f.find_all('input')
                textareas = f.find_all('textarea')
                selects = f.find_all('select')
                
                has_reg_field = False
                field_names = []
                
                for inp in inputs:
                    name = inp.get('name', '').lower()
                    field_type = inp.get('type', '').lower()
                    
                    if any(keyword in name for keyword in ['first', 'last', 'email', 'pass', 'birth', 'sex', 'gender']):
                        has_reg_field = True
                        field_names.append(name)
                    elif field_type in ['text', 'email', 'password']:
                        has_reg_field = True
                
                if has_reg_field:
                    form = f
                    print(f"{get_time_tag()}     [✅] Tìm thấy form có fields: {field_names}")
                    break
        
        # PHƯƠNG PHÁP 3: TÌM FORM GẦN NỘI DUNG "SIGN UP"
        if not form:
            print(f"{get_time_tag()}     [🔍] Tìm form gần text 'Sign Up'...")
            
            # Tìm text Sign Up
            signup_texts = soup.find_all(string=lambda text: text and 'sign' in text.lower() and 'up' in text.lower())
            
            for signup_text in signup_texts:
                # Tìm form gần nhất
                parent_form = signup_text.find_parent('form')
                if parent_form:
                    form = parent_form
                    print(f"{get_time_tag()}     [✅] Tìm thấy form gần 'Sign Up'")
                    break
        
        # PHƯƠNG PHÁP 4: LẤY FORM ĐẦU TIÊN CÓ METHOD POST
        if not form:
            print(f"{get_time_tag()}     [🔍] Lấy form POST đầu tiên...")
            for f in soup.find_all('form'):
                if f.get('method', '').lower() == 'post':
                    form = f
                    print(f"{get_time_tag()}     [✅] Lấy form POST đầu tiên")
                    break
        
        # PHƯƠNG PHÁP 5: LẤY FORM ĐẦU TIÊN
        if not form and soup.find_all('form'):
            form = soup.find_all('form')[0]
            print(f"{get_time_tag()}     [⚠️] Lấy form đầu tiên (có thể không đúng)")
        
        if not form:
            # Debug: In ra tất cả form để phân tích
            all_forms = soup.find_all('form')
            print(f"{get_time_tag()}     [DEBUG] Tất cả form tìm thấy: {len(all_forms)}")
            for i, f in enumerate(all_forms[:3]):
                print(f"{get_time_tag()}     Form {i}: {str(f)[:200]}...")
            
            return False, "Không tìm thấy form đăng ký trên mobile"
        
        print(f"{get_time_tag()}     [✅] Đã tìm thấy form mobile")
        
        # THU THẬP FIELD - PHƯƠNG PHÁP THÔNG MINH
        form_data = {}
        
        # Lấy tất cả input, select, textarea
        all_inputs = form.find_all(['input', 'select', 'textarea'])
        
        print(f"{get_time_tag()}     [🔍] Đang phân tích {len(all_inputs)} fields...")
        
        for element in all_inputs:
            element_name = element.get('name')
            element_type = element.get('type', '').lower()
            element_tag = element.name
            
            if not element_name:
                continue
            
            # Giá trị mặc định
            default_value = element.get('value', '')
            
            # Xử lý theo từng loại
            if element_tag == 'input':
                if element_type in ['hidden', 'submit', 'button']:
                    form_data[element_name] = default_value
                elif element_type in ['text', 'email', 'password']:
                    form_data[element_name] = ''  # Để trống, sẽ điền sau
                elif element_type == 'radio':
                    if element.get('checked'):
                        form_data[element_name] = element.get('value', '')
                else:
                    form_data[element_name] = default_value
            
            elif element_tag == 'select':
                # Lấy option đầu tiên
                first_option = element.find('option')
                if first_option:
                    form_data[element_name] = first_option.get('value', '')
                else:
                    form_data[element_name] = ''
            
            elif element_tag == 'textarea':
                form_data[element_name] = ''
        
        # ĐIỀN THÔNG TIN ĐĂNG KÝ THÔNG MINH
        parts = fullname.split()
        firstname = parts[0]
        lastname = " ".join(parts[1:]) if len(parts) > 1 else firstname
        day, month, year = birthday.split("/")
        
        print(f"{get_time_tag()}     [📝] Điền thông tin: {firstname} {lastname}, {email}")
        
        # TÌM VÀ ĐIỀN FIELD TỰ ĐỘNG
        for field_name in form_data.keys():
            field_lower = field_name.lower()
            
            # Tên
            if any(keyword in field_lower for keyword in ['first', 'given', 'ten', 'ho']):
                if 'last' not in field_lower:  # Tránh nhầm với lastname
                    form_data[field_name] = firstname
            
            elif any(keyword in field_lower for keyword in ['last', 'family', 'dem', 'lot']):
                form_data[field_name] = lastname
            
            # Email
            elif any(keyword in field_lower for keyword in ['email', 'mail', 'e-mail']):
                form_data[field_name] = email
                # Tìm field xác nhận email
                for confirm_field in form_data.keys():
                    if confirm_field != field_name and 'confirm' in confirm_field.lower() and 'email' in confirm_field.lower():
                        form_data[confirm_field] = email
            
            # Mật khẩu
            elif any(keyword in field_lower for keyword in ['pass', 'pwd', 'matkhau']):
                form_data[field_name] = password
            
            # Ngày sinh
            elif 'day' in field_lower or 'ngay' in field_lower:
                form_data[field_name] = day
            elif 'month' in field_lower or 'thang' in field_lower:
                form_data[field_name] = month
            elif 'year' in field_lower or 'nam' in field_lower:
                form_data[field_name] = year
            
            # Giới tính
            elif any(keyword in field_lower for keyword in ['sex', 'gender', 'gioitinh']):
                if 'female' in field_lower or 'nu' in field_lower or '1' in field_lower:
                    form_data[field_name] = '1'  # Nữ
                elif 'male' in field_lower or 'nam' in field_lower or '2' in field_lower:
                    form_data[field_name] = '2'  # Nam
                else:
                    form_data[field_name] = str(random.choice([1, 2]))
        
        # XỬ LÝ ACTION URL
        action = form.get('action', '')
        base_url = response.url
        
        if action.startswith('http'):
            submit_url = action
        elif action.startswith('/'):
            parsed_base = urlparse(base_url)
            domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
            submit_url = domain + action
        elif action:
            submit_url = urljoin(base_url, action)
        else:
            submit_url = base_url
        
        print(f"{get_time_tag()} [2/3] Đang submit form mobile...")
        time.sleep(random.uniform(2, 3))
        
        # HEADERS CHO SUBMIT
        submit_headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': parsed_base.scheme + '://' + parsed_base.netloc if parsed_base.netloc else 'https://mbasic.facebook.com',
            'Referer': response.url,
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # GỬI REQUEST
        print(f"{get_time_tag()}     Submitting to: {submit_url}")
        print(f"{get_time_tag()}     Data fields: {len(form_data)}")
        
        submit_response = session.post(
            submit_url,
            data=form_data,
            timeout=30,
            allow_redirects=True,
            headers=submit_headers
        )
        
        print(f"{get_time_tag()} [3/3] Kiểm tra kết quả mobile...")
        
        # DEBUG: Lưu response
        if RAILWAY_MODE:
            debug_save_html("debug_mobile_response.html", submit_response.text[:3000])
        
        # KIỂM TRA KẾT QUẢ
        # 1. Kiểm tra cookie
        if 'c_user' in session.cookies:
            uid = session.cookies.get('c_user')
            print(f"{get_time_tag()}     [✅] Found c_user cookie: {uid}")
            return True, f"Thành công (Mobile - UID: {uid})"
        
        # 2. Kiểm tra trong HTML có thông tin thành công
        response_text = submit_response.text.lower()
        response_url = submit_response.url.lower()
        
        # Các dấu hiệu thành công
        success_indicators = [
            'welcome', 'home', 'news feed', 'bảng feed',
            'profile', 'trang cá nhân', 'timeline',
            'confirmed', 'xác nhận', 'check your email',
            'continue', 'tiếp tục'
        ]
        
        for indicator in success_indicators:
            if indicator in response_text or indicator in response_url:
                # Cố gắng tìm UID trong HTML
                uid_patterns = [
                    r'c_user=(\d+)',
                    r'id=(\d+)',
                    r'uid=(\d+)',
                    r'profile\.php\?id=(\d+)'
                ]
                
                for pattern in uid_patterns:
                    match = re.search(pattern, response_text)
                    if match:
                        uid = match.group(1)
                        return True, f"Thành công (Mobile - UID: {uid})"
                
                return True, "Thành công (Mobile - cần xác nhận)"
        
        # 3. Kiểm tra checkpoint
        if 'checkpoint' in response_url or 'security' in response_url:
            return True, "Checkpoint (Mobile - cần xác minh)"
        
        # 4. Kiểm tra lỗi
        error_patterns = [
            r'class="[^"]*error[^"]*"[^>]*>([^<]+)',
            r'id="error"[^>]*>([^<]+)',
            r'>([^<]*error[^<]*)<',
            r'alert[^>]*>([^<]+)'
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, submit_response.text, re.IGNORECASE)
            if matches:
                error_msg = matches[0][:100]
                return False, f"Lỗi mobile: {error_msg}"
        
        # 5. Kiểm tra nếu bị chặn
        block_keywords = ['blocked', 'temporarily', 'suspended', 'banned', 'chặn', 'khóa']
        for keyword in block_keywords:
            if keyword in response_text:
                return False, f"Facebook chặn: {keyword}"
        
        # Mặc định
        print(f"{get_time_tag()}     [ℹ️] Response URL: {submit_response.url}")
        print(f"{get_time_tag()}     [ℹ️] Response length: {len(submit_response.text)} chars")
        
        return False, "Không xác định (Mobile - không có cookie, không có lỗi rõ ràng)"
            
    except Exception as e:
        error_msg = str(e)
        print(f"{get_time_tag()} ❌ Lỗi mobile registration: {error_msg}")
        import traceback
        traceback.print_exc()
        return False, f"Lỗi mobile: {error_msg[:100]}"

# ================= WEB FACEBOOK REGISTRATION =================
def simple_facebook_registration(session, fullname, email, password, birthday):
    """Đăng ký Facebook web - Fallback method"""
    try:
        print(f"{get_time_tag()} [1/3] Đang thử đăng ký web...")
        
        # Thử mobile trước (đáng tin cậy hơn)
        print(f"{get_time_tag()}     [🔄] Chuyển sang mobile method...")
        return mobile_facebook_registration(session, fullname, email, password, birthday)
            
    except Exception as e:
        print(f"{get_time_tag()} ❌ Web error: {str(e)[:100]}")
        return False, f"Lỗi web: {str(e)[:100]}"

def check_live_status(session):
    """Kiểm tra account có live không"""
    try:
        cookies_dict = {}
        for cookie in session.cookies:
            cookies_dict[cookie.name] = cookie.value
        
        # Kiểm tra với nhiều URL
        check_urls = [
            "https://www.facebook.com/me",
            "https://m.facebook.com/me",
            "https://mbasic.facebook.com/me"
        ]
        
        for url in check_urls:
            try:
                response = session.get(url, timeout=10, allow_redirects=True)
                if 'checkpoint' in response.url.lower():
                    return False, "Checkpoint", None, None
                
                if 'c_user' in cookies_dict:
                    uid = cookies_dict['c_user']
                    if uid and len(uid) > 5:
                        return True, "LIVE", f"https://www.facebook.com/profile.php?id={uid}", uid
            except:
                continue
        
        if 'c_user' in cookies_dict:
            uid = cookies_dict['c_user']
            return True, "LIVE (cookie only)", f"https://www.facebook.com/profile.php?id={uid}", uid
        
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
        time.sleep(random.uniform(1.0, 2.0))
        
        # Tạo thông tin account
        fullname = ten_gha()
        email = mail_ao()
        password = matkhau()
        birthday = birth()
        
        tg_edit(chat_id, msg_id, 
            f"{get_time_tag()} 📝 Thông tin acc:\n"
            f"• Tên: {fullname}\n"
            f"• Email: {email}\n"
            f"• Pass: {password}\n"
            f"• Sinh nhật: {birthday}"
        )
        time.sleep(2)

        # Tạo session
        tg_edit(chat_id, msg_id, f"{get_time_tag()} 🌐 Đang tạo session...")
        session = create_session_with_retry()
        if not session:
            tg_edit(chat_id, msg_id, f"{get_time_tag()} ❌ Không tạo được session")
            RUNNING_CHAT.remove(chat_id)
            return
        
        # LUÔN DÙNG MOBILE METHOD (đáng tin cậy hơn)
        tg_edit(chat_id, msg_id, f"{get_time_tag()} 📱 Đang đăng ký qua mobile...")
        success, message = mobile_facebook_registration(session, fullname, email, password, birthday)
        
        if not success:
            tg_edit(chat_id, msg_id, f"{get_time_tag()} ❌ Đăng ký thất bại: {message}")
            
            # Thử lần 2 với delay
            tg_edit(chat_id, msg_id, f"{get_time_tag()} 🔄 Thử lần 2...")
            time.sleep(5)
            
            # Tạo session mới
            session.close()
            session = create_session_with_retry()
            if session:
                success, message = mobile_facebook_registration(session, fullname, email, password, birthday)
            
            if not success:
                # Kiểm tra lần cuối
                time.sleep(3)
                is_live, live_msg, profile_url, uid = check_live_status(session)
                
                if is_live:
                    tg_edit(chat_id, msg_id, f"{get_time_tag()} ⚠️ Lỗi reg nhưng acc vẫn LIVE!")
                else:
                    if session:
                        session.close()
                    RUNNING_CHAT.remove(chat_id)
                    return
        else:
            # Xử lý kết quả
            time.sleep(5)
            is_live, live_msg, profile_url, uid = check_live_status(session)
            
            if is_live:
                tg_edit(chat_id, msg_id, f"{get_time_tag()} 🎉 ACC LIVE")
            else:
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
        
        # Lưu account nếu có UID thực
        if uid and uid != '0':
            save_account_to_file(fullname, email, password, profile_url, cookies_dict)
            tg_send(chat_id, f"✅ <b><i>{uid}</i></b>", reply_to_message_id=message_id)

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
        "<code><i>Thông tin acc bên dưới:</i></code>      ᓚ₍⑅^..^₎ฅ\n"
        "╭────-_Ი𐑼_-─────────⭓\n"
        f"│ 👤 Tên: ⤷ ゛<code>{html_escape(d['name'])}</code>  ˎˊ˗\n"
        f"│ 📧 Email: <code>{html_escape(d['email'])}</code>\n"
        f"│ 🔑 Mật khẩu: <tg-spoiler><code>{(d['password'])}</code></tg-spoiler>\n"
        f"│ 📌 Trạng thái: <b>🟢Live!</b>      ୨ৎ⊹ˑ ֗\n"
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
        f"<b><i>Bot phục vụ bạn: @nuxw_bot</i></b>\n\n"
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
