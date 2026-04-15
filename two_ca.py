import sys


def clean_line(line: str) -> str:
    """Remove comments, spaces, tabs, and trailing newline."""
    line = line.split("//", 1)[0]
    line = line.replace(" ", "").replace("\t", "").rstrip("\n")
    return line


def parse_transition(line: str):
    """
    Parse one transition line.

    Returns:
        ((from_state, symbol, c1_cond, c2_cond), (to_state, c1_action, c2_action))
    """
    left, right = line.split("->")

    left = left.strip()
    right = right.strip()

    if not (left.startswith("(") and left.endswith(")")):
        raise ValueError(f"Bad left side: {left}")
    if not (right.startswith("(") and right.endswith(")")):
        raise ValueError(f"Bad right side: {right}")

    left_parts = left[1:-1].split(",")
    right_parts = right[1:-1].split(",")

    if len(left_parts) != 4:
        raise ValueError(f"Left side should have 4 parts: {left}")
    if len(right_parts) != 3:
        raise ValueError(f"Right side should have 3 parts: {right}")

    from_state, symbol, c1_cond, c2_cond = left_parts
    to_state, c1_action, c2_action = right_parts

    return (
        (from_state, symbol, c1_cond, c2_cond),
        (to_state, c1_action, c2_action),
    )


def expand_condition(cond: str):
    """Expand wildcard '*' into both '=' and '>'."""
    if cond == "*":
        return ["=", ">"]
    return [cond]


def add_transition(transitions: dict, key, value):
    """Add one concrete transition to the dictionary."""
    if key in transitions:
        raise ValueError(f"Duplicate transition detected for key {key}")
    transitions[key] = value


def load_transitions(filename: str):
    """Read and parse all transitions from file into a dictionary."""
    transitions = {}

    with open(filename, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    for raw_line in raw_lines:
        line = clean_line(raw_line)

        if not line:
            continue

        key, value = parse_transition(line)
        from_state, symbol, c1_cond, c2_cond = key

        for real_c1 in expand_condition(c1_cond):
            for real_c2 in expand_condition(c2_cond):
                real_key = (from_state, symbol, real_c1, real_c2)
                add_transition(transitions, real_key, value)

    return transitions


def sign(counter: int) -> str:
    """Return '=' if counter is 0, else '>'."""
    return "=" if counter == 0 else ">"


def delta(action: str) -> int:
    """Convert action symbol into integer change."""
    if action == "+":
        return 1
    if action == "=":
        return 0
    if action == "-":
        return -1
    raise ValueError(f"Unknown action: {action}")


def apply_action(counter: int, action: str) -> int:
    """Apply an action to a counter without going below 0."""
    return max(0, counter + delta(action))


def get_successor(transitions: dict, state: str, remaining: str, c1: int, c2: int):
    """
    Return the next configuration as:
        (new_state, new_remaining, new_c1, new_c2)
    or None if no successor exists.
    """
    c1_sign = sign(c1)
    c2_sign = sign(c2)

    # Try non-epsilon transition first if input remains.
    if remaining:
        next_symbol = remaining[0]
        key = (state, next_symbol, c1_sign, c2_sign)

        if key in transitions:
            new_state, a1, a2 = transitions[key]
            return (
                new_state,
                remaining[1:],
                apply_action(c1, a1),
                apply_action(c2, a2),
            )

    # If no normal transition worked, try epsilon.
    epsilon_key = (state, "", c1_sign, c2_sign)
    if epsilon_key in transitions:
        new_state, a1, a2 = transitions[epsilon_key]
        return (
            new_state,
            remaining,
            apply_action(c1, a1),
            apply_action(c2, a2),
        )

    return None


def is_accepting(remaining: str, c1: int, c2: int) -> bool:
    """Return True if this is an accepting configuration."""
    return remaining == "" and c1 == 0 and c2 == 0


def print_config(state: str, remaining: str, c1: int, c2: int):
    """Print one configuration to standard output."""
    print(f"{state:>16}, {remaining:>20}, {c1:>3}, {c2:>3}")


def simulate(transitions: dict, input_string: str):
    state = "#"
    remaining = input_string
    c1 = 0
    c2 = 0

    while True:
        print_config(state, remaining, c1, c2)

        successor = get_successor(transitions, state, remaining, c1, c2)
        if successor is None:
            if is_accepting(remaining, c1, c2):
                print("----ACCEPT")
            else:
                print("----REJECT")
            return

        state, remaining, c1, c2 = successor

        if is_accepting(remaining, c1, c2):
            print("----ACCEPT")
    else:
            print("----REJECT")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 two_ca.py <automaton_file>", file=sys.stderr)
        sys.exit(1)

    filename = sys.argv[1]

    try:
        transitions = load_transitions(filename)
    except FileNotFoundError:
        print("File not found.", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        sys.exit(1)

    for line in sys.stdin:
        input_string = line.rstrip("\n")
        simulate(transitions, input_string)


if __name__ == "__main__":
    main()