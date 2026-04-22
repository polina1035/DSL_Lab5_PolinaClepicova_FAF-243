import itertools


class CFGtoCNF:
    def __init__(self, start_symbol, productions):
        self.start = start_symbol
        self.p = productions  # Dictionary format: {'S': ['abAB'], ...}
        self.new_var_counter = 1

    def normalize(self):
        print("--- Original Grammar ---")
        self.print_grammar()

        self.eliminate_epsilon()
        self.eliminate_unit()
        self.eliminate_inaccessible()
        self.eliminate_non_productive()
        self.convert_to_cnf()

        print("\n--- Final Chomsky Normal Form ---")
        self.print_grammar()
        return self.p

    def eliminate_epsilon(self):
        # 1. Find nullable variables
        nullables = set(nt for nt, rules in self.p.items() if 'eps' in rules)

        # 2. Add rules without nullables
        new_p = {nt: set(rules) for nt, rules in self.p.items()}
        for nt in new_p:
            new_p[nt].discard('eps')

        for nt, rules in self.p.items():
            for rule in rules:
                if rule == 'eps': continue
                # Find positions of nullable variables in the rule
                nullable_indices = [i for i, char in enumerate(rule) if char in nullables]
                if not nullable_indices: continue

                # Generate all combinations of removing nullable variables
                for r in range(1, len(nullable_indices) + 1):
                    for combo in itertools.combinations(nullable_indices, r):
                        new_rule = "".join([char for i, char in enumerate(rule) if i not in combo])
                        if new_rule:  # avoid adding empty string if not intended
                            new_p[nt].add(new_rule)

        self.p = {nt: list(rules) for nt, rules in new_p.items()}

    def eliminate_unit(self):
        # Keep resolving A -> B until no changes
        changed = True
        while changed:
            changed = False
            new_p = {nt: set(rules) for nt, rules in self.p.items()}
            for nt, rules in self.p.items():
                for rule in rules:
                    if len(rule) == 1 and rule.isupper():  # It's a unit production
                        new_p[nt].remove(rule)
                        if rule in self.p:
                            for sub_rule in self.p[rule]:
                                if sub_rule not in new_p[nt]:
                                    new_p[nt].add(sub_rule)
                                    changed = True
            self.p = {nt: list(rules) for nt, rules in new_p.items()}

    def eliminate_inaccessible(self):
        accessible = set([self.start])
        queue = [self.start]

        while queue:
            current = queue.pop(0)
            if current not in self.p: continue
            for rule in self.p[current]:
                for char in rule:
                    if char.isupper() and char not in accessible:
                        accessible.add(char)
                        queue.append(char)

        self.p = {nt: rules for nt, rules in self.p.items() if nt in accessible}

    def eliminate_non_productive(self):
        productive = set()
        changed = True

        while changed:
            changed = False
            for nt, rules in self.p.items():
                if nt in productive: continue
                for rule in rules:
                    # A rule is productive if all its symbols are terminals or productive non-terminals
                    if all((char.islower() or char in productive) for char in rule):
                        productive.add(nt)
                        changed = True
                        break

        self.p = {nt: rules for nt, rules in self.p.items() if nt in productive}

    def _get_new_var(self):
        var = f"Z{self.new_var_counter}"
        self.new_var_counter += 1
        return var

    def convert_to_cnf(self):
        new_p = {}
        terminals_map = {}  # Maps 'a' to 'X', 'b' to 'Y'

        # Step A: Replace terminals in long rules
        temp_p = {}
        for nt, rules in self.p.items():
            temp_p[nt] = []
            for rule in rules:
                if len(rule) == 1 and rule.islower():
                    temp_p[nt].append(rule)
                else:
                    new_rule = ""
                    for char in rule:
                        if char.islower():
                            if char not in terminals_map:
                                new_nt = 'X' if char == 'a' else 'Y'
                                terminals_map[char] = new_nt
                                new_p[new_nt] = [char]
                            new_rule += terminals_map[char]
                        else:
                            new_rule += char
                    temp_p[nt].append(new_rule)

        # Step B: Break rules longer than 2 non-terminals
        final_p = dict(new_p)
        for nt, rules in temp_p.items():
            final_p[nt] = []
            for rule in rules:
                while len(rule) > 2:
                    first_two = rule[:2]
                    # Check if we already have a variable for this pair
                    new_var = None
                    for k, v in final_p.items():
                        if v == [first_two] and k.startswith('Z'):
                            new_var = k
                            break
                    if not new_var:
                        new_var = self._get_new_var()
                        final_p[new_var] = [first_two]
                    rule = new_var + rule[2:]
                final_p[nt].append(rule)

        self.p = final_p

    def print_grammar(self):
        for nt, rules in self.p.items():
            print(f"{nt} -> {' | '.join(rules)}")


if __name__ == "__main__":
    # VARIANT 16
    productions = {
        'S': ['abAB'],
        'A': ['aSab', 'BS', 'aA', 'b'],
        'B': ['BA', 'ababB', 'b', 'eps'],
        'C': ['AS']
    }

    grammar = CFGtoCNF(start_symbol='S', productions=productions)
    grammar.normalize()
