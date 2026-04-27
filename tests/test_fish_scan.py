import pytest
import time
import json
import os
import base64
from pages.scan_page import ScanPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy

def get_fish_test_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    json_path = os.path.join(project_root, 'data', 'fish_test_data.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data if isinstance(data, list) else [data]
    except FileNotFoundError:
        pytest.fail(f"Không tìm thấy file fish_test_data.json tại: {json_path}")

@pytest.mark.parametrize("test_data", get_fish_test_data())
def test_fish_scan_functionality(driver, test_data):
    scan_page = ScanPage(driver)

    test_id = test_data.get('test_id', 'Unknown_Fish')
    image_name = test_data['image_name']
    remote_path = test_data['remote_path']
    scanner_type = test_data.get('scanner_type', 'fish')

    print(f"\n[{test_id}] Bắt đầu chuẩn bị ảnh Cá: {image_name}")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    local_image_path = os.path.join(os.path.dirname(current_dir), 'images', image_name)

    try:
        with open(local_image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        driver.push_file(remote_path, encoded_string)
        print(f"[{test_id}] Push thành công ảnh vào: {remote_path}")
        time.sleep(2)
    except Exception as e:
        pytest.fail(f"Lỗi chuẩn bị ảnh: {e}")

    print(f"[{test_id}] Đang đánh thức ứng dụng Plant Identifier...")
    driver.activate_app('com.plantidentification.ai')
    time.sleep(5)

    try:
        scan_page.execute_scan_flow(scanner_type=scanner_type)

        print(f"[{test_id}] Đang đợi màn hình kết quả xuất hiện...")
        wait = WebDriverWait(driver, 50)

        fish_name_locator = (AppiumBy.ID, "com.plantidentification.ai:id/nameFish")
        wait.until(EC.visibility_of_element_located(fish_name_locator))

        print(f"[{test_id}] Đã thấy kết quả. Nghỉ 20s để AI tải data hoàn toàn...")
        time.sleep(20)

        data_fields = {
            "Tên cá": "com.plantidentification.ai:id/nameFish",
            "Mô tả cá": "com.plantidentification.ai:id/descriptionTv"
        }

        for label, resource_id in data_fields.items():
            print(f"[{test_id}] Đang cuộn tìm mục: {label}...")


            scroll_cmd = (
                'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView('
                f'new UiSelector().resourceId("{resource_id}"))'
            )

            try:
                element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll_cmd)


                wait.until(lambda d: element.text.strip() != "")
                print(f"[{test_id}] ✅ {label} load xong: {element.text[:40]}...")
            except Exception:
                print(f"[{test_id}] ⚠️ Cảnh báo: Không thể cuộn tới hoặc thiếu dữ liệu cho {label}")

        print(f"[{test_id}] HOÀN THÀNH: Nhận dạng cá thành công!")

    except Exception as e:
        error_img = f"error_{test_id}_{int(time.time())}.png"
        driver.save_screenshot(error_img)
        print(f"[{test_id}] TEST FAIL. Đã lưu ảnh lỗi: {error_img}")
        raise e

    finally:
        print(f"[{test_id}] Đang bấm nút Back để chuẩn bị cho case tiếp theo...")
        try:
            back_btn_id = "com.plantidentification.ai:id/btBack"
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.ID, back_btn_id))
            ).click()
            print(f"[{test_id}] Đã quay về màn hình Home.")
            time.sleep(3)
        except Exception:
            print(f"[{test_id}] Không thấy nút Back ID, đang thử dùng driver.back()...")
            driver.back()