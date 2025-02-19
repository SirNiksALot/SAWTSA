# Running the Application

## Running the agent:

```bash
python agent.py
```

## Working

```python
@ctx.room.on("user_started_speaking")
async def on_participant_connected(participant: rtc.RemoteParticipant):
    if len(assistant.chat_ctx.messages) <= 2:
        stream = assistant.llm.chat(chat_ctx=assistant.chat_ctx)
        return await assistant.say(stream, allow_interruptions=False)
    else:
        stream = assistant.llm.chat(chat_ctx=assistant.chat_ctx)
        return await assistant.say(stream, allow_interruptions=True)
```

The agent listens for when a user starts speaking.

- **If the user is speaking for the first time**, interruptions are disabled (`allow_interruptions=False`).
- **After the first response is complete**, interruptions are allowed again.


## Assumptions

- The first input is defined as the first **completed** speech input by the user.
- LiveKit’s `user_started_speaking` event is reliable for detecting interruptions.

