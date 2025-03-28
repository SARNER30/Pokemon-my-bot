from aiogram import F, types
from aiogram import Router
from database import cursor, conn

router = Router()

@router.message(F.text == "⚔️ Битва")
async def battle_command(message: types.Message):
    if not message.reply_to_message:
        return await message.answer("❌ Ответьте на сообщение пользователя, с которым хотите сразиться!")

    attacker_id = message.from_user.id
    defender_id = message.reply_to_message.from_user.id

    if attacker_id == defender_id:
        return await message.answer("❌ Вы не можете сражаться сами с собой!")

    # Получаем главных покемонов обоих игроков
    attacker_pokemon = cursor.execute("""
        SELECT p.* FROM pokemons p
        JOIN main_pokemon mp ON p.pokemon_id = mp.pokemon_id
        WHERE mp.user_id = ?
    """, (attacker_id,)).fetchone()

    defender_pokemon = cursor.execute("""
        SELECT p.* FROM pokemons p
        JOIN main_pokemon mp ON p.pokemon_id = mp.pokemon_id
        WHERE mp.user_id = ?
    """, (defender_id,)).fetchone()

    if not attacker_pokemon:
        return await message.answer("❌ Выберите главного покемона для битвы!")
    if not defender_pokemon:
        return await message.answer("❌ У противника нет главного покемона!")

    # Простая боевая система
    attacker_power = attacker_pokemon[5] + attacker_pokemon[6]  # атака + защита
    defender_power = defender_pokemon[5] + defender_pokemon[6]  # атака + защита

    winner_id = attacker_id if attacker_power > defender_power else defender_id
    loser_id = defender_id if attacker_power > defender_power else attacker_id

    # Награда победителю
    reward = 10000
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (reward, winner_id))

    await message.answer(
        f"⚔️ Битва!\n"
        f"{attacker_pokemon[3]} (💪 {attacker_power}) vs {defender_pokemon[3]} (💪 {defender_power})\n"
        f"🏆 Победитель получает {reward} монет!"
    )
    conn.commit()
