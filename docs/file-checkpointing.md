# Rewind file changes with checkpointing

Track file changes during agent sessions and restore files to any previous state

---

File checkpointing tracks file modifications made through the Write, Edit, and NotebookEdit tools during an agent session, allowing you to rewind files to any previous state.

With checkpointing, you can:

- **Undo unwanted changes** by restoring files to a known good state
- **Explore alternatives** by restoring to a checkpoint and trying a different approach
- **Recover from errors** when the agent makes incorrect modifications

> **Warning:** Only changes made through the Write, Edit, and NotebookEdit tools are tracked. Changes made through Bash commands (like `echo > file.txt` or `sed -i`) are not captured by the checkpoint system.

## How checkpointing works

When you enable file checkpointing, the SDK creates backups of files before modifying them through the Write, Edit, or NotebookEdit tools. User messages in the response stream include a checkpoint UUID that you can use as a restore point.

Checkpoint works with these built-in tools that the agent uses to modify files:

| Tool | Description |
|------|-------------|
| Write | Creates a new file or overwrites an existing file with new content |
| Edit | Makes targeted edits to specific parts of an existing file |
| NotebookEdit | Modifies cells in Jupyter notebooks (`.ipynb` files) |

> **Note:** File rewinding restores files on disk to a previous state. It does not rewind the conversation itself. The conversation history and context remain intact after calling `rewind_files()`.

The checkpoint system tracks:

- Files created during the session
- Files modified during the session
- The original content of modified files

When you rewind to a checkpoint, created files are deleted and modified files are restored to their content at that point.

## Implement checkpointing

To use file checkpointing, enable it in your options, capture checkpoint UUIDs from the response stream, then call `rewind_files()` when you need to restore.

The following example shows the complete flow: enable checkpointing, capture the checkpoint UUID and session ID from the response stream, then resume the session later to rewind files.

```python
import asyncio
import os
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, UserMessage, ResultMessage

async def main():
    # Step 1: Enable checkpointing
    options = ClaudeAgentOptions(
        enable_file_checkpointing=True,
        permission_mode="acceptEdits",  # Auto-accept file edits without prompting
        extra_args={"replay-user-messages": None},  # Required to receive checkpoint UUIDs in the response stream
        env={**os.environ, "CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING": "1"}
    )

    checkpoint_id = None
    session_id = None

    # Run the query and capture checkpoint UUID and session ID
    async with ClaudeSDKClient(options) as client:
        await client.query("Refactor the authentication module")

        # Step 2: Capture checkpoint UUID from the first user message
        async for message in client.receive_response():
            if isinstance(message, UserMessage) and message.uuid and not checkpoint_id:
                checkpoint_id = message.uuid
            if isinstance(message, ResultMessage) and not session_id:
                session_id = message.session_id

    # Step 3: Later, rewind by resuming the session with an empty prompt
    if checkpoint_id and session_id:
        async with ClaudeSDKClient(ClaudeAgentOptions(
            enable_file_checkpointing=True,
            resume=session_id
        )) as client:
            await client.query("")  # Empty prompt to open the connection
            async for message in client.receive_response():
                await client.rewind_files(checkpoint_id)
                break
        print(f"Rewound to checkpoint: {checkpoint_id}")

asyncio.run(main())
```

### Step 1: Set the environment variable

File checkpointing requires the `CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING` environment variable. You can set it either via command line before running your script, or directly in the SDK options.

**Option 1: Set via command line**

```bash
export CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING=1
```

**Option 2: Set in SDK options**

```python
import os

options = ClaudeAgentOptions(
    enable_file_checkpointing=True,
    env={**os.environ, "CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING": "1"}
)
```

### Step 2: Enable checkpointing

Configure your SDK options to enable checkpointing and receive checkpoint UUIDs:

| Option | Python | Description |
|--------|--------|-------------|
| Enable checkpointing | `enable_file_checkpointing=True` | Tracks file changes for rewinding |
| Receive checkpoint UUIDs | `extra_args={"replay-user-messages": None}` | Required to get user message UUIDs in the stream |

```python
options = ClaudeAgentOptions(
    enable_file_checkpointing=True,
    permission_mode="acceptEdits",
    extra_args={"replay-user-messages": None}
)

async with ClaudeSDKClient(options) as client:
    await client.query("Refactor the authentication module")
```

### Step 3: Capture checkpoint UUID and session ID

With the `replay-user-messages` option set, each user message in the response stream has a UUID that serves as a checkpoint.

For most use cases, capture the first user message UUID (`message.uuid`); rewinding to it restores all files to their original state. To store multiple checkpoints and rewind to intermediate states, see Multiple restore points below.

```python
checkpoint_id = None
session_id = None

async for message in client.receive_response():
    # Update checkpoint on each user message (keeps the latest)
    if isinstance(message, UserMessage) and message.uuid:
        checkpoint_id = message.uuid
    # Capture session ID from the result message
    if isinstance(message, ResultMessage):
        session_id = message.session_id
```

### Step 4: Rewind files

To rewind after the stream completes, resume the session with an empty prompt and call `rewind_files()` with your checkpoint UUID.

```python
async with ClaudeSDKClient(ClaudeAgentOptions(
    enable_file_checkpointing=True,
    resume=session_id
)) as client:
    await client.query("")  # Empty prompt to open the connection
    async for message in client.receive_response():
        await client.rewind_files(checkpoint_id)
        break
```

If you capture the session ID and checkpoint ID, you can also rewind from the CLI:

```bash
claude --resume <session-id> --rewind-files <checkpoint-uuid>
```

## Common patterns

### Checkpoint before risky operations

This pattern keeps only the most recent checkpoint UUID, updating it before each agent turn. If something goes wrong during processing, you can immediately rewind to the last safe state and break out of the loop.

```python
import asyncio
import os
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, UserMessage

async def main():
    options = ClaudeAgentOptions(
        enable_file_checkpointing=True,
        permission_mode="acceptEdits",
        extra_args={"replay-user-messages": None},
        env={**os.environ, "CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING": "1"}
    )

    safe_checkpoint = None

    async with ClaudeSDKClient(options) as client:
        await client.query("Refactor the authentication module")

        async for message in client.receive_response():
            # Update checkpoint before each agent turn starts
            # This overwrites the previous checkpoint. Only keep the latest
            if isinstance(message, UserMessage) and message.uuid:
                safe_checkpoint = message.uuid

            # Decide when to revert based on your own logic
            # For example: error detection, validation failure, or user input
            if your_revert_condition and safe_checkpoint:
                await client.rewind_files(safe_checkpoint)
                # Exit the loop after rewinding, files are restored
                break

asyncio.run(main())
```

### Multiple restore points

If Claude makes changes across multiple turns, you might want to rewind to a specific point rather than all the way back.

```python
import asyncio
import os
from dataclasses import dataclass
from datetime import datetime
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, UserMessage, ResultMessage

@dataclass
class Checkpoint:
    id: str
    description: str
    timestamp: datetime

async def main():
    options = ClaudeAgentOptions(
        enable_file_checkpointing=True,
        permission_mode="acceptEdits",
        extra_args={"replay-user-messages": None},
        env={**os.environ, "CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING": "1"}
    )

    checkpoints = []
    session_id = None

    async with ClaudeSDKClient(options) as client:
        await client.query("Refactor the authentication module")

        async for message in client.receive_response():
            if isinstance(message, UserMessage) and message.uuid:
                checkpoints.append(Checkpoint(
                    id=message.uuid,
                    description=f"After turn {len(checkpoints) + 1}",
                    timestamp=datetime.now()
                ))
            if isinstance(message, ResultMessage) and not session_id:
                session_id = message.session_id

    # Later: rewind to any checkpoint by resuming the session
    if checkpoints and session_id:
        target = checkpoints[0]  # Pick any checkpoint
        async with ClaudeSDKClient(ClaudeAgentOptions(
            enable_file_checkpointing=True,
            resume=session_id
        )) as client:
            await client.query("")  # Empty prompt to open the connection
            async for message in client.receive_response():
                await client.rewind_files(target.id)
                break
        print(f"Rewound to: {target.description}")

asyncio.run(main())
```

## Limitations

File checkpointing has the following limitations:

| Limitation | Description |
|------------|-------------|
| Write/Edit/NotebookEdit tools only | Changes made through Bash commands are not tracked |
| Same session | Checkpoints are tied to the session that created them |
| File content only | Creating, moving, or deleting directories is not undone by rewinding |
| Local files | Remote or network files are not tracked |

## Troubleshooting

### Checkpointing options not recognized

If `enable_file_checkpointing` or `rewind_files()` isn't available, you may be on an older SDK version.

**Solution**: Update to the latest SDK version: `pip install --upgrade claude-agent-sdk`

### User messages don't have UUIDs

If `message.uuid` is missing, you're not receiving checkpoint UUIDs.

**Cause**: The `replay-user-messages` option isn't set.

**Solution**: Add `extra_args={"replay-user-messages": None}` to your options.

### "No file checkpoint found for message" error

This error occurs when the checkpoint data doesn't exist for the specified user message UUID.

**Common causes**:
- The `CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING` environment variable isn't set
- The session wasn't properly completed before attempting to resume and rewind

**Solution**: Make sure you've set the environment variable, then use the pattern shown in the examples.

### "ProcessTransport is not ready for writing" error

This error occurs when you call `rewind_files()` after you've finished iterating through the response.

**Solution**: Resume the session with an empty prompt, then call rewind on the new query.

## Next steps

- **[Sessions](/docs/en/agent-sdk/sessions)**: learn how to resume sessions, which is required for rewinding after the stream completes
- **[Permissions](/docs/en/agent-sdk/permissions)**: configure which tools Claude can use and how file modifications are approved
- **[Python SDK reference](/docs/en/agent-sdk/python)**: complete API reference
