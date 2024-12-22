from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
import os
import logging
import asyncio

app = FastAPI()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command"""
    await update.message.reply_text("Hey Welcome, I am powered by FastAPI!!")

async def bot_tele(update_data):
    """Process Telegram updates"""
    application = Application.builder().token(os.getenv("TOKEN")).build()
    application.add_handler(CommandHandler("start", start))

    await application.bot.set_webhook(url=os.getenv("webhook"))
    await application.update_queue.put(Update.de_json(data=update_data, bot=application.bot))

    async with application:
        await application.start()
        await application.stop()


@app.post("/")
async def webhook_post(request: Request):
    """Handle POST requests for Telegram webhook"""
    try:
        update_data = await request.json()
        if update_data:
            await bot_tele(update_data)
            return JSONResponse(content={"status": "ok"}, status_code=200)
    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid request")

    raise HTTPException(status_code=400, detail="Invalid request")


@app.get("/")
async def webhook_get():
    """Handle GET requests for health check"""
    return JSONResponse(content={"message": "Webhook is up and running!"}, status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
