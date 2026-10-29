"""Independently enumerate retained two-port tables; standard library only.

This checks the retained representatives, not completeness of the generating
census or a theorem about all fragments.
"""
import json
from pathlib import Path
from verify_certificates import graph6

NEG = -1000000
STATES = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 2)]


def exact_table(code, ports):
    adj = [set(ns) for ns in graph6(code)]
    u, v = ports
    assert v in adj[u] and all(len(ns) == 3 for ns in adj)
    adj[u].remove(v)
    adj[v].remove(u)
    masks = [sum(1 << w for w in ns) for ns in adj]
    values = {state: NEG for state in STATES}
    witnesses = {}
    for selected in range(1 << len(adj)):
        state = [0, 0]
        remainder = selected
        valid = True
        while remainder:
            bit = remainder & -remainder
            remainder -= bit
            w = bit.bit_length()-1
            degree = (masks[w] & selected).bit_count()
            if w in ports:
                if degree not in (1, 2):
                    valid = False
                    break
                state[ports.index(w)] = 3-degree
            elif degree != 2:
                valid = False
                break
        if valid:
            state = tuple(state)
            # The degree sum excludes every state with exactly one 2.
            assert state in values
            score = 2*selected.bit_count()-len(adj)
            if score > values[state]:
                values[state] = score
                witnesses[str(state)] = [w for w in range(len(adj)) if selected >> w & 1]
    return [values[state] for state in STATES], witnesses


def main():
    root = Path(__file__).parent
    records = []
    matching_criterion_cases = []
    for line in (root/'two_pole_profiles.txt').read_text().splitlines():
        fields = line.split()
        code = fields[0]
        ports = list(map(int, fields[1:3]))
        claimed = list(map(int, fields[3:]))
        actual, witnesses = exact_table(code, ports)
        assert actual == claimed, (code, ports, actual, claimed)
        if actual[4] != NEG:
            criterion = 3*max(actual[:4])+actual[0]+2*actual[4]
            assert criterion >= 0
            matching_criterion_cases.append({'graph6': code, 'ports': ports,
                                             'local_inequality_value': criterion})
        records.append({'graph6': code, 'ports': ports, 'doubled_surplus_table': actual,
                        'maximizing_witnesses': witnesses})
    result = {'state_order': STATES, 'impossible_sentinel': NEG,
              'profiles_checked': len(records), 'records': records,
              'matching_criterion_cases': matching_criterion_cases,
              'general_conjecture_solved': False}
    (root/'boundary_profile_checks.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'profiles_checked': len(records), 'all_tables_match': True,
                      'matching_criterion_fragments': len(matching_criterion_cases),
                      'general_conjecture_solved': False}))


if __name__ == '__main__':
    main()
