import sys


def clean_line(line: str) -> str:
    line = line.split("//", 1)[0]
    line = line.replace(" ", "").replace("\t", "").rstrip("\n")
    return line


def parse_transition(line: str):
    left, right = line.split("->")

    left = left.strip()
    right = right.strip()

    left_parts = left[1:-1].split(",")
    right_parts = right[1:-1].split(",")

    from_state, symbol, c1_cond, c2_cond = left_parts
    to_state, c1_action, c2_action = right_parts

    return (
        (from_state, symbol, c1_cond, c2_cond),
        (to_state, c1_action, c2_action),
    )


def expand_condition(cond: str):
    return ["=", ">"] if cond == "*" else [cond]


def add_transition(transitions: dict, key, value):
    transitions[key] = value


def load_transitions(filename: str):
    transitions = {}

    with open(filename, "r") as f:
        for raw_line in f:
            line = clean_line(raw_line)
            if not line:
                continue

            key, value = parse_transition(line)
            from_state, symbol, c1_cond, c2_cond = key

            for c1 in expand_condition(c1_cond):
                for c2 in expand_condition(c2_cond):
                    transitions[(from_state, symbol, c1, c2)] = value

    return transitions


def sign(counter: int) -> str:
    return "=" if counter == 0 else ">"


def apply_action(counter: int, action: str) -> int:
    if action == "+":
        return counter + 1
    if action == "-":
        return max(0, counter - 1)
    return counter


def get_successor(transitions, state, remaining, c1, c2):
    c1s = sign(c1)
    c2s = sign(c2)

    if remaining:
        key = (state, remaining[0], c1s, c2s)
        if key in transitions:
            ns, a1, a2 = transitions[key]
            return ns, remaining[1:], apply_action(c1, a1), apply_action(c2, a2)

    key = (state, "", c1s, c2s)
    if key in transitions:
        ns, a1, a2 = transitions[key]
        return ns, remaining, apply_action(c1, a1), apply_action(c2, a2)

    return None


def is_accepting(remaining, c1, c2):
    return remaining == "" and c1 == 0 and c2 == 0


def print_config(state, remaining, c1, c2):
    print(f"{state:>16}, {remaining:>20}, {c1:>3}, {c2:>3}")


def simulate(transitions, input_string):
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


def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    transitions = load_transitions(sys.argv[1])

    for line in sys.stdin:
        simulate(transitions, line.rstrip("\n"))

    print()


if __name__ == "__main__":
    main()