#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Code By: 0xdolan
# GitHub: https://github.com/0xdolan/Ottoman_Dictionary

import asyncio
import json
import logging
import os
from pathlib import Path

import aiofiles  # type: ignore
import aiohttp  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from rich.progress import Progress

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Create a logger
logger = logging.getLogger(__name__)

# List of URLs to scrape
urls = [
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h11.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h12.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h13.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h14.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h15.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h16.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h17.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h18.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h19.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h20.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h21.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h22.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h23.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h24.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h25.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h26.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h27.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h28.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h29.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h30.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h31.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h32.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h33.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h34.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h35.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h36.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h38.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h39.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h40.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h41.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h42.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h43.html",
    "https://www.osmanlicasozlukler.com/ingilizce/sozluk-h44.html",
]

CURRENT_PATH = Path(__file__).parent
data_folder = CURRENT_PATH / "data"
visited_file = CURRENT_PATH / "visited_urls.json"
images_folder = CURRENT_PATH / "images"
data_folder.mkdir(exist_ok=True)  # Create the data folder if it doesn't exist
images_folder.mkdir(exist_ok=True)  # Create the images folder if it doesn't exist


# Define the function to download images
async def download_image(url, session):
    try:
        async with session.get(url, allow_redirects=True) as response:
            if response.status == 200:
                final_url = str(response.url)
                filename = os.path.basename(final_url)
                image_path = images_folder / filename

                # Check if the image already exists
                if image_path.exists():
                    logger.debug(f"Image already exists: {image_path}")
                    return str(image_path)

                async with aiofiles.open(image_path, "wb") as file:
                    await file.write(await response.read())
                logger.debug(f"Image successfully downloaded: {image_path}")
                return str(image_path)
            else:
                logger.debug(
                    f"Failed to retrieve image. Status code: {response.status}"
                )
                return None
    except aiohttp.ClientError as e:
        logger.error(f"Request failed: {e}")
        return None


# Load visited URLs
async def load_visited_urls():
    if visited_file.exists():
        async with aiofiles.open(visited_file, "r", encoding="utf-8") as f:
            visited_urls = set(json.loads(await f.read()))
    else:
        visited_urls = set()
    return visited_urls


# Define the function to scrape data
async def scrape_data(urls, visited_urls):
    async with aiohttp.ClientSession() as session:
        with Progress() as progress:
            task = progress.add_task("[cyan]Scraping...", total=len(urls) * 180)

            for link in urls:
                for page in range(1, 180):
                    new_link = f"{link}?s={page}"
                    if new_link in visited_urls:
                        continue
                    try:
                        async with session.get(new_link) as response:
                            if response.status == 200:
                                soup = BeautifulSoup(await response.text(), "lxml")
                                box = soup.select_one(
                                    "body > div > div.main-content > div > section.section.bg-white > div > div.row.g-3"
                                )
                                if box:
                                    for button in box.find_all("div"):
                                        for a in button.find_all("a"):
                                            url = a.get("href")
                                            if url in visited_urls:
                                                continue
                                            title = a.get("title")
                                            entry = a.text.strip()

                                            # Check if JSON file for this entry already exists
                                            filename = f"{title}.json".replace(" ", "_")
                                            entry_path = data_folder / filename
                                            if entry_path.exists():
                                                logger.debug(
                                                    f"Entry already exists: {entry_path}"
                                                )
                                                continue

                                            new_response = await session.get(url)
                                            new_soup = BeautifulSoup(
                                                await new_response.text(), "lxml"
                                            )
                                            card = new_soup.select_one(
                                                "body > div > div.main-content > div > section.section.bg-white > div > div.col-lg-12 > div.card.job-detail.overflow-hidden > div > div > div"
                                            )
                                            header = card.find("h5", "mb-1").text
                                            details_html = str(card)
                                            details = card.text.strip()
                                            imgs = card.find_all("img")
                                            image_urls = []
                                            image_names = []
                                            if imgs:
                                                image_urls = [
                                                    await download_image(
                                                        img.get("src"), session
                                                    )
                                                    for img in imgs
                                                ]
                                                image_names = [
                                                    Path(image).name
                                                    for image in image_urls
                                                    if image
                                                ]
                                            result = {
                                                "url": url,
                                                "title": title,
                                                "entry": entry,
                                                "header": header,
                                                "details_html": details_html,
                                                "details": details,
                                                "image_urls": image_urls,
                                                "image_names": image_names,
                                            }

                                            # Write the entry to its own JSON file
                                            async with aiofiles.open(
                                                entry_path, "w", encoding="utf-8"
                                            ) as f:
                                                await f.write(
                                                    json.dumps(
                                                        result,
                                                        ensure_ascii=False,
                                                        indent=4,
                                                    )
                                                )

                                            visited_urls.add(url)
                                            async with aiofiles.open(
                                                visited_file, "w", encoding="utf-8"
                                            ) as f:
                                                await f.write(
                                                    json.dumps(
                                                        list(visited_urls),
                                                        ensure_ascii=False,
                                                        indent=4,
                                                    )
                                                )
                            progress.advance(task)
                    except aiohttp.ClientError as e:
                        logger.error(f"Request failed: {e}")
                        continue


# Main function
async def main():
    visited_urls = await load_visited_urls()
    await scrape_data(urls, visited_urls)


if __name__ == "__main__":
    asyncio.run(main())
