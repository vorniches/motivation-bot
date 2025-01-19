import logging
from django.core.management.base import BaseCommand
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from django.conf import settings
from prototype.helpers.openai_helper import send_prompt_to_openai
from prototype.telegram_bot.models import Task
from asgiref.sync import sync_to_async

# Configure logging to output to console
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run the Telegram bot'

    # Synchronous helper functions
    def get_last_tasks_sync(self, user_id):
        return list(Task.objects.filter(user_id=user_id).order_by('-timestamp')[:5])

    def create_task_sync(self, user_id, task_type, task_content, user_response=None, is_correct=None):
        return Task.objects.create(
            user_id=user_id,
            task_type=task_type,
            task_content=task_content,
            user_response=user_response,
            is_correct=is_correct
        )

    def get_latest_text_task_sync(self, user_id):
        return Task.objects.filter(user_id=user_id, task_type='text_task').order_by('-timestamp').first()

    def get_latest_brain_train_sync(self, user_id):
        return Task.objects.filter(user_id=user_id, task_type='brain_train').order_by('-timestamp').first()

    def save_task_sync(self, task):
        task.save()

    # Use this to GENERATE new content/prompts
    def generate_content_sync(self, system_content, user_prompt):
        return send_prompt_to_openai(system_content, user_prompt)

    # Use this to EVALUATE user's response
    def evaluate_response_sync(self, system_content, user_prompt):
        return send_prompt_to_openai(system_content, user_prompt)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user = update.effective_user
            logger.info(f"User {user.first_name} started the bot.")

            keyboard = [
                [
                    InlineKeyboardButton("💡 Self-help Coach", callback_data='self_help'),
                    InlineKeyboardButton("✍️ Text Task", callback_data='text_task'),
                ],
                [
                    InlineKeyboardButton("🧘 Mindfulness & Gratitude", callback_data='mindfulness'),
                    InlineKeyboardButton("🧩 Brain-train", callback_data='brain_train'),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"Hello {user.first_name}! How can I assist you today?",
                reply_markup=reply_markup
            )
            logger.info("Sent greeting message with options.")
        except Exception as e:
            logger.error(f"Error in start handler: {e}")

    async def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            query = update.callback_query
            await query.answer()
            user = query.from_user
            task_type = query.data

            logger.info(f"User {user.first_name} selected {task_type}.")

            # Fetch last 5 tasks
            last_tasks = await sync_to_async(self.get_last_tasks_sync)(user.id)
            last_prompts = "\n".join([f"{task.task_type}: {task.task_content}" for task in last_tasks])

            # Prepare general keyboard for after we respond
            keyboard = [
                [
                    InlineKeyboardButton("💡 Self-help Coach", callback_data='self_help'),
                    InlineKeyboardButton("✍️ Text Task", callback_data='text_task'),
                ],
                [
                    InlineKeyboardButton("🧘 Mindfulness & Gratitude", callback_data='mindfulness'),
                    InlineKeyboardButton("🧩 Brain-train", callback_data='brain_train'),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if task_type == 'self_help':
                system = (
                    "You are a self-help coach. Provide a short, fresh tip on self-improvement. "
                    f"Last 5 tasks:\n{last_prompts}\n"
                    "Do not repeat or closely resemble previous tips. Keep it under 40 words."
                )
                user_prompt = "Generate a new short self-help tip."
                response = await sync_to_async(self.generate_content_sync)(system, user_prompt)
                task_content = response or "Here is your self-help tip."
                await sync_to_async(self.create_task_sync)(user.id, 'self_help', task_content)
                await query.message.reply_text(task_content)
                logger.info("Sent Self-help Coach tip.")

            elif task_type == 'text_task':
                system = (
                    "You are a productivity assistant. Provide a short writing task for self-improvement. "
                    f"Last 5 tasks:\n{last_prompts}\n"
                    "Do not repeat or closely resemble previous tasks. Keep it under 50 words."
                )
                user_prompt = "Generate a new text task for the user."
                response = await sync_to_async(self.generate_content_sync)(system, user_prompt)
                task_content = response or "Write about your goals for this week."
                await sync_to_async(self.create_task_sync)(user.id, 'text_task', task_content)
                await query.message.reply_text(task_content)
                logger.info("Sent Text Task.")
                context.user_data['awaiting_response'] = 'text_task'

            elif task_type == 'mindfulness':
                system = (
                    "You are a mindfulness coach. Provide a short mindfulness or gratitude exercise. "
                    f"Last 5 tasks:\n{last_prompts}\n"
                    "Do not repeat or closely resemble previous tasks."
                )
                user_prompt = "Generate a new mindfulness/gratitude exercise."
                response = await sync_to_async(self.generate_content_sync)(system, user_prompt)
                task_content = response or "Take a 5-minute meditation break and note three things you're grateful for."
                await sync_to_async(self.create_task_sync)(user.id, 'mindfulness', task_content)
                await query.message.reply_text(task_content)
                logger.info("Sent Mindfulness and Gratitude task.")

            elif task_type == 'brain_train':
                system = (
                    "You are a brain trainer providing a single short puzzle or quiz question. "
                    f"Last 5 tasks:\n{last_prompts}\n"
                    "Do not repeat or closely resemble previous puzzles."
                )
                user_prompt = "Generate a new one-question puzzle or quiz."
                response = await sync_to_async(self.generate_content_sync)(system, user_prompt)
                task_content = response or "What has keys but can't open locks?"
                await sync_to_async(self.create_task_sync)(user.id, 'brain_train', task_content)
                await query.message.reply_text(task_content)
                logger.info("Sent Brain-train puzzle.")
                context.user_data['awaiting_response'] = 'brain_train'

            await query.message.reply_text("What do you want to do next?", reply_markup=reply_markup)
            logger.info("Displayed options again to the user.")
        except Exception as e:
            logger.error(f"Error in button handler: {e}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user = update.effective_user
            text = update.message.text
            awaiting = context.user_data.get('awaiting_response')

            # Evaluate user responses if they are in the middle of a text_task
            if awaiting == 'text_task':
                logger.info(f"Received user response for Text Task from {user.first_name}: {text}")
                task = await sync_to_async(self.get_latest_text_task_sync)(user.id)
                if task:
                    last_tasks = await sync_to_async(self.get_last_tasks_sync)(user.id)
                    last_prompts = "\n".join([f"{t.task_type}: {t.task_content}" for t in last_tasks])
                    system = (
                        "You are an assistant evaluating a user's written text. "
                        "Provide short, constructive feedback on self-improvement. "
                        f"Previous tasks:\n{last_prompts}\n"
                        "Do not repeat or be overly verbose."
                    )
                    user_prompt = f"User's text:\n{text}\nEvaluate and give feedback."
                    response = await sync_to_async(self.evaluate_response_sync)(system, user_prompt)
                    task.user_response = text
                    task.is_correct = True  # or any custom logic
                    await sync_to_async(self.save_task_sync)(task)
                    await update.message.reply_text(response or "Your response has been evaluated.")
                    logger.info("Evaluated user response for Text Task.")
                context.user_data['awaiting_response'] = None

            # Evaluate user responses if they are in the middle of a brain_train
            elif awaiting == 'brain_train':
                logger.info(f"Received user response for Brain-train from {user.first_name}: {text}")
                task = await sync_to_async(self.get_latest_brain_train_sync)(user.id)
                if task:
                    last_tasks = await sync_to_async(self.get_last_tasks_sync)(user.id)
                    last_prompts = "\n".join([f"{t.task_type}: {t.task_content}" for t in last_tasks])
                    system = (
                        "You are an assistant evaluating a short puzzle or quiz response. "
                        "Provide brief validation or correction. "
                        f"Previous tasks:\n{last_prompts}\n"
                        "Do not repeat yourself or be overly verbose."
                    )
                    user_prompt = f"Puzzle was: {task.task_content}\nUser's answer: {text}\nEvaluate correctness."
                    response = await sync_to_async(self.evaluate_response_sync)(system, user_prompt)
                    task.user_response = text
                    # You could parse the response to decide is_correct; here we assume True
                    task.is_correct = True
                    await sync_to_async(self.save_task_sync)(task)
                    await update.message.reply_text(response or "Your puzzle answer has been evaluated.")
                    logger.info("Evaluated user response for Brain-train.")
                context.user_data['awaiting_response'] = None

            else:
                logger.info(f"Received message from {user.first_name}: {text} (No action taken)")

            # After handling or ignoring, show main buttons again
            keyboard = [
                [
                    InlineKeyboardButton("💡 Self-help Coach", callback_data='self_help'),
                    InlineKeyboardButton("✍️ Text Task", callback_data='text_task'),
                ],
                [
                    InlineKeyboardButton("🧘 Mindfulness & Gratitude", callback_data='mindfulness'),
                    InlineKeyboardButton("🧩 Brain-train", callback_data='brain_train'),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("What do you want to do next?", reply_markup=reply_markup)
            logger.info("Displayed options again to the user after handling message.")
        except Exception as e:
            logger.error(f"Error in handle_message handler: {e}")

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error and send a message to notify the user."""
        logger.error(msg="Exception while handling an update:", exc_info=context.error)
        # Notify the user about the error
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text("An unexpected error occurred. Please try again later.")

    def handle(self, *args, **kwargs):
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN is not set in environment variables.")
            return

        application = ApplicationBuilder().token(token).build()

        # Register handlers
        start_handler = CommandHandler('start', self.start)
        button_handler = CallbackQueryHandler(self.button)
        message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)

        application.add_handler(start_handler)
        application.add_handler(button_handler)
        application.add_handler(message_handler)

        # Register error handler
        application.add_error_handler(self.error_handler)

        logger.info("Starting Telegram bot polling.")
        application.run_polling()
        logger.info("Telegram bot stopped.")
