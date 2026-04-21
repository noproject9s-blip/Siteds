from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(slots=True)
class Config:
    bot_token: str
    admin_ids: set[int]
    currency_name: str
    rub_per_coin: int
    db_path: Path



def load_config() -> Config:
    load_dotenv()

    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise ValueError("BOT_TOKEN is required")

    admin_raw = os.getenv("ADMIN_IDS", "")
    admin_ids: set[int] = set()
    for value in admin_raw.split(","):
        value = value.strip()
        if value:
            admin_ids.add(int(value))

    currency_name = os.getenv("CURRENCY_NAME", "NOVA")
    rub_per_coin = int(os.getenv("RUB_PER_COIN", "15"))
    db_path = Path(os.getenv("DB_PATH", "data/shop.json"))

    return Config(
        bot_token=token,
        admin_ids=admin_ids,
        currency_name=currency_name,
        rub_per_coin=rub_per_coin,
        db_path=db_path,
    )
