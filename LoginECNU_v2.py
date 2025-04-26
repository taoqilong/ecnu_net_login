'''
Author       : Renjie Ji & Qilong Tao
School       : East Chine Normal University
E-mail       : renjie.ji@foxmail.com
Date         : 2023-07-15 10:17:11
Descripttion : 
version      : 
LastEditors  : Qilong Tao
LastEditTime : 2025-04-25 11:30:00
'''
import requests
import time
import re
import json
from encryption.srun_md5 import *
from encryption.srun_sha1 import *
from encryption.srun_base64 import *
from encryption.srun_xencode import *


# --- Configuration ---
USERNAME = "5126XXXXXXX" # Your username
PASSWORD = "XXXXXXXXXXX"   # Your password
AC_ID = '1'


# -------------------

# --- Globals ---
# It's generally better practice to pass variables as arguments
# instead of using globals, but we'll keep them for now
# to minimize changes to the original structure.
ip = ""
token = ""
i = ""
hmd5 = ""
chksum = ""
# ---------------

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36'
}
init_url = "https://login.ecnu.edu.cn/srun_portal_pc?ac_id=1&theme=pro"
get_challenge_api = "https://login.ecnu.edu.cn/cgi-bin/get_challenge"
srun_portal_api = "https://login.ecnu.edu.cn/cgi-bin/srun_portal"
n = '200'
type = '1'
# ac_id = '1' # Defined in Configuration
enc = "srun_bx1"

def extract_json_from_callback(text):
    """Extracts JSON string from jQuery callback."""
    match = re.search(r'jQuery\d+_\d+\((.*)\)', text)
    if match:
        return match.group(1)
    return None

def get_chksum():
    # Uses global variables: token, username, hmd5, ac_id, ip, n, type, i
    chkstr = token + USERNAME
    chkstr += token + hmd5
    chkstr += token + AC_ID
    chkstr += token + ip
    chkstr += token + n
    chkstr += token + type
    chkstr += token + i
    return get_sha1(chkstr) # Directly call get_sha1

def get_info():
    # Uses global variables: username, password, ip, ac_id, enc
    info_temp = {
        "username": USERNAME,
        "password": PASSWORD,
        "ip": ip,
        "acid": AC_ID,
        "enc_ver": enc
    }
    # Use json.dumps for proper JSON formatting, safer than string manipulation
    return json.dumps(info_temp, separators=(',', ':'))

def init_getip():
    global ip
    print("[INFO] Initializing and fetching IP address...")
    try:
        init_res = requests.get(init_url, headers=header, timeout=10)
        init_res.raise_for_status() # Check for HTTP errors
        # More robust IP extraction
        ip_match = re.search(r'ip\s*:\s*"([^"]+)"', init_res.text)
        if ip_match:
            ip = ip_match.group(1)
            print(f"[ OK ] Detected IP: {ip}")
        else:
            print("[ERROR] Could not extract IP address from initial page.")
            # Consider exiting or retrying
            exit(1) # Exit if IP is crucial
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to connect to {init_url}: {e}")
        exit(1)


def get_token():
    global token
    print("[INFO] Requesting challenge token...")
    if not ip:
        print("[ERROR] IP address not available. Cannot request token.")
        exit(1)

    get_challenge_params = {
        "callback": "jQuery1124005186017536424603_" + str(int(time.time() * 1000)),
        "username": USERNAME,
        "ip": ip,
        "_": int(time.time() * 1000),
    }
    try:
        get_challenge_res = requests.get(get_challenge_api, params=get_challenge_params, headers=header, timeout=10)
        get_challenge_res.raise_for_status()

        json_str = extract_json_from_callback(get_challenge_res.text)
        if not json_str:
            print("[ERROR] Could not extract JSON from challenge response.")
            print(f"       Raw response: {get_challenge_res.text[:200]}...") # Print partial raw response
            exit(1)

        try:
            data = json.loads(json_str)
            if data.get("res") == "ok" and "challenge" in data:
                token = data["challenge"]
                print(f"[ OK ] Obtained challenge token: {token[:10]}...") # Print partial token
            else:
                error_msg = data.get("error_msg", "Unknown error")
                print(f"[ERROR] Failed to get challenge token: {error_msg}")
                print(f"        Full JSON response: {data}")
                exit(1)
        except json.JSONDecodeError:
            print("[ERROR] Failed to parse JSON from challenge response.")
            print(f"        Extracted string: {json_str}")
            exit(1)

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to connect to {get_challenge_api}: {e}")
        exit(1)


def do_complex_work():
    global i, hmd5, chksum
    print("[INFO] Preparing login credentials...")
    if not token:
        print("[ERROR] Token not available. Cannot prepare credentials.")
        exit(1)

    info_json = get_info()
    # Assuming srun_base64.py has been corrected as per previous instructions
    encoded_info = get_base64(get_xencode(info_json, token))
    i = "{SRBX1}" + encoded_info # Store the final encoded info string globally

    hmd5 = get_md5(PASSWORD, token) # Calculate MD5 hash
    chksum = get_chksum()        # Calculate SHA1 checksum

    print("[ OK ] Credentials prepared.")


def login():
    print("[INFO] Attempting login...")
    if not all([ip, token, i, hmd5, chksum, USERNAME, PASSWORD, AC_ID]): # Added checks for constants too
         print("[ERROR] Missing necessary information for login.")
         exit(1)

    srun_portal_params = {
        'callback': 'jQuery1124005186017536424603_' + str(int(time.time() * 1000)),
        'action': 'login',
        'username': USERNAME,
        'password': '{MD5}' + hmd5,
        'ac_id': AC_ID,
        'ip': ip,
        'chksum': chksum,
        'info': i,
        'n': n,
        'type': type,
        'os': 'windows+10', # Consider making dynamic if needed
        'name': 'windows',
        'double_stack': '0',
        '_': int(time.time() * 1000)
    }

    try:
        srun_portal_res = requests.get(srun_portal_api, params=srun_portal_params, headers=header, timeout=15)
        srun_portal_res.raise_for_status() # Check for HTTP errors (like 4xx or 5xx)

        json_str = extract_json_from_callback(srun_portal_res.text) # Assuming extract_json_from_callback exists
        if not json_str:
            print("[ERROR] Could not extract JSON from login response.")
            print(f"       Raw response: {srun_portal_res.text[:200]}...")
            # Consider exiting or handling based on needs
            return # Stop further processing in this function

        try:
            data = json.loads(json_str)
            # Check for successful login first
            if data.get("res") == "ok" and data.get("suc_msg") == "login_ok":
                success_msg = data.get("ploy_msg", "Login successful!")
                print(f"[SUCCESS] {success_msg}")
                print(f"          Username: {data.get('username', 'N/A')}")
                print(f"          Client IP: {data.get('client_ip', 'N/A')}")
            # Check for specific known error conditions
            elif data.get("suc_msg") == "ip_already_online_error":
                 print(f"[ FAILED] Login failed: This IP address ({data.get('online_ip', ip)}) is already online.")
                 print(f"          Username associated: {data.get('username', 'N/A')}")
            elif data.get("ecode") == "E2901" or data.get("error") == "login_error":
                 # Prioritize specific error message if available
                 error_detail = data.get("error_msg", "Incorrect username or password.")
                 # Optional: Simplify common LDAP error message
                 if "LDAP password verification error" in error_detail:
                     error_detail = "Incorrect username or password (Authentication failed)."
                 print(f"[ FAILED] Login failed: {error_detail}")
            # Fallback for other errors indicated by the server
            else:
                # Try to find the most descriptive error message available
                error_msg = data.get("error_msg") or data.get("ploy_msg") or data.get("error") or "Unknown login error"
                print(f"[ FAILED] Login failed: {error_msg}")
                # Optionally print full details for unknown errors for debugging
                print(f"          Response details: {data}")

        except json.JSONDecodeError:
            print("[ERROR] Failed to parse JSON from login response.")
            print(f"        Extracted string: {json_str}")
            print(f"        Raw response: {srun_portal_res.text[:200]}...")

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Login request failed: {e}")


if __name__ == '__main__':
    print("=" * 30)
    print(" ECNU Network Login Script")
    print("=" * 30)

    init_getip()
    get_token()
    do_complex_work()
    login()
