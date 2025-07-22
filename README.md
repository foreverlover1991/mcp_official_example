# mcp_official_example

## 🛠️ 项目说明
```
本文旨在解决根据MCP官文示例测试失败，使用qwen替代官方模型测试通过的简单示例
```

### 环境搭建与运行步骤

1. **配置 API Key**  
   在项目根目录下新建 `api_key.py` 文件，内容如下：
   ```python
   api_key = "sk-xxxxxxxxxxx"  # 替换为你的实际 API Key
   ```

2. **创建虚拟环境**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # 或者 Windows：
   # .venv\Scripts\activate
   ```

3. **运行服务端**
   ```bash
   python3 weather.py
   ```

4. **运行客户端**
   ```bash
   # 根据实际路径配置
   python3 client.py "/pathto/mcp_official_example/weather.py" 
   ```

5. **测试输入**
   - 输入示例：`三藩市的天气怎么样`
   - 输出结果：将返回如下格式的天气信息


        ---

        # 🌤️ 三藩市（旧金山）天气简报

        欢迎查看三藩市近期的天气信息摘要。本报告基于当前提供的天气数据整理而成。

        ---

        ## 📅 今天下午
        - **气温**：66°F  
        - **风速**：15 mph（西风），阵风最高可达 24 mph  
        - **天气状况**：局部多云，稍后气温将下降至约 64°F  

        ---

        ## 🌙 今晚
        - **气温**：57°F  
        - **风速**：7 至 15 mph（西南西风），阵风最高 23 mph  
        - **天气状况**：多云为主  
        - **降水概率**：凌晨 5 点后有轻微毛毛雨可能（20% 概率）
        ---
        .
        .
        .
        .
        .
        .
        略

        ---

## 📁 项目结构
```
mcp_official_example/
├── api_key.py          # 存放 API Key
├── weather.py          # 天气模拟服务端
├── client.py           # 客户端脚本
├── aliyun_tool.py      # 阿里云调用工具测试脚本
├── .gitignore          # 忽略文件
├── requirements.txt    # python模块文件
└── README.md           # 项目说明文档
```

---

## 🧠 使用模型
本项目基于 **Qwen3** 模型，适配 [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol) 官方示例，实现本地插件调用与自然语言响应生成。

---
