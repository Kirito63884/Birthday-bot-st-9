import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
from datetime import datetime, timedelta
import pytz
import random

# ------------------ НАСТРОЙКИ ------------------
TOKEN = ''  # Вставь новый токен!
CHANNEL_ID = 1546509618480549910  # ID канала для поздравлений
TIMEZONE = pytz.timezone('Europe/Moscow')
DATA_FILE = 'birthdays.json'
# ----------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Удаляем стандартную команду help
bot.remove_command('help')

# Цвета для Embed
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


# ------------------ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ------------------
def create_embed(title, description, color, fields=None, footer=None):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now(TIMEZONE)
    )
    if fields:
        for field in fields:
            embed.add_field(
                name=field['name'],
                value=field['value'],
                inline=field.get('inline', False)
            )
    if footer:
        embed.set_footer(text=footer)
    return embed


def get_birthday_embed(user, date, action='add'):
    if action == 'add':
        embed = discord.Embed(
            title="🎂 День рождения добавлен!",
            description=f"Пользователь **{user.display_name}** успешно добавлен в список именинников!",
            color=COLORS['success'],
            timestamp=datetime.now(TIMEZONE)
        )
        embed.add_field(name="📅 Дата", value=f"`{date}`", inline=True)
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
        embed = discord.Embed(
            title="🎉🎂 С ДНЁМ РОЖДЕНИЯ! 🎂🎉",
            description=f"""
            **{user.mention}** сегодня празднует свой день рождения!

            🥳 Желаем тебе:
            • Счастья и здоровья
            • Удачи и успехов
            • Исполнения всех желаний
            • Много подарков и улыбок!
            """,
            color=COLORS['birthday'],
            timestamp=datetime.now(TIMEZONE)
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_image(url="https://media.giphy.com/media/3o6Zt481isNVuQI1l6/giphy.gif")
        embed.set_footer(text="🎊 С наилучшими пожеланиями от бота!")
        return embed


# ------------------ КОМАНДА ПОМОЩИ (СЛЕШ) ------------------
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
        `/add_bd <дата> [пользователь]` — Добавить день рождения
        `/remove_bd [пользователь]` — Удалить день рождения
        `/my_bd` — Показать мой день рождения
        `/list_bd` — Показать список всех ДР
        `/bd_help` — Показать это сообщение
        """,
        inline=False
    )

    embed.add_field(
        name="📖 **Как использовать:**",
        value="""
        **Добавить свой ДР:** `/add_bd 15.07`
        **Добавить ДР друга:** `/add_bd 15.07 @Пользователь`
        **Удалить свой ДР:** `/remove_bd`
        **Удалить ДР друга:** `/remove_bd @Пользователь`
        """,
        inline=False
    )

    embed.add_field(
        name="🎂 **Автоматические функции:**",
        value="""
        • Ежедневная проверка в **9:00 МСК**
        • Автоматическое поздравление именинников
        • Напоминание за день до ДР
        • Автоудаление ушедших с сервера
        """,
        inline=False
    )

    embed.add_field(
        name="📌 **Примеры:**",
        value="""
        `🔹 /add_bd 25.12` — Добавить свой ДР 25 декабря
        `🔹 /add_bd 01.01 @Иван` — Добавить ДР Ивана 1 января
        `🔹 /list_bd` — Показать всех именинников
        """,
        inline=False
    )

    embed.set_footer(
        text="💡 Все команды начинаются с / (слеш)",
        icon_url=interaction.user.display_avatar.url
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await interaction.response.send_message(embed=embed)

#проверка поздравления командой
@bot.tree.command(name="force_check", description="Принудительная проверка именинников (только для админов)")
async def force_check(interaction: discord.Interaction):
    """Принудительная проверка именинников"""
    # Проверка на админа
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="⛔ Доступ запрещён",
            description="Только администраторы могут использовать эту команду!",
            color=COLORS['error']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    await interaction.response.send_message("🔄 Выполняю проверку именинников...")

    # Запускаем проверку
    await check_birthdays()

    embed = discord.Embed(
        title="✅ Проверка выполнена",
        description="Бот проверил именинников на сегодня.",
        color=COLORS['success'],
        timestamp=datetime.now(TIMEZONE)
    )
    embed.set_footer(text="Если у кого-то сегодня ДР — поздравление уже отправлено!")

    await interaction.edit_original_response(content=None, embed=embed)

# ------------------ ПРЕФИКСНАЯ КОМАНДА ПОМОЩИ ------------------
@bot.command(name='bothelp')
async def prefix_help(ctx):
    """Альтернативная команда помощи через !bothelp"""
    embed = discord.Embed(
        title="🎯 **Помощь по боту дней рождения**",
        description="Вот список всех доступных команд:",
        color=COLORS['help'],
        timestamp=datetime.now(TIMEZONE)
    )

    embed.add_field(
        name="📝 **Основные команды:**",
        value="""
        `/add_bd <дата> [пользователь]` — Добавить день рождения
        `/remove_bd [пользователь]` — Удалить день рождения
        `/my_bd` — Показать мой день рождения
        `/list_bd` — Показать список всех ДР
        `/bd_help` — Показать это сообщение
        """,
        inline=False
    )

    embed.add_field(
        name="📖 **Примеры:**",
        value="""
        `/add_bd 15.07` — добавить свой ДР 15 июля
        `/add_bd 01.01 @Пользователь` — добавить ДР пользователя
        `/list_bd` — посмотреть список
        """,
        inline=False
    )

    embed.set_footer(text="💡 Используй / (слеш) для вызова команд")

    await ctx.send(embed=embed)


# ------------------ СЛЕШ-КОМАНДЫ ------------------
@bot.tree.command(name="add_bd", description="Добавить день рождения")
@app_commands.describe(
    user="Пользователь (оставь пустым для себя)",
    date="Дата в формате ДД.ММ (например, 15.07)"
)
async def add_birthday(interaction: discord.Interaction, date: str, user: discord.User = None):
    if user is None:
        user = interaction.user

    try:
        datetime.strptime(date, '%d.%m')
    except ValueError:
        embed = create_embed(
            "❌ Ошибка!",
            "Неверный формат даты! Используй **ДД.ММ**\nПример: `15.07`",
            COLORS['error']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    day, month = map(int, date.split('.'))
    if day > 31 or month > 12:
        embed = create_embed(
            "❌ Ошибка!",
            "Неверная дата! Проверь день и месяц.",
            COLORS['error']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    data = load_data()
    user_id = str(user.id)

    if user_id in data:
        embed = create_embed(
            "⚠️ Предупреждение",
            f"День рождения для **{user.display_name}** уже есть в базе!\nДата: `{data[user_id]['date']}`",
            COLORS['warning']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    data[user_id] = {
        "name": user.display_name,
        "date": date
    }
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
        embed = create_embed(
            "❌ Ошибка!",
            f"День рождения для **{user.display_name}** не найден в базе.",
            COLORS['error']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    del data[user_id]
    save_data(data)

    embed = get_birthday_embed(user, None, 'remove')
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="list_bd", description="Показать все дни рождения")
async def list_birthdays(interaction: discord.Interaction):
    data = load_data()

    if not data:
        embed = create_embed(
            "📭 Список пуст",
            "В базе пока нет ни одного дня рождения.\nДобавь свой с помощью `/add_bd`!",
            COLORS['info']
        )
        await interaction.response.send_message(embed=embed)
        return

    sorted_users = sorted(data.items(), key=lambda x: x[1]['date'])

    months = {
        '01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
        '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
        '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'
    }

    description = "🎂 **Список всех дней рождений:**\n\n"
    current_month = None

    for user_id, info in sorted_users:
        date_parts = info['date'].split('.')
        month = date_parts[1]
        day = date_parts[0]

        if month != current_month:
            current_month = month
            description += f"\n**📅 {months[month]}:**\n"

        try:
            user = await bot.fetch_user(int(user_id))
            name = user.mention
        except:
            name = f"~~{info['name']}~~ *(покинул сервер)*"

        description += f"  • {day} число — {name}\n"

    if len(description) > 4000:
        description = description[:3997] + "..."

    embed = discord.Embed(
        title="📅 Календарь дней рождений",
        description=description,
        color=COLORS['info'],
        timestamp=datetime.now(TIMEZONE)
    )
    embed.set_footer(text=f"Всего: {len(data)} именинников")

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="my_bd", description="Показать мой день рождения")
async def my_birthday(interaction: discord.Interaction):
    data = load_data()
    user_id = str(interaction.user.id)

    if user_id not in data:
        embed = create_embed(
            "❌ Не найден",
            "Твой день рождения не добавлен в базу!\nИспользуй `/add_bd` чтобы добавить.",
            COLORS['error']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    date = data[user_id]['date']
    embed = discord.Embed(
        title="🎂 Твой день рождения",
        description=f"Твой день рождения: **{date}**",
        color=COLORS['info'],
        timestamp=datetime.now(TIMEZONE)
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_footer(text="🎉 Готовься к празднику!")

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

    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"❌ Канал с ID {CHANNEL_ID} не найден!")
        return

    today = datetime.now(TIMEZONE).strftime('%d.%m')
    data = load_data()

    birthday_users = []

    for user_id, info in data.items():
        if info['date'] == today:
            try:
                user = await bot.fetch_user(int(user_id))
                birthday_users.append(user)
            except:
                del data[user_id]
                save_data(data)
                print(f"🗑️ {info['name']} удалён из базы (не найден в Discord)")

    if birthday_users:
        greetings = [
            "🎊 С Днём Рождения!",
            "🎉 Поздравляем!",
            "🥳 Хэппи бездей!",
            "🎈 С праздником!"
        ]

        for user in birthday_users:
            embed = get_birthday_embed(user, None, 'birthday')
            embed.set_footer(text=f"{random.choice(greetings)}")
            await channel.send(f"🎉 ВНИМАНИЕ! {user.mention}", embed=embed)

    # Проверка на завтрашних именинников
    tomorrow = (datetime.now(TIMEZONE) + timedelta(days=1)).strftime('%d.%m')
    for user_id, info in data.items():
        if info['date'] == tomorrow:
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
            except:
                pass


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


if __name__ == '__main__':
    bot.run(TOKEN)