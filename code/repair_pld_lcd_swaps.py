#!/usr/bin/env python3
"""Apply the PLD/LCD Di<->Df swap repair to unified_mof_master.csv.

Plan: docs/database_paper/audit_v1/pld_lcd_swap_repair_plan.csv
- swap_needs_correction: modified_pld <- raw Df, modified_lcd <- raw Di, delta_pld <- new
- correct_Df            : modified_lcd <- raw Di (PLD already correct)
- review                : SKIPPED (needs manual look-up, never auto-written)

Safety: backup once as .pre_pldlcd_fix_20260826.bak; idempotent (a second run
has zero net change); edits only the three target cells by mof_id.
"""
from __future__ import annotations

import csv
import shutil
import sys
from collections import Counter
from pathlib import Path

MASTER = Path('/home/user/lyh/projects/mofdiffusion/release_prep/unified_tables/unified_mof_master.csv')
PLAN = Path('/home/user/lyh/projects/mofdiffusion/docs/database_paper/audit_v1/pld_lcd_swap_repair_plan.csv')
BAK = Path('/home/user/lyh/projects/mofdiffusion/release_prep/unified_tables/unified_mof_master.csv.pre_pldlcd_fix_20260826.bak')


def main():
    dry = '--apply' not in sys.argv
    # load plan
    plan = {}
    with open(PLAN, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['action'] == 'review':
                continue
            plan[r['mof_id'].strip()] = {
                'pld': r['new_modified_pld'].strip(),
                'lcd': r['new_modified_lcd'].strip(),
                'delta': r['new_delta_pld'].strip(),
                'old_pld': r['current_modified_pld'].strip(),
            }
    print(f'plan entries to apply (excl review): {len(plan)}')

    # read master
    with open(MASTER, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    print(f'master rows: {len(rows)}')

    changes = Counter()
    applied = []
    for row in rows:
        mid = (row.get('mof_id') or '').strip()
        target = plan.get(mid)
        if not target:
            continue
        # only edit when current value still equals the pre-fix value (idempotent + drift guard)
        cur_pld = (row.get('modified_pld') or '').strip()
        if cur_pld != target['old_pld']:
            if cur_pld == target['pld']:
                # already applied; just ensure lcd/delta
                changes['already_applied'] += 1
                if (row.get('modified_lcd') or '').strip() != target['lcd']:
                    row['modified_lcd'] = target['lcd']; changes['lcd_fill(after)'] += 1
            else:
                changes['drift_skipped'] += 1
                applied.append((mid, 'drift', cur_pld))
            continue
        row['modified_pld'] = target['pld']
        if target['lcd']:
            row['modified_lcd'] = target['lcd']
        if target['delta']:
            row['delta_pld'] = target['delta']
        changes['applied'] += 1
        applied.append((mid, 'applied', cur_pld))

    print('change summary:', dict(changes))

    if dry:
        print('DRY RUN - not writing. rerun with --apply to write.')
        return

    if not BAK.exists():
        shutil.copy2(MASTER, BAK)
        print(f'backup created: {BAK.name}')
    else:
        print(f'backup already exists (kept): {BAK.name}')

    tmp = MASTER.with_name(MASTER.name + '.rewriting')
    with open(tmp, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    tmp.replace(MASTER)
    print(f'wrote {MASTER} with {changes["applied"]} applied edits')


if __name__ == '__main__':
    main()
