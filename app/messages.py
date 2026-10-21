from html import escape

def quote(text: str) -> str: return f"<blockquote>{escape(text)}</blockquote>"
WELCOME = quote("Welcome to the Game Hub. Pick a game, chase the rankings, or check your profile.")
GAMES = quote("Games\n\nChoose a game below. More games can be added without changing the menu system.")
DOODLE = quote("Doodle Covert\n\nSlip through eight rooms, avoid guard vision, collect all intel, and extract at the far end of the hall.")
SETTINGS = quote("Settings\n\nSound is controlled inside each game. More account settings will appear here later.")
