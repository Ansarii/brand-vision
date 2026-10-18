import time
from playwright.sync_api import sync_playwright

def verify_clean_urls():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Test 1: Desktop v2 URL clean test
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        print("--- Test 1.1: Direct visit to /v2/ ---")
        page.goto("http://localhost:8765/v2/")
        page.wait_for_load_state("networkidle")
        print("Initial URL:", page.url)
        assert page.url.rstrip("/") == "http://localhost:8765/v2"
        
        print("--- Test 1.2: Click Portfolio link ---")
        page.click("a.coral-nav-link[href='#portfolio']")
        time.sleep(1.0)
        print("URL after clicking Portfolio:", page.url)
        assert page.url == "http://localhost:8765/v2/#portfolio"
        scroll_y = page.evaluate("window.scrollY")
        print(f"Scroll position for Portfolio: {scroll_y}px")
        assert scroll_y > 400
        page.screenshot(path="/Users/ansari/.gemini/antigravity/brain/b037a575-4d6b-41eb-bc93-5a0717031971/test_v2_desktop_portfolio_landing.png")
        
        print("--- Test 1.3: Click Home link / Logo ---")
        page.click("a.coral-brand-logo")
        time.sleep(1.0)
        print("URL after clicking Brand Logo:", page.url)
        # MUST NOT contain #top
        assert page.url.rstrip("/") == "http://localhost:8765/v2"
        assert "#top" not in page.url
        scroll_y = page.evaluate("window.scrollY")
        print(f"Scroll position after clicking Logo: {scroll_y}px")
        assert scroll_y < 10
        page.screenshot(path="/Users/ansari/.gemini/antigravity/brain/b037a575-4d6b-41eb-bc93-5a0717031971/test_v2_desktop_home_clean.png")

        print("--- Test 1.4: Direct visit with legacy #inventory ---")
        page.goto("http://localhost:8765/v2/#inventory")
        time.sleep(1.0)
        print("URL after visiting legacy #inventory:", page.url)
        assert page.url == "http://localhost:8765/v2/#portfolio"
        assert "#inventory" not in page.url
        
        print("--- Test 1.5: Direct visit with legacy #top ---")
        page.goto("http://localhost:8765/v2/#top")
        time.sleep(1.0)
        print("URL after visiting legacy #top:", page.url)
        assert page.url.rstrip("/") == "http://localhost:8765/v2"
        assert "#top" not in page.url

        page.close()
        
        # Test 2: Mobile v2 URL clean test
        page_mobile = browser.new_page(viewport={"width": 390, "height": 844})
        
        print("--- Test 2.1: Mobile visit to /v2/ ---")
        page_mobile.goto("http://localhost:8765/v2/")
        page_mobile.wait_for_load_state("networkidle")
        print("Mobile Initial URL:", page_mobile.url)
        assert page_mobile.url.rstrip("/") == "http://localhost:8765/v2"
        
        print("--- Test 2.2: Click Portfolio in Mobile Subnav ---")
        page_mobile.click(".mv-subnav a[href='#portfolio']")
        time.sleep(1.0)
        print("Mobile URL after clicking Portfolio:", page_mobile.url)
        assert page_mobile.url == "http://localhost:8765/v2/#portfolio"
        mobile_scroll_y = page_mobile.evaluate("window.scrollY")
        print(f"Mobile Scroll position for Portfolio: {mobile_scroll_y}px")
        assert mobile_scroll_y > 400
        page_mobile.screenshot(path="/Users/ansari/.gemini/antigravity/brain/b037a575-4d6b-41eb-bc93-5a0717031971/test_v2_mobile_portfolio_landing.png")
        
        print("--- Test 2.3: Click Home in Mobile Subnav ---")
        page_mobile.click(".mv-subnav a[href='#top']")
        time.sleep(1.0)
        print("Mobile URL after clicking Home in Subnav:", page_mobile.url)
        assert page_mobile.url.rstrip("/") == "http://localhost:8765/v2"
        assert "#top" not in page_mobile.url
        mobile_scroll_y = page_mobile.evaluate("window.scrollY")
        print(f"Mobile Scroll position after clicking Home: {mobile_scroll_y}px")
        assert mobile_scroll_y < 10
        page_mobile.screenshot(path="/Users/ansari/.gemini/antigravity/brain/b037a575-4d6b-41eb-bc93-5a0717031971/test_v2_mobile_home_clean.png")

        page_mobile.close()
        
        # Test 3: Root index.html clean URL test
        page_root = browser.new_page(viewport={"width": 1440, "height": 900})
        print("--- Test 3.1: Direct visit to root / ---")
        page_root.goto("http://localhost:8765/")
        page_root.wait_for_load_state("networkidle")
        print("Root Initial URL:", page_root.url)
        assert page_root.url.rstrip("/") == "http://localhost:8765"
        
        print("--- Test 3.2: Click Portfolio on root ---")
        page_root.click("a.coral-nav-link[href='#portfolio']")
        time.sleep(1.0)
        print("Root URL after clicking Portfolio:", page_root.url)
        assert page_root.url == "http://localhost:8765/#portfolio"
        
        print("--- Test 3.3: Click Brand Logo on root ---")
        page_root.click("a.coral-brand-logo")
        time.sleep(1.0)
        print("Root URL after clicking Logo:", page_root.url)
        assert page_root.url.rstrip("/") == "http://localhost:8765"
        assert "#top" not in page_root.url

        page_root.close()
        browser.close()
        print("\nALL CLEAN URL TESTS PASSED 100%!")

if __name__ == "__main__":
    verify_clean_urls()
