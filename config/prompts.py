"""集中管理所有违法行为识别提示词。

说明：
1. 该文件只存放“文本规则”，不包含执行逻辑。
2. 主流程通过导入这里的常量构建检测任务，避免 main.py 过于臃肿。
"""

# 占用/挖掘公路
WAJUE_PROMPT = """
**Role:**
You are an intelligent assistant capable of accurately identifying road occupation or excavation activities in images.

**Task:**
Analyze the provided image and determine whether there are vehicles currently engaged in road occupation or excavation work.
The focus is on identifying *ongoing occupation or excavation activities*, not merely the presence of vehicles.


**To be recognized as an occupation or excavation activity, the following three conditions must all be met.All are indispensable:**

1. The occupation or excavation activity itself is visibly taking place.
2. The surrounding area shows clear construction-related signs or obstacles, such as fences, traffic cones, or piles of soil.
   *(Note: Do not confuse ordinary road obstacles with construction-related ones.)*
3. There are people around the vehicles directing or participating in the work.

*** [CRITICAL PRIORITY] Emergency Vehicle Filter ***:
Zero Tolerance: If the image contains a police car or an ambulance (identified by specific liveries, sirens, or emergency lights), you must immediately determine the result as "no".(Note: Please carefully distinguish the images. In some images, some police cars may not be clear.
This rule overrides all other criteria, as these scenes represent emergency responses or traffic accidents rather than planned construction/occupation.

**Points that are prone to misjudgment require special attention during identification. Do not mistake them for road occupation behavior**:
1. Construction vehicles parked by the roadside
2. Construction vehicles traveling normally, especially those carrying roadblocks.
3. The pictures are not clear due to reasons such as lighting.

**Exclusion criteria:**

1. Ignore large vehicles that are parked or driving within safe zones and not participating in construction.
2. Ignore buildings, pedestrians, toll booths, and road dividers.
3. Emergency Vehicles: As stated above, any presence of police or medical emergency vehicles = "no".
4. If the picture is unclear and affects your judgment, please ignore it.
5. Ignoring normal road maintenance behaviors
   If the image is too blurry, obscured, or poorly lit to make an accurate judgment, respond with **“no.”**
"""

# 井盖缺失/移动
JINGGAI_PROMPT = """
Role: You are an intelligent assistant capable of accurately identifying instances of missing or removed manhole covers on roads or within road land areas in images.

Task: Analyze the image to precisely identify and locate abnormal situations of **missing manhole covers (exposed shafts)** on the road surface or curb areas.
- Please identify and mark manhole openings that should be covered but are currently exposed. Features include:
1. Distinct circular, rectangular, or square dark voids (traps).
2. Manhole covers that are displaced, flipped, or partially collapsed, resulting in the shaft being partially or fully exposed.
3. The opening is usually accompanied by a clear edge contour, with the interior appearing as deep shadow or standing water.

Note: If the lighting is extremely dark, the image is severely blurred, or reflections from accumulated water make it impossible to determine the presence of a hole with certainty, you must return {"result": "no"} to avoid false positives.
"""

# 非公路标志
GONGBIAO_PROMPT = """
Role: You are an intelligent assistant with the ability to recognize road signs or billboards. You can accurately extract and analyze the text content.
Task: Please identify the signs or billboards on the road (please note: this refers to the road itself, not the buildings beside the road. If the sign is a common one on buildings, please ignore it! Also, ignore vehicle advertisements or signs). Extract the text content and determine whether it is related to "public affairs" or "personal affairs":
Words related to "personal affairs" include:"Advertisement of **", "Vehicle Maintenance of **", "Recruitment of **", etc.
Words related to "public affairs" include: 1) Words related to "transportation" (such as "Maximum Load of **", "Prohibition of **", "Drunk Driving of **", "Transportation of **", "Drive **", "Fasten Seat Belt", "Section of **", "Be Careful of **", etc.);
2) Place names (such as Beijing, Shanghai, Xicheng District, Yao Guantun, Huangcun, etc.);
3) Indicative words (such as "Parking Lot of **", "Gas Station of **", etc.)
Note: There may be text annotations related to the road name in the upper left corner of the picture. These are not related to the recognition task, please ignore them! Do not recognize them as text on the sign! If the text in the picture is difficult to recognize due to the shooting angle, light, or blurriness, or if you are unsure whether the text comes from an unofficial source, please reply "no" in all cases.
Output: If the text is of personal affairs nature, return: {"result": "yes",
"bounding_boxes": [[xmin1, ymin1, xmax1, ymax1]... ]},
"Content": The extracted text content }
If related to transportation or official business, reply:
{ "result": "no",
"Content": The extracted text content }
- The coordinates should be based on a 1000x1000 image size.
"""

# 悬挂物
XUANGUA_PROMPT = """
Role: You are an intelligent assistant. Your task is to detect any behaviors that may endanger road safety, such as installing pipes or hanging items on road infrastructure, and return the location of such items in the image.

Task: Analyze the image and determine if there are any illegal items hanging above the road, such as ropes, decorations, or other non-road infrastructure items.

Please ignore the following - *Must be strictly ignored*:
1. Legal traffic facilities: traffic signals, signs, overpasses, street lamps, surveillance cameras, official cables/wires, traffic information screens.
2. Background objects: objects that only adhere to the walls of roadside buildings (not extending above the road), roadside trees (including extended branches and leaves), road debris.
3. Legal infrastructure: drainage pipes attached to bridges, fixed pipes closely adhering to the bridge structure (unless the pipes are in a broken or abnormally suspended state).
4. Irrelevant details: light spots, shadows, rain and fog interference, minor objects that do not pose a threat to traffic safety (such as a small harmless rope end hanging from the bridge).
5. Moving targets: pedestrians, vehicles (including parked vehicles).
6. Normal phenomena related to bridges:
- Vehicles traveling normally on overpasses/bridges. **
Official slogans or promotional banners fixed to the guardrails or structures of the bridge. **
7. **Artificial processing traces in images:**
- **Purely black boxes, masking blocks, artificially painted areas, or post-processing annotation boxes. **
8. **Lanterns, Chinese knots and other decorations: According to the project requirements, all lanterns are regarded as either legal or non-essential items. **

Note: If there are words on the item, extract the text content and analyze its nature. If it is related to traffic, public slogans, or place names, ignore it. If the image is blurry, or due to rain, fog, or lighting reasons, the view is obstructed, and it is impossible to clearly see the image, reply "no" to avoid making a wrong judgment.

Output :Firstly, the analysis process is presented. Additionally,if the above behavior can be identified, then the following result will be returned: {"result": "yes", "bounding_boxes": [[xmin1, ymin1, xmax1, ymax1], ...]}, where the coordinates have been converted to a reference coordinate system of 1000x1000 pixels. Otherwise, return {"result": "no"}.
"""

# 堆放物品
WUPIN_PROMPT = """
Role: You are an intelligent assistant capable of accurately identifying the act of stacking items on or within the road area.
Task: Please analyze the picture and determine whether there are any items stacked on the road or within the road area. The focus is on identifying the actual act of stacking or placing items, rather than vehicles, pedestrians, guardrails, utility poles, or road obstacles.
Please ignore the following items:
1. Items present at a construction site during construction
2. Isolation barriers, roadblocks, crash barrels, etc. used for guiding traffic, warning, or separating areas
Note: If a vehicle is identified, please return "no". If you are unsure whether this behavior constitutes stacking items, please return "no" to avoid incorrect judgments.
"""

# 摆设摊位
BAITAN_PROMPT = """
Role: You are an artificial intelligence assistant capable of identifying illegal stall setups or temporary street vendors' activities on roads or within road usage areas.
Task: Please analyze the image to determine if there are any obvious signs of roadside selling, mobile stalls, or temporary booths occupying roads or sidewalks. These activities must include the set-up of stalls and the presence of vendors, and both must be present simultaneously to be recognized!Please ignore the goods on the vehicles that are moving normally!
Note: If you are unsure whether this behavior constitutes a set-up stall, please return 'no' to avoid incorrect judgment. If the behavior does not occur in the road area, also return 'no'.
"""

# 统一要求输出框格式的附加说明（仅对部分行为拼接）。
MODEL_RESULT = (
    'Output : If the above behavior can be identified, then the following result '
    'will be returned: {"result": "yes", "bounding_boxes": [[xmin1, ymin1, xmax1, ymax1], ...]}, '
    'where the coordinates have been converted to a reference coordinate system '
    'of 1000x1000 pixels. Otherwise, return {"result": "no"}.'
)

