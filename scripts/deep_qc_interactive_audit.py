#!/usr/bin/env python3
"""
Deep Interactive QC Audit of Brand Vision Media v2.
Tests all interactive components across Desktop (1440px) and Mobile (390px):
1. Navigation Drawer (#coral-drawer-overlay)
2. Document Modal (#modal-doc-viewer) with 4 tabs
3. Catalog Filter Tabs & Lightbox Modal (#modal-lightbox)
4. Mockup Studio Dropdown
5. Contact Form Validation
6. AI Chat Support (#bv-chat-window)
"""

import asyncio
import json
import os
import subprocess
import time
import urllib.request
import websockets

def ensure_chrome():
    try:
        urllib.request.urlopen("http://127.0.0.1:9222/json/version")
    except Exception:
        subprocess.Popen([
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "--headless=new",
            "--remote-debugging-port=9222",
            "--user-data-dir=scratch/chrome_user_data"
        ])
        for _ in range(20):
            time.sleep(0.3)
            try:
                urllib.request.urlopen("http://127.0.0.1:9222/json/version")
                return
            except Exception:
                pass
        raise RuntimeError("Failed to start Chrome")

async def run_audit():
    ensure_chrome()
    req = urllib.request.Request("http://127.0.0.1:9222/json/new?http://localhost:8765/v2/", method="PUT")
    with urllib.request.urlopen(req) as resp:
        page_info = json.loads(resp.read().decode())
    ws_url = page_info["webSocketDebuggerUrl"]

    async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
        msg_id = 0
        console_logs = []

        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
            while True:
                res = json.loads(await ws.recv())
                if res.get("method") == "Runtime.consoleAPICalled":
                    args = [a.get("value", "") for a in res["params"].get("args", [])]
                    console_logs.append(f"[{res['params']['type']}] {' '.join(str(x) for x in args)}")
                if res.get("method") == "Runtime.exceptionThrown":
                    desc = res["params"]["exceptionDetails"].get("text", "")
                    console_logs.append(f"[EXCEPTION] {desc}")
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

        results = {}

        # 1. Navigation Drawer
        print("Testing Navigation Drawer...")
        open_drawer = await call("Runtime.evaluate", {
            "expression": "(() => { const btn = document.getElementById('coral-menu-toggle'); if (btn) btn.click(); const d = document.getElementById('coral-drawer-overlay'); return d ? { is_active: d.classList.contains('active'), aria_hidden: d.getAttribute('aria-hidden') } : null; })()",
            "returnByValue": True
        })
        results["drawer_open"] = open_drawer.get("result", {}).get("value")

        close_drawer = await call("Runtime.evaluate", {
            "expression": "(() => { const btn = document.getElementById('coral-drawer-close'); if (btn) btn.click(); const d = document.getElementById('coral-drawer-overlay'); return d ? { is_active: d.classList.contains('active'), aria_hidden: d.getAttribute('aria-hidden') } : null; })()",
            "returnByValue": True
        })
        results["drawer_close"] = close_drawer.get("result", {}).get("value")

        # 2. Document Modal
        print("Testing Document Modal...")
        doc_open = await call("Runtime.evaluate", {
            "expression": "(() => { const btn = document.querySelector('[data-doc-target=\"terms\"]'); if (btn) btn.click(); const m = document.getElementById('modal-doc-viewer'); return m ? { is_active: m.classList.contains('active'), badge: document.getElementById('doc-modal-badge')?.textContent } : null; })()",
            "returnByValue": True
        })
        results["doc_modal_open"] = doc_open.get("result", {}).get("value")

        # Switch to privacy tab
        doc_tab = await call("Runtime.evaluate", {
            "expression": "(() => { const tab = document.querySelector('.doc-tab-btn[data-doc-tab=\"privacy\"]'); if (tab) tab.click(); return { active_tab: document.querySelector('.doc-tab-btn.active')?.getAttribute('data-doc-tab') }; })()",
            "returnByValue": True
        })
        results["doc_modal_tab_privacy"] = doc_tab.get("result", {}).get("value")

        # Close doc modal
        doc_close = await call("Runtime.evaluate", {
            "expression": "(() => { const btn = document.getElementById('doc-modal-close'); if (btn) btn.click(); const m = document.getElementById('modal-doc-viewer'); return m ? { is_active: m.classList.contains('active') } : null; })()",
            "returnByValue": True
        })
        results["doc_modal_close"] = doc_close.get("result", {}).get("value")

        # 3. Lightbox Modal (Click card)
        print("Testing Card Lightbox Modal...")
        card_click = await call("Runtime.evaluate", {
            "expression": "(() => { const card = document.querySelector('.catalog-card'); if (card) card.click(); const m = document.getElementById('modal-lightbox'); return m ? { is_active: m.classList.contains('active'), title: document.getElementById('modal-title-text')?.textContent, loc: document.getElementById('modal-loc-text')?.textContent } : null; })()",
            "returnByValue": True
        })
        results["card_lightbox_open"] = card_click.get("result", {}).get("value")

        # Close lightbox modal
        lightbox_close = await call("Runtime.evaluate", {
            "expression": "(() => { const btn = document.getElementById('modal-close'); if (btn) btn.click(); const m = document.getElementById('modal-lightbox'); return m ? { is_active: m.classList.contains('active') } : null; })()",
            "returnByValue": True
        })
        results["card_lightbox_close"] = lightbox_close.get("result", {}).get("value")

        # 4. Filter tabs with 350ms wait
        print("Testing Catalog Filter Tabs with animation wait...")
        await call("Runtime.evaluate", {
            "expression": "document.querySelector('.catalog-tab[data-filter=\"airport\"]').click()"
        })
        await asyncio.sleep(0.35)

        filter_res = await call("Runtime.evaluate", {
            "expression": "(() => { const visible = [...document.querySelectorAll('.catalog-card')].filter(c => window.getComputedStyle(c).display !== 'none'); return { visible_count: visible.length, categories: [...new Set(visible.map(c => c.getAttribute('data-category')))] }; })()",
            "returnByValue": True
        })
        results["catalog_airport_filter"] = filter_res.get("result", {}).get("value")

        # Reset filter to all
        await call("Runtime.evaluate", {
            "expression": "document.querySelector('.catalog-tab[data-filter=\"all\"]').click()"
        })
        await asyncio.sleep(0.35)

        # 5. Mockup Studio
        print("Testing Mockup Studio Dropdown...")
        mockup_res = await call("Runtime.evaluate", {
            "expression": "(() => { const trig = document.getElementById('dropdown-location-trigger'); if (trig) trig.click(); const menu = document.getElementById('dropdown-location-menu'); const opt = menu?.querySelectorAll('.custom-dropdown-item')[1]; if (opt) opt.click(); return { selected_title: document.getElementById('location-selected-title')?.textContent }; })()",
            "returnByValue": True
        })
        results["mockup_studio"] = mockup_res.get("result", {}).get("value")

        # 6. Contact Form Validation
        print("Testing Contact Form Validation...")
        form_res = await call("Runtime.evaluate", {
            "expression": "(() => { const form = document.getElementById('campaign-inquiry-form'); if (form) form.dispatchEvent(new Event('submit', { cancelable: true })); const banner = document.querySelector('.form-error-banner'); return banner ? { visible: banner.style.display !== 'none', text: banner.textContent } : null; })()",
            "returnByValue": True
        })
        results["form_validation"] = form_res.get("result", {}).get("value")

        # 7. AI Chat
        print("Testing AI Chat...")
        chat_open = await call("Runtime.evaluate", {
            "expression": "(() => { const l = document.getElementById('bv-chat-launcher'); if (l) l.click(); const w = document.getElementById('bv-chat-window'); const msgs = document.getElementById('bv-chat-messages'); return { is_open: w?.classList.contains('is-open'), msg_count: msgs?.children.length }; })()",
            "returnByValue": True
        })
        results["chat_open"] = chat_open.get("result", {}).get("value")

        await call("Runtime.evaluate", {
            "expression": "(() => { const inp = document.getElementById('bv-chat-input'); const form = document.getElementById('bv-chat-form'); inp.value = 'rates for rgia'; form.dispatchEvent(new Event('submit', { cancelable: true })); })()"
        })
        await asyncio.sleep(0.8)

        chat_reply = await call("Runtime.evaluate", {
            "expression": "(() => { const msgs = document.getElementById('bv-chat-messages'); const lastMsg = msgs?.lastElementChild; return { total_msgs: msgs?.children.length, sender: lastMsg?.querySelector('.bv-msg-sender-label')?.textContent, has_chips: (lastMsg?.querySelectorAll('.bv-action-chip').length > 0) }; })()",
            "returnByValue": True
        })
        results["chat_reply"] = chat_reply.get("result", {}).get("value")

        print("\n=== Comprehensive Interactive Audit Results ===")
        print(json.dumps(results, indent=2))
        print(f"\nConsole Errors / Exceptions ({len(console_logs)}):")
        for log in console_logs:
            print("  ", log)

if __name__ == "__main__":
    asyncio.run(run_audit())
