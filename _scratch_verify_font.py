import os, sys, zipfile, tempfile
sys.path.insert(0, os.path.join('deliverable-tools', 'pptx', 'scripts'))

import master_font_binder as m
from defusedxml.minidom import parseString

# 1. Extract theme from master into a temp unpack dir to test extraction + find_theme_path.
master = r'templates\pptx\masters\envision-china-template-2023.pptx'
tmp = tempfile.mkdtemp(prefix='_theme_')
with zipfile.ZipFile(master) as z:
    z.extractall(tmp)

theme_path = m.find_theme_path(tmp)
print('find_theme_path ->', theme_path)
fonts = m.extract_master_fonts(theme_path)
print('MasterFonts ->', fonts)
colors = m.extract_master_colors(theme_path)
print('colors ->', colors)

# 2. Split runs on mixed string.
text = "远景Envision智能"
segs = m.split_runs_by_script(text)
print('split ->', segs)
assert [s[1] for s in segs] == ['cjk', 'latin', 'cjk'], segs
assert segs[0][0] == '远景' and segs[1][0] == 'Envision' and segs[2][0] == '智能'

# 3. build_run_specs
specs = m.build_run_specs(text, fonts)
print('specs:')
for s in specs:
    print('   ', s)
for s in specs:
    if s.script == 'cjk':
        assert s.attr == 'a:ea' and s.typeface == fonts.cjk_minor
    else:
        assert s.attr == 'a:latin' and s.typeface == fonts.latin_minor

# 4. apply_run_fonts writes ea for cjk, latin for latin into rPr.
doc = parseString('<a:r xmlns:a="%s"><a:rPr/><a:t>x</a:t></a:r>' % m.A_NAMESPACE)
rpr = doc.getElementsByTagName('a:rPr')[0]
tf_cjk = m.apply_run_fonts(rpr, 'cjk', fonts, doc)
print('rPr after cjk ->', rpr.toxml(), '| bound', tf_cjk)
assert '<a:ea' in rpr.toxml() and ('typeface="%s"' % fonts.cjk_minor) in rpr.toxml()

doc2 = parseString('<a:r xmlns:a="%s"><a:rPr/><a:t>x</a:t></a:r>' % m.A_NAMESPACE)
rpr2 = doc2.getElementsByTagName('a:rPr')[0]
tf_lat = m.apply_run_fonts(rpr2, 'latin', fonts, doc2)
print('rPr after latin ->', rpr2.toxml(), '| bound', tf_lat)
assert '<a:latin' in rpr2.toxml() and ('typeface="%s"' % fonts.latin_minor) in rpr2.toxml()

# 5. is_cjk sanity
assert m.is_cjk('远') and not m.is_cjk('E') and not m.is_cjk('1')

# 6. edge: empty + latin-only + cjk-only
assert m.split_runs_by_script('') == []
assert m.split_runs_by_script('Hello') == [('Hello', 'latin')]
assert m.split_runs_by_script('远景') == [('远景', 'cjk')]

print('\nALL VERIFICATION CHECKS PASSED')
