import asyncio
import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
from datetime import datetime, timedelta
import pytz
import random

# ------------------ НАСТРОЙКИ ------------------
TOKEN = 'СЮДА_ВСТАВЬ_СВОЙ_ТОКЕН'  # Вставь свой токен
CHANNEL_ID = 123456789012345678  # ID канала для поздравлений
TIMEZONE = pytz.timezone('Europe/Moscow')
DATA_FILE = 'birthdays.json'
# ----------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

bot.remove_command('help')

COLORS = {
    'success': 0x00FF00,
    'error': 0xFF0000,
    'info': 0x00BFFF,
    'birthday': 0xFF69B4,
    'warning': 0xFFA500,
    'help': 0x9B59B6
}

# ------------------ РАБОТА С ДАННЫМИ ------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ------------------ РАСЧЁТ ВОЗРАСТА ------------------
def calculate_age(birth_date):
    today = datetime.now(TIMEZONE)
    day, month, year = map(int, birth_date.split('.'))
    
    try:
        birthday = datetime(year, month, day)
    except ValueError:
        birthday = datetime(year, 3, 1)
    
    age = today.year - birthday.year
    if (today.month, today.day) < (month, day):
        age -= 1
    
    last_digit = age % 10
    last_two_digits = age % 100
    
    if 11 <= last_two_digits <= 14:
        age_text = f"{age} лет"
    elif last_digit == 1:
        age_text = f"{age} год"
    elif 2 <= last_digit <= 4:
        age_text = f"{age} года"
    else:
        age_text = f"{age} лет"
    
    return age, age_text

# ------------------ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ------------------
def get_birthday_embed(user, date, action='add'):
    if action == 'add':
        day, month, year = date.split('.')
        months = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля',
                  '05': 'мая', '06': 'июня', '07': 'июля', '08': 'августа',
                  '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'}
        date_formatted = f"{int(day)} {months[month]} {year} года"
        
        embed = discord.Embed(
            title="🎂 День рождения добавлен!",
            description=f"Пользователь **{user.display_name}** успешно добавлен в список именинников!",
            color=COLORS['success'],
            timestamp=datetime.now(TIMEZONE)
        )
        embed.add_field(name="📅 Дата рождения", value=f"`{date_formatted}`", inline=True)
        embed.add_field(name="👤 Пользователь", value=user.mention, inline=True)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="Бот будет поздравлять каждый год!")
        return embed
    
    elif action == 'remove':
        embed = discord.Embed(
            title="🗑️ День рождения удалён!",
            description=f"День рождения пользователя **{user.display_name}** был удалён из базы.",
            color=COLORS['warning'],
            timestamp=datetime.now(TIMEZONE)
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="Если это ошибка, добавьте заново!")
        return embed
    
    elif action == 'birthday':
        age, age_text = calculate_age(date)
        day, month, year = date.split('.')
        months = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля',
                  '05': 'мая', '06': 'июня', '07': 'июля', '08': 'августа',
                  '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'}
        date_formatted = f"{int(day)} {months[month]} {year} года"
        
        wishes = [
            "Счастья, здоровья и успехов! 🍀",
            "Исполнения всех желаний! ✨",
            "Много улыбок и радости! 😊",
            "Пусть всё задуманное сбудется! 🌟",
            "Любви, добра и удачи! 💖",
            "Пусть каждый день приносит радость! 🌈",
            "Будь счастлив(а) каждый день! 💫"
        ]
        
        embed = discord.Embed(
            title=f"🎉🎂 С ДНЁМ РОЖДЕНИЯ! 🎂🎉",
            description=f"""
            **{user.mention}** сегодня празднует свой день рождения!
            
            📅 **Сегодня исполняется {age_text}** 🎈
            📆 Родился(ась): {date_formatted}
            
            🥳 Желаем тебе:
            • Счастья и здоровья
            • Удачи и успехов
            • Исполнения всех желаний
            • Много подарков и улыбок!
            
            {random.choice(wishes)}
            """,
            color=COLORS['birthday'],
            timestamp=datetime.now(TIMEZONE)
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_image(url="https://media.giphy.com/media/3o6Zt481isNVuQI1l6/giphy.gif")
        embed.set_footer(text=f"🎊 С наилучшими пожеланиями от бота! • {age_text}")
        return embed

# ------------------ КОМАНДА ПОМОЩИ ------------------
@bot.tree.command(name="bd_help", description="Показать все команды бота для дней рождения")
async def bd_help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎯 **Помощь по боту дней рождения**",
        description="Вот список всех доступных команд:",
        color=COLORS['help'],
        timestamp=datetime.now(TIMEZONE)
    )
    embed.add_field(
        name="📝 **Основные команды**",
        value="""
        `/add_bd <дата> [пользователь]` — Добавить день рождения (ДД.ММ.ГГГГ)
        `/remove_bd [пользователь]` — Удалить день рождения
        `/my_bd` — Показать мой день рождения
        `/age [пользователь]` — Узнать возраст
        `/list_bd` — Показать список всех ДР
        `/bd_help` — Показать это сообщение
        """,
        inline=False
    )
    embed.add_field(
        name="📖 **Примеры:**",
        value="""
        `/add_bd 15.07.2000` — добавить свой ДР 15 июля 2000 года
        `/add_bd 01.01.1995 @Пользователь` — добавить ДР пользователя
        `/list_bd` — посмотреть список
        """,
        inline=False
    )
    embed.set_footer(text="💡 Используй / (слеш) для вызова команд")
    await interaction.response.send_message(embed=embed)

# ------------------ ПРЕФИКСНАЯ КОМАНДА ПОМОЩИ ------------------
@bot.command(name='bothelp')
async def prefix_help(ctx):
    embed = discord.Embed(
        title="🎯 **Помощь по боту дней рождения**",
        description="Вот список всех доступных команд:",
        color=COLORS['help'],
        timestamp=datetime.now(TIMEZONE)
    )
    embed.add_field(
        name="📝 **Основные команды:**",
        value="""
        `/add_bd <дата> [пользователь]` — Добавить день рождения (ДД.ММ.ГГГГ)
        `/remove_bd [пользователь]` — Удалить день рождения
        `/my_bd` — Показать мой день рождения
        `/age [пользователь]` — Узнать возраст
        `/list_bd` — Показать список всех ДР
        `/bd_help` — Показать это сообщение
        """,
        inline=False
    )
    embed.set_footer(text="💡 Используй / (слеш) для вызова команд")
    await ctx.send(embed=embed)

# ------------------ СЛЕШ-КОМАНДЫ ------------------
@bot.tree.command(name="add_bd", description="Добавить день рождения")
@app_commands.describe(
    date="Дата в формате ДД.ММ.ГГГГ (например, 15.07.2000)",
    user="Пользователь (оставь пустым для себя)"
)
async def add_birthday(interaction: discord.Interaction, date: str, user: discord.User = None):
    if user is None:
        user = interaction.user
    
    try:
        datetime.strptime(date, '%d.%m.%Y')
    except ValueError:
        embed = discord.Embed(
            title="❌ Ошибка!",
            description="Неверный формат! Используй ДД.ММ.ГГГГ\nПример: `15.07.2000`",
            color=COLORS['error']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    day, month, year = map(int, date.split('.'))
    current_year = datetime.now(TIMEZONE).year
    if year > current_year:
        embed = discord.Embed(
            title="❌ Ошибка!",
            description="Год рождения не может быть в будущем!",
            color=COLORS['error']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if day > 31 or month > 12:
        embed = discord.Embed(
            title="❌ Ошибка!",
            description="Неверная дата! Проверь день и месяц.",
            color=COLORS['error']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    data = load_data()
    user_id = str(user.id)
    
    if user_id in data:
        embed = discord.Embed(
            title="⚠️ Предупреждение",
            description=f"День рождения для **{user.display_name}** уже есть в базе!\nДата: `{data[user_id]['date']}`",
            color=COLORS['warning']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    data[user_id] = {"name": user.display_name, "date": date}
    save_data(data)
    
    embed = get_birthday_embed(user, date, 'add')
    await interaction.response.send_message(embed=embed)
    
    # Проверка: если сегодня ДР — поздравить через 5 минут
    today = datetime.now(TIMEZONE).strftime('%d.%m')
    date_parts = date.split('.')
    date_check = f"{date_parts[0]}.{date_parts[1]}"
    
    if date_check == today:
        await interaction.followup.send("⏳ Сегодня день рождения! Проверю через 5 минут...")
        asyncio.create_task(delayed_birthday_check(user, date, interaction))

async def delayed_birthday_check(user: discord.User, date: str, interaction: discord.Interaction):
    """Отложенная проверка через 5 минут"""
    await asyncio.sleep(300)
    
    today = datetime.now(TIMEZONE).strftime('%d.%m')
    date_parts = date.split('.')
    date_check = f"{date_parts[0]}.{date_parts[1]}"
    
    if date_check != today:
        await interaction.followup.send("ℹ️ День рождения уже прошёл или ещё не наступил.")
        return
    
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        await interaction.followup.send("❌ Не удалось найти канал для поздравлений!")
        return
    
    embed = get_birthday_embed(user, date, 'birthday')
    await channel.send(f"🎉 ВНИМАНИЕ! {user.mention}", embed=embed)
    await interaction.followup.send("✅ Поздравление отправлено в канал!")
    print(f"🎉 Отложенное поздравление отправлено для {user.display_name}")

@bot.tree.command(name="remove_bd", description="Удалить день рождения")
@app_commands.describe(user="Пользователь (оставь пустым для себя)")
async def remove_birthday(interaction: discord.Interaction, user: discord.User = None):
    if user is None:
        user = interaction.user
    
    data = load_data()
    user_id = str(user.id)
    if user_id not in data:
        embed = discord.Embed(
            title="❌ Ошибка!",
            description=f"День рождения для **{user.display_name}** не найден.",
            color=COLORS['error']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    del data[user_id]
    save_data(data)
    embed = get_birthday_embed(user, None, 'remove')
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="my_bd", description="Показать мой день рождения")
async def my_birthday(interaction: discord.Interaction):
    await interaction.response.defer()
    
    try:
        data = load_data()
        user_id = str(interaction.user.id)
        
        if user_id not in data:
            embed = discord.Embed(
                title="❌ Не найден",
                description="Твой ДР не добавлен! Используй `/add_bd`",
                color=COLORS['error']
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        date = data[user_id]['date']
        age, age_text = calculate_age(date)
        
        day, month, year = date.split('.')
        months = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля',
                  '05': 'мая', '06': 'июня', '07': 'июля', '08': 'августа',
                  '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'}
        date_formatted = f"{int(day)} {months[month]} {year} года"
        
        embed = discord.Embed(
            title="🎂 Твой день рождения",
            description=f"📅 День рождения: **{date_formatted}**\n🎈 Возраст: **{age_text}**",
            color=COLORS['info'],
            timestamp=datetime.now(TIMEZONE)
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="🎉 Готовься к празднику!")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"❌ Ошибка в my_bd: {e}")
        await interaction.followup.send("❌ Произошла ошибка. Попробуй позже.")

@bot.tree.command(name="list_bd", description="Показать все дни рождения")
async def list_birthdays(interaction: discord.Interaction):
    await interaction.response.defer()
    
    try:
        data = load_data()
        
        if not data:
            embed = discord.Embed(
                title="📭 Список пуст",
                description="Добавьте ДР с помощью `/add_bd`!",
                color=COLORS['info']
            )
            await interaction.followup.send(embed=embed)
            return
        
        months = {
            '01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
            '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
            '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'
        }
        
        # 🔥 СОРТИРОВКА: сначала по месяцу, потом по дню
        def sort_key(item):
            date = item[1]['date']  # ДД.ММ.ГГГГ
            day, month, year = date.split('.')
            return (int(month), int(day))
        
        sorted_users = sorted(data.items(), key=sort_key)
        
        description = "🎂 **Список всех дней рождений:**\n"
        current_month = None
        
        for user_id, info in sorted_users:
            date_parts = info['date'].split('.')
            day = date_parts[0]
            month = date_parts[1]
            year = date_parts[2]
            
            if month != current_month:
                current_month = month
                description += f"\n**📅 {months[month]}:**\n"
            
            name = info['name']
            description += f"  • {int(day)} число — {name} ({year} г.)\n"
        
        if len(description) > 4000:
            first_part = description[:3997] + "..."
            embed = discord.Embed(
                title="📅 Календарь дней рождений (часть 1)",
                description=first_part,
                color=COLORS['info'],
                timestamp=datetime.now(TIMEZONE)
            )
            embed.set_footer(text=f"Всего: {len(data)} именинников")
            await interaction.followup.send(embed=embed)
            
            remaining = description[3997:]
            chunk_number = 2
            
            while remaining:
                chunk = remaining[:3997]
                remaining = remaining[3997:]
                
                embed = discord.Embed(
                    title=f"📅 Календарь дней рождений (часть {chunk_number})",
                    description=chunk,
                    color=COLORS['info'],
                    timestamp=datetime.now(TIMEZONE)
                )
                await interaction.followup.send(embed=embed)
                chunk_number += 1
        else:
            embed = discord.Embed(
                title="📅 Календарь дней рождений",
                description=description,
                color=COLORS['info'],
                timestamp=datetime.now(TIMEZONE)
            )
            embed.set_footer(text=f"Всего: {len(data)} именинников")
            await interaction.followup.send(embed=embed)
            
    except Exception as e:
        print(f"❌ Ошибка в list_bd: {e}")
        await interaction.followup.send("❌ Произошла ошибка при загрузке списка. Попробуй позже.")

@bot.tree.command(name="age", description="Узнать возраст пользователя")
@app_commands.describe(user="Пользователь (оставь пустым для себя)")
async def get_age(interaction: discord.Interaction, user: discord.User = None):
    await interaction.response.defer()
    
    try:
        if user is None:
            user = interaction.user
        
        data = load_data()
        user_id = str(user.id)
        
        if user_id not in data:
            embed = discord.Embed(
                title="❌ Не найден",
                description=f"ДР для **{user.display_name}** не добавлен!",
                color=COLORS['error']
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        date = data[user_id]['date']
        age, age_text = calculate_age(date)
        
        day, month, year = date.split('.')
        months = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля',
                  '05': 'мая', '06': 'июня', '07': 'июля', '08': 'августа',
                  '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'}
        date_formatted = f"{int(day)} {months[month]} {year} года"
        
        embed = discord.Embed(
            title=f"🎂 Возраст {user.display_name}",
            description=f"📅 День рождения: **{date_formatted}**\n🎈 Возраст: **{age_text}**",
            color=COLORS['info'],
            timestamp=datetime.now(TIMEZONE)
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"❌ Ошибка в age: {e}")
        await interaction.followup.send("❌ Произошла ошибка. Попробуй позже.")

@bot.tree.command(name="force_check", description="Принудительная проверка именинников (только для админов)")
async def force_check(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="⛔ Доступ запрещён",
            description="Только администраторы!",
            color=COLORS['error']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.send_message("🔄 Выполняю проверку...")
    await check_birthdays()
    embed = discord.Embed(title="✅ Проверка выполнена", color=COLORS['success'])
    await interaction.edit_original_response(content=None, embed=embed)

@bot.tree.command(name="ping", description="Проверить задержку бота")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Понг!",
        description=f"Задержка: **{latency}мс**",
        color=COLORS['success'] if latency < 100 else COLORS['warning'],
        timestamp=datetime.now(TIMEZONE)
    )
    await interaction.response.send_message(embed=embed)

# ------------------ АВТОУДАЛЕНИЕ УШЕДШИХ ------------------
@bot.event
async def on_member_remove(member):
    data = load_data()
    user_id = str(member.id)
    
    if user_id in data:
        del data[user_id]
        save_data(data)
        print(f"🗑️ {member.display_name} покинул сервер — ДР удалён из базы")
        
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="👋 Пользователь покинул сервер",
                description=f"**{member.display_name}** покинул сервер.\nЕго день рождения автоматически удалён из базы.",
                color=COLORS['warning'],
                timestamp=datetime.now(TIMEZONE)
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

# ------------------ АВТОПОЗДРАВЛЕНИЕ ------------------
@tasks.loop(time=datetime.strptime('09:00', '%H:%M').time())
async def check_birthdays():
    await bot.wait_until_ready()
    
    print(f"⏰ Запущена проверка в {datetime.now(TIMEZONE).strftime('%H:%M:%S')}")
    
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"❌ Канал с ID {CHANNEL_ID} не найден!")
        return
    
    today = datetime.now(TIMEZONE).strftime('%d.%m')
    print(f"📅 Сегодня: {today}")
    data = load_data()
    print(f"📊 В базе: {len(data)} записей")
    
    birthday_users = []
    
    for user_id, info in data.items():
        date_parts = info['date'].split('.')
        date_check = f"{date_parts[0]}.{date_parts[1]}"
        
        print(f"🔍 Проверяю {info['name']}: {date_check} == {today}? {'ДА' if date_check == today else 'НЕТ'}")
        
        if date_check == today:
            try:
                user = await bot.fetch_user(int(user_id))
                birthday_users.append(user)
                print(f"✅ Найден именинник: {user.display_name}")
            except:
                del data[user_id]
                save_data(data)
                print(f"🗑️ {info['name']} удалён из базы (не найден в Discord)")
    
    if birthday_users:
        print(f"🎉 Найдено {len(birthday_users)} именинников!")
        for user in birthday_users:
            user_data = data.get(str(user.id))
            if user_data:
                date = user_data['date']
                embed = get_birthday_embed(user, date, 'birthday')
                await channel.send(f"🎉 ВНИМАНИЕ! {user.mention}", embed=embed)
                print(f"✅ Поздравление отправлено для {user.display_name}")
    else:
        print("📭 Именинников сегодня нет")
    
    # Проверка на завтрашних именинников
    tomorrow = (datetime.now(TIMEZONE) + timedelta(days=1)).strftime('%d.%m')
    for user_id, info in data.items():
        date_parts = info['date'].split('.')
        date_check = f"{date_parts[0]}.{date_parts[1]}"
        
        if date_check == tomorrow:
            try:
                user = await bot.fetch_user(int(user_id))
                embed = discord.Embed(
                    title="⏰ Напоминание!",
                    description=f"Завтра день рождения у **{user.display_name}** ({user.mention})!\nНе забудьте поздравить! 🎂",
                    color=COLORS['warning'],
                    timestamp=datetime.now(TIMEZONE)
                )
                embed.set_thumbnail(url=user.display_avatar.url)
                await channel.send(embed=embed)
                print(f"⏰ Напоминание отправлено для {user.display_name} (завтра ДР)")
            except:
                pass
    
    print("✅ Проверка завершена!")

# ------------------ ЗАПУСК БОТА ------------------
@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} запущен!')
    print(f'📊 На сервере: {len(bot.guilds)} гильдий')
    
    try:
        synced = await bot.tree.sync()
        print(f'✅ Синхронизировано {len(synced)} слеш-команд!')
        print('📋 Доступные команды:')
        for cmd in synced:
            print(f'  • /{cmd.name} — {cmd.description}')
    except Exception as e:
        print(f'❌ Ошибка синхронизации: {e}')
    
    check_birthdays.start()
    print('✅ Ежедневная проверка запущена!')
    
    await check_birthdays()
    print('✅ Первичная проверка выполнена!')

if __name__ == '__main__':
    bot.run(TOKEN)
