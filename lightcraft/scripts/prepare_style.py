#!/usr/bin/env python3
"""Print a partial set_develop.settings patch. Does not contact or edit LightCraft."""
import argparse
import json
import math
from pathlib import Path

RECIPES = Path(__file__).resolve().parents[1] / 'references' / 'emulsion-recipes.json'


def leaves(obj, prefix=()):
    for key, value in obj.items():
        if isinstance(value, dict):
            yield from leaves(value, prefix + (key,))
        else:
            yield prefix + (key,), value


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Expected a finite numeric develop setting')
    return float(value)


def xy(point):
    if isinstance(point, dict) and set(point) == {'x','y'}:
        return number(point['x']), number(point['y'])
    if isinstance(point, (list,tuple)) and len(point)==2:
        return number(point[0]), number(point[1])
    raise ValueError('Invalid curve point')


def allowed(path):
    return (path in [('light', 'contrast'), ('light', 'blacks'), ('treatment',), ('curve', 'master')]
            or len(path) == 2 and path[0] == 'color' and path[1] in ('saturation', 'vibrance')
            or len(path) == 2 and path[0] == 'effects' and path[1] in ('clarity', 'dehaze')
            or len(path) == 2 and path[0] == 'bw_mix' and path[1] in ('red','orange','yellow','green','aqua','blue','purple','magenta')
            or len(path) == 3 and path[0] == 'mixer' and path[1] in ('red','orange','yellow','green','aqua','blue','purple','magenta') and path[2] in ('hue','sat','lum')
            or len(path) == 2 and path[0] == 'grading' and path[1] in ('blending','balance')
            or len(path) == 3 and path[0] == 'grading' and path[1] in ('shadows','highlights') and path[2] in ('hue','sat'))


def prepare(baseline, recipe, strength, skip_curve=False):
    strength = number(strength)
    if not 0 <= strength <= 1:
        raise ValueError('strength must be within 0..1')
    if strength == 0:
        return {}
    if baseline.get('treatment') == 'bw' and recipe['id'] != 'hp5-mono':
        raise ValueError('Color recipe on an existing B&W edit needs a separate creative decision')
    patch = {}
    for path, target in leaves(recipe['settings']):
        if not allowed(path):
            raise ValueError('Recipe contains an unapproved field: ' + '.'.join(path))
        if skip_curve and path == ('curve', 'master'):
            continue
        old = baseline
        for key in path:
            if not isinstance(old, dict) or key not in old:
                raise ValueError('Missing baseline field: ' + '.'.join(path))
            old = old[key]
        if path == ('treatment',):
            if target != 'bw':
                raise ValueError('Only explicit B&W conversion is supported')
            value = target  # Categorical: any positive strength converts fully to B&W.
        elif path == ('curve', 'master'):
            # Existing curves belong to the user; never flatten them while applying a recipe.
            curve = baseline['curve']
            if any(curve.get(k, 0) != 0 for k in ('shadows','darks','lights','highlights')):
                raise ValueError('Existing parametric curve: inspect and use --skip-curve if appropriate')
            for key in ('master','red','green','blue'):
                points = curve[key]
                if any(abs(x-y) > 1e-8 for x,y in map(xy, points)):
                    raise ValueError('Existing point curve: inspect and use --skip-curve if appropriate')
            points = [xy(p) for p in target]
            if len(points)<2 or points[0][0]!=0 or points[-1][0]!=1 or any(not(0<=x<=1 and 0<=y<=1) for x,y in points) or any(a[0]>=b[0] for a,b in zip(points,points[1:])):
                raise ValueError('Invalid normalized curve')
            value = [[x, x + (y-x)*strength] for x,y in points]
        elif path[0] == 'grading' and path[-1] == 'hue':
            old, target = number(old), number(target)
            if not 0 <= old <= 360 or not 0 <= target <= 360:
                raise ValueError('Invalid grading hue')
            if number(baseline['grading'][path[1]]['sat']) == 0:
                value = target  # Hue is undefined at zero saturation; do not fade through red.
            else:
                value = (old + ((target-old+180)%360-180)*strength)%360
        else:
            old, target = number(old), number(target)
            limit = (0,100) if path[0]=='grading' and path[-1] in ('sat','blending') else (-100,100)
            if not limit[0] <= target <= limit[1]:
                raise ValueError('Out-of-range recipe field: ' + '.'.join(path))
            value = old + (target-old)*strength
        node = patch
        for key in path[:-1]:
            node = node.setdefault(key,{})
        node[path[-1]] = value
    return patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path, help='Unwrapped get_develop JSON saved before trials')
    parser.add_argument('--recipe', required=True)
    parser.add_argument('--strength', type=float, default=0.35, help='Baseline-to-target interpolation, 0..1; unrelated to preset.apply amount')
    parser.add_argument('--skip-curve', action='store_true')
    args = parser.parse_args()
    catalog = json.loads(RECIPES.read_text())
    recipe = next((r for r in catalog['recipes'] if r['id'] == args.recipe),None)
    if recipe is None:
        parser.error('Unknown recipe; choose '+', '.join(r['id'] for r in catalog['recipes']))
    try:
        patch=prepare(json.loads(args.baseline.read_text()),recipe,args.strength,args.skip_curve)
    except (ValueError,KeyError,TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps(patch,ensure_ascii=False,indent=2,allow_nan=False))


if __name__ == '__main__':
    main()
