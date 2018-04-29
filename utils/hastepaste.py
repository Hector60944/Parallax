import aiohttp

_session = aiohttp.ClientSession()
_headers = {
    'User-Agent': 'Parallax (https://github.com/Devoxin/Parallax)',
    'Content-Type': 'application/x-www-form-urlencoded'
}


async def create(content: str):
    async with _session.post('https://hastepaste.com/api/create',
                             data=f'raw=false&text={content}', headers=_headers) as res:
        if res.status == 200:
            return await res.text()
