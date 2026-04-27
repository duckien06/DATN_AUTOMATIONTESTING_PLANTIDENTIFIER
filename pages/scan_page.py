from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime


class ScanPage:
    def __init__(self, driver):
        self.driver = driver
        self.scanner_buttons = {
            "plant": (AppiumBy.ID, "com.plantidentification.ai:id/viewIdentify"),
            "mushroom": (AppiumBy.ID, "com.plantidentification.ai:id/cardViewMushroom"),
            "insect": (AppiumBy.ID, "com.plantidentification.ai:id/cardViewRecognizeInsect"),
            "fish": (AppiumBy.ID, "com.plantidentification.ai:id/cardViewFish")
        }
        self.import_image_btn = (AppiumBy.ID, "com.plantidentification.ai:id/galleryBtn")
        self.first_photo_google_thumbnail = (
            AppiumBy.XPATH,
            "(//android.view.View[@clickable='true' and .//*[contains(@content-desc,'Ảnh được chụp lúc')]])[1]"
        )
        self.first_photo_fallback = (AppiumBy.XPATH, '(//android.widget.ImageView)[1]')
        self.photo_done_btn = (
            AppiumBy.XPATH,
            "//*[@clickable='true' and .//*[@text='Xong']][1]"
        )
        self.photo_done_btn_fallback = (
            AppiumBy.XPATH,
            "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View/android.view.View[6]/android.view.View/android.view.View[3]/android.widget.Button"
        )
        self.photo_access_allow = (
            AppiumBy.XPATH,
            "//*[@clickable='true' and .//*[@text='Ảnh' or @content-desc='Ảnh']][1]"
        )
        self.photo_access_close = (
            AppiumBy.XPATH,
            "//*[@clickable='true' and .//*[@text='Đóng' or @content-desc='Đóng']][1]"
        )
        self.result_title = (AppiumBy.ID, "com.plantidentification.ai:id/txt_result_name")

    def _handle_photo_access_popup(self):
        for _ in range(4):
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable(self.photo_access_allow)
                ).click()
                time.sleep(0.5)
            except TimeoutException:
                break
        try:
            WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable(self.photo_access_close)
            ).click()
        except TimeoutException:
            return

    def execute_scan_flow(self, scanner_type="plant"):
        print("\n[HÀNH ĐỘNG] Chờ màn hình chính load...")
        time.sleep(2)
        try:
            print(f"[HÀNH ĐỘNG] Đang tìm nút {scanner_type} Scanner...")
            target_btn = self.scanner_buttons.get(scanner_type)
            if not target_btn:
                raise ValueError(f"Loại scan '{scanner_type}' chưa được cấu hình trong Page Object!")
            element = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(target_btn)
            )
            element.click()
            print(f"[THÀNH CÔNG] Đã click nút {scanner_type} Scanner")

            print("[HÀNH ĐỘNG] Đang tìm nút Gallery...")
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.import_image_btn)
            ).click()

            print("[HÀNH ĐỘNG] Đang xử lý popup quyền ảnh (nếu có)...")
            self._handle_photo_access_popup()
            time.sleep(1)
            self._handle_photo_access_popup()

            def _try_click_photo(locator, wait_seconds=20):
                try:
                    photo_el = WebDriverWait(self.driver, wait_seconds).until(
                        EC.element_to_be_clickable(locator)
                    )
                except TimeoutException:
                    photo_el = WebDriverWait(self.driver, wait_seconds).until(
                        EC.presence_of_element_located(locator)
                    )
                photo_el.click()

            print("[HÀNH ĐỘNG] Đang chọn ảnh đầu tiên từ thư viện...")
            try:
                _try_click_photo(self.first_photo_google_thumbnail, wait_seconds=15)
            except TimeoutException:
                try:
                    _try_click_photo(self.first_photo_google_thumbnail, wait_seconds=15)
                except TimeoutException:
                    _try_click_photo(self.first_photo_fallback, wait_seconds=10)

            print("[HÀNH ĐỘNG] Bấm nút 'xong' để xác nhận ảnh...")
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable(self.photo_done_btn)
                ).click()
            except TimeoutException:
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(self.photo_done_btn_fallback)
                ).click()

            print("[HOÀN TẤT FLOW] Đã gửi ảnh lên hệ thống AI. Trả quyền kiểm tra lại cho file Test...")
        except TimeoutException:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"error_screen_{scanner_type}_{ts}.png"
            page_source_name = f"page_source_{scanner_type}_{ts}.xml"
            self.driver.save_screenshot(screenshot_name)
            try:
                with open(page_source_name, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
            except Exception:
                pass
            print(f"[LỖI] Không tìm thấy phần tử trong thao tác. Đã chụp '{screenshot_name}'")
            raise
        except Exception as e:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"error_screen_{scanner_type}_{ts}.png"
            self.driver.save_screenshot(screenshot_name)
            print(f"[LỖI] Lỗi không mong đợi: {e}. Đã chụp '{screenshot_name}'")
            raise

    def get_result_text(self):
        try:
            return self.driver.find_element(*self.result_title).text
        except:
            return "Không tìm thấy text kết quả"