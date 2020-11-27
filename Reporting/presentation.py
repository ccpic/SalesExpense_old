from pptx import Presentation
from Reporting.reporting import *
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# 创建ppt
prs = Presentation("template.pptx")
w = prs.slide_width
h = prs.slide_height


# Page3 标题分隔页
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.placeholders[0]
title.text = "现有客户档案\n数量和分布"
for i in range(2):
    font = title.text_frame.paragraphs[i].runs[0].font
    font.size = Pt(32)

# Page4 客户档案基本情况
slide = prs.slides.add_slide(prs.slide_layouts[0])
title = slide.placeholders[0]
title.text = "客户档案基本情况"

shapes = slide.shapes
for i in range(4):
    oval_width = oval_height = Inches(2)
    shape = shapes.add_shape(
        MSO_SHAPE.OVAL, w / 8 * (2 * i + 1) - oval_width / 2, h / 2 - oval_height / 2, oval_width, oval_height
    )
    shape.fill.background()
    line = shape.line
    line.color.rgb = RGBColor(255, 0, 0)
    line.width = Pt(2.5)

# 保存ppt文件
prs.save("presentation.pptx")
