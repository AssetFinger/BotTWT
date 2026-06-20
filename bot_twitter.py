import os
import json
import time
import random
from playwright.sync_api import sync_playwright

# File penyimpanan data
COOKIE_DIR = "cookies"
LINKS_FILE = "saved_links.json"

if not os.path.exists(COOKIE_DIR):
    os.makedirs(COOKIE_DIR)

def load_saved_links():
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_link(link):
    links = load_saved_links()
    if link not in links:
        links.append(link)
        with open(LINKS_FILE, 'w') as f:
            json.dump(links, f, indent=4)

def get_logged_in_accounts():
    return [f for f in os.listdir(COOKIE_DIR) if f.endswith('.json')]

# --- FUNGSI CLEAN COOKIES ---
def clean_cookies(cookies_list):
    """Membersihkan properti sameSite null/invalid & memformat struktur sesuai standar Playwright"""
    cleaned = []
    for c in cookies_list:
        s_site = c.get("sameSite")
        if s_site is None or str(s_site).lower() not in ["strict", "lax", "none"]:
            s_site = "None"
        else:
            s_site = str(s_site).capitalize()

        new_cookie = {
            "name": c.get("name"),
            "value": c.get("value"),
            "domain": c.get("domain"),
            "path": c.get("path", "/"),
            "secure": c.get("secure", True),
            "sameSite": s_site
        }
        
        if "expirationDate" in c and isinstance(c["expirationDate"], (int, float)):
            new_cookie["expires"] = float(c["expirationDate"])

        cleaned.append(new_cookie)
    return cleaned

# --- FUNGSI CEK STATUS AKUN ---
def check_account_status(page, acc_name):
    try:
        page.goto("https://x.com/home", wait_until="domcontentloaded")
        time.sleep(4)
        
        url_sekarang = page.url
        
        if "login" in url_sekarang or "i/flow/login" in url_sekarang:
            print(f"❌ {acc_name}: COOKIE EXPIRED / LOGOUT (Silakan perbarui cookie)")
            return "expired"
            
        body_text = page.locator("body").inner_text()
        if "suspended" in body_text.lower() or "ditangguhkan" in body_text.lower():
            print(f"❌ {acc_name}: ACCOUNT BANNED / SUSPENDED")
            return "banned"
        if "locked" in body_text.lower() or "terkunci" in body_text.lower():
            print(f"⚠ {acc_name}: ACCOUNT LOCKED / NEED VERIFICATION")
            return "locked"
            
        if page.locator('a[data-testid="SideNav_NewTweet_Button"]').is_visible() or "home" in url_sekarang:
            print(f"✅ {acc_name}: AKTIF & AMAN")
            return "active"
            
        print(f"❓ {acc_name}: Status tidak diketahui (Kemungkinan aman, cek manual jika ragu)")
        return "unknown"
        
    except Exception as e:
        print(f"❌ {acc_name}: Gagal cek status ({str(e)})")
        return "error"

# --- FITUR 1: INPUT COOKIE ---
def input_cookie():
    print("\n=== 1. MASUKKAN COOKIE BARU ===")
    account_name = input("Masukkan nama akun (contoh: akun1): ").strip()
    print("Masukkan/Paste isi cookie JSON di bawah ini (Tekan Enter, lalu F6 atau Ctrl+Z, lalu Enter):")
    
    lines = []
    while True:
        try:
            line = input()
            lines.append(line)
        except EOFError:
            break
    
    cookie_str = "".join(lines).strip()
    try:
        cookie_data = json.loads(cookie_str)
        if not isinstance(cookie_data, list):
            cookie_data = [cookie_data]
            
        file_path = os.path.join(COOKIE_DIR, f"{account_name}.json")
        with open(file_path, 'w') as f:
            json.dump(cookie_data, f, indent=4)
        print(f"✅ Cookie untuk akun '{account_name}' berhasil disimpan!")
    except json.JSONDecodeError:
        print("❌ Gagal: Format JSON tidak valid.")

# --- FITUR 2: LIST AKUN ---
def list_accounts():
    print("\n=== 2. DAFTAR AKUN TERLOGIN ===")
    accounts = get_logged_in_accounts()
    if not accounts:
        print("Belum ada akun di folder 'cookies'.")
        return []
    
    for idx, acc in enumerate(accounts, 1):
        print(f"[{idx}] {acc.replace('.json', '')}")
    return accounts

# --- FITUR MENU 5: MASS CHECK STATUS ---
def mass_check_accounts():
    print("\n=== 5. CEK STATUS SEMUA AKUN ===")
    accounts = get_logged_in_accounts()
    if not accounts:
        print("❌ Tidak ada akun untuk dicek.")
        return
        
    print(f"Memulai pengecekan {len(accounts)} akun...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        
        for acc in accounts:
            acc_name = acc.replace('.json', '')
            context = browser.new_context()
            try:
                with open(os.path.join(COOKIE_DIR, acc), 'r') as f:
                    cookies = json.load(f)
                
                cleaned = clean_cookies(cookies)
                context.add_cookies(cleaned)
                
                page = context.new_page()
                check_account_status(page, acc_name)
                
            except Exception as e:
                print(f"❌ Error pada {acc_name}: {str(e)}")
            finally:
                context.close()
                time.sleep(2) 
                
        browser.close()
    print("[+] Proses pengecekan selesai.")

# --- FITUR 3: BOT FOLLOW TARGET (UPDATED: OPSI MASSAL / MANUAL) ---
def mass_follow():
    print("\n=== 3. BOT FOLLOW TARGET ===")
    all_accounts = get_logged_in_accounts()
    if not all_accounts:
        print("❌ Tidak ada akun yang tersedia di folder cookies.")
        return
    
    # Berikan opsi pemilihan metode akun
    print("[1] Gunakan SEMUA akun yang ada")
    print("[2] Pilih akun secara manual")
    opsi_akun = input("Pilih metode penggunaan akun (1/2): ").strip()
    
    selected_accounts = []
    if opsi_akun == '2':
        list_accounts()
        pilihan_idx = input("\nPilih nomor akun untuk follow (pisahkan dengan koma, misal: 1,3): ").strip()
        indices = [int(i.strip()) - 1 for i in pilihan_idx.split(',')]
        for index in indices:
            if 0 <= index < len(all_accounts):
                selected_accounts.append(all_accounts[index])
    else:
        # Default gunakan semua akun
        selected_accounts = all_accounts

    if not selected_accounts:
        print("❌ Tidak ada akun valid yang dipilih.")
        return

    target = input("\nMasukkan username target (tanpa @) atau link profil: ").strip()
    if not target.startswith("http"):
        target = f"https://x.com/{target}"
        
    print(f"\nMemulai proses follow ke: {target} menggunakan {len(selected_accounts)} akun.")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        
        for acc in selected_accounts:
            acc_name = acc.replace('.json', '')
            print(f"\n[+] Memproses akun: {acc_name}")
            
            context = browser.new_context()
            try:
                with open(os.path.join(COOKIE_DIR, acc), 'r') as f:
                    cookies = json.load(f)
                
                cleaned = clean_cookies(cookies)
                context.add_cookies(cleaned)
                
                page = context.new_page()
                
                status = check_account_status(page, acc_name)
                if status != "active":
                    print(f"⏭ Melompati {acc_name} karena status tidak aktif ({status}).")
                    continue
                
                page.goto(target, wait_until="domcontentloaded")
                time.sleep(3)
                
                follow_btn = page.locator('button:has-text("Follow"), button:has-text("Ikuti")').first
                
                if follow_btn.is_visible():
                    follow_btn.click()
                    print(f"✅ Berhasil follow menggunakan {acc_name}")
                else:
                    print(f"⚠ Tombol follow tidak ditemukan (mungkin sudah follow).")
                    
            except Exception as e:
                print(f"❌ Error pada akun {acc_name}: {str(e)}")
            finally:
                context.close()
                
            # Jeda antar-akun biar aman dari amukan robot X
            delay = random.randint(15, 30)
            print(f"⏳ Jeda aman... menunggu {delay} detik sebelum akun berikutnya.")
            time.sleep(delay)
            
        browser.close()
    print("\n[+] Proses follow target selesai.")

# --- FITUR 4: KOMENTAR TARGET ---
def bot_comment():
    print("\n=== 4. BOT KOMENTAR ===")
    saved_links = load_saved_links()
    target_link = ""
    
    if saved_links:
        print("[1] Gunakan Link Tersimpan")
        print("[2] Masukkan Link Baru")
        opsi_link = input("Pilih opsi link (1/2): ").strip()
        
        if opsi_link == '1':
            print("\nDaftar Link Tersimpan:")
            for idx, lnk in enumerate(saved_links, 1):
                print(f"[{idx}] {lnk}")
            pilihan_lnk = int(input("Pilih nomor link: ")) - 1
            target_link = saved_links[pilihan_lnk]
        else:
            target_link = input("Masukkan link tweet target: ").strip()
            save_link(target_link)
    else:
        target_link = input("Masukkan link tweet target: ").strip()
        save_link(target_link)
        
    accounts = list_accounts()
    if not accounts:
        return
        
    pilihan_acc = input("\nPilih nomor akun untuk komentar (pisahkan dengan koma, misal: 1,2): ").strip()
    selected_indices = [int(i.strip()) - 1 for i in pilihan_acc.split(',')]
    comment_text = input("Masukkan isi komentar: ").strip()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        for index in selected_indices:
            if index < 0 or index >= len(accounts):
                continue
                
            acc = accounts[index]
            acc_name = acc.replace('.json', '')
            print(f"\n[+] Memproses {acc_name} untuk komentar...")
            
            context = browser.new_context()
            try:
                with open(os.path.join(COOKIE_DIR, acc), 'r') as f:
                    cookies = json.load(f)
                
                cleaned = clean_cookies(cookies)
                context.add_cookies(cleaned)
                
                page = context.new_page()
                
                status = check_account_status(page, acc_name)
                if status != "active":
                    print(f"⏭ Melompati {acc_name} karena status tidak aktif ({status}).")
                    continue
                
                page.goto(target_link, wait_until="domcontentloaded")
                time.sleep(5)  
                
                reply_box = None
                selectors_reply = [
                    'div[data-testid="tweetTextarea_0"]',
                    'div[role="textbox"]',
                    '.public-DraftEditor-content'
                ]
                
                for sel in selectors_reply:
                    if page.locator(sel).first.is_visible():
                        reply_box = page.locator(sel).first
                        break
                
                if not reply_box:
                    page.evaluate("window.scrollBy(0, 250)")
                    time.sleep(2)
                    for sel in selectors_reply:
                        if page.locator(sel).first.is_visible():
                            reply_box = page.locator(sel).first
                            break

                if reply_box:
                    reply_box.click()
                    time.sleep(1)
                    reply_box.fill(comment_text)
                    time.sleep(2)
                    
                    reply_btn = None
                    selectors_btn = [
                        'button[data-testid="tweetButtonInline"]',
                        'button[data-testid="tweetButton"]',
                        'button:has-text("Reply")',
                        'button:has-text("Balas")'
                    ]
                    
                    for sel_b in selectors_btn:
                        if page.locator(sel_b).first.is_visible():
                            reply_btn = page.locator(sel_b).first
                            break
                            
                    if reply_btn:
                        reply_btn.click()
                        print(f"✅ Komentar berhasil dikirim oleh {acc_name}")
                        time.sleep(3)
                    else:
                        print(f"❌ Gagal menemukan tombol 'Reply' untuk {acc_name}.")
                else:
                    print(f"❌ Gagal menemukan kolom komentar untuk {acc_name}.")
                    
            except Exception as e:
                print(f"❌ Error pada akun {acc_name}: {str(e)}")
            finally:
                context.close()
                
            if len(selected_indices) > 1:
                delay = random.randint(20, 40)
                print(f"⏳ Jeda aman komentar... menunggu {delay} detik.")
                time.sleep(delay)
                
        browser.close()

# --- MAIN MENU ---
def main():
    while True:
        print("\n=============================== ")
        print("      BOT TWITTER AUTOMATION    ")
        print("=============================== ")
        print("[1] Masukkan cookie.json")
        print("[2] List daftar akun terlogin")
        print("[3] Bot Mass/Manual Follow Target")
        print("[4] Bot Komentar Tweet")
        print("[5] Cek Status Akun (Aktif/Banned)")
        print("[0] Keluar")
        
        pilihan = input("Pilih menu (0-5): ").strip()
        
        if pilihan == '1':
            input_cookie()
        elif pilihan == '2':
            list_accounts()
        elif pilihan == '3':
            mass_follow()
        elif pilihan == '4':
            bot_comment()
        elif pilihan == '5':
            mass_check_accounts()
        elif pilihan == '0':
            print("Terima kasih! Selesai.")
            break
        else:
            print("❌ Pilihan tidak valid.")

if __name__ == "__main__":
    main()
