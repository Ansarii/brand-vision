#!/usr/bin/env python3
"""
Test and measure exact scroll positions and visual landings for buttons and navigation links.
Tests:
1. "Get a Quote" in header (desktop)
2. "Get a Quote" in mobile bottom bar
3. Navigation links: Portfolio, Clients, About, Contact
4. Drawer links: #journey, #locations, #day-night, #preview
5. Chat chips: href="#contact", href="#preview"
"""

import asyncio
import base64
import json
import os
import urllib.request
import websockets

def ensure_chrome():
    try:
        urllib.request.urlopen("http://127.0.0.1:9222/json/version")
    except Exception:
        import subprocess, shutil
        shutil.rmtree("/tmp/chrome_dev_user_dir", ignore_errors=True)
        subprocess.Popen([
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "--headless=new",
            "--remote-debugging-port=9222",
            "--user-data-dir=/tmp/chrome_dev_user_dir"
        ])
        import time
        for _ in range(25):
            time.sleep(0.3)
            try:
                urllib.request.urlopen("http://127.0.0.1:9222/json/version")
                return
            except Exception:
                pass
        raise RuntimeError("Failed to start Chrome")

async def test_scroll():
    ensure_chrome()
    os.makedirs("scratch/qc", exist_ok=True)

    # 1. Desktop Test (1440x900)
    print("\n=== Desktop Scroll Position Audit (1440x900) ===")
    req = urllib.request.Request("http://127.0.0.1:9222/json/new?http://localhost:8765/v2/", method="PUT")
    with urllib.request.urlopen(req) as resp:
        page_info = json.loads(resp.read().decode())
    ws_url = page_info["webSocketDebuggerUrl"]

    async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
        msg_id = 0
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
            while True:
                res = json.loads(await ws.recv())
                if res.get("id") == msg_id:
                    return res.get("result", {})

        await call("Page.enable")
        await call("Runtime.enable")
        await call("Emulation.setDeviceMetricsOverride", {
            "width": 1440,
            "height": 900,
            "deviceScaleFactor": 1,
            "mobile": False
        })
        await asyncio.sleep(1.0)

        # Test: Click "Get a Quote" in header
        res_quote = await call("Runtime.evaluate", {
            "expression": """(() => {
                const btn = document.querySelector('.coral-quote-btn');
                const target = document.getElementById('contact');
                const header = document.querySelector('.coral-site-header');
                const initialScrollY = window.scrollY;
                btn.click();
                return {
                    initialScrollY,
                    targetId: target ? target.id : null,
                    headerHeight: header ? header.getBoundingClientRect().height : null
                };
            })()""",
            "returnByValue": True
        })
        print("Clicking 'Get a Quote'...", res_quote.get("result", {}).get("value"))
        await asyncio.sleep(1.2) # wait for smooth scroll

        # Check landing measurements
        landing = await call("Runtime.evaluate", {
            "expression": """(() => {
                const target = document.getElementById('contact');
                const header = document.querySelector('.coral-site-header');
                const headerRect = header ? header.getBoundingClientRect() : null;
                const targetRect = target ? target.getBoundingClientRect() : null;
                const tagline = target ? target.querySelector('.tagline') : null;
                const taglineRect = tagline ? tagline.getBoundingClientRect() : null;
                const title = target ? target.querySelector('.section-title') : null;
                const titleRect = title ? title.getBoundingClientRect() : null;
                return {
                    scrollY: window.scrollY,
                    headerBottom: headerRect ? headerRect.bottom : null,
                    targetTop: targetRect ? targetRect.top : null,
                    taglineTop: taglineRect ? taglineRect.top : null,
                    titleTop: titleRect ? titleRect.top : null,
                    clearanceBelowHeader: (taglineRect && headerRect) ? (taglineRect.top - headerRect.bottom) : null
                };
            })()""",
            "returnByValue": True
        })
        land_val = landing.get("result", {}).get("value")
        print("Landing after 'Get a Quote':", json.dumps(land_val, indent=2))

        # Capture visual proof
        shot = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/qc/scroll_landing_desktop_get_quote.png", "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        print("Saved scratch/qc/scroll_landing_desktop_get_quote.png")

        # Now test Portfolio link in header
        await call("Runtime.evaluate", {
            "expression": "document.querySelector('a[href=\"#inventory\"]').click();"
        })
        await asyncio.sleep(1.2)
        land_port = await call("Runtime.evaluate", {
            "expression": """(() => {
                const target = document.getElementById('inventory');
                const header = document.querySelector('.coral-site-header');
                const hRect = header ? header.getBoundingClientRect() : null;
                const tRect = target ? target.getBoundingClientRect() : null;
                const title = target ? target.querySelector('h2, .section-title') : null;
                const titleRect = title ? title.getBoundingClientRect() : null;
                return {
                    scrollY: window.scrollY,
                    headerBottom: hRect ? hRect.bottom : null,
                    targetTop: tRect ? tRect.top : null,
                    titleTop: titleRect ? titleRect.top : null,
                    clearanceBelowHeader: (titleRect && hRect) ? (titleRect.top - hRect.bottom) : null
                };
            })()""",
            "returnByValue": True
        })
        print("Landing after 'Portfolio':", json.dumps(land_port.get("result", {}).get("value"), indent=2))

    # 2. Mobile Test (390x844)
    print("\n=== Mobile Scroll Position Audit (390x844) ===")
    req = urllib.request.Request("http://127.0.0.1:9222/json/new?http://localhost:8765/v2/", method="PUT")
    with urllib.request.urlopen(req) as resp:
        page_info = json.loads(resp.read().decode())
    ws_url = page_info["webSocketDebuggerUrl"]

    async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
        msg_id = 0
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
            while True:
                res = json.loads(await ws.recv())
                if res.get("id") == msg_id:
                    return res.get("result", {})

        await call("Page.enable")
        await call("Runtime.enable")
        await call("Emulation.setDeviceMetricsOverride", {
            "width": 390,
            "height": 844,
            "deviceScaleFactor": 2,
            "mobile": True
        })
        await asyncio.sleep(1.0)

        # Click "Get a Quote" in mobile bottom bar (.mv-quote)
        res_mquote = await call("Runtime.evaluate", {
            "expression": """(() => {
                const btn = document.querySelector('.mv-quote');
                if (btn) btn.click();
            })()"""
        })
        await asyncio.sleep(1.2)

        # Check mobile landing
        land_m = await call("Runtime.evaluate", {
            "expression": """(() => {
                const target = document.getElementById('contact');
                const header = document.querySelector('.coral-site-header');
                const hRect = header ? header.getBoundingClientRect() : null;
                const targetRect = target ? target.getBoundingClientRect() : null;
                const tagline = target ? target.querySelector('.tagline') : null;
                const tagRect = tagline ? tagline.getBoundingClientRect() : null;
                const title = target ? target.querySelector('.section-title') : null;
                const titleRect = title ? title.getBoundingClientRect() : null;
                const formCard = target ? target.querySelector('.contact-modern-layout') : null;
                const formRect = formCard ? formCard.getBoundingClientRect() : null;
                return {
                    scrollY: window.scrollY,
                    headerBottom: hRect ? hRect.bottom : null,
                    targetTop: targetRect ? targetRect.top : null,
                    taglineTop: tagRect ? tagRect.top : null,
                    titleTop: titleRect ? titleRect.top : null,
                    formCardTop: formRect ? formRect.top : null,
                    clearanceBelowHeader: (tagRect && hRect) ? (tagRect.top - hRect.bottom) : null
                };
            })()""",
            "returnByValue": True
        })
        m_val = land_m.get("result", {}).get("value")
        print("Mobile Landing after 'Get a Quote':", json.dumps(m_val, indent=2))

        shot_m = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/qc/scroll_landing_mobile_get_quote.png", "wb") as f:
            f.write(base64.b64decode(shot_m["data"]))
        print("Saved scratch/qc/scroll_landing_mobile_get_quote.png")

if __name__ == "__main__":
    asyncio.run(test_scroll())
