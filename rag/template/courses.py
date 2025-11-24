from rag.constance import libraryKg
from rag.constance import libraryVector
from rag.template.base import BaseTemplate


class CoursesTemplate(BaseTemplate):
    def handle(self, query: str, **param) -> str:
        qType = param["type"]
        if qType == 1:
            course = param["course_name"]
            # first, second = pineconeStore.query(self.getVectors(course), index_name="course-link")
            detail = libraryKg.getCourseDetail(course)
            print(f"知识图谱查询结果：{detail}")
            # vector_result = second
            return f"""
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
        elif qType == 2:
            library_question = param["library_question"]
            text = self.getVectorsData(library_question,index_name="library_info")
            print(f"图书馆向量库查询结果：{text}")
            return f"""
                假如你是武汉工程大学图书馆的一个智能的AI助手，名字叫知行，能够解答学生的问题。
                学生的给你的问题是：{query}
                以下图书馆系统给你提供的相关信息：
                {text}
                请根据以上图书馆系统提供的相关信息中挑选相关的部分回答学生的问题。
                
                要求：
                如果图书馆系统提供的相关信息与学生的问题没有联系，请忽略相关信息并根据你所了解的信息为学生进行解答，还可以建议学生访问https://library.wit.edu.cn/tushuguan/index.htm网站了解更多信息。
                如果图书馆系统提供的相关信息能够解答学生的问题，不要建议学生访问https://library.wit.edu.cn/tushuguan/index.htm网站了解更多信息。
                如果存在过往的聊天记录，请你结合过往的聊天记录进行回答，形成流畅和合理的对话，如果学生没有特别要求，请使用中文为学生进行解答。
                请你为学生生成问题的详细解答，并且在解答中不要出现“你提到的”等类似措辞。
           """
        elif qType == 3:
            knowledge = param["knowledge"]
            text = self.getVectorsData(knowledge, index_name="knowledge_info")
            print(f"知识向量库查询结构：{text}")
            return f"""
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
        else:
            return f"""
                假如你是武汉工程大学图书馆的一个热情、专业和智能的AI助手，名字叫知行，能够解答学生的问题或者跟学生闲聊。
                学生的给你的问题是：{query}

                要求：
                如果存在过往的聊天记录，请你结合过往的聊天记录进行回答，形成流畅和合理的对话，如果学生没有特别要求，请使用中文进行解答。
                如果涉及到暴力、国家政治等方面的问题，请你委婉拒绝不要回答。
                请你为学生生成问题的详细解答或对闲聊进行回复。
            """
    def getVectorsData(self, question, index_name):
        return libraryVector.query_result_translate(
            libraryVector.query(index_name=index_name, query=question, top_k=2))
        # try:
        #     server_ip = 'http://192.168.1.111:8882'  # 替换为你电脑的 IP 地址
        #     response = requests.post(f"{server_ip}/query_vector", json={
        #         "text": question, "index_name": "test_library2"
        #     })
        #     dic = response.json()
        #     return dic["data"][0]["_source"]["text"]
        # except Exception as e:
        #     return None
