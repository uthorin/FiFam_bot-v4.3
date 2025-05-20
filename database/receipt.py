from typing import Optional



async def add_receipt(db, user_id: int, total: float, purchase_date: Optional[str] = None) -> int:
    query = """
    INSERT INTO receipts (user_id, total, purchase_date)
    VALUES ($1, $2, COALESCE($3, CURRENT_DATE))
    RETURNING id;
    """
    async with db.acquire() as conn:
        receipt_id = await conn.fetchval(query, user_id, total, purchase_date)
        return receipt_id

async def add_receipt_item(db, receipt_id: int, name: str, category: str, price: float, purchase_date: Optional[str] = None):
    query = """
    INSERT INTO receipt_items (receipt_id, name, category, price, purchase_date)
    VALUES ($1, $2, $3, $4, COALESCE($5, CURRENT_DATE));
    """
    async with db.acquire() as conn:
        await conn.execute(query, receipt_id, name, category, price, purchase_date)
