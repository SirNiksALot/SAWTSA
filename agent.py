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
            "Respond the the users first message with a big speech explaining who you are"
            "When you are done explaining scream the words IM DONE"
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

    flag=False

    @assistant.on("user_speech_committed")
    def on_user_speech_committed(msg: llm.ChatMessage):
        nonlocal flag
        messages = assistant.chat_ctx.messages
        if len(messages)==3 and messages[-1].role=="user":
            stream = assistant.llm.chat(chat_ctx=assistant.chat_ctx)
            flag=True
            return asyncio.create_task(assistant.say(stream,allow_interruptions=False))
        else:
            stream = assistant.llm.chat(chat_ctx=assistant.chat_ctx)
            return asyncio.create_task(assistant.say(stream,allow_interruptions=True))
        
    
    
    @assistant.on("agent_speech_committed")
    def on_agent_speech_committed(msg):
        nonlocal flag
        if flag:
            messages=assistant.chat_ctx.messages
            msgs_ignore=messages[:3]
            msgs_ignore.append(messages[-1])
            chat_ctx_new=ChatContext(messages=msgs_ignore)
            stream = assistant.llm.chat(chat_ctx=chat_ctx_new)
            flag=False
            return asyncio.create_task(assistant.say(stream,allow_interruptions=True))
        else:
            stream = assistant.llm.chat(chat_ctx=assistant.chat_ctx)
            return asyncio.create_task(assistant.say(stream,allow_interruptions=True))

    

    await asyncio.sleep(1)
    await assistant.say("Hey! Shall i start the explanation",allow_interruptions=False)

if __name__=="__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
