import asyncio
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup
from lxml import html
from tqdm import tqdm


async def download_file(session, url_link, path, pbar):
    pbar.set_description(f"Downloading file: {path}")
    async with session.get(url_link) as response:
        with open(path, 'wb') as f:
            while True:
                chunk = await response.content.read(1024)
                if not chunk:
                    break
                f.write(chunk)
    pbar.set_description(f"Downloaded file: {path}")
    pbar.update()


async def download_mp3_files(url_link: str, folder: str) -> None:
    # Send a GET request to the webpage
    async with aiohttp.ClientSession() as session:
        async with session.get(url_link) as response:
            text = await response.text()

            tree = html.fromstring(text)

            # Find the ol tag with the xpath (//*[@id="post-72943"]/div/div/ol)
            ol_tag = tree.xpath('//*[@id="post-72943"]/div/div/ol')[0]

            # Find all li tags under the ol tag
            li_tags = ol_tag.findall('li')

            # Create a directory to save the downloaded files
            Path(folder).mkdir(exist_ok=True)

            pbar = tqdm(total=len(li_tags), ncols=70)

            # Loop through each li tag
            for li in li_tags:
                # Extract the mp3 file url from the data-target attribute
                mp3_url = li.get('data-target')

                # Extract the file name from the url
                file_name = Path(mp3_url).name

                # Save the mp3 file in the specified directory
                path = Path(folder) / file_name
                await download_file(session, mp3_url, path, pbar)

            pbar.close()


# URL of the page to be scraped
url = "https://www.emaanlibrary.com/lecture/audio-complete-quran-with-urdu-translation/"
directory = 'Quran'

# Run the async function
asyncio.run(download_mp3_files(url, directory))
