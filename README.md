# Laboratory Work No. 5: Chomsky Normal Form

### Course: Formal Languages & Finite Automata
### Author: Polina Clepicova FAF-243
### Variant 16

---

## Theory
Chomsky Normal Form (CNF) is a simplified form of Context-Free Grammars (CFG). A grammar is in CNF if all its production rules are in one of the following forms:
- $A \rightarrow BC$ (A non-terminal leading to exactly two non-terminals)
- $A \rightarrow a$ (A non-terminal leading to exactly one terminal)
- $S \rightarrow \epsilon$ (Only if the start symbol can derive an empty string and does not appear on the right side of any rule)

The process of normalization involves five main steps: eliminating epsilon productions, removing unit productions (renaming), deleting inaccessible symbols, removing non-productive symbols, and finally, binarizing long rules while replacing terminals in mixed strings.

---

## Objectives:
- Familiarize with the theoretical background of Chomsky Normal Form.
- Implement an automated algorithm to transform any input Context-Free Grammar into its equivalent CNF.
- Apply the implementation to Variant 16 and verify the correctness of the transformation steps.
- Ensure the code is modular, following Object-Oriented Programming (OOP) principles.

---

## Implementation description

### 1. Epsilon Production Elimination
The `eliminate_epsilon` method first identifies all "nullable" symbols (those that can derive an empty string). It then iterates through all existing rules and generates all possible combinations of strings where these nullable symbols are either present or removed, effectively compensating for the removal of $B \rightarrow \epsilon$.
```python
def eliminate_epsilon(self):
        nullables = set(nt for nt, rules in self.p.items() if 'eps' in rules)
        new_p = {nt: set(rules) for nt, rules in self.p.items()}
        for nt in new_p:
            new_p[nt].discard('eps')
            
        for nt, rules in self.p.items():
            for rule in rules:
                if rule == 'eps': continue
                nullable_indices = [i for i, char in enumerate(rule) if char in nullables]
                for r in range(1, len(nullable_indices) + 1):
                    for combo in itertools.combinations(nullable_indices, r):
                        new_rule = "".join([char for i, char in enumerate(rule) if i not in combo])
                        if new_rule:
                            new_p[nt].add(new_rule)
        self.p = {nt: list(rules) for nt, rules in new_p.items()}
```
### 2. Unit Production Elimination
The `eliminate_unit` method handles renaming rules like $A \rightarrow B$. It uses an iterative approach to find chains of unit productions and replaces the unit non-terminal with the full set of production rules that the target non-terminal points to, ensuring no direct links between non-terminals remain.
```python
def eliminate_unit(self):
        changed = True
        while changed:
            changed = False
            new_p = {nt: set(rules) for nt, rules in self.p.items()}
            for nt, rules in self.p.items():
                for rule in rules:
                    if len(rule) == 1 and rule.isupper():
                        new_p[nt].remove(rule)
                        if rule in self.p:
                            for sub_rule in self.p[rule]:
                                if sub_rule not in new_p[nt]:
                                    new_p[nt].add(sub_rule)
                                    changed = True
            self.p = {nt: list(rules) for nt, rules in new_p.items()}
```
### 3. Inaccessible and Non-Productive Symbols
The `eliminate_inaccessible` method uses a Breadth-First Search (BFS) starting from the start symbol 'S' to identify all reachable non-terminals, discarding those that cannot be reached. Following this, `eliminate_non_productive` ensures that every symbol in the grammar can eventually derive a string of terminals, purging any "dead-end" symbols like $D$.
```python
def eliminate_inaccessible(self):
        accessible = {self.start}
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
                    if all((char.islower() or char in productive) for char in rule):
                        productive.add(nt)
                        changed = True
                        break
        self.p = {nt: rules for nt, rules in self.p.items() if nt in productive}
```
### 4. CNF Conversion (Binarization)
The `convert_to_cnf` method performs the final transformation. It first extracts terminals into their own dedicated non-terminal rules (e.g., $X \rightarrow a$) and then breaks down any production string longer than two symbols into a series of binary rules using newly generated intermediate variables ($Z_1, Z_2$, etc.).
```python
def convert_to_cnf(self):
        # Step A: Replace terminals and create mapping
        # Step B: Break rules longer than 2 symbols using Z_i variables
        # ... (full logic implemented in the main script)
```


---
## Challenges and Difficulties
One of the primary challenges encountered during the implementation was maintaining the strict logical dependency between the transformation steps. Specifically, removing $\epsilon$-productions often creates new unit productions, meaning the sequence of execution is critical; if performed in the wrong order, the resulting grammar might not be fully normalized. Another significant difficulty was managing the combinatorial expansion of rules during the $\epsilon$-elimination phase, where it was essential to generate all possible variations of a rule without creating redundant duplicates or invalid empty strings. Finally, ensuring the binarization process correctly handled long strings by generating unique intermediate non-terminals (e.g., $Z_1, Z_2$) while avoiding naming collisions with the original grammar required careful state management and indexing.

---

## Conclusions
In this laboratory work, I implemented an algorithm to convert a Context-Free Grammar into Chomsky Normal Form. The process highlighted the importance of systematic simplification: removing $\epsilon$-rules and unit productions often increases the number of rules, but it makes the grammar much more predictable for parsing algorithms like CYK. The implementation successfully handled Variant 16, and the modular design allows it to process any valid CFG, fulfilling the bonus requirement.

---
## References
[1] Chomsky Normal Form - Wikipedia. https://en.wikipedia.org/wiki/Chomsky_normal_form
[2] Formal Languages and Finite Automata, Course Materials.
