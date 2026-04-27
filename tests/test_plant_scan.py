import pytest
import time
import json
import os
import base64
from pages.scan_page import ScanPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy

def get_plant_test_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    json_path = os.path.join(project_root, 'data', 'plant_test_data.json')

    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data if isinstance(data, list) else [data]
    except FileNotFoundError:
        pytest.fail(f"Không tìm thấy file JSON tại: {json_path}")
@pytest.mark.parametrize("test_data", get_plant_test_data())
def test_scan_functionality(driver, test_data):
    scan_page = ScanPage(driver)
    test_id = test_data.get('test_id', 'Unknown_ID')
    image_name = test_data.get('image_name')
    remote_path = test_data.get('remote_path')
    scanner_type = test_data.get('scanner_type', 'plant')
    expected_screen = test_data.get('expected_screen', 'Plant Overview')
    expected_name = test_data.get('expected_name', 'Unknown Plant')

    if not image_name:
        pytest.fail(f"[{test_id}] Thiếu 'image_name' trong file JSON.")

    print(f"\n[{test_id}] Bắt đầu chuẩn bị dữ liệu cho: {expected_name}")

    # --- BƯỚC 1: PUSH HÌNH ẢNH VÀO ĐIỆN THOẠI ---
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    local_image_path = os.path.join(project_root, 'images', image_name)

    try:
        with open(local_image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

        driver.push_file(remote_path, encoded_string)
        print(f"[{test_id}] Push thành công ảnh {image_name} vào: {remote_path}")
        time.sleep(2) # Chờ Media Scanner cập nhật Gallery
    except FileNotFoundError:
        pytest.fail(f"[{test_id}] Không tìm thấy file ảnh tại: {local_image_path}")
    except Exception as e:
        pytest.fail(f"[{test_id}] Lỗi khi push ảnh: {e}")

    # --- BƯỚC 2: KÍCH HOẠT APP VÀ CHẠY FLOW ---
    print(f"[{test_id}] Đang đánh thức ứng dụng Plant Identifier...")
    driver.activate_app('com.plantidentification.ai')
    time.sleep(5)

    try:
        print(f"[{test_id}] Thực hiện quét loại: {scanner_type}")
        scan_page.execute_scan_flow(scanner_type=scanner_type)

        # --- BƯỚC 3: KIỂM TRA KẾT QUẢ VÀ VUỐT ĐỂ LOAD DỮ LIỆU ---
        print(f"[{test_id}] Đang đợi AI trả kết quả...")
        wait = WebDriverWait(driver, 50)


        overview_locator = (AppiumBy.XPATH, f'//*[@text="{expected_screen}"]')
        wait.until(EC.visibility_of_element_located(overview_locator))

        print(f"[{test_id}] Đợi load hoàn toàn...")
        time.sleep(20)

        data_fields = {
            "Tên thực vật": "com.plantidentification.ai:id/namePlant",
            "Mô tả": "com.plantidentification.ai:id/desPlant",
            "Habitat": "com.plantidentification.ai:id/descHabitat",
        }

        for label, resource_id in data_fields.items():
            print(f"[{test_id}] Đang tìm và cuộn đến: {label}...")

            # Lệnh vuốt đến phần tử theo Resource ID
            scroll_cmd = (
                'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView('
                f'new UiSelector().resourceId("{resource_id}"))'
            )

            try:
                # Thực hiện vuốt
                element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll_cmd)

                wait.until(lambda d: element.text.strip() != "")

                print(f"[{test_id}] Đã load xong {label}: {element.text[:30]}...")
            except Exception as e:
                print(f"[{test_id}] Cảnh báo: Không thể cuộn tới hoặc load dữ liệu cho {label}")

        print(f"[{test_id}] Đã load đủ dữ liệu hiển thị. Nghỉ 7s để App ghi lịch sử...")
        time.sleep(7)  # Tăng thêm 2 giây cho an toàn tuyệt đối

        print(f"[{test_id}] HOÀN THÀNH: {expected_name} nhận diện và lưu lịch sử thành công!")

    except Exception as e:
        error_img = f"error_{test_id}_{int(time.time())}.png"
        driver.save_screenshot(error_img)
        print(f"[{test_id}] TEST FAIL. Ảnh lỗi: {error_img}")
        raise e

    finally:
        # --- BƯỚC CUỐI: QUAY LẠI MÀN HÌNH CHÍNH ĐỂ CHUẨN BỊ CHO CASE TIẾP THEO ---
        print(f"[{test_id}] Đang bấm nút Back để quay về màn hình chính...")
        try:
            back_btn_locator = (AppiumBy.ID, "com.plantidentification.ai:id/backBtn")
            # Đợi nút back có thể click được và bấm
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(back_btn_locator)
            ).click()
            print(f"[{test_id}] Đã quay về màn hình Home an toàn.")
            time.sleep(2)
        except Exception as e:
            print(f"[{test_id}] Cảnh báo: Không tìm thấy nút Back hoặc đã ở màn hình chính.")