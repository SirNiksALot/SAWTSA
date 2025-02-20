import asyncio
from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions,cli,llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai , silero
from livekit.agents.llm import ChatContext
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
            "Respond the the users first message with a breif introductiion explaining who you are , and start with I WILL BE IGNORING YOUR MMESSAGES TILL I FINISH YAPPING"
            "When you are done explaining scream the words IM DONE YOU CAN TALK NOW , YOU WORDS WILL NOT BE IGNORE NOW "
        ),
    )
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    assistant =VoiceAssistant(
        llm=openai.LLM(),
        stt=openai.STT(),
        vad=silero.VAD.load(),
        tts=openai.TTS(),
        chat_ctx=initial_ctx,
        allow_interruptions=False     
    )
    assistant.start(ctx.room)

    ignore_flag=False

    @assistant.on("user_speech_committed")
    def on_user_speech_committed(msg: llm.ChatMessage):
        nonlocal ignore_flag
        if ignore_flag:
            messages=assistant.chat_ctx.messages
            for i in range(len(messages)-1,-1,-1):
                if messages[i].role=="user":
                    messages[i].content=""
            chat_ctx_new=ChatContext(messages=messages)
            stream = assistant.llm.chat(chat_ctx=chat_ctx_new)
            ignore_flag=False
            return asyncio.create_task(assistant.say(stream,allow_interruptions=True))
        else:
            stream = assistant.llm.chat(chat_ctx=assistant.chat_ctx)
            return asyncio.create_task(assistant.say(stream,allow_interruptions=True))
        
    
    
    @assistant.on("agent_speech_committed")
    def on_agent_speech_committed(msg):
        nonlocal ignore_flag
        if len(assistant.chat_ctx.messages)==3 and assistant.chat_ctx.messages[-1].role=="user":
            ignore_flag=True
        

    

    await asyncio.sleep(1)
    await assistant.say("Hey! Shall i start the explanation",allow_interruptions=False)

if __name__=="__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
