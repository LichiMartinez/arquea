from dotenv import load_dotenv, dotenv_values
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from models.user.model import UserCreate, UserRole
from models.user.service import UserService
from utils.date_utils import utc_now

load_dotenv()
env = dotenv_values()


class ArqueaBot():
    def __init__(self):
        self._token = env.get("TELEGRAM_TOKEN")
        self.bot = telebot.TeleBot(self._token)
        self.register_handlers()
        self.user_service = UserService()
        data = UserCreate(first_name="Lichi", last_name="Martinez", telegram_id="12345", role=UserRole.ADMIN, viewed_at=utc_now())
        self.user_service.create(data=data)

        if not all([self._token]):
            raise ValueError("Some required environment variables are missing")

    def start_bot(self):
        self.bot.polling()

    def register_handlers(self):
        @self.bot.message_handler(commands=["start"])
        def handle_start(message):
            self.on_start(message)

        @self.bot.message_handler(commands=["menu"])
        def send_menu(message):
            self.menu(message)

    def on_start(self, message):
        nombre_usuario = message.from_user.first_name
        self.bot.send_message(message.chat.id, f"¡Hola, {nombre_usuario}! Por favor, identifícate con tu usuario.")
        markup = ReplyKeyboardMarkup(one_time_keyboard=True)
        btn = KeyboardButton("Enviar mi nombre de usuario")
        markup.add(btn)
        self.bot.send_message(message.chat.id, "Pulsa el botón para continuar:", reply_markup=markup)

    def menu(self, message):
        markup = ReplyKeyboardMarkup(row_width=2)
        btn1 = KeyboardButton("Añadir Cliente")
        btn2 = KeyboardButton("Recolección")
        markup.add(btn1, btn2)

        self.bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)


def main():
    bot = ArqueaBot()
    # bot.start_bot()
