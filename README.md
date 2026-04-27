# Plant Identifier - Mobile Automation Testing

Dự án kiểm thử tự động cho ứng dụng **Plant Identifier** sử dụng framework Appium và Pytest. Hệ thống tập trung kiểm tra độ ổn định và chính xác của tính năng nhận dạng AI (thực vật, nấm, côn trùng, cá) và các công cụ hỗ trợ tiện ích.

## 🌿 Giới thiệu ngắn gọn
Dự án automation này được xây dựng theo mô hình **Page Object Model (POM)** để đảm bảo mã nguồn được tổ chức khoa học, tách biệt giữa phần định nghĩa giao diện và dữ liệu test, giúp dễ bảo trì và mở rộng.

**Phạm vi kiểm thử:**
* **Nhận dạng thông minh:** Kiểm tra khả năng nhận diện AI (Thực vật, Nấm, Côn trùng, Cá) với bộ dữ liệu mẫu 5 hình ảnh cho mỗi chức năng.
* **Tiện ích:** Kiểm thử chức năng đo cường độ ánh sáng (Light Meter).
* **Luồng cơ bản:** Kiểm tra tính đúng đắn của các thao tác và điều hướng (Lưu ý: Ứng dụng không yêu cầu đăng nhập).

## 🛠 Công nghệ sử dụng
* **Ngôn ngữ:** Python
* **Framework Test:** Pytest
* **Automation Tool:** Appium (Mobile Automation)
* **Kiến trúc:** Page Object Model (POM)
* **Báo cáo:** `pytest-html`
* **Môi trường:** Android 16 (Thiết bị thực tế: Samsung S23+)

## 🚀 Hướng dẫn cài đặt

### 1. Yêu cầu hệ thống
Đảm bảo máy tính của bạn đã được cài đặt sẵn:
* Python 3.x
* Appium Server (GUI hoặc cài đặt qua Node.js)
* Android SDK (Đã cấu hình biến môi trường `ANDROID_HOME`)
* Java JDK (Đã cấu hình biến môi trường `JAVA_HOME`)

### 2. Tải mã nguồn và cài đặt thư viện
Clone project về máy và cài đặt các package Python cần thiết:
```bash
git clone <url-cua-repo-ban>
cd <ten-thu-muc-du-an>
pip install -r requirements.txt
```

### 3. Thiết lập thông số thiết bị (Desired Capabilities)
Cập nhật thông số thiết bị thật của bạn vào file cấu hình (ví dụ: `conftest.py` hoặc file khởi tạo driver):
```python
desired_caps = {
    "platformName": "Android",
    "automationName": "UiAutomator2",
    "platformVersion": "16",
    "deviceName": "Samsung S23+",
    "appPackage": "com.plant.identifier", 
    "appActivity": ".MainActivity",        
    "noReset": True                        
}
```

## 🧪 Hướng dẫn chạy Test

### Bước 1: Khởi động Appium Server
Mở terminal mới và khởi chạy Appium:
```bash
appium
```
*(Đảm bảo điện thoại Samsung S23+ đã được kết nối với máy tính, bật chế độ Developer Options > USB Debugging và màn hình đang mở khóa).*

### Bước 2: Thực thi kịch bản kiểm thử
Mở terminal tại thư mục gốc của dự án, bạn có thể sử dụng các lệnh `pytest` sau:

**Chạy toàn bộ các test case:**

```bash
pytest
```

**Chạy toàn bộ test case và xuất báo cáo HTML trực quan:**

```bash
pytest --html=reports/report.html --self-contained-html
```

**Chạy riêng biệt một module (Ví dụ: Chức năng Light Meter):**

```bash
pytest src/tests/test_light_meter.py
```

## 📂 Cấu trúc dự án

```text
├── src/
│   ├── pages/          
│   ├── tests/          
│   └── utils/          
├── data/               
├── reports/            
├── requirements.txt    
└── README.md
```

## 📊 Lưu ý khi thực thi
* Hệ thống AI cần thời gian để gọi API và phân tích hình ảnh (đặc biệt khi xử lý vòng lặp 5 ảnh), vui lòng đảm bảo kết nối mạng WiFi/4G trên thiết bị thật ổn định để tránh lỗi timeout.
* Cơ chế `Wait` đã được thiết lập trong framework, tuy nhiên do chạy trên thiết bị vật lý, đôi khi có thể xảy ra độ trễ phần cứng nhẹ ở lần chạy đầu tiên.
