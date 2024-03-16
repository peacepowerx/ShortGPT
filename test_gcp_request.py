import requests
import json
import time

# 定义目标URL和要发送的数据
# url = "https://shortgpt-dpxtvldafa-uc.a.run.app/script2video"
url = "http://127.0.0.1:8080/emailvideo"
data = {
    "email":"ruoyu.zheng2016@gmail.com",
    #"script": "Discover the majestic Tratzberg Castle, nestled in the heart of picturesque landscapes, offering a journey through history and breathtaking architecture. Come and be enchanted!Savor the ambiance: intimate gatherings, delectable cuisine, and joyful moments await your presence. Join the feast!",
    "script":"i love cat",
    "isVertical": True,
    "openai_key": "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",
    "pexels_key": "miJI4iDuoQKdcTg7Nr0EL8KpTj736EGfQnLvy9JOPh3FFeqGehqXJBBV",
    "eleven_key": "d21d5bab981ac696c87a744579c540e8"
}

# 将字典转换为JSON格式的字符串
json_data = json.dumps(data)


# 记录发送请求前的时间戳
start_time = time.time()

# 发送POST请求
response = requests.post(url, headers={"Content-Type": "application/json"}, data=json_data)

# 记录接收到响应的时间戳
end_time = time.time()

# 计算并打印请求响应所需的时间
elapsed_time = end_time - start_time
print(f"Time taken to get response: {elapsed_time} seconds")

print(str(response))

# 打印响应内容
print("Status Code:", response.status_code)
print("Response Text:", response.text)

