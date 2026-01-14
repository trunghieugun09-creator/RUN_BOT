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
import gzip
import sys
import threading
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote
from pystyle import Colors, Colorate

keep_alive.keep_alive()

BOT_TOKEN = "8251269112:AAHHNsg-qLeChDAVodfchwegFhFnGPTWsMU"
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
UID_FILE = "tele_uid.txt"
OFFSET = 0
REG_DELAY = 10
LAST_REG_TIME = {}
RUNNING_CHAT = set()

MANDATORY_GROUP_ID = -1003444341292
MANDATORY_GROUP_TITLE = "𝗣𝗮𝗿𝗮𝗴𝗼𝗻 𝗦𝗲𝗹 ᵎ!ᵎ 𝐟𝐫𝐬 𝐜𝐨𝐝𝐞"

proxy_reg = [
    ""
]

user_agent_reg = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.116 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.58 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.137 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.92 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.127 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.142 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.118 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
]

window = platform.system().lower().startswith("win")
thu_muc_luu = "accounts_output"
os.makedirs(thu_muc_luu, exist_ok=True)

API_KEY = "apikeysumi"
API_INFO_URL = "https://adidaphat.site/facebook/getinfo"
UID_API_URL = "https://keyherlyswar.x10.mx/Apidocs/getuidfb.php?link="

PRIVATE_ONLY_MSG = (
    "<b>⛔ LƯU Ý TỪ BOT!!!</b>\n"
    "━━━━━━━━━━━━━━━━\n"
    "␥ <b><i>Bot chỉ hoạt động trong Tin nhắn riêng (Private), không hỗ trợ sử dụng trong group!.</i></b>\n"
    "␥ Vui lòng nhắn tin riêng cho bot để tiếp tục sử dụng các tính năng!.\n"
)

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
    time.sleep(delay)
    tg_delete_message(chat_id, sent_msg_id)
    tg_delete_message(chat_id, original_msg_id)

def check_group_membership(user_id):
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
    except:
        return False

def safe_int(n):
    try:
        return int(n)
    except:
        return 0

def format_number(n):
    return format(safe_int(n), ",")

def format_created(time_str):
    try:
        parts = re.split(r'\|\||\s*\|\s*', time_str.strip())
        if len(parts) >= 2:
            d, t = parts[0], parts[1]
            return f"{t} | {d}"
        return time_str.replace("||", " | ")
    except:
        return "Không rõ"
        
def extract_uid_from_input(input_str):
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
    except:
        return None

def get_fb_info(uid):
    try:
        url = f"{API_INFO_URL}?uid={uid}&apikey={API_KEY}"
        r = requests.get(url, timeout=15)
        try:
            res = r.json()
        except:
            return {"error": f"API lỗi: Phản hồi không phải JSON. Code: {r.status_code}"}

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
    except:
        return {"error": "Lỗi hệ thống không xác định"}

def create_caption(res):
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

def parse_proxy(proxy_str):
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
        
    except:
        return proxy_str

def get_proxy_for_account():
    if not proxy_reg:
        return None
        
    proxy_str = random.choice(proxy_reg)
    parsed_proxy = parse_proxy(proxy_str)
    return parsed_proxy

def get_random_user_agent():
    return random.choice(user_agent_reg)

def ten_gha():
    first = ["Bạch","Uyển","Cố","Sở","Trạch","Lam","Thanh","Mặc","Kim","Thiên","Hồng","Kính","Thủy","Kiều","Minh","Nhật","Băng","Hải","Tâm","Phi"]
    mid = ["Vũ","Hạ","Tỉnh","Vân","Khúc","Ảnh","Huyết","Vô","Tuyệt","Mệnh","Ngản","Ngạn","Bi","Lưu","Tĩnh","Lộ","Phong","Tư","Khiết","Vĩ"]
    last = ["Khách","Xuẫn","Nghi","Ning","Nhạn","Quân","Hiên","Lâm","Ca","Cầm","Lang","Tiêu","Lâu","Tháp","Diệp","Yến","Phủ","Đồ","Hào"]
    return f"{random.choice(first)} {random.choice(mid)} {random.choice(last)}"

def birth():
    year = random.randint(1995, 2004)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{day:02d}/{month:02d}/{year}"

def matkhau(length=12):
    fixed_prefix = "tghieux#!"
    random_characters = string.ascii_letters + string.digits
    fixed_suffix = "#@!₫"
    random_part = ''.join(random.choice(random_characters) for _ in range(11))
    return fixed_prefix + random_part + fixed_suffix

def ten_mail():
    chars = string.ascii_lowercase + string.digits
    username = ''.join(random.choice(chars) for _ in range(8))
    return username

def mail_ao():
    username = ten_mail()
    domains = ["hotmail.com", "outlook.de", "outlook.jp"]
    domain = random.choice(domains)
    return f"{username}@{domain}"

def decode_response_content(response):
    try:
        if 'gzip' in response.headers.get('Content-Encoding', ''):
            return gzip.decompress(response.content).decode('utf-8', errors='ignore')
        elif 'br' in response.headers.get('Content-Encoding', ''):
            return response.text
        else:
            return response.content.decode('utf-8', errors='ignore')
    except:
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1258', 'utf-16']
        for encoding in encodings:
            try:
                return response.content.decode(encoding, errors='ignore')
            except:
                continue
        return str(response.content)

def create_session_with_retry(retries=3):
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

        except:
            time.sleep(3)
    
    for attempt in range(retries):
        try:
            session = requests.Session()
            mobile_agents = [
                'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'
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
        except:
            time.sleep(2)
    
    raise Exception("Không thể tạo session")

def extract_form_from_mbasic(soup):
    forms = soup.find_all('form')
    if not forms:
        return None, {}
    
    reg_form = None
    for form in forms:
        form_html = str(form).lower()
        if any(keyword in form_html for keyword in ['register', 'sign up', 'đăng ký', 'tạo tài khoản']):
            reg_form = form
            break
    
    if not reg_form:
        reg_form = forms[0]
    
    fields = {}
    for inp in reg_form.find_all('input'):
        name = inp.get('name')
        value = inp.get('value', '')
        if name:
            fields[name] = value
    
    return reg_form, fields

def register_with_mbasic(session, fullname, email, password, birthday):
    try:
        response = session.get("https://www.facebook.com/reg/", timeout=20)
        
        if response.status_code != 200:
            return False, "HTTP Error", None
        
        content = decode_response_content(response)
        soup = BeautifulSoup(content, 'html.parser')
        form, fields = extract_form_from_mbasic(soup)
        
        if not form:
            return False, "Không tìm thấy form", None

        parts = fullname.split()
        firstname = parts[0]
        lastname = " ".join(parts[1:]) if len(parts) > 1 else parts[0]
        day, month, year = birthday.split("/")

        fields.update({
            'firstname': firstname,
            'lastname': lastname,
            'reg_email__': email,
            'reg_email_confirmation__': email,
            'reg_passwd__': password,
            'birthday_day': day,
            'birthday_month': month,
            'birthday_year': year,
            'sex': str(random.choice([1, 2])),
        })
        
        time.sleep(3)
        
        action = form.get('action', '')
        if action.startswith('/'):
            action_url = 'https://www.facebook.com' + action
        elif action.startswith('http'):
            action_url = action
        else:
            action_url = 'https://www.facebook.com/reg/'
            
        response = session.post(action_url, data=fields, timeout=30, allow_redirects=True)
        content = decode_response_content(response)
        
        time.sleep(2)
        
        cookies_dict = get_account_cookies(session)
        uid = cookies_dict.get('c_user', '0')
        
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in ['confirm', 'xác nhận', 'mã', 'code']):
            return True, "Need email confirmation", uid
            
        elif any(keyword in response.url.lower() for keyword in ['home', 'feed', 'welcome']):
            return True, "Success", uid
            
        elif 'error' in content_lower:
            soup2 = BeautifulSoup(content, 'html.parser')
            error_div = soup2.find('div', class_=re.compile(r'error|alert'))
            if error_div:
                error_msg = error_div.get_text(strip=True)[:100]
                return False, error_msg, uid
            else:
                return False, "Unknown error", uid
        else:
            return False, "Registration failed", uid

    except Exception as e:
        return False, str(e), None

def get_account_cookies(session):
    cookies = {}
    try:
        for cookie in session.cookies:
            cookies[cookie.name] = cookie.value
    except:
        pass
    return cookies

def cookies_to_string(cookies_dict):
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

def get_symbols_from_web(url, source_name):
    symbols = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html_content = response.text
        
        pattern = r'[^\w\s.,!?;:()\[\]{}\-\+\=\'"<>/\\|@#$%^&*`~]+'
        all_matches = re.findall(pattern, html_content)
        
        for match in all_matches:
            match = match.strip()
            if (len(match) >= 1 and len(match) <= 10 and 
                not re.search(r'&[a-z]+;', match) and
                not match.isalnum() and
                not match.isspace()):
                
                if (any(char in match for char in ['ı', 'l', '⊹', 'ᶻ', 'z', '!', '៸', '␥', '✶', '✦', 'ⵢ', '₊', '˚', '.', '₍', 'ᐢ', '₎', '˓', '𓄹', 'ָ', '⸰', '𓂃', '✃', '_', '★', '◟', '𖥻', '๑', '.', 'ૢ', '🗯', 'Ꞌ', 'ꞌ', '✧', 'ּ', 'ִ', 'ֶ', 'ָ', 'ఌ', '⎙']) or
                    re.search(r'[\u2600-\u26FF\u2700-\u27BF\u1F300-\u1F5FF\u1F600-\u1F64F\u00B0-\u00FF\u2E80-\u9FFF]', match)):
                    symbols.append((match, source_name))
        
        return symbols
        
    except:
        return []

def smart_shuffle_with_priority(symbols, count=150, priority_chars=None):
    if not symbols:
        return []
    
    source_groups = {}
    for symbol, source in symbols:
        if source not in source_groups:
            source_groups[source] = []
        source_groups[source].append(symbol)
    selected_symbols = []
    if priority_chars:
        priority_symbols = []
        for symbol, source in symbols:
            if any(p_char in symbol for p_char in priority_chars):
                priority_symbols.append(symbol)
        
        if priority_symbols:
            selected_symbols.extend(random.sample(
                priority_symbols, 
                min(30, len(priority_symbols))
            ))
    
    min_per_source = max(1, (count - len(selected_symbols)) // len(source_groups))
    
    for source, source_symbols in source_groups.items():
        unique_source_symbols = list(set(source_symbols) - set(selected_symbols))
        
        if len(unique_source_symbols) >= min_per_source:
            selected_symbols.extend(random.sample(
                unique_source_symbols, 
                min_per_source
            ))
        else:
            selected_symbols.extend(unique_source_symbols)

    if len(selected_symbols) < count:
        remaining_symbols = [s for s, _ in symbols if s not in selected_symbols]
        if remaining_symbols:
            need = count - len(selected_symbols)
            selected_symbols.extend(random.sample(
                remaining_symbols, 
                min(need, len(remaining_symbols))
            ))
    
    if len(selected_symbols) > count:
        selected_symbols = selected_symbols[:count]
    elif len(selected_symbols) < count:
        while len(selected_symbols) < count:
            selected_symbols.append(random.choice([s for s, _ in symbols]))
    
    random.shuffle(selected_symbols)
    
    return selected_symbols

def get_aesthetic_symbols(count=150):
    all_symbols = []
    websites = [
        ("https://emojidb.org/aesthetic-symbols-for-bio-emojis", "test"),
        ("https://emojidb.org/aesthetic-symbols-emojis", "db"),
        ("https://emojicombos.com/aesthetic-symbols", "emojicombos"),
        ("https://emojidb.org/bio-emojis", "tu"),
        ("https://emojidb.org/aesthetic-text-emojis", "text")
    ]
    
    for url, name in websites:
        symbols = get_symbols_from_web(url, name)
        all_symbols.extend(symbols)
    
    priority_examples = [
        'ı', 'l', '⊹', 'ᶻ', 'z', '!', '៸', '␥', '✶', '˚', '.', '✦', 'ⵢ', '₊', 
        '₍', 'ᐢ', '₎', '˓', '𓄹', 'ָ', '⸰', '𓂃', '✃', '_', '★', '◟', '𖥻', 
        '๑', '‧', 'ૢ', '🗯', 'Ꞌ', 'ꞌ', '✧', 'ּ', 'ִ', 'ֶ', 'ָ', 'ఌ', '⎙', 
        '⟡', '⭓', '୨ৎ'
    ]
    for char in priority_examples:
        all_symbols.append((char, "priority"))
    
    priority_chars = priority_examples
    
    selected_symbols = smart_shuffle_with_priority(
        all_symbols, 
        count=count,
        priority_chars=priority_chars
    )
    
    line = ' '.join(selected_symbols)
    
    return line

def reg_single_account(chat_id, user_id, user_name, message_id):
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

    msg_id = tg_send(chat_id, f"{get_time_tag()} 🚀 Đang reg...", reply_to_message_id=message_id) 
    if not msg_id:
        RUNNING_CHAT.remove(chat_id)
        return

    session = None
    try:
        tg_edit(chat_id, msg_id, f"{get_time_tag()} 📝 Đang tạo thông tin...")
        
        fullname = ten_gha()
        email = mail_ao()
        password = matkhau()
        birthday = birth()

        tg_edit(chat_id, msg_id, f"{get_time_tag()} 🌐 Đang kết nối...")
        session = create_session_with_retry()

        tg_edit(chat_id, msg_id, f"{get_time_tag()} 🗞️ Đang gửi form...")
        success, message, uid = register_with_mbasic(session, fullname, email, password, birthday)

        cookies_dict = get_account_cookies(session)
        cookie_str = cookies_to_string(cookies_dict)
        
        profile_url = f"https://www.facebook.com/profile.php?id={uid}" if uid and uid != '0' else None
        
        if success:
            if uid and uid != '0':
                status = f"✅ Thành công "
                is_live = True
            else:
                status = f"⚠️ {message} "
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
            "is_live": is_live
        }

        tg_edit(chat_id, msg_id, format_result(result, success))
        
        if uid and uid != '0':
            save_account_to_file(fullname, email, password, profile_url, cookies_dict)

    except Exception as e:
        error_result = {
            "user_name": user_name,
            "status": f"❌ Lỗi hệ thống: {str(e)[:50]}"
        }
        tg_edit(chat_id, msg_id, format_result(error_result, False))

    finally:
        RUNNING_CHAT.remove(chat_id)
        if session:
            try:
                session.close()
            except:
                pass

def save_account_to_file(fullname, email, password, profile_url, cookies_dict):
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
            
    except:
        pass

def format_result(d, success):
    now = datetime.datetime.now().strftime("%H:%M:%S | %d/%m/%y")
    user_name = html_escape(d.get('user_name', 'Unknown User'))

    if not success:
        return f"👤 Người sử dụng bot: <b>{user_name}</b>\n❌ Reg thất bại\n⏰ {now}\nLỗi: {html_escape(d.get('status', 'Không xác định'))}"

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

def handle_start(chat_id, user_name, message_id):
    text = (
        f"<b><i>🎉 Chào mừng {html_escape(user_name)} đã đến!👋</i></b>\n"
        f"<b><i>💌 Hãy sử dụng lệnh /help để xem hướng dẫn!</i></b>"
    )
    tg_send(chat_id, text, reply_to_message_id=message_id)

def handle_help(chat_id, message_id):
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
    text = format_myinfo(chat_id, user_info)
    sent_msg_id = tg_send(chat_id, text, reply_to_message_id=message_id)
    
    if sent_msg_id:
        threading.Thread(target=self_destruct_message, args=(chat_id, sent_msg_id, message_id, 60), daemon=True).start()

def handle_symbols(chat_id, message_id):
    processing_msg = tg_send(chat_id, "⏱️ Đang lấy...", reply_to_message_id=message_id)
    if not processing_msg:
        return
        
    try:
        symbols_line = get_aesthetic_symbols(count=150)
        
        if symbols_line:
            result_text = (
                "✅ <b>THÀNH CÔNG, BÊN DƯỚI LÀ SYMBOLS ĐÃ LẤY!:</b>\n"
                f"<code>{html_escape(symbols_line)}</code>\n\n"
                "<b><i>⚠️ Tin nhắn sẽ tự xoá sau 1 phút!</i></b>"
            )
        else:
             result_text = "❌ <b>LỖI</b>: Không thể cào symbols hoặc API cào lỗi."

        tg_edit(chat_id, processing_msg, result_text)
        threading.Thread(target=self_destruct_message, args=(chat_id, processing_msg, message_id, 60), daemon=True).start()

    except Exception as e:
        error_text = f"❌ Lỗi hệ thống khi lấy symbols: {str(e)[:100]}"
        tg_edit(chat_id, processing_msg, error_text)

def handle_checkif(chat_id, user_input, message_id, user_name):
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

def get_bot_username():
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
"<b>␥ 🫧 Để sử dụng đầy đủ các tính năng của bot, bạn cần tham gia group bắt buộc bên dưới:</b>\n"
"\n"
"␥ 「 👥 GROUP YÊU CẦU 」\n"
"𖥻𓂃 𝗣𝗮𝗿𝗮𝗴𝗼𝗻 𝗦𝗲𝗹 ᵎ!ᵎ 𝐟𝐫𝐬 𝐜𝐨𝐝𝐞\n"
"\n"
"␥ 「 🔗 LINK GROUP 」\n"
"𖥻𓂃 https://t.me/ParaGontoolfree\n"
"\n"
"━━━━━━━━━━━━━━━━\n"
"␥ Sau khi tham gia group,\n"
"vui lòng quay lại và sử dụng bot\n"
                )
                
                sent_msg_id = tg_send(chat_id, require_join_msg, reply_to_message_id=message_id)
                if sent_msg_id:
                     threading.Thread(target=self_destruct_message, args=(chat_id, sent_msg_id, message_id, 60), daemon=True).start()
                         
                continue

        if chat_id < 0 and text.startswith('/'):
            tg_send(chat_id, PRIVATE_ONLY_MSG, reply_to_message_id=message_id)
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
