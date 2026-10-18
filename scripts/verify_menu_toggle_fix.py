import time
from playwright.sync_api import sync_playwright

def test_menu_toggle():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        
        for base_url in ['http://localhost:8765/v2/', 'http://localhost:8765/']:
            print(f"\n==========================================")
            print(f"Testing Menu Toggle State on: {base_url}")
            print(f"==========================================")
            
            page = browser.new_page(viewport={'width': 1440, 'height': 900})
            page.goto(base_url)
            page.wait_for_load_state('networkidle')
            
            toggle = page.locator('#coral-menu-toggle')
            drawer = page.locator('#coral-drawer-overlay')
            close_btn = page.locator('#coral-drawer-close')
            
            # Helper to check closed state
            def check_closed(context_msg):
                expanded = toggle.get_attribute('aria-expanded')
                d_active = 'active' in (drawer.get_attribute('class') or '')
                print(f"[{context_msg}] aria-expanded: {expanded}, drawer active: {d_active}")
                assert expanded == 'false', f"FAIL: {context_msg} left aria-expanded='{expanded}'"
                assert not d_active, f"FAIL: {context_msg} left drawer active"

            # 1. Close via close button
            toggle.click()
            time.sleep(0.3)
            assert toggle.get_attribute('aria-expanded') == 'true'
            close_btn.click()
            time.sleep(0.3)
            check_closed("1. Close Button")

            # 2. Close via backdrop
            toggle.click()
            time.sleep(0.3)
            page.click('#coral-drawer-backdrop', position={'x': 50, 'y': 50})
            time.sleep(0.3)
            check_closed("2. Backdrop Click")

            # 3. Close via Quick Nav link (Portfolio)
            toggle.click()
            time.sleep(0.3)
            page.click('.coral-drawer-link[href="#portfolio"]')
            time.sleep(0.3)
            check_closed("3. Portfolio Link")

            # 4. Close via Action button (Book a Hoarding)
            toggle.click()
            time.sleep(0.3)
            page.click('a.coral-drawer-action-btn[href="#contact"]')
            time.sleep(0.3)
            check_closed("4. Action Button (Book)")

            # 5. Close via Policy button (Blogs)
            toggle.click()
            time.sleep(0.3)
            page.click('button.coral-drawer-policy-btn[data-doc-target="blogs"]')
            time.sleep(0.3)
            check_closed("5. Policy Button (Blogs)")
            # Close doc modal
            page.click('#doc-modal-close')
            time.sleep(0.2)
            check_closed("5b. After Doc Modal Close")

            # 6. Close via Escape key
            toggle.click()
            time.sleep(0.3)
            page.keyboard.press('Escape')
            time.sleep(0.3)
            check_closed("6. Escape Key")

            # 7. MutationObserver test: direct removal of active class
            toggle.click()
            time.sleep(0.3)
            assert toggle.get_attribute('aria-expanded') == 'true'
            page.evaluate("document.getElementById('coral-drawer-overlay').classList.remove('active')")
            time.sleep(0.1)
            check_closed("7. MutationObserver Direct Removal")

            # Take screenshot of the closed menu toggle button
            screenshot_path = f"/Users/ansari/.gemini/antigravity/brain/b037a575-4d6b-41eb-bc93-5a0717031971/test_menu_toggle_closed_{'v2' if 'v2' in base_url else 'root'}.png"
            toggle.screenshot(path=screenshot_path)
            print(f"Captured clean closed button screenshot: {screenshot_path}")

            page.close()

        browser.close()
        print("\nALL MENU TOGGLE TESTS PASSED 100%!")

if __name__ == '__main__':
    test_menu_toggle()
