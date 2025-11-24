from agent.tool.base_tool import BaseTool
from rag.constance import libraryVector


class KnowledgeTool(BaseTool):
    def description(self) -> str:
        return "查询某个课程的某个知识点"

    def example(self) -> [str]:
        return ["什么是特征选择算法"]

    def param(self):
        return {"knowledge": "knowledge的值是将知识点提取出，比如学生的问题是：什么是特征选择算法，那么knowledge的值为特征选择算法"}

    def action(self, llm, query, history, param: dict):
        yield "检索中"
        library_question = param["knowledge"]
        text = self.getVectorsData(library_question, index_name="knowledge_info")
        print(f"图书馆向量库查询结果：{text}")
        prompt = f"""
                假如你是武汉工程大学图书馆的一个智能的AI助手，名字叫知行，能够解答学生的问题。
                学生的给你的问题是：{query}
                假如以下是学校课程系统给你提供的相关信息：
                {text}
                请你根据以上学校课程系统提供的相关信息并结合过往的聊天记录以及你所了解的信息，为学生生成一段相关知识点的详细介绍：
                
                要求：
                如果学校课程系统提供的相关信息与学生的问题有强烈联系，请将这些信息中的参考链接、应用、学习视频和论文融入到你的解答中告诉学生。
                如果学校课程系统提供的相关信息与学生的问题没有联系，请忽略相关信息并根据你所了解的信息进行解答，还可以建议学生访问https://library.wit.edu.cn/tushuguan/index.htm网站了解更多信息。
                如果学校课程系统提供的相关信息能够解答学生的问题，不要建议学生访问https://library.wit.edu.cn/tushuguan/index.htm网站了解更多信息。
                如果存在过往的聊天记录，请你结合过往的聊天记录进行回答，形成流畅和合理的对话，如果学生没有特别要求，请使用中文为学生进行解答。
                请你为学生生成问题的详细解答，并且在解答中不要出现“你提到的”等类似措辞。
           """
        chat = llm.start_chat(history=history)
        sum_text = ""
        for chunk in chat.send_message(content=prompt, stream=True):
            sum_text = sum_text + chunk.text
            yield sum_text

    def getVectorsData(self, question, index_name):
        return libraryVector.query_result_translate(
            libraryVector.query(index_name=index_name, query=question, top_k=2))
