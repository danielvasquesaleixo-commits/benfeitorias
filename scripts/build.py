"""Monta dist/: injeta o Leaflet (CSS+JS) inline em src/app.html -> dist/index.html e copia public/."""
import os, shutil
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(R, 'src/app.html'), encoding='utf-8').read()
L = os.path.join(R, 'node_modules/leaflet/dist')
css = open(os.path.join(L, 'leaflet.css'), encoding='utf-8').read()
js = open(os.path.join(L, 'leaflet.js'), encoding='utf-8').read().replace('</script', '<\\/script')
assert '/*LEAFLET_CSS*/' in s and '/*LEAFLET_JS*/' in s
s = s.replace('/*LEAFLET_CSS*/', css, 1).replace('/*LEAFLET_JS*/', js, 1)
D = os.path.join(R, 'dist'); os.makedirs(D, exist_ok=True)
open(os.path.join(D, 'index.html'), 'w', encoding='utf-8').write(s)
for f in os.listdir(os.path.join(R, 'public')):
    shutil.copy(os.path.join(R, 'public', f), D)
print('dist/ pronto:', sorted(os.listdir(D)))
