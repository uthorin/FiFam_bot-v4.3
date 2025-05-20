from typing import Optional
from datetime import date

async def get_detailed_statistics(pool, user_id: int, start_date: date, end_date: date) -> dict:
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT type, category, SUM(amount) as sum
            FROM transactions
            WHERE user_id = $1 AND date BETWEEN $2 AND $3
            GROUP BY type, category

            UNION ALL

            SELECT 'expense' as type, ri.category, SUM(ri.price) as sum
            FROM receipt_items ri
            JOIN receipts r ON ri.receipt_id = r.id
            WHERE r.user_id = $1 AND ri.purchase_date BETWEEN $2 AND $3
            GROUP BY ri.category
        """, user_id, start_date, end_date)

    income = {}
    expense = {}

    for row in rows:
        type_, category, amount = row["type"], row["category"], float(row["sum"])
        if type_ == "income":
            income[category] = income.get(category, 0) + amount
        elif type_ == "expense":
            expense[category] = expense.get(category, 0) + amount

    total_income = sum(income.values())
    total_expense = sum(expense.values())

    return {
        "income": income,
        "expense": expense,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense
    }


async def get_transactions_for_analysis(pool, user_id: int):
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT type, amount, category, date
            FROM transactions
            WHERE user_id = $1

            UNION ALL

            SELECT 'expense' as type, ri.price as amount, ri.category, ri.purchase_date as date
            FROM receipt_items ri
            JOIN receipts r ON ri.receipt_id = r.id
            WHERE r.user_id = $1

            ORDER BY date DESC LIMIT 500
        """, user_id)

    return [
        {
            "type": row["type"],
            "amount": float(row["amount"]),
            "category": row["category"],
            "date": row["date"]
        }
        for row in rows
    ]


async def add_user(pool, telegram_id: int, full_name: str):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (telegram_id, full_name)
            VALUES ($1, $2)
            ON CONFLICT (telegram_id) DO NOTHING
        """, telegram_id, full_name)

async def add_transaction(pool, user_id: int, type_: str, amount: float, category: str, date_, description: str = ""):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO transactions (user_id, type, amount, category, date, description)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, user_id, type_, amount, category, date_, description)