from agent.tool.base_tool import BaseTool
from rag.constance import libraryKg


class CourseTool(BaseTool):
    def description(self) -> str:
        return "咨询课程相关信息"

    def example(self) -> [str]:
        return ["怎么学习C++"]

    def param(self):
        return {"course_name": "course_name值是从问题中提取出的课程名字，比如问题是：怎么学习C++课程，那么course_name的值为C++。"}

    def action(self, llm, query, history, param: dict):
        yield "检索中"
        course = param["course_name"]
        # first, second = pineconeStore.query(self.getVectors(course), index_name="course-link")
        detail = libraryKg.getCourseDetail(course)
        print(f"知识图谱查询结果：{detail}")
        prompt = f"""
                假如你是武汉工程大学图书馆的一个智能的AI助手，名字叫知行，能够解答学生关于课程的问题。
                学生想了解的课程是：{course}。
                学生的问题是：{query}
                假如以下是学校课程系统给你提供的相关信息：
                {detail}
                请你根据以上学校课程系统提供的相关信息并结合过往的聊天记录以及你所了解的信息，为学生生成一段课程的详细介绍：
                
                要求：
                如果学校课程系统提供的相关信息为空或者与学生想了解的课程没有关联，请忽略课程信息并根据你所了解的信息生成详细介绍并建议学生访问https://library.wit.edu.cn/tushuguan/index.htm进一步了解。
                如果学校课程系统提供的相关信息能够解答学生的问题，不要建议学生访问https://library.wit.edu.cn/tushuguan/index.htm网站了解更多信息。
                如果存在过往的聊天记录，请你结合过往的聊天记录进行回答，形成流畅和合理的对话。
                如果学生没有特别要求，请使用中文进行回答，确保介绍内容准确、全面，涵盖课程的核心内容、特点和相关背景并使用连贯的语言将学习网站链接自然地融合在一起。
                请你为学生生成问题的详细解答，并且在解答中不要出现“你提到的”等类似措辞。
            """
        chat = llm.start_chat(history=history)
        sum_text = ""
        for chunk in chat.send_message(content=prompt, stream=True):
            sum_text = sum_text + chunk.text
            yield sum_text
