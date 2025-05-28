import streamlit as st
import pandas as pd
from openai import OpenAI
import io
import re
import requests

DEEPSEEK_API_KEY = "YOUR_AIP_KEY"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

def load_excel(file_path):
    """加载 Excel 文件并返回 DataFrame."""
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        st.error(f"错误：文件 {file_path} 未找到。")
        return None

def is_valid_url(url):
    """简易的 URL 格式校验。"""
    url_pattern = re.compile(r'^(https?://)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$')
    return bool(url_pattern.match(url))

def check_url_validity(url, timeout=10):
    """使用 GET 请求检查 URL 是否可访问，并进行更严格的判断。"""
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()  # 如果状态码是 4xx 或 5xx，会抛出 HTTPError 异常
        return True
    except requests.exceptions.RequestException:
        return False
    except requests.exceptions.HTTPError:
        return False

def perform_audit(product_info, audit_rule, deepseek_client):
    rule_id = audit_rule['规则ID']
    rule_reason = audit_rule['驳回原因']
    rule_module = audit_rule['审核模块']
    product_value = product_info.get(rule_module)

    if rule_module == "电商价链接":
        if is_valid_url(product_value):
            if not check_url_validity(product_value):
                return False, [f"规则ID: {rule_id}, 模块: {rule_module}, 原因: 电商价链接无法正常访问"]
            else:
                return True, []
        else:
            return False, [f"规则ID: {rule_id}, 模块: {rule_module}, 原因: 电商价链接格式不正确"]

    elif rule_reason == "协议价大于或等于电商价":
        try:
            agreement_price = product_info.get('协议价')
            ecommerce_price = product_info.get('电商价')

            if agreement_price is not None and ecommerce_price is not None:
                agreement_price = float(agreement_price)
                ecommerce_price = float(ecommerce_price)

                if agreement_price >= ecommerce_price:
                    return False, [f"规则ID: {rule_id}, 原因: {rule_reason}"]
                else:
                    return True, []
            else:
                st.warning(f"商品信息缺少协议价或电商价，无法判断规则ID: {rule_id}")
                return True, []

        except ValueError:
            st.warning(f"协议价或电商价无法转换为数值，无法判断规则ID: {rule_id}")
            return True, []

    elif rule_reason == "电商价为0":
        ecommerce_price = product_info.get('电商价')
        if ecommerce_price is not None:
            try:
                ecommerce_price = float(ecommerce_price)
                if ecommerce_price == 0:
                    return False, [f"规则ID: {rule_id}, 原因: {rule_reason}"]
                else:
                    return True, []
            except ValueError:
                st.warning(f"电商价无法转换为数值，无法判断规则ID: {rule_id}")
                return True, []
        else:
            st.warning(f"商品信息缺少电商价，无法判断规则ID: {rule_id}")
            return True, []

    else:
        product_info_str = "\n".join([f"{key}: {value}" for key, value in product_info.items()])
        prompt = f"""请根据以下审核规则，判断给定的商品信息是否符合要求。注意：审核类目时参考给定的类目表，判断该商品最合适的类目。所有商品的类目都必须从该类目表中选择。如果模型判断商品的原始类目不正确，请从类目表中选择最相近的类目。如果选择的最相近类目与之前原始类目相同，请将审核结果标记为“符合”。

审核规则：
规则ID: {rule_id}
如果违反此规则，驳回原因描述为: {rule_reason}

商品信息：
{product_info_str}

请输出你的判断（'符合' 或 '不符合'）以及你的判断依据。如果判断为'不符合'，请务必说明是违反了哪条规则（通过规则ID和驳回原因描述）。

"""

        try:
            response = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个智能商品信息审核助手，你需要说明你的判断依据。"},
                    {"role": "user", "content": prompt},
                ],
                stream=False,
                timeout=30
            )

            if response.choices and response.choices[0].message.content:
                model_response = response.choices[0].message.content.strip()
                if "不符合" in model_response:
                    return False, [f"规则ID: {rule_id}, 原因: {rule_reason} (依据: {model_response}) \n\n"]
                elif "符合" in model_response:
                    return True, []
                else:
                    st.warning(f"DeepSeek 模型返回了意外的响应: {model_response}")
                    return True, []
            else:
                st.warning(f"DeepSeek 模型没有返回有效内容。规则ID: {rule_id}, 驳回原因: {rule_reason}")
                return True, []

        except Exception as e:
            st.error(f"调用 DeepSeek 模型时发生异常: {e}")
            return False, [f"规则ID: {rule_id}, 原因: 调用模型失败: {e}"]

def batch_audit(product_df, rules_df, deepseek_client):
    if product_df is None or rules_df is None:
        return None

    results = []
    for index, row in product_df.iterrows():
        product_info = row.to_dict()
        product_id = product_info.get('商品ID', f'未知ID_{index}')
        audit_passed = True
        all_reasons = set()
        for _, rule in rules_df.iterrows():
            passed, reasons = perform_audit(product_info, rule, deepseek_client)
            if not passed:
                audit_passed = False
                all_reasons.update(reasons)

        results.append({
            "商品ID": product_id,
            "审核结果": "通过" if audit_passed else "不通过",
            "驳回原因": "; ".join(sorted(list(all_reasons))) if all_reasons else ""
        })

    return pd.DataFrame(results)

st.title("商品审核")

uploaded_product_file = st.file_uploader("上传商品信息 Excel 文件", type=["xlsx"])
uploaded_rules_file = st.file_uploader("上传审核规则 Excel 文件", type=["xlsx"])

if uploaded_product_file and uploaded_rules_file:
    product_df = pd.read_excel(uploaded_product_file)
    rules_df = pd.read_excel(uploaded_rules_file)

    if st.button("开始审核"):
        with st.spinner("正在进行审核..."):
            audit_results_df = batch_audit(product_df, rules_df, client)

        if audit_results_df is not None:
            st.subheader("审核结果")
            st.dataframe(audit_results_df)

            # 提供下载审核结果的链接
            def download_excel(df):
                 in_memory_excel = io.BytesIO()
                 df.to_excel(in_memory_excel, index=False)
                 in_memory_excel.seek(0)
                 return in_memory_excel

            st.download_button(
                 label="下载审核结果 (Excel)",
                 data=download_excel(audit_results_df),
                 file_name="审核结果.xlsx",
                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
             )
        else:
            st.error("审核过程中发生错误，请检查上传的文件。")