# Commodity-review
此次Github文档中包含两个文件，分别为getimage.py和app.py。\
原始的商品信息.xlsx文件中包含的信息包括：商品ID	商品名	类目	品牌	协议价	电商价	电商价链接	规格参数	主图链接![image](https://github.com/user-attachments/assets/0f53cf75-ed82-42da-ac60-bd8db5033f29)

其中getimage.py文件用于获取商品主图链接所对应图片的文字信息，注意在使用此文件时确保待审核商品信息文件中有主图链接的列，并且包含一个对应的主图链接。
另外需要将下面的YOUR_AIP_KEY替换为可用的GLM-4V API 密钥：
```
API_KEY = "YOUR_AIP_KEY"
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
```
\
