"""Everything the analysis fixes in advance: seeds, contrasts, bounds, the design, and the
registered values every grid run must carry. Each value names the protocol section it comes from.
"""

# Seeds (protocol sections 5.3 and 8.1)
ANALYSIS_SEED = "61f43c6f3593702f"   # every permutation and every bootstrap
DRAW_SEED = "bb696caef027c79c"       # the quality-sample and re-grade draws (blind_tools.py)

# Resampling sizes (protocol section 8.1)
N_PERM = 10000
N_BOOT = 10000

# The design (protocol sections 2.3, 2.4 and 5.2)
TASKS = ("message-board", "kanban-board")
CONDITIONS = ("no_verification", "execution", "interactive")
FEEDBACK_CONDITIONS = ("execution", "interactive")
ARMS = {
    "gemma-q4": ("off", "unseen", "seen"),
    "qwen-q4": ("off", "unseen", "seen"),
    "seed-q4": ("off", "unseen", "seen"),
    "gptoss-20b": ("unseen", "seen"),
    "glm-q4": ("off", "unseen", "seen"),
    "qwen-moe-q4": ("off", "unseen", "seen"),
    "gemma-moe-q4": ("off", "unseen", "seen"),
    "muse-q4xl": ("unseen", "seen"),
}
TIERS = {
    "tier1": ("gemma-q4", "qwen-q4"),
    "tier2": ("seed-q4",),
    "tier3": ("gptoss-20b",),
    "tier4": ("glm-q4",),
    "tier5": ("qwen-moe-q4", "gemma-moe-q4"),
    "tier6": ("muse-q4xl",),
}
REPLICATES = 20
QUALITY_PER_CELL = 10

# The within-lab pairs (protocol section 8.4): (twin, sibling)
TWINS = (("qwen-moe-q4", "qwen-q4"), ("gemma-moe-q4", "gemma-q4"))

# The contrasts (protocol sections 1.3 and 8.1): (name, reference arm a, treatment arm b).
# Every difference is reported as b minus a.
CONTRASTS = (("H1", "unseen", "seen"), ("H2", "off", "unseen"))
MECHANISM = ("H3", "H4", "H5")       # UNSEEN against SEEN, one-sided
ALPHA = 0.05

# Every terminal status the frozen harness can record for a run that is analysed, as
# harness/agent.py returns them (run_agent's docstring and its return statements). Every
# status but "finished" is a failure (protocol section 6.1). "api_error", "interrupted" and
# "crashed: ..." end a run whose runner fails, so they are voids and never reach the table.
STATUSES = (
    "finished",
    "stuck_looping",            # a loop guard fired (which one: manifest loop_guard_fired)
    "stuck_blocked_tool",       # three calls in a row to a tool the condition does not offer
    "stopped_no_tool_call",     # two turns in a row without a tool call, the second after the nudge
    "runaway_no_tool_call",     # a reply without a tool call that used the whole reply allowance
    "truncated_no_tool_call",   # a reply without a tool call cut off below the allowance
    "truncated_tool_args",      # the same call repeated, its arguments cut off and unparseable
    "context_overflow",         # the server refused a request that outgrew the context window
    "token_budget_exhausted",   # the 20M-token budget ran out
    "budget_exhausted",         # MAX_STEPS (10,000) reached
)
FAIL_STATUSES = STATUSES[1:]

# Equivalence bounds (protocol section 8.2)
EQUIV_FAILURE = 0.10                 # +/- 10 percentage points
EQUIV_STEPS = (0.8, 1.25)            # ratio of geometric means

# The registered configuration every grid run must carry (protocol section 9, "One configuration")
REGISTERED = {
    "harness_git": "90a47586ec6ce82858d4c9da3346b3d333ffa227",
    "base_prompt_sha": "a1b949af9e7bda1c",
    "condition_briefing_sha": "c988f43155c49538",
    "decoding_registry_sha": "d3149737912ebbde",
    "think_preamble_sha": "e3b0c44298fc1c14",
    "briefing_mode": "universal",
    "replay_format": "field",
    "max_total_tokens": 20000000,
}
TASK_SHA = {"message-board": "296815692d88f5cb", "kanban-board": "01d2615d510ad8b1"}

# The copy of the smoke gate script whose reasoning rules H3 to H5 count by (DESIGN.md section 3)
VERIFY_SMOKES_SHA256 = "201744dad1dd84a2cb32df9c9bd4694841832e9c283fbeb5c1c9f6bd281c1d0d"

# Energy (protocol section 6.2): the bound used for a batch without a power log
BOARD_POWER_LIMIT_W = 300.0


def seed_int(seed_hex, salt=""):
    """A 64-bit integer seed from a hex seed and a salt, so that each use has its own stream."""
    import hashlib
    h = hashlib.sha256((seed_hex + ":" + salt).encode()).hexdigest()
    return int(h[:16], 16)
