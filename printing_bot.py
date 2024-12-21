from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Stages
SERVICE, FILE_OR_AMOUNT, CONTACT, COMMENT = range(4)

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [['🎨 Color Printing', '🖤 Black & White'], ['📄 Paper Sheets', '📚 Binding']]
    await update.message.reply_text(
        "Welcome! Please choose a service:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SERVICE

# Service Selection
async def service_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['service'] = update.message.text
    if context.user_data['service'] in ['🎨 Color Printing', '🖤 Black & White', '📚 Binding']:
        await update.message.reply_text("Please upload your file.")
        return FILE_OR_AMOUNT
    elif context.user_data['service'] == '📄 Paper Sheets':
        await update.message.reply_text("How many sheets do you need?")
        return FILE_OR_AMOUNT
    else:
        await update.message.reply_text("Invalid choice. Please start again with /start.")
        return ConversationHandler.END

# File or Amount Input
async def file_or_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.user_data['service'] == '📄 Paper Sheets':
        context.user_data['amount'] = update.message.text
        await update.message.reply_text("Thank you! Please send your name and phone number.")
    else:
        # Store the file ID
        context.user_data['file_id'] = update.message.document.file_id
        
        # Send confirmation to the user
        await update.message.reply_text("File received! Now, please send your name and phone number.")
        
        # Send the file to the admin
        admin_chat_id = 5040963728  # Replace with your Chat ID
        await context.bot.send_document(chat_id=admin_chat_id, document=context.user_data['file_id'])
        
        # Clear the file ID to avoid sending it again
        del context.user_data['file_id']
        
    return CONTACT


# Contact Input
async def contact_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['contact'] = update.message.text
    await update.message.reply_text("Any additional comment or consideration? If none, type 'No'.")
    return COMMENT

# Comment Input and Final Confirmation
async def comment_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['comment'] = update.message.text

    # Send confirmation to the user
    await update.message.reply_text("Your order is submitted! We'll call you in a moment. Thank you!")

    # Notify admin (replace with your admin chat ID)
    admin_chat_id = 5040963728  # Replace with your Chat ID
    order_details = (
        f"New order:\n"
        f"Service: {context.user_data['service']}\n"
    )
    if 'file_id' in context.user_data:
        order_details += f"File attached: (file sent to admin)\n"
    if 'amount' in context.user_data:
        order_details += f"Amount: {context.user_data['amount']}\n"
    order_details += (
        f"Contact: {context.user_data['contact']}\n"
        f"Comment: {context.user_data['comment']}"
    )
    
    # Send the order details to the admin
    await context.bot.send_message(chat_id=admin_chat_id, text=order_details)

    # Send the file to the admin
    if 'file_id' in context.user_data:
        await context.bot.send_document(chat_id=admin_chat_id, document=context.user_data['file_id'])

    return ConversationHandler.END


# Cancel Command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Order canceled. Feel free to start again with /start.")
    return ConversationHandler.END

# Main Function
def main():
    application = Application.builder().token("7466695570:AAH4Nrh3lA7IWZSsgokkmDzrVNrszbAycP0").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SERVICE: [MessageHandler(filters.TEXT, service_selected)],
            FILE_OR_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, file_or_amount_received),
                MessageHandler(filters.Document.ALL, file_or_amount_received),
            ],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_received)],
            COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, comment_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
