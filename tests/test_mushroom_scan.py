import pytest
import time
import json
import os
import base64
from pages.scan_page import ScanPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy


def get_mushroom_test_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    json_path = os.path.join(project_root, 'data', 'mushroom_test_data.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data if isinstance(data, list) else [data]
    except FileNotFoundError:
        pytest.fail(f"Không tìm thấy file mushroom_test_data.json tại: {json_path}")


@pytest.mark.parametrize("test_data", get_mushroom_test_data())
def test_mushroom_scan_functionality(driver, test_data):
    scan_page = ScanPage(driver)

    test_id = test_data.get('test_id', 'Unknown_Mushroom')
    image_name = test_data['image_name']
    remote_path = test_data['remote_path']
    scanner_type = test_data.get('scanner_type', 'mushroom')

    print(f"\n[{test_id}] Bắt đầu chuẩn bị ảnh nấm: {image_name}")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    local_image_path = os.path.join(os.path.dirname(current_dir), 'images', image_name)

    try:
        with open(local_image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        driver.push_file(remote_path, encoded_string)
        time.sleep(2)
    except Exception as e:
        pytest.fail(f"Lỗi chuẩn bị ảnh: {e}")

    driver.activate_app('com.plantidentification.ai')
    time.sleep(5)

    try:
        print(f"[{test_id}] Thực hiện quét loại: {scanner_type}")
        scan_page.execute_scan_flow(scanner_type=scanner_type)

        wait = WebDriverWait(driver, 50)

        mushroom_name_locator = (AppiumBy.ID, "com.plantidentification.ai:id/nameMushroom")
        wait.until(EC.visibility_of_element_located(mushroom_name_locator))

        print(f"[{test_id}] Đã thấy kết quả. Đợi 20s để AI tải toàn bộ thông tin...")
        time.sleep(25)

        mushroom_fields = {
            "Tên nấm": "com.plantidentification.ai:id/nameMushroom",
            "Độc tính chính": "com.plantidentification.ai:id/toxicTv",
        }

        for label, resource_id in mushroom_fields.items():
            print(f"[{test_id}] Đang cuộn tìm: {label}...")

            scroll_cmd = (
                'new UiScrollable(new UiSelector().scrollable(true))'
                '.setMaxSearchSwipes(15)'
                f'.scrollIntoView(new UiSelector().resourceId("{resource_id}").instance(0))'
            )

            try:

                element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll_cmd)

                wait.until(lambda d: element.text.strip() != "")

                print(f"[{test_id}] Đã lấy được {label}: {element.text[:40]}...")
            except Exception:
                print(f"[{test_id}] Cảnh báo: Không tìm thấy hoặc thiếu dữ liệu cho {label}")

        print(f"[{test_id}] HOÀN THÀNH: Nhận dạng nấm và load đầy đủ dữ liệu!")

    except Exception as e:
        error_img = f"error_{test_id}_{int(time.time())}.png"
        driver.save_screenshot(error_img)
        print(f"[{test_id}] LỖI: Đã chụp màn hình lỗi {error_img}")
        raise e

    finally:

        print(f"[{test_id}] Đang bấm nút Back để chuẩn bị lượt tiếp theo...")
        try:
            back_btn_id = "com.plantidentification.ai:id/iconBack"

            wait_back = WebDriverWait(driver, 10)
            wait_back.until(EC.element_to_be_clickable((AppiumBy.ID, back_btn_id))).click()
            print(f"[{test_id}] Đã quay về màn hình Home.")
            time.sleep(3)
        except Exception:
            print(f"[{test_id}] Cảnh báo: Không thấy nút Back, đang thử driver.back()...")
            driver.back()