import zipfile, re
p = r'd:\eng_files\envision_consulting_skill\envision_consulting_skill_ver_2.6\envision_consulting_skill\templates\pptx\masters\envision-china-template-2023.pptx'
z = zipfile.ZipFile(p)
data = z.read('ppt/theme/theme1.xml').decode('utf-8')
# print fontScheme and clrScheme sections
for tag in ('clrScheme', 'fontScheme'):
    m = re.search(r'<a:%s.*?</a:%s>' % (tag, tag), data, re.S)
    print('==== %s ====' % tag)
    print(m.group(0) if m else 'NOT FOUND')
    print()
