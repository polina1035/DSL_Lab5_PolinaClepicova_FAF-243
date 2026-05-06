import itertools


class CFGtoCNF:
    def __init__(self, start_symbol, productions):
        self.start = start_symbol
        # Превращаем строки в списки токенов: 'abAB' -> ['a', 'b', 'A', 'B']
        self.p = {nt: [list(rule) if rule != 'eps' else [] for rule in rules]
                  for nt, rules in productions.items()}
        self.new_var_counter = 1

    def normalize(self):
        print("--- Original Grammar ---")
        self.print_grammar()

        self.eliminate_epsilon()
        self.eliminate_unit()
        self.eliminate_non_productive()
        self.eliminate_inaccessible()
        self.convert_to_cnf()

        print("\n--- Final Chomsky Normal Form ---")
        self.print_grammar()
        return self.p

    def eliminate_epsilon(self):
        nullables = set(nt for nt, rules in self.p.items() if [] in rules)

        new_p = {nt: [r for r in rules if r != []] for nt, rules in self.p.items()}

        for nt, rules in self.p.items():
            for rule in rules:
                if not rule: continue
                indices = [i for i, sym in enumerate(rule) if sym in nullables]
                for r in range(1, len(indices) + 1):
                    for combo in itertools.combinations(indices, r):
                        # Создаем новую комбинацию без nullable символов
                        new_rule = [sym for i, sym in enumerate(rule) if i not in combo]
                        if new_rule and new_rule not in new_p[nt]:
                            new_p[nt].append(new_rule)
        self.p = new_p

    def eliminate_unit(self):
        changed = True
        while changed:
            changed = False
            for nt in list(self.p.keys()):
                for rule in self.p[nt]:
                    if len(rule) == 1 and rule[0].isupper():  # Unit production
                        unit_target = rule[0]
                        self.p[nt].remove(rule)
                        if unit_target in self.p:
                            for target_rule in self.p[unit_target]:
                                if target_rule not in self.p[nt]:
                                    self.p[nt].append(target_rule)
                                    changed = True
                        break  # Начинаем заново после изменения

    def eliminate_inaccessible(self):
        accessible = {self.start}
        queue = [self.start]
        while queue:
            curr = queue.pop(0)
            if curr in self.p:
                for rule in self.p[curr]:
                    for sym in rule:
                        if sym.isupper() and sym not in accessible:
                            accessible.add(sym)
                            queue.append(sym)
        self.p = {nt: rules for nt, rules in self.p.items() if nt in accessible}

    def eliminate_non_productive(self):
        productive = set()
        changed = True
        while changed:
            changed = False
            for nt, rules in self.p.items():
                if nt in productive: continue
                for rule in rules:
                    if all(not sym.isupper() or sym in productive for sym in rule):
                        productive.add(nt)
                        changed = True
                        break
        self.p = {nt: rules for nt, rules in self.p.items() if nt in productive}

    def _get_new_var(self):
        var = f"Z{self.new_var_counter}"
        self.new_var_counter += 1
        return var

    def convert_to_cnf(self):
        term_map = {}
        final_p = {}

        # 1. Заменяем терминалы в длинных правилах
        for nt, rules in self.p.items():
            new_rules = []
            for rule in rules:
                if len(rule) <= 1:
                    new_rules.append(rule)
                else:
                    processed_rule = []
                    for sym in rule:
                        if not sym.isupper():  # Это терминал
                            if sym not in term_map:
                                new_v = f"T{sym.upper()}"
                                term_map[sym] = new_v
                                final_p[new_v] = [[sym]]
                            processed_rule.append(term_map[sym])
                        else:
                            processed_rule.append(sym)
                    new_rules.append(processed_rule)
            final_p[nt] = new_rules

        # 2. Бинаризация (разбиение правил длиннее 2)
        changed = True
        while changed:
            changed = False
            for nt in list(final_p.keys()):
                new_rules = []
                for rule in final_p[nt]:
                    if len(rule) > 2:
                        new_v = self._get_new_var()
                        first_two = rule[:2]
                        rest = rule[2:]

                        final_p[new_v] = [first_two]
                        new_rules.append([new_v] + rest)
                        changed = True
                    else:
                        new_rules.append(rule)
                final_p[nt] = new_rules

        self.p = final_p

    def print_grammar(self):
        for nt, rules in self.p.items():
            formatted_rules = [''.join(r) if r else 'eps' for r in rules]
            print(f"{nt} -> {' | '.join(formatted_rules)}")


if __name__ == "__main__":
    productions = {
        'S': ['abAB'],
        'A': ['aSab', 'BS', 'aA', 'b'],
        'B': ['BA', 'ababB', 'b', 'eps'],
        'C': ['AS']
    }

    grammar = CFGtoCNF(start_symbol='S', productions=productions)
    grammar.normalize()
