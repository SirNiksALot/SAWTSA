import asyncio
from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions,cli,llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai , silero
from livekit import rtc
import logging

load_dotenv()
"""
load the following env variables 
LIVEKIT_URL
LIVEKIT_API_KEY
LIVEKIT_API_SECRET
OPENAI_API_KEY
"""

async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role = "system",
        text=(
            "You are a voice assistant meant for yapping. Your interface with users will be voice. "
            "Respond the the users first message with a big speech explaining who you are"
        ),
    )
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    assistant =VoiceAssistant(
        llm=openai.LLM(),
        stt=openai.STT(),
        vad=silero.VAD.load(),
        tts=openai.TTS(),
        chat_ctx=initial_ctx,     
    )
    assistant.start(ctx.room)

    first_message_from_user=True

    @ctx.room.on("user_speech_committed")
    def on_user_speech_committed(participant: rtc.RemoteParticipant):
        nonlocal first_message_from_user
        if first_message_from_user : 
            logging.info("FIRST MESSAGE FROM USER RECEIVED")
            stream = assistant.llm.chat(chat_ctx=assistant.chat_ctx)
            first_message_from_user=False
            return asyncio.create_task(assistant.say(stream,allow_interruptions=False))
        else:
            logging.info("NOT FIRST MESSAGE FROM USER THEREFORE INTERRUPTIONS ALLOWED")
            stream = assistant.llm.chat(chat_ctx=assistant.chat_ctx) 
            return asyncio.create_task(assistant.say(stream,allow_interruptions=True))
    

    await asyncio.sleep(1)
    await assistant.say("Hey! Shall i start the explanation",allow_interruptions=False)

if __name__=="__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
