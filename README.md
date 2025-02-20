# Running the Application

## Running the agent:

```bash
python agent.py
```

## Working

```python
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
```

The agent listens for when a user starts speaking.

- **If the user is speaking for the first time**, interruptions are disabled (`allow_interruptions=False`).
- **After the first response is complete**, interruptions are allowed again.


## Assumptions

- The first input is defined as the first **completed** speech input by the user.
- LiveKit’s `user_started_speaking` event is reliable for detecting interruptions.

