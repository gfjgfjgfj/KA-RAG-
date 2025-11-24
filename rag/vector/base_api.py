import requests


class Api:
    def __init__(self, ip: str = "http://123.57.1.176:8000"):
        self.ip = ip

    # post请求
    def post(self, interface: str, body):
        response = requests.post(url=f"{self.ip}/{interface}", json=body)
        return response.json()

    # get请求
    def get(self, interface: str, params):
        return requests.get(url=f"{self.ip}/{interface}", params=params).json()

    # 接口请求是否成功
    def isSuccess(self, response):
        print(response)
        try:
            return response["code"] == 200
        except Exception as e:
            return False

    # 获取接口返回的数据
    def getData(self, response):
        try:
            return response["data"]
        except Exception as e:
            return None
