from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackGame

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Games", callback_data="menu:games"), InlineKeyboardButton(text="🏆 Rankings", callback_data="menu:rankings")],
        [InlineKeyboardButton(text="👤 Profile", callback_data="menu:profile"), InlineKeyboardButton(text="💬 Feedback", callback_data="menu:feedback")],
        [InlineKeyboardButton(text="⚙ Settings", callback_data="menu:settings")],
    ])

def games_menu(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🕵️ Doodle Covert", callback_data="game:doodle_covert")],[InlineKeyboardButton(text="‹ Back", callback_data="menu:home")]])
def game_details(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶️ Play", callback_data="game:send:doodle_covert")],[InlineKeyboardButton(text="🏆 Top Agents", callback_data="rank:doodle_covert"), InlineKeyboardButton(text="‹ Back", callback_data="menu:games")]])
def native_game(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="▶️ PLAY DOODLE COVERT", callback_game=CallbackGame())],[InlineKeyboardButton(text="🏆 Global Top 5", callback_data="rank:doodle_covert")]])
def back_home(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="‹ Main menu", callback_data="menu:home")]])
