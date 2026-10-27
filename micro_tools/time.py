from datetime import datetime, timezone
import asyncio
from typing import Optional

async def get_utc():
    return datetime.now(timezone.utc)