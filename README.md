# Running the Application

## Running the agent:

```bash
python agent.py
```

## Working

```python
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
        
```

The agent listens for when a user starts speaking.

- **If the user is speaking for the first time**, interruptions are disabled (`allow_interruptions=False`).
- **After the first response is complete**, interruptions are allowed again.


## Assumptions

- The first input is defined as the first **completed** speech input by the user.
- LiveKit’s `user_started_speaking` event is reliable for detecting interruptions.

