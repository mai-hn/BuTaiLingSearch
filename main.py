import json
from urllib.parse import quote

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


BASE_URL = "https://web5.mukaku.com"
SEARCH_CARD_SELECTOR = ".video-card"
RESOURCE_GROUP_SELECTOR = ".resource-items-group.modern-list"


def print_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def collect_search_results(page, keyword):
    api_items = []

    def capture_video_list(response):
        nonlocal api_items
        if "getVideoList" not in response.url:
            return

        try:
            payload = response.json()
        except Exception:
            return

        api_items = payload.get("data", {}).get("data", []) or []

    page.on("response", capture_video_list)
    page.goto(f"{BASE_URL}/search?sb={quote(keyword)}", wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")

    cards = page.locator(SEARCH_CARD_SELECTOR)
    try:
        cards.first.wait_for(state="attached", timeout=10_000)
    except PlaywrightTimeoutError:
        return []

    dom_items = cards.evaluate_all(
        """cards => cards.map((card, index) => ({
            index: index + 1,
            title: card.querySelector(".card-title")?.getAttribute("title")
                || card.querySelector(".card-title")?.textContent?.trim()
                || card.querySelector("img")?.getAttribute("alt")
                || "",
            clickable: {
                selector: ".video-card",
                index: index
            }
        }))"""
    )

    results = []
    for index, dom_item in enumerate(dom_items):
        api_item = api_items[index] if index < len(api_items) else {}
        idcode = api_item.get("idcode")
        link = f"{BASE_URL}/mv/{idcode}" if idcode else ""

        results.append(
            {
                "index": dom_item["index"],
                "title": api_item.get("title") or dom_item["title"],
                "link": link,
                "clickable": dom_item["clickable"],
            }
        )

    return results


def open_selected_result(page, selected_item):
    current_url = page.url
    clickable = selected_item.get("clickable", {})

    try:
        page.locator(clickable["selector"]).nth(clickable["index"]).click(
            timeout=5_000,
            force=True,
        )
        page.wait_for_timeout(1_500)
    except Exception:
        pass

    if page.url == current_url:
        page.goto(selected_item["link"], wait_until="domcontentloaded")

    page.wait_for_load_state("networkidle")


def collect_resources(page):
    group = page.locator(RESOURCE_GROUP_SELECTOR)
    group.wait_for(state="attached", timeout=10_000)

    return group.locator(".resource-item-card-modern").evaluate_all(
        """cards => cards.map(card => ({
            title: card.querySelector(".text-wrapper")?.textContent?.trim() || "",
            magnet: card.querySelector(".magnet-link[href^='magnet:']")?.href || ""
        })).filter(item => item.title && item.magnet)"""
    )


def main():
    keyword = input("请输入搜索关键词：").strip()
    if not keyword:
        print("搜索关键词不能为空")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        search_results = collect_search_results(page, keyword)
        print_json(search_results)

        if not search_results:
            browser.close()
            return

        selected = input("请输入要点击的元素序号：").strip()
        try:
            selected_index = int(selected)
        except ValueError:
            print("请输入数字序号")
            browser.close()
            return

        selected_item = next(
            (item for item in search_results if item["index"] == selected_index),
            None,
        )
        if not selected_item:
            print(f"没有找到序号 {selected_index}")
            browser.close()
            return

        open_selected_result(page, selected_item)
        resources = collect_resources(page)
        print_json(
            {
                "selected": {
                    "index": selected_item["index"],
                    "title": selected_item["title"],
                    "link": selected_item["link"],
                },
                "resources": resources,
            }
        )

        browser.close()


if __name__ == "__main__":
    main()
