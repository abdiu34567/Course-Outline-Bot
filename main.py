from pydoc import text
from telegram.ext import *
from telegram import *
from telegram.utils.helpers import effective_message_type, escape_markdown
from Token import *
from mongodb import *


_ADMIN = [712156622]
_Courses = OutlineCollection.find_one()['vals']
_List = OutlineCollection.find_one()['courses']
_CODE = OutlineCollection.find_one()['code']
availableCourses = list(_CODE.keys())
_OPTION = []
reset = 0
tempL = []
for code in range(0, len(availableCourses)-1, 2):
    if reset == 5:
        reset = 0
        _OPTION.append(tempL)
        tempL = []
    else:
        tempL.append(availableCourses[code] +
                     "        "+availableCourses[code+1])
        reset += 1


def welcome(update: Update, context: CallbackContext):
    buttons = [[InlineKeyboardButton("Get Started", callback_data="start")], [InlineKeyboardButton("Available Courses", callback_data="available")],
               [InlineKeyboardButton("Search for course",
                                     callback_data="search")],
               [InlineKeyboardButton("How to Use Me!", callback_data="usage")]]
    context.bot.send_message(
        chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons), text="Welcome to ASTU Course Outline Robot\nChoose from the below choices to get started")


def add(update: Update, context: CallbackContext):
    context.user_data["step"] = 0
    if update.message.chat.id in _ADMIN:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Send me Course name")
        context.user_data["step"] = 1


def start(update: Update, context: CallbackContext, query: CallbackQuery):

    buttons = []
    _KEYS = list(_Courses.keys())
    for key in _KEYS:
        buttons.append([InlineKeyboardButton(key, callback_data=key)])
    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(
        buttons))
    context.user_data["current"] = []


def semHandler(update: Update, context: CallbackContext):
    query = update.callback_query
    text = query.data
    current = context.user_data.get("current", [])
    if text == "start":
        start(update, context, query)
    elif text == "usage":
        pass
    elif text == "available":
        query.delete_message()
        button = [[InlineKeyboardButton("More ...", callback_data="more")]]
        ind = context.user_data["index"] = 0
        context.bot.send_message(
            chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(button), text='\n'.join(_OPTION[ind]))
        welcome(update, context)
        context.user_data["index"] += 1
    elif text == "search":
        context.user_data["now"] = text
        query.edit_message_text(text="Send me the any course Title")
    else:
        if text == "back":
            current.pop()
        else:
            current.append(text)

        context.user_data["current"] = current
        tempD = _Courses
        for cur in current:
            tempD = tempD[cur]
        if type(tempD) == str:
            query.delete_message()
            context.bot.send_document(
                chat_id=update.effective_chat.id, document=_CODE[tempD])
        else:
            buttons = []
            keys = list(tempD.keys())
            key_len = len(keys)
            if key_len > 3:
                if key_len % 2 == 0:
                    key1 = keys[:key_len//2]
                    key2 = keys[key_len//2:]
                    for key in range(key_len//2):
                        buttons.append([InlineKeyboardButton(key1[key], callback_data=key1[key]),
                                        InlineKeyboardButton(key2[key], callback_data=key2[key])])
                else:
                    key1 = keys[:key_len//2]
                    key2 = keys[key_len//2:key_len-1]
                    for key in range(key_len//2):
                        buttons.append([InlineKeyboardButton(key1[key], callback_data=key1[key]),
                                        InlineKeyboardButton(key2[key], callback_data=key2[key])])
                    buttons.append([InlineKeyboardButton(
                        keys[-1], callback_data=keys[-1])])

            else:
                for key in keys:
                    buttons.append(
                        [InlineKeyboardButton(key, callback_data=key)])
            if current:
                buttons.append([InlineKeyboardButton(
                    "<< Back", callback_data="back")])
            query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(buttons))


def inlineQuery(update: Update, context: CallbackContext):
    query = update.inline_query.query

    if query == "":
        return
    _KEYS = list(_List.keys())
    tempKeys = []
    for key in _KEYS:
        if query.lower() in key.lower():
            tempKeys.append(key)
    result = []
    for i in tempKeys:
        result.append(InlineQueryResultCachedDocument(
            id=i+"_co",
            title=i,
            document_file_id=_List[i]
        ))

    update.inline_query.answer(result)


def messageHandler(update: Update, context: CallbackContext):
    if context.user_data.get("now", "") == "search":
        context.bot.send_document(
            chat_id=update.effective_chat.id, document=_CODE[update.message.text])
    elif context.user_data.get("step", "") == 1:
        context.user_data["title"] = update.message.text
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Send me Course Code")
        context.user_data["step"] = 2
    elif context.user_data.get("step", "") == 2:
        context.user_data["code"] = update.message.text
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Send me Course Outline Document ")
        context.user_data["step"] = 3


def documentHandler(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="hello")


def moreHandler(update: Update, context: CallbackContext):
    query = update.callback_query
    text = query.data
    ind = context.user_data.get("index", 0)
    if _OPTION[ind]:
        query.edit_message_text(text='\n'.join(_OPTION[ind]))
        context.user_data["index"] += 1
    else:
        query.edit_message_text(text="")


def main():
    updater = Updater(key)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", welcome))
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(MessageHandler(Filters.document, documentHandler))
    dispatcher.add_handler(CallbackQueryHandler(moreHandler, pattern="more"))
    dispatcher.add_handler(CallbackQueryHandler(semHandler))
    dispatcher.add_handler(InlineQueryHandler(inlineQuery))
    dispatcher.add_handler(MessageHandler(Filters.text, messageHandler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
