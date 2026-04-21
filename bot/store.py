from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(slots=True)
class Item:
    id: int
    title: str
    category: str
    description: str
    price: int
    stock: int
    payload: str


class Store:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            self._save({"users": {}, "items": [], "last_item_id": 0})

    def _load(self) -> dict:
        return json.loads(self.db_path.read_text(encoding="utf-8"))

    def _save(self, data: dict) -> None:
        self.db_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def ensure_user(self, user_id: int) -> None:
        data = self._load()
        users = data["users"]
        key = str(user_id)
        if key not in users:
            users[key] = {"balance": 0, "purchases": []}
            self._save(data)

    def get_balance(self, user_id: int) -> int:
        self.ensure_user(user_id)
        data = self._load()
        return int(data["users"][str(user_id)]["balance"])

    def add_balance(self, user_id: int, amount: int) -> None:
        self.ensure_user(user_id)
        data = self._load()
        user = data["users"][str(user_id)]
        user["balance"] = int(user["balance"]) + amount
        self._save(data)

    def add_item(
        self,
        title: str,
        category: str,
        description: str,
        price: int,
        stock: int,
        payload: str,
    ) -> Item:
        data = self._load()
        data["last_item_id"] += 1
        item = Item(
            id=data["last_item_id"],
            title=title,
            category=category,
            description=description,
            price=price,
            stock=stock,
            payload=payload,
        )
        data["items"].append(asdict(item))
        self._save(data)
        return item

    def list_items(self) -> list[Item]:
        data = self._load()
        return [Item(**item) for item in data["items"] if item["stock"] > 0]

    def stock_report(self) -> list[Item]:
        data = self._load()
        return [Item(**item) for item in data["items"]]

    def buy(self, user_id: int, item_id: int) -> tuple[bool, str]:
        self.ensure_user(user_id)
        data = self._load()
        user = data["users"][str(user_id)]

        item = next((x for x in data["items"] if x["id"] == item_id), None)
        if not item:
            return False, "Товар не найден."
        if item["stock"] <= 0:
            return False, "Товар закончился."
        if user["balance"] < item["price"]:
            return False, "Недостаточно NOVA на балансе."

        user["balance"] -= item["price"]
        item["stock"] -= 1
        user["purchases"].append(
            {
                "item_id": item["id"],
                "title": item["title"],
                "payload": item["payload"],
            }
        )
        self._save(data)

        return True, item["payload"]
