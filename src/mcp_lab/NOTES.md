# MCP workspace-scope lab: handoff note

**Goal:** see for yourself that MCP server availability follows the workspace (CCA-F Round 5 Q35), and how that connects to stdio, secrets, and headless (CI-style) runs.

**Status:** setup and experiments 1-6 done. Only the optional pipeline simulation remains.

## How the lab maps to the exam diagrams

| Lab piece | Exam concept |
|---|---|
| `~/mcp-lab/client-a`, `client-b` folders | Two workspaces (Round 5 Block 3 clients) |
| `client-a/.mcp.json` | The workspace's "project config" box |
| Claude Code | MCP host (it creates one client per server) |
| `lab_server.py` | MCP server, launched as a subprocess over stdio |
| `client-a/.claude/settings.local.json` | Personal approval of that workspace's servers |
| `claude -p` (experiment 6) | The headless review-agent stage of a CI pipeline |

## Environment facts

- macOS, zsh, VS Code, `uv`, Homebrew Python 3.12.4
- Lab folder: `~/mcp-lab` (outside the `claude-architect-cert` repo, on purpose)
- Lab environment: `~/mcp-lab/.venv`, with `mcp` **pinned below version 2**
  (`uv pip install --python ~/mcp-lab/.venv/bin/python "mcp[cli]<2"`).
  mcp 2.x renamed FastMCP; the pin is Round 5 Q37 in practice.
- Server file: `~/mcp-lab/lab_server.py`: one tool (`whoami`) and one resource (`lab://policy`). It reads its label from the launch command (`sys.argv[1]`). Never use `print()` in it: stdout is the protocol channel.

## What's done

1. Folders, environment, and `lab_server.py` created and tested by hand (it waits silently for a client, which is correct).
2. `lab-a` registered in `client-a`, `lab-b` in `client-b` (`claude mcp add --scope project ...`). Both `.mcp.json` files checked with `cat`.
3. **Experiment 1:** in `client-a`, `/mcp` showed `lab-a` connected (config location `client-a/.mcp.json`). `whoami` returned `Hello from the client-a server. Token present: no`.
4. **Experiment 2:** in `client-b`, `/mcp` listed only `lab-b` under Project MCPs. `lab-a` was absent. `whoami` returned `Hello from the client-b server. Token present: no`. A separate approval prompt appeared, and `client-b/.claude` was created: approvals are per workspace.
5. Noticed: the `claude.ai` connectors (Claude Docs, Google Drive) appeared in both workspaces. They belong to the account, so they follow the person everywhere.

## Results

- **Exp 3 (user scope):** `lab-everywhere` appeared in both client-a and client-b, under User MCPs, config location `~/.claude.json`. User scope follows the person, not the workspace (why Q35's "user-scoped toggled per engagement" lost).
- **Exp 4 (process tree):** both `lab_server.py` processes had the `claude` process as parent. Host = `claude`, servers = its child processes, clients live inside the host (no separate process). A removed server keeps running until the session exits.
- **Exp 5 (secret by reference):** `.mcp.json` holds `${LAB_TOKEN}`, never the value. See the open question in Gotchas.
- **Exp 6 (headless):** with `--allowedTools "mcp__lab-a__whoami"` the call ran with no prompt. Without it the call was blocked, because no human is there to approve it. CI agents need permissions granted up front (R5-Q5).


## Resume checklist (do this first)

1. Open VS Code on the **mcp-lab** folder (File, Open Folder). The Explorer header should read MCP-LAB.
2. Open a terminal (Ctrl + `). Set the shortcut again if this is a new tab:
   ```bash
   PY=~/mcp-lab/.venv/bin/python
   echo $PY
   ```
3. Check the prompt: it should show `(mcp-lab)` or similar and the folder name. Folder decides workspace.
4. Each time you start `claude`, run `/model` and pick **Sonnet** (the lab doesn't need Opus). If it says "Not logged in", run `/login`.
5. Permission mode: newer Claude Code defaults to **auto mode**. Press Shift + Tab to cycle back to manual if you want to see approval prompts.

## Remaining experiments: these experiments are done 

Write your prediction **before** each run.

| # | Do this | Predict, then check | Exam link |
|---|---|---|---|
| 3 | Add a user-scope server: `claude mcp add --scope user lab-everywhere -- $PY ~/mcp-lab/lab_server.py user`. Start `claude` in `client-a`, run `/mcp`, note where `lab-everywhere` appears and its config location. Repeat in `client-b`. Clean up: `claude mcp remove lab-everywhere --scope user` | Does it appear in `client-a`, `client-b`, both, or neither? | Why "user-scoped config toggled per engagement" lost in Q35 |
| 4 | With a session open in `client-a`, in a **second** terminal tab run `ps aux \| grep lab_server` | Who started the server process? (Ignore the `grep` line itself.) | R4-Q5: local server = host's subprocess = stdio |
| 5 | In `client-a/.mcp.json`, add `"env": {"LAB_TOKEN": "${LAB_TOKEN}"}` inside `lab-a`. Run `claude` with the variable **unset**, ask for `whoami`. Then `export LAB_TOKEN=demo`, restart `claude`, ask again | Does `whoami` change from `no` to `yes`? Is the token value anywhere in the file? | R5-Q36: config references the secret; the value lives elsewhere |
| 6 | In `client-a`: `claude -p "Call the whoami tool and report the result" --allowedTools "mcp__lab-a__whoami"` (add `--model sonnet` to save usage) | Any approval prompt? What happens without `--allowedTools`? | CI: headless runs need permissions granted in advance (R5-Q5) |

## Step 4: reflection questions (one sentence each)

1. Which file was the "project config" box, and which was user scope?
2. In experiment 4, which process was the **host**, which the **server**, and where was the **client**?
3. In experiment 5, why is `${LAB_TOKEN}` acceptable in a committed file when the token itself is not?
4. Experiment 6 ran with no human present. Which pipeline diagram does it belong to?

## Gotchas learned

- **Read the prompt before running a command.** Parentheses show the active environment; the word before `%` is the current folder.
- **Name the target explicitly.** `uv pip install --python <path>` beat letting uv guess; it twice installed into the wrong environment.
- **Silence usually means success.** `mkdir` and `py_compile` print nothing when they work; a stdio server prints nothing while it waits.
- **Ctrl + C stops anything running** in a terminal.
- **Restricted Mode** switches off VS Code extensions until you trust the folder.
- `.mcp.json` holds **absolute paths** (`/Users/Spring/...`). It works on this Mac, but would break on a teammate's laptop or a CI runner. Real shared configs avoid machine-specific paths and reference secrets with `${VARIABLE}`.
- `settings.local.json` is personal approval state. Don't commit it.
- **Open question:** `whoami` said `Token present: yes` with `LAB_TOKEN` unset in my shell (also in headless mode). The server checks `os.environ.get("LAB_TOKEN")` for truthiness, so it received a non-empty value. Cause unconfirmed, perhaps the literal `${LAB_TOKEN}` text. Don't treat `whoami` output as proof the secret arrived. `ps eww -p <server PID>` would show the real value.
- **`/model` takes an alias** (`/model sonnet`) or the picker, not names like `sonnet5.5`.
- **Don't type `<PID>` placeholders literally.** zsh reads `<` as redirection and gives a parse error. Use the real number.
- **Shell commands typed into the Claude session run through the model** and use your quota. Use a plain terminal tab.



## Optional follow-up after experiment 6

Simulate one pipeline run end to end: clone the lab into a fresh temporary folder (the "ephemeral runner"), run `claude -p` there with JSON output (`--output-format json`), and have a tiny script read the JSON and exit with pass or fail (the "gate").

## Moving this into your repo

Copy only the server and this note, not the environment or personal settings:

```bash
mkdir -p ~/projects/claude-architect-cert/src/mcp_lab
cp ~/mcp-lab/lab_server.py ~/projects/claude-architect-cert/src/mcp_lab/
# also copy this note as NOTES.md into that folder
cd ~/projects/claude-architect-cert
git status
git add src/mcp_lab
git commit -m "Add MCP workspace-scope lab: server and notes (experiments 1-2 done)"
git push
```

Stage only `src/mcp_lab`: your repo already has other uncommitted changes. Don't copy `.venv` or any `.claude/settings.local.json`.
