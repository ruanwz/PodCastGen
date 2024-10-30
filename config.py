# config.py

# GroqProvider settings
# DEFAULT_MODEL = "llama-3.1-70b-versatile"
DEFAULT_MODEL = "llama-3.1-8b-instant"
MAX_TOKENS = {
    "outline": 8000,
    "full_script": 8000,
    "dialogue": 8000
}

# Host profiles
HOST_PROFILES = """
Host1 (Rachel): Enthusiastic, prone to personal anecdotes, likes to relate concepts to everyday life. Occasionally interrupts with excitement to add to a point.
Host2 (Mike): More analytical, enjoys making pop culture references, often asks clarifying questions. Sometimes finishes Rachel's sentences when he sees where she's going.
"""

# Prompt templates
OUTLINE_PROMPT_TEMPLATE = """
请用中文创建一个双人播客节目的详细大纲，基于以下输入内容：

{input_text}

大纲应包含：
1. 吸引人的开场白
2. 要讨论的主要观点，可以包含个人轶事或例子
3. 有趣的类比或流行文化引用
4. 总结关键要点并预告下一集的结尾
5. 所有内容必须用中文！

请用清晰的章节和要点格式编排大纲。
"""

EXPAND_PROMPT_TEMPLATE = """
请将以下大纲扩展为一个双人播客的完整脚本，主持人是Rachel和Mike：

{outline}

主持人简介：
{host_profiles}

指南：
- 使脚本生动有趣，对话自然，易于理解
- 包含类比、例子和解释，使复杂概念通俗易懂
- 加入每个主持人的个人轶事和经历
- 使用口语化表达，包括语气词（比如"嗯"、"你知道吗"、"我是说"）
- 加入幽默、热情等情感元素
- 确保主持人能够互相呼应，适时提问
- 用个人评论或问题实现话题之间的自然过渡
- 偶尔让一个主持人打断另一个，补充观点或接上对方的想法
- 所有对话必须用中文！

脚本应该像朋友之间的自然对话，而不是正式演讲。
"""

DIALOGUE_PROMPT_TEMPLATE = """
请将以下播客脚本转换为Rachel和Mike之间自然生动的中文对话：

{full_script}

主持人简介：
{host_profiles}

指南：
- 我们的目标是既要引人入胜又要信息丰富，像朋友间的真实对话一样有趣和娱乐性
- Rachel和Mike轮流发言
- 让对话自然流畅，主持人之间能够互相呼应
- 公平坦诚地讨论任何话题的正反两面
- 如有分歧，要以尊重的态度探讨不同观点
- 使用口语化表达和语气词（如"这个"、"你知道吗"、"就是说"）
- 加入简短的个人轶事和经历，使内容更有共鸣
- 融入幽默、热情等情感元素
- 适时重述或澄清要点，模仿自然说话方式
- 用个人评论或问题实现话题间的流畅过渡
- 在保持科学准确性和主要观点的同时，让对话显得自然随意
- 偶尔（整个脚本中2-3次）加入一方打断或接上另一方话的情况，例如：
  Rachel："俗话说，人非圣贤，孰能--"
  Mike："孰能无过！没错。"
  或者
  Mike："整数、圆数--"
  Rachel："还有虚数呢！对吧？"
  Mike："对啊！我都没想到这点。"

输出格式：
Rachel：[Rachel的对话]
Mike：[Mike的对话]
Rachel：[Rachel的对话]
...以此类推

记住要让对话听起来尽可能自然生动，就像两个朋友在随意讨论话题，偶尔会有友好的打断。

重要提示：所有对话必须用中文！不要出现任何英文对话！
"""