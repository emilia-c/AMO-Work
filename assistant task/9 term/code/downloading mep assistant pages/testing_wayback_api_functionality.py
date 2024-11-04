import asyncio
import aiohttp
import aiofiles

async def fetch_snapshot(url, save_path):
    """Fetch a specific snapshot URL asynchronously."""
    async with aiohttp.ClientSession(trust_env=True) as session:
        try:
            # Set a longer timeout
            timeout = aiohttp.ClientTimeout(total=30)  # 30 seconds
            async with session.get(url, timeout=timeout) as response:
                response.raise_for_status()  # Raise an error for bad responses
                content = await response.text()
                
                # Save HTML file
                async with aiofiles.open(save_path, 'w', encoding='utf-8') as f:
                    await f.write(content)
                print(f"Downloaded successfully from: {url}")

        except Exception as e:
            print(f"Error downloading {url}: {e}")


async def main():
    # Known working URL
    url = "https://web.archive.org/web/20190521182953/http://www.europarl.europa.eu/meps/en/96656/BORIS_ZALA/assistants"
    save_path = "boris_assistants.html"  # Change to your desired file path
    await fetch_snapshot(url, save_path)

if __name__ == "__main__":
    asyncio.run(main())
