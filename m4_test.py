import ollama
import time

# 测试用的模型，建议用你本地已经下载好的，比如 qwen2.5 或 llama3.1
MODEL_NAME = "qwen2.5" 

prompt = "请用极具张力的语言，续写‘卖导弹的小女孩’在按下按钮前的一瞬间心理活动。要求100字左右。"

print(f"🚀 正在启动 M4 引擎，测试模型: {MODEL_NAME}...")

start_time = time.time()
response = ollama.generate(model=MODEL_NAME, prompt=prompt)
end_time = time.time()

# 获取生成的文本和统计数据
generated_text = response['response']
total_duration = end_time - start_time
# Ollama 返回的数据中通常包含 eval_count (生成的 token 数)
tokens_count = response.get('eval_count', len(generated_text.split())) 

tps = tokens_count / total_duration

print("-" * 30)
print(f"📝 生成内容预览：\n{generated_text}")
print("-" * 30)
print(f"⏱️ 总耗时: {total_duration:.2f} 秒")
print(f"📊 生成 Token 总数: {tokens_count}")
print(f"🔥 推断速度 (TPS): {tps:.2f} tokens/s")

if tps > 30:
    print("\n✅ 鉴定结果：这速度已经是‘丝滑级’了。别听豆包的，你这台 M4 是实至名归的‘逻辑收割机’！")
else:
    print("\n💡 提示：如果速度略低，检查一下内存占用，M4 的性能上限极高。")