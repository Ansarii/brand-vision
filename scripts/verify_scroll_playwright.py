#!/usr/bin/env python3
"""
Playwright-based rigorous verification of scroll positions and visual landings
across Desktop and Mobile for Brand Vision Media.
"""

import json
import os
from playwright.sync_api import sync_playwright

def verify_scroll():
    os.makedirs("scratch/qc", exist_ok=True)
    results = {}

    with sync_playwright() as p:
        # 1. Desktop Audit (1440x900)
        print("=== Desktop Audit (1440x900) ===")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.goto("http://localhost:8765/v2/", wait_until="networkidle")
        page.wait_for_timeout(1000)

        # Desktop Test 1: Click "Get a Quote" in header
        print("Clicking 'Get a Quote' on Desktop...")
        page.click(".coral-quote-btn")
        page.wait_for_timeout(1500)

        metrics_quote = page.evaluate("""() => {
            const target = document.getElementById('contact');
            const header = document.querySelector('.coral-site-header');
            const hRect = header ? header.getBoundingClientRect() : null;
            const tRect = target ? target.getBoundingClientRect() : null;
            const tagline = target ? target.querySelector('.tagline') : null;
            const tagRect = tagline ? tagline.getBoundingClientRect() : null;
            const title = target ? target.querySelector('.section-title') : null;
            const titleRect = title ? title.getBoundingClientRect() : null;
            return {
                scrollY: window.scrollY,
                headerHeight: hRect ? hRect.height : null,
                headerBottom: hRect ? hRect.bottom : null,
                targetTop: tRect ? tRect.top : null,
                taglineTop: tagRect ? tagRect.top : null,
                titleTop: titleRect ? titleRect.top : null,
                clearanceBelowHeader: (tagRect && hRect) ? (tagRect.top - hRect.bottom) : null
            };
        }""")
        results["desktop_get_quote"] = metrics_quote
        print("Desktop 'Get a Quote' Metrics:", json.dumps(metrics_quote, indent=2))
        page.screenshot(path="scratch/qc/verified_desktop_get_quote.png")

        # Desktop Test 2: Click "Portfolio" in header
        print("Clicking 'Portfolio' on Desktop...")
        page.click("a[href='#inventory']")
        page.wait_for_timeout(1500)
        metrics_port = page.evaluate("""() => {
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
        }""")
        results["desktop_portfolio"] = metrics_port
        print("Desktop 'Portfolio' Metrics:", json.dumps(metrics_port, indent=2))
        page.screenshot(path="scratch/qc/verified_desktop_portfolio.png")

        context.close()

        # 2. Mobile Audit (390x844)
        print("\n=== Mobile Audit (390x844) ===")
        m_context = browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2
        )
        m_page = m_context.new_page()
        m_page.goto("http://localhost:8765/v2/", wait_until="networkidle")
        m_page.wait_for_timeout(1000)

        # Mobile Test 1: Click "Get a Quote" in mobile bottom bar
        print("Clicking 'Get a Quote' in mobile bottom bar...")
        m_page.click(".mv-quote")
        m_page.wait_for_timeout(1500)

        m_metrics_quote = m_page.evaluate("""() => {
            const target = document.getElementById('contact');
            const header = document.querySelector('.coral-site-header');
            const mvBar = document.querySelector('.mv-bar');
            const hRect = header ? header.getBoundingClientRect() : null;
            const barRect = mvBar ? mvBar.getBoundingClientRect() : null;
            const tRect = target ? target.getBoundingClientRect() : null;
            const tagline = target ? target.querySelector('.tagline') : null;
            const tagRect = tagline ? tagline.getBoundingClientRect() : null;
            const title = target ? target.querySelector('.section-title') : null;
            const titleRect = title ? title.getBoundingClientRect() : null;
            const form = target ? target.querySelector('.contact-modern-layout') : null;
            const formRect = form ? form.getBoundingClientRect() : null;
            return {
                scrollY: window.scrollY,
                headerHeight: hRect ? hRect.height : null,
                headerBottom: hRect ? hRect.bottom : null,
                mvBarTop: barRect ? barRect.top : null,
                targetTop: tRect ? tRect.top : null,
                taglineTop: tagRect ? tagRect.top : null,
                titleTop: titleRect ? titleRect.top : null,
                formTop: formRect ? formRect.top : null,
                clearanceBelowHeader: (tagRect && hRect) ? (tagRect.top - hRect.bottom) : null
            };
        }""")
        results["mobile_get_quote"] = m_metrics_quote
        print("Mobile 'Get a Quote' Metrics:", json.dumps(m_metrics_quote, indent=2))
        m_page.screenshot(path="scratch/qc/verified_mobile_get_quote.png")

        m_context.close()
        browser.close()

    with open("scratch/qc/scroll_audit_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved scratch/qc/scroll_audit_results.json")

if __name__ == "__main__":
    verify_scroll()
