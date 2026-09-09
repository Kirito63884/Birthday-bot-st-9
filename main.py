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
CHANNEL_ID = 1546509618480549910# ID канала для поздравлений
TIMEZONE = pytz.timezone('Europe/Moscow')
DATA_FILE = 'birthdays.json'  # Файл будет в папке с ботом
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
            "Любви, добра и удачи! 💖"
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

# ------------------ КОМАНДЫ ------------------
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
        embed = discord.Embed(title="❌ Ошибка!", description="Неверный формат! Используй ДД.ММ.ГГГГ", color=COLORS['error'])
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    data = load_data()
    data[str(user.id)] = {"name": user.display_name, "date": date}
    save_data(data)
    
    embed = get_birthday_embed(user, date, 'add')
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="remove_bd", description="Удалить день рождения")
@app_commands.describe(user="Пользователь (оставь пустым для себя)")
async def remove_birthday(interaction: discord.Interaction, user: discord.User = None):
    if user is None:
        user = interaction.user
    
    data = load_data()
    user_id = str(user.id)
    if user_id not in data:
        embed = discord.Embed(title="❌ Ошибка!", description=f"День рождения для **{user.display_name}** не найден.", color=COLORS['error'])
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    del data[user_id]
    save_data(data)
    embed = get_birthday_embed(user, None, 'remove')
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="my_bd", description="Показать мой день рождения")
async def my_birthday(interaction: discord.Interaction):
    data = load_data()
    user_id = str(interaction.user.id)
    if user_id not in data:
        embed = discord.Embed(title="❌ Не найден", description="Твой ДР не добавлен!", color=COLORS['error'])
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    date = data[user_id]['date']
    age, age_text = calculate_age(date)
    embed = discord.Embed(
        title="🎂 Твой день рождения",
        description=f"📅 День рождения: **{date}**\n🎈 Возраст: **{age_text}**",
        color=COLORS['info'],
        timestamp=datetime.now(TIMEZONE)
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="list_bd", description="Показать все дни рождения")
async def list_birthdays(interaction: discord.Interaction):
    data = load_data()
    if not data:
        embed = discord.Embed(title="📭 Список пуст", description="Добавьте ДР с помощью `/add_bd`!", color=COLORS['info'])
        await interaction.response.send_message(embed=embed)
        return
    
    sorted_users = sorted(data.items(), key=lambda x: x[1]['date'])
    months = {'01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
              '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
              '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'}
    
    description = "🎂 **Список всех дней рождений:**\n\n"
    current_month = None
    
    for user_id, info in sorted_users:
        date_parts = info['date'].split('.')
        month = date_parts[1]
        day = date_parts[0]
        year = date_parts[2]
        
        if month != current_month:
            current_month = month
            description += f"\n**📅 {months[month]}:**\n"
        
        try:
            user = await bot.fetch_user(int(user_id))
            name = user.mention
        except:
            name = f"~~{info['name']}~~ *(покинул сервер)*"
        
        description += f"  • {int(day)} число — {name} ({year} г.)\n"
    
    embed = discord.Embed(
        title="📅 Календарь дней рождений",
        description=description,
        color=COLORS['info'],
        timestamp=datetime.now(TIMEZONE)
    )
    embed.set_footer(text=f"Всего: {len(data)} именинников")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="age", description="Узнать возраст пользователя")
@app_commands.describe(user="Пользователь (оставь пустым для себя)")
async def get_age(interaction: discord.Interaction, user: discord.User = None):
    if user is None:
        user = interaction.user
    
    data = load_data()
    user_id = str(user.id)
    if user_id not in data:
        embed = discord.Embed(title="❌ Не найден", description=f"ДР для **{user.display_name}** не добавлен!", color=COLORS['error'])
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    date = data[user_id]['date']
    age, age_text = calculate_age(date)
    
    embed = discord.Embed(
        title=f"🎂 Возраст {user.display_name}",
        description=f"📅 День рождения: **{date}**\n🎈 Возраст: **{age_text}**",
        color=COLORS['info'],
        timestamp=datetime.now(TIMEZONE)
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="force_check", description="Принудительная проверка именинников (только для админов)")
async def force_check(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(title="⛔ Доступ запрещён", description="Только администраторы!", color=COLORS['error'])
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
    
    print("✅ Проверка завершена!")

# ------------------ ЗАПУСК БОТА ------------------
@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} запущен!')
    print(f'📊 На сервере: {len(bot.guilds)} гильдий')
    
    try:
        synced = await bot.tree.sync()
        print(f'✅ Синхронизировано {len(synced)} слеш-команд!')
    except Exception as e:
        print(f'❌ Ошибка синхронизации: {e}')
    
    # Запускаем ежедневную проверку
    check_birthdays.start()
    print('✅ Ежедневная проверка запущена!')
    
    # Проверяем именинников СРАЗУ при запуске
    await check_birthdays()
    print('✅ Первичная проверка выполнена!')

if __name__ == '__main__':
    bot.run(TOKEN)
