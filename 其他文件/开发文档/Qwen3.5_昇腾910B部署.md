# 昇腾 910B 部署 Qwen3.5-VL 多模态大模型开发文档 (基于 vLLM)

**文档版本**: v1.0
**更新日期**: 2026-03-25
**核心架构**: Huawei Ascend 910B (双卡) + vLLM 昇腾适配版 + Qwen3.5-VL-27B

---

## 1. 环境与资源准备

### 1.1 硬件与基础环境
- **底层算力**: 华为昇腾 Atlas 300T A2 (Ascend 910B) 
- **分配显卡**: 2 张 (161服务器卡 6 和卡 7)
- **宿主机环境**: Ubuntu + 华为 NPU 驱动及固件 (CANN)

### 1.2 核心文件准备
- **Docker 镜像**: `Vllm-ascend-Qwen3_5-A2-Ubuntu-v0.tar` 
(华为官方针对 Qwen3.5 定制的纯血 ARM 架构镜像，网址：https://modelers.cn/models/Eco-Tech/Qwen3.5-397B-A17B-w8a8-mtp/tree/main/vllm-image)
- **模型权重**: `Qwen3.5-VL-27B-Baitan-Merged` (已存放在宿主机目录 `/data01/HTC/rws/model/`，由llama factory框架微调后的模型)

---

## 2. 容器配置与启动

### 2.1 加载本地镜像
将物理包上传至服务器后，执行镜像加载：
```bash
docker load -i Vllm-ascend-Qwen3_5-A2-Ubuntu-v0.tar
# 成功加载后镜像名通常为：vllm-ascend:qwen3_5-v0-a2
```

### 2.2 启动 NPU 专属容器
启动容器时，必须映射 NPU 专属的设备控制符和 CANN 驱动目录：

```bash
docker run -itd \
  --name Qwen3.5-VL-27B-Container \
  --restart unless-stopped \
  --net=host \
  --shm-size=20g \
  --device /dev/davinci6 \
  --device /dev/davinci7 \
  --device /dev/davinci_manager \
  --device /dev/devmm_svm \
  --device /dev/hisi_hdc \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
  -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v /data01/HTC/rws/model:/root/Models \
  -v /data:/data \
  vllm-ascend:qwen3_5-v0-a2 \
  bash
  
  
# 重启容器
docker restart Qwen3.5-VL-27B-Baitan-Container
```

---

## 3. 模型服务点火 (核心避坑指南)

> ⚠️ **高危避坑警告**：
> 华为魔改版 vLLM 镜像中，`vllm serve` CLI 外壳代码存在模块缺失，且默认工作目录 `/vllm-workspace` 存在源码依赖冲突。**绝不能直接使用 `vllm serve` 启动！**

### 3.1 启动推理服务
进入容器内部后，必须**先切换到根目录**，然后通过 Python 核心模块启动 OpenAI 兼容接口：

```bash
# 1. 进入容器
docker exec -it Qwen3.5-VL-27B-Baitan-Container bash

# 2. 逃离冲突目录 (关键操作！)
cd /

# 3. 配置 NPU 与 vLLM 环境变量
`export VLLM_USE_MODELSCOPE=False`
export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256
# export VLLM_USE_V1=0

# 4. 启动核心 API Server
nohup python3 -m vllm.entrypoints.openai.api_server \
  --model /root/Models/Qwen3.5-VL-27B-Baitan-Merged \
  --tensor-parallel-size 2 \
  --max-model-len 8192 \
  --trust-remote-code \
  --limit-mm-per-prompt.video 0 \
  --port 5359 \
  --served-model-name Qwen3.5-VL-27B > /vllm.log 2>&1 &
  
nohup python3 -m vllm.entrypoints.openai.api_server \
  --model /root/Models/Qwen3.5_35B_A3B \
  --tensor-parallel-size 2 \
  --max-model-len 4096 \
  --trust-remote-code \
  --gpu-memory-utilization 0.85 \
  --enforce-eager \
  --port 5359 \
  --served-model-name Qwen3.5-VL-27B > /vllm.log 2>&1 &

# 5.查看日志
tail -f /vllm.log

# 6.关闭进程
pkill -9 python
或者
npu-smi info  查看进程
kill -9 6625 6626  杀死对应进程ID
```

### 3.2 核心启动参数解析
- `--tensor-parallel-size 2`: 启用双卡张量并行（Tensor Parallelism），将 27B 模型切分至两张 910B 显卡。
- `--max-model-len 4096`: 限制最大上下文长度。调小此值可大幅节省 KV Cache 显存，提升并发吞吐量。
- `--limit-mm-per-prompt.video 0`: **显存优化关键**。关闭视频处理的显存预留，将资源全部让给图片处理。
- `--trust-remote-code`: 允许执行 Qwen 模型自带的自定义 Python 脚本。

当日志打印出 `Uvicorn running on http://0.0.0.0:5359` 时，即代表模型加载完毕。

---

## 4. 客户端 API 调用 

### 1.Python 示例
模型服务完全兼容 OpenAI Vision API 规范。针对工业级流水线，建议加入严格的 System Prompt，并适当放宽请求超时时间。

```python
import requests

LIANTONG_MODEL = "http://192.168.0.161:5359/v1/chat/completions"

def detect_frame(question, image_base64):
    image_data_url = f"data:image/png;base64,{image_base64}"
    
    data = {
        "model": "Qwen3.5-VL-27B",
        "messages": [
            {
                # 严厉的 System Prompt，限制模型只输出 JSON，提高解析稳定性
                "role": "system",
                "content": "You are a strict image analysis program. No matter what you see, you must and can only output valid JSON format. Under no circumstances are you allowed to output any introductory remarks, concluding remarks, English text, analysis processes, or thought processes."
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                    {"type": "text", "text": question}
                ]
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.1,    # 降低随机性，保证确定性输出
        "top_p": 0.9,
        "top_k": 50,
        "repetition_penalty": 1.1
    }

    try:
        # NPU 冷启动编译或高并发排队时耗时较长，timeout 建议设为 120s
        response = requests.post(LIANTONG_MODEL, json=data, timeout=120)
        response.raise_for_status()
        
        reply = response.json()["choices"][0]["message"]["content"]
        return reply

    except Exception as e:
        print(f"[detect_frame] 调用异常: {type(e).__name__} - {e}")
        return '{"result": "错误"}'
```
### 2.命令行调用
```bash
curl http://192.168.0.161:5359/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "Qwen3.5-VL-27B", "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": [{"type": "text", "text": "请介绍一下你自己"}]}]}'
```
