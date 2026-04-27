import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options


@pytest.fixture(scope="function")
def driver():
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.automation_name = 'UiAutomator2'

    # CHỈ khai báo package, BỎ app_activity để tránh crash Intent
    options.app_package = 'com.plantidentification.ai'

    # --- BỘ CẤU HÌNH TỐI GIẢN & CHUẨN NHẤT ---
    options.no_reset = True  # Không xóa data (lịch sử, settings...)
    options.full_reset = False  # Không gỡ cài đặt app

    # Không ép buộc dừng app, giữ nguyên trạng thái nếu app đang mở
    options.set_capability("appium:dontStopAppOnReset", True)

    # Cho phép UiAutomator2 có thêm thời gian khởi tạo trên S23+ (tránh Invalid Session)
    options.set_capability("appium:uiautomator2ServerLaunchTimeout", 60000)
    options.set_capability("appium:newCommandTimeout", 300)

    print("\n[Setup] Khởi tạo Driver với cấu hình tối giản...")

    # Khởi tạo driver
    driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
    driver.implicitly_wait(15)

    yield driver

    print("\n[Teardown] Đóng session an toàn...")
    driver.quit()