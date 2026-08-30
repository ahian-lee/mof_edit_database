#!/usr/bin/env python3
"""PLD/LCD swap repair — Part 1 indexer: row -> raw .res -> Di/Df classification.

Read-only. Builds the bridge between the release master's AL rows and the
raw Zeo++ .res files, then classifies each row's current modified_pld as
matching raw Df (correct) or raw Di (swap, needs correction).

Two-phase:
  phase=index:  scan round manifests + zeo_output -> write job index CSV
  phase=class:  load master blank-lcd rows, join to jobs, write classification
"""
from __future__ import annotations

import argparse
import csv
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

MASTER = Path('/home/user/lyh/projects/mofdiffusion/release_prep/unified_tables/unified_mof_master.csv')
AL = Path('/home/user/data/active_learning')
OUT = Path('/home/user/lyh/projects/mofdiffusion/docs/database_paper/audit_v1')

MANIFESTS = [
    # (base_dir, dirname, manifest_file, job_id_col, edited_col)
    (AL, 'round_005', 'transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (AL, 'round_008', 'round008_candidate_manifest.csv', 'validation_id', 'edited_edge_id'),
    (AL, 'round_009', 'round009_manifest.csv', 'validation_id', 'edited_edge_id'),
    (AL, 'round_011', 'round011_manifest.csv', 'validation_id', 'edited_edge_id'),
    (AL, 'round_012', 'round012_manifest.csv', 'validation_id', 'edited_edge_id'),
    (AL, 'm62_candidates_8000', 'transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (AL, 'm6_candidates_5000', 'transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (AL, 'taskD_overnight_acquisition_20260619_m5c_5000_diverse', 'transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (AL, 'taskj', 'transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (AL, 'taskp', 'transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (AL, 'taskZ_dense_unseen_edge_panel_12800', 'transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (AL, 'taskS_medium_6a_validation_2000', 'transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (AL, 'taskY_feature_edge_tb_gfn_1536', 'transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (AL, 'fg_matched_acquisition_2000', 'transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (AL, 'ref_base_missing_4444', 'transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (AL, 'gfn_validation_v2', '05_transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (AL, 'round004c_gfn_panel', '05_transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (AL, 'round_gnn_gfn_next_small_pore_exploit', 'transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (AL, 'round_002_reward_v2', '05_transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (AL, 'round_001_pilot500', '05_transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (AL, 'round_001', '05_transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (Path('/home/user/data/mof_data/m7_candidates_8000'), 'results_4090', 'transfer_map_jobs.csv', 'job_id', 'edited_edge'),
    (Path('/home/user/data/mof_data/taskl_v3_results'), 'results_4090', 'transfer_map_jobs.csv', 'job_id', 'edited_edge'),
]

ROUND_ALIAS = {
    'm5c': 'taskD_overnight_acquisition_20260619_m5c_5000_diverse',
    'taskD': 'taskD_overnight_acquisition_20260619_m5c_5000_diverse',
    'm6': 'm6_candidates_5000',
    'm62': 'm62_candidates_8000',
    'taskj': 'taskj', 'taskJ': 'taskj', 'taskl': 'taskl',
    '005': 'round_005', '008': 'round_008', '009': 'round_009',
    '011': 'round_011', '012': 'round_012',
    'gnn_exploit': 'round_gnn_gfn_next_small_pore_exploit',
    'gnn_smoke': 'round_gnn_gfn_smoke',
    '002_reward_v2': 'round_002_reward_v2', 'round002_reward_v2': 'round_002_reward_v2',
}

# legacy <-> canonical edge-id crosswalk (loaded once)
_CROSSWALK = None


def load_crosswalk():
    global _CROSSWALK
    if _CROSSWALK is not None:
        return _CROSSWALK
    _CROSSWALK = {'leg2can': {}, 'can2leg': {}}
    p = Path('/home/user/lyh/projects/mofdiffusion/edge_augmentation/base_edge_aug/edge_id_crosswalk_v2.csv')
    with open(p, newline='', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            leg = (r.get('legacy_edge_id') or '').strip()
            can = (r.get('edge_id') or r.get('canonical_edge_id') or '').strip()
            if leg and can:
                _CROSSWALK['leg2can'][leg] = can
                _CROSSWALK['can2leg'][can] = leg
    return _CROSSWALK


def canonicalize_edge_id(eid):
    """Map an edited/base edge id to canonical E<1000+n> form.
    Handles suffixes (E159_H2_x -> E1159_H2_x) and bare ids (E159 -> E1159)."""
    load_crosswalk()
    eid = norm(eid)
    if not eid:
        return eid
    m = re.match(r'^(E\d+)(.*)$', eid)
    if not m:
        return eid
    fam, suffix = m.group(1), m.group(2)
    can = _CROSSWALK['leg2can'].get(fam)
    return (can + suffix) if can else eid


def legacy_edge_id(eid):
    """Map an edited/base edge id to legacy E<n> form (inverse crosswalk)."""
    load_crosswalk()
    eid = norm(eid)
    if not eid:
        return eid
    m = re.match(r'^(E\d+)(.*)$', eid)
    if not m:
        return eid
    fam, suffix = m.group(1), m.group(2)
    leg = _CROSSWALK['can2leg'].get(fam)
    return (leg + suffix) if leg else eid


def norm(v):
    return '' if (v or '').strip() in {'', 'nan', 'None', '__none__', 'none'} else str(v).strip()


def recipe_key(t, n, o, b, e, m):
    return '|'.join([norm(t), norm(n), norm(o), norm(b), norm(e), norm(m)])


def recipe_key_legacy(t, n, o, b, e, m):
    """Recipe key with both edge fields normalized to legacy E<n> form and the
    mod_token reduced to its concise H.._.. part (drops verbose FG=[...]|n=N)."""
    return '|'.join([norm(t), norm(n), norm(o), legacy_edge_id(b), legacy_edge_id(e), mod_token_concise(norm(m))])


def mod_token_concise(m):
    m = norm(m)
    if not m:
        return ''
    if m.startswith('FG='):
        # verbose: FG=["A", "B"]|n=3  -- no concise equivalent in manifest,
        # match on edited_edge which already encodes the concise actions
        return 'ANY'
    return m


def recipe_key_no_token(t, n, o, b, e, _m=None):
    """Key ignoring mod_token; used to bridge rounds whose manifest stores a
    verbose FG= token with no concise equivalent."""
    return '|'.join([norm(t), norm(n), norm(o), legacy_edge_id(b), legacy_edge_id(e), '@notok'])


def parse_res(path: Path):
    """Return (Di, Df, Dif) from a Zeo++ -res file using the scaffold parser order."""
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            text = f.read()
    except OSError:
        return None
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        parts = s.split()
        payload = ' '.join(parts[1:]) if len(parts) > 1 else s
        nums = re.findall(r'[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?', payload)
        if len(nums) >= 3:
            return float(nums[0]), float(nums[1]), float(nums[2])
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--phase', choices=['index', 'class'], required=True)
    ap.add_argument('--round', dest='only_round', default=None)
    args = ap.parse_args()

    if args.phase == 'index':
        rows = []
        for base, dname, fn, jid_col, ed_col in MANIFESTS:
            if args.only_round and args.only_round not in (dname,):
                continue
            d = base / dname
            if not d.is_dir():
                print(f'[skip] {dname} dir missing ({d})')
                continue
            # collect zeo_output dirs
            zeo_dirs = [z for z in d.rglob('zeo_output') if z.is_dir()]
            res_map = {}
            for z in zeo_dirs:
                for rf in z.glob('*.res'):
                    res_map.setdefault(rf.stem, str(rf))
            mf = d / fn
            if not mf.exists():
                print(f'[skip] {dname} manifest missing')
                continue
            n = 0
            n_res = 0
            with open(mf, newline='', encoding='utf-8-sig', errors='replace') as f:
                for r in csv.DictReader(f):
                    jid = (r.get(jid_col) or '').strip()
                    if not jid:
                        continue
                    n += 1
                    ed = r.get(ed_col) or r.get('edited_edge') or r.get('edited_edge_id') or ''
                    key = recipe_key(r.get('topo'), r.get('node_inorg'),
                                     r.get('node_org'), r.get('base_edge'), ed,
                                     r.get('mod_token'))
                    res_path = res_map.get(jid, '')
                    if res_path:
                        n_res += 1
                    rows.append({
                        'round_dir': dname, 'job_id': jid,
                        'topo': norm(r.get('topo')), 'node_inorg': norm(r.get('node_inorg')),
                        'node_org': norm(r.get('node_org')), 'base_edge': norm(r.get('base_edge')),
                        'edited_edge': norm(ed), 'mod_token': norm(r.get('mod_token')),
                        'recipe_key': key, 'res_path': res_path,
                    })
            print(f'[index] {dname}: manifest {n} jobs, {n_res} with local .res')
        op = OUT / 'pld_lcd_job_index.csv'
        with open(op, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f'wrote {op} rows={len(rows)}')

    else:  # class
        idx = []
        with open(OUT / 'pld_lcd_job_index.csv', newline='', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                if r['res_path']:
                    idx.append(r)
        # index by BOTH raw and legacy-normalized recipe key (plus no-token variant)
        by_key = defaultdict(list)
        by_key_leg = defaultdict(list)
        by_key_notok = defaultdict(list)
        for r in idx:
            by_key[r['recipe_key']].append(r)
            by_key_leg[recipe_key_legacy(
                r['topo'], r['node_inorg'], r['node_org'],
                r['base_edge'], r['edited_edge'], r['mod_token'])].append(r)
            by_key_notok[recipe_key_no_token(
                r['topo'], r['node_inorg'], r['node_org'],
                r['base_edge'], r['edited_edge'])].append(r)
        print(f'job index with res: {len(idx)}')
        del idx

        # load master blank-lcd rows
        master_rows = []
        with open(MASTER, newline='', encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                if (r.get('modified_lcd') or '').strip():
                    continue
                if (r.get('layer') or '') != 'al_active_learning':
                    continue
                master_rows.append(r)
        print(f'blank-lcd AL master rows: {len(master_rows)}')

        out_rows = []
        FIELDS = ['row_id', 'source_round', 'recipe_key', 'status', 'round_dir', 'job_id',
                  'res_path', 'raw_Di_LCD', 'raw_Df_PLD', 'raw_Dif', 'current_modified_pld',
                  'classification', 'recipe_key_matched']
        report = Counter()
        for r in master_rows:
            src_round = (r.get('source_round') or '').strip()
            ed = (r.get('modified_edge_id') or r.get('edited_edge_id') or '').strip()
            key = recipe_key(r.get('topo'), r.get('node_inorg'), r.get('node_org'),
                             r.get('base_edge'), ed, r.get('mod_token'))
            out = {k: '' for k in FIELDS}
            out.update({'row_id': r.get('mof_id'), 'source_round': src_round,
                        'recipe_key': key, 'current_modified_pld': norm(r.get('modified_pld'))})
            candidates = []
            matched_via = ''
            key = recipe_key(r.get('topo'), r.get('node_inorg'), r.get('node_org'),
                             r.get('base_edge'), ed, r.get('mod_token'))
            if key in by_key:
                candidates = by_key[key]
                matched_via = 'raw'
            else:
                leg = recipe_key_legacy(r.get('topo'), r.get('node_inorg'), r.get('node_org'),
                                        r.get('base_edge'), ed, r.get('mod_token'))
                if leg in by_key_leg:
                    candidates = by_key_leg[leg]
                    matched_via = 'legacy'
                else:
                    ntk = recipe_key_no_token(r.get('topo'), r.get('node_inorg'), r.get('node_org'),
                                              r.get('base_edge'), ed)
                    if ntk in by_key_notok:
                        candidates = by_key_notok[ntk]
                        matched_via = 'legacy_notok'
            cands = candidates
            out['recipe_key_matched'] = matched_via
            if not cands:
                report['no_job_match'] += 1
                out['status'] = 'no_job_match'
                out_rows.append(out)
                continue
            # prefer a round_dir matching source_round alias
            alias_dirs = []
            if src_round in ROUND_ALIAS:
                alias_dirs.append(ROUND_ALIAS[src_round])
            picked = None
            for c in cands:
                if c['round_dir'] in alias_dirs or c['round_dir'] == src_round:
                    picked = c
                    break
            if picked is None:
                picked = cands[0]
            res = parse_res(Path(picked['res_path']))
            if res is None:
                report['res_parse_fail'] += 1
                out['status'] = 'res_parse_fail'
                out_rows.append(out)
                continue
            di, df, dif = res
            out.update({
                'status': 'recovered', 'round_dir': picked['round_dir'],
                'job_id': picked['job_id'], 'res_path': picked['res_path'],
                'raw_Di_LCD': f'{di:.5f}', 'raw_Df_PLD': f'{df:.5f}',
                'raw_Dif': f'{dif:.5f}',
            })
            # classify
            try:
                curv = float(norm(r.get('modified_pld')))
            except ValueError:
                report['current_pld_not_numeric'] += 1
                out['classification'] = 'not_numeric'
                out_rows.append(out)
                continue
            tol = 2e-3
            match_df = abs(curv - df) <= max(tol, 2e-3 * abs(df))
            match_di = abs(curv - di) <= max(tol, 2e-3 * abs(di))
            if match_df:
                out['classification'] = 'correct_Df'
                report['correct_Df'] += 1
            elif match_di:
                out['classification'] = 'swap_needs_correction'
                report['swap_needs_correction'] += 1
            else:
                out['classification'] = 'neither'
                report['neither'] += 1
            out_rows.append(out)

        print('classification report:', dict(report))
        op = OUT / 'pld_lcd_classification_parts.csv'
        with open(op, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(out_rows)
        print(f'wrote {op} rows={len(out_rows)}')


if __name__ == '__main__':
    main()
