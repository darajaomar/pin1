import json
import requests
import tempfile
from playwright.sync_api import sync_playwright
from flask import Flask, request

app = Flask(__name__)

PINTEREST_EMAIL = "omarghost007@gmail.com"
PINTEREST_PASSWORD = "Lowkey.123?"
BOARD_NAME = "Tasteswinebar"

def download_image(url):
    response = requests.get(url)
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp.write(response.content)
    temp.close()
    return temp.name

@app.post("/pin")
def create_pin():
    data = request.json

    title = data.get("title")
    description = data.get("description")
    image_url = data.get("image_url")
    link = data.get("link")

    img_path = download_image(image_url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Login
        page.goto("https://www.pinterest.com/login/")
        page.fill('input[type="email"]', PINTEREST_EMAIL)
        page.fill('input[type="password"]', PINTEREST_PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        # Go to create pin
        page.goto("https://www.pinterest.com/pin-creation-tool/")
        page.wait_for_timeout(3000)

        # Upload image
        page.set_input_files('input[type="file"]', img_path)

        # Fill fields
        page.fill('textarea[data-test-id="pin-draft-title"]', title[:100])
        page.fill('textarea[data-test-id="pin-draft-description"]', description[:500])
        page.fill('input[data-test-id="pin-draft-destination-link"]', link)

        # Choose board
        page.click('[data-test-id="board-dropdown-select-button"]')
        page.click(f'text="{BOARD_NAME}"')

        # Publish pin
        page.click('[data-test-id="pin-draft-publish-button"]')

        # Wait for Pinterest to finish
        page.wait_for_timeout(6000)

        browser.close()

    return {"status": "success", "message": "Pin uploaded."}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
