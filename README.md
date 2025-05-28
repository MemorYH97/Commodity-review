# Commodity-review
此次Github文档中包含两个文件，分别为getimage.py和app.py。\
正确运行该demo除了上述两个文件外，还需要商品信息.xlsx以及相应的审核规则.xlsx\
原始的商品信息.xlsx文件中包含的信息包括：![image](https://github.com/user-attachments/assets/0f53cf75-ed82-42da-ac60-bd8db5033f29)

其中getimage.py文件用于获取商品主图链接所对应图片的文字信息，注意在使用此文件时确保待审核商品信息文件中有主图链接的列，并且包含一个对应的主图链接。
另外需要将下面的YOUR_AIP_KEY替换为可用的GLM-4V API key：
```
API_KEY = "YOUR_AIP_KEY"
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
```
在修改完成后，运行python getimage.py后，将会生成新的包含主图描述的xlsx文件并替换原文件（所以要确保在运行getimage.py的时候，文件夹中有原始的商品信息.xlsx）。下载更新完的商品信息.xlsx文件，以备后用。\

对于app.py文件，我们需要进行相同的工作，更换api key：
```
DEEPSEEK_API_KEY = "YOUR_AIP_KEY"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
```
在修改完api key之后，可运行streamlit run app.py。在打开的网页中提交之前保存的商品信息.xlsx文件和审核规则.xlsx文件，之后进行审核。审核结束后可对审核结果进行下载。
