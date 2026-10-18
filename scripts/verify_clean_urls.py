import time
from playwright.sync_api import sync_playwright

def verify_clean_urls():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Test 1: Desktop Clean Root Routing
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        print("--- Test 1.1: Direct visit to root / ---")
        page.goto("http://localhost:8765/")
        page.wait_for_load_state("networkidle")
        print("Initial URL:", page.url)
        assert page.url.rstrip("/") == "http://localhost:8765"
        
        print("--- Test 1.2: Click Portfolio link on root ---")
        page.click("a.coral-nav-link[href='#portfolio']")
        time.sleep(1.0)
        print("URL after clicking Portfolio:", page.url)
        assert page.url == "http://localhost:8765/#portfolio"
        scroll_y = page.evaluate("window.scrollY")
        print(f"Scroll position for Portfolio: {scroll_y}px")
        assert scroll_y > 400
        
        print("--- Test 1.3: Click Home link / Logo on root ---")
        page.click("a.coral-brand-logo")
        time.sleep(1.0)
        print("URL after clicking Brand Logo:", page.url)
        assert page.url.rstrip("/") == "http://localhost:8765"
        assert "#top" not in page.url
        scroll_y = page.evaluate("window.scrollY")
        print(f"Scroll position after clicking Logo: {scroll_y}px")
        assert scroll_y < 10

        print("--- Test 1.4: Legacy /v2/ redirect to clean root ---")
        page.goto("http://localhost:8765/v2/")
        time.sleep(1.0)
        print("URL after visiting legacy /v2/:", page.url)
        assert page.url.rstrip("/") == "http://localhost:8765"
        assert "/v2" not in page.url

        print("--- Test 1.5: Legacy /v2/#portfolio redirect to clean root #portfolio ---")
        page.goto("http://localhost:8765/v2/#portfolio")
        time.sleep(1.0)
        print("URL after visiting legacy /v2/#portfolio:", page.url)
        assert page.url == "http://localhost:8765/#portfolio"
        assert "/v2" not in page.url

        print("--- Test 1.6: Direct visit with legacy #inventory ---")
        page.goto("http://localhost:8765/#inventory")
        time.sleep(1.0)
        print("URL after visiting legacy #inventory:", page.url)
        assert page.url == "http://localhost:8765/#portfolio"
        assert "#inventory" not in page.url
        
        print("--- Test 1.7: Direct visit with legacy #top ---")
        page.goto("http://localhost:8765/#top")
        time.sleep(1.0)
        print("URL after visiting legacy #top:", page.url)
        assert page.url.rstrip("/") == "http://localhost:8765"
        assert "#top" not in page.url

        page.close()
        
        # Test 2: Mobile Clean Root Routing
        page_mobile = browser.new_page(viewport={"width": 390, "height": 844})
        
        print("--- Test 2.1: Mobile visit to root / ---")
        page_mobile.goto("http://localhost:8765/")
        page_mobile.wait_for_load_state("networkidle")
        print("Mobile Initial URL:", page_mobile.url)
        assert page_mobile.url.rstrip("/") == "http://localhost:8765"
        
        print("--- Test 2.2: Click Portfolio in Mobile Subnav ---")
        page_mobile.click(".mv-subnav a[href='#portfolio']")
        time.sleep(1.0)
        print("Mobile URL after clicking Portfolio:", page_mobile.url)
        assert page_mobile.url == "http://localhost:8765/#portfolio"
        mobile_scroll_y = page_mobile.evaluate("window.scrollY")
        print(f"Mobile Scroll position for Portfolio: {mobile_scroll_y}px")
        assert mobile_scroll_y > 400
        
        print("--- Test 2.3: Click Home in Mobile Subnav ---")
        page_mobile.click(".mv-subnav a[href='#top']")
        time.sleep(1.0)
        print("Mobile URL after clicking Home in Subnav:", page_mobile.url)
        assert page_mobile.url.rstrip("/") == "http://localhost:8765"
        assert "#top" not in page_mobile.url
        mobile_scroll_y = page_mobile.evaluate("window.scrollY")
        print(f"Mobile Scroll position after clicking Home: {mobile_scroll_y}px")
        assert mobile_scroll_y < 10

        page_mobile.close()
        browser.close()
        print("\nALL CLEAN URL TESTS PASSED 100%!")

if __name__ == "__main__":
    verify_clean_urls()
