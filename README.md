# Running the Application

## Run the LiveKit agent using:

```bash
python main.py
```

## Code Breakdown

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

## Handling Timing and Edge Cases

- **Edge Case: User speaks before the assistant starts responding** → Ensured that the first response is fully spoken before allowing further interactions.
- **Edge Case: Long responses from the assistant** → Uses `allow_interruptions=False` only for the first response to avoid blocking future inputs.
- **Edge Case: Multiple users speaking** → Only the first interaction is gated; subsequent ones allow normal interruptions.

## Deliverables

- **Demo Video**: Shows an example conversation where a user’s interruptions during the first response are ignored.
- **GitHub Repository**: Contains the full implementation with instructions to run the agent.
- **Explanation of Timing & Edge Cases**: Described in the section above.

## Assumptions

- The first input is defined as the first **completed** speech input by the user.
- LiveKit’s `user_started_speaking` event is reliable for detecting interruptions.

