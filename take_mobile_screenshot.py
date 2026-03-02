import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        iphone_13 = p.devices['iPhone 13']
        browser = await p.chromium.launch()
        context = await browser.new_context(**iphone_13)
        page = await context.new_page()
        await page.goto('http://localhost:4321')
        await page.wait_for_timeout(2000)
        await page.screenshot(path='mobile_screenshot.png', full_page=True)
        print("Screenshot saved to mobile_screenshot.png")
        await browser.close()

asyncio.run(run())
