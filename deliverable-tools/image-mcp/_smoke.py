# @AI_GENERATED
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import image_server as S
# 测 list_images + read_image 的核心编码逻辑
d = r"d:\eng_files\envision_consulting_skill\envision_consulting_skill\ppt_result\muyuan-zero-carbon\build"
print("list_images:")
print(S.list_images(d))
p = os.path.join(d, "slide-01.png")
data, size = S._encode(p)
print("encoded slide-01:", size, "b64_len", len(data))
print("server name:", S.mcp.name)
print("SMOKE OK")
# @AI_GENERATED: end
