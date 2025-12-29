import discord
from discord.ext import commands
import os

# Загрузка переменных окружения
load_dotenv()

# ВАЖНО: Настраиваем все необходимые intents
intents = discord.Intents.default()
intents.members = True  # Включаем доступ к участникам
intents.message_content = True  # Включаем чтение содержимого сообщений
intents.guilds = True  # Включаем доступ к серверам
intents.guild_messages = True  # Включаем доступ к сообщениям на серверах

# Инициализация бота с intents
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None  # Отключаем стандартную команду help (опционально)
)


@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} успешно запущен!')
    print(f'ID бота: {bot.user.id}')
    print(f'Подключен к {len(bot.guilds)} серверам')

    # Выводим список серверов
    for guild in bot.guilds:
        print(f'  - {guild.name} (ID: {guild.id})')


@bot.command(name='ping')
async def ping(ctx):
    """Простая команда для проверки работы бота"""
    await ctx.send(f'🏓 Pong! Задержка: {round(bot.latency * 1000)}ms')


@bot.command(name='rename', help='Переименовать пользователя: !rename @user новое_имя')
@commands.has_permissions(manage_nicknames=True)
async def rename_user(ctx, member: discord.Member, *, new_nickname: str):
    """Переименование пользователя"""
    try:
        # Проверяем права бота
        if not ctx.guild.me.guild_permissions.manage_nicknames:
            await ctx.send("❌ У меня нет прав на изменение никнеймов!")
            return

        # Проверяем иерархию ролей
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send(f"❌ Не могу изменить никнейм {member.mention} - у него роль выше моей!")
            return

        # Сохраняем старое имя
        old_name = member.nick if member.nick else member.name

        # Меняем никнейм
        await member.edit(nick=new_nickname)

        # Отправляем подтверждение
        embed = discord.Embed(
            title="✅ Успешно!",
            description=f"**{old_name}** переименован в **{new_nickname}**",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Изменено: {ctx.author}")
        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("❌ Недостаточно прав для изменения никнейма!")
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {str(e)}")


@rename_user.error
async def rename_error(ctx, error):
    """Обработчик ошибок для команды rename"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ У вас нет прав на использование этой команды!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Неправильный формат!\nИспользуйте: `!rename @пользователь новое_имя`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Пользователь не найден! Укажите существующего пользователя через @упоминание.")
    else:
        await ctx.send(f"❌ Ошибка: {str(error)}")


@bot.command(name='help_bot')
async def help_command(ctx):
    """Показать справку по командам"""
    embed = discord.Embed(
        title="📚 Команды бота для переименования",
        description="Все доступные команды:",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="`!ping`",
        value="Проверка работы бота",
        inline=False
    )

    embed.add_field(
        name="`!rename @пользователь новое_имя`",
        value="Переименовать пользователя\n*(Требуются права: Управление никнеймами)*",
        inline=False
    )

    embed.add_field(
        name="`!help_bot`",
        value="Показать это сообщение",
        inline=False
    )

    embed.set_footer(text="Бот для управления никнеймами")
    await ctx.send(embed=embed)


# Запуск бота
if __name__ == "__main__":
    # Сначала пробуем получить из переменных окружения (для хостинга)
    token = os.environ.get('API_TOKEN')

    # Если нет, пробуем из .env (для локальной разработки)
    if not token:
        from dotenv import load_dotenv
        load_dotenv()
        token = os.getenv('DISCORD_TOKEN')

    if not token:
        print("❌ ОШИБКА: Токен не найден в файле .env")
        print("Создайте файл .env в папке с ботом и добавьте:")
        print("API_TOKEN=ваш_токен_бота")
    else:
        print("🚀 Запуск бота...")
        print("=" * 50)
        bot.run(token)