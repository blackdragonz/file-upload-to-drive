from flask import Flask, request, render_template, redirect, url_for
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import datetime
import os

app = Flask(__name__)

# ตั้งค่า Google Drive API credentials
credentials = service_account.Credentials.from_service_account_file("path_to_your_service_account.json")
drive_service = build("drive", "v3", credentials=credentials)

# ฟังก์ชันสำหรับอัปโหลดไฟล์ไป Google Drive
def upload_to_drive(file_path, file_name):
    media = MediaFileUpload(file_path, resumable=True)
    request = drive_service.files().create(
        media_body=media,
        body={
            "name": file_name,
            "parents": ["your_drive_folder_id"]  # เปลี่ยน "your_drive_folder_id" เป็น Folder ID ที่คุณต้องการเก็บไฟล์
        }
    )
    response = request.execute()
    return response.get("id")

# หน้าฟอร์มอัปโหลด
@app.route('/')
def index():
    return render_template('upload.html')

# Endpoint สำหรับอัปโหลดไฟล์
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'company' not in request.form:
        return "No file or company data provided", 400

    file = request.files['file']
    company_name = request.form['company']
    
    # ตั้งชื่อไฟล์ด้วยข้อมูลบริษัทและเวลาอัปโหลด
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{company_name}_{timestamp}_{file.filename}"

    # บันทึกไฟล์ลงบนเซิร์ฟเวอร์ชั่วคราว
    temp_path = os.path.join("/tmp", file_name)
    file.save(temp_path)
    
    # อัปโหลดไฟล์ไปยัง Google Drive
    try:
        file_id = upload_to_drive(temp_path, file_name)
    finally:
        os.remove(temp_path)  # ลบไฟล์ออกจากเซิร์ฟเวอร์หลังอัปโหลดเสร็จ

    return f"File uploaded successfully! File ID: {file_id}"

# เริ่ม Flask server
if __name__ == '__main__':
    app.run(debug=True)
