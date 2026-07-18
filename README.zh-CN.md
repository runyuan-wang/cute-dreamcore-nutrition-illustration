# 可爱中国梦核营养插画

这是一个严格限定为六个阶段的产品链：把任意科普主题变成一张可爱中国梦核浮空岛插画及其可检查的输出包。

## 作者

**王润圆 (Wang Runyuan)**

昆明医科大学营养与食品卫生学硕士，中国注册营养师，云南天文爱好者协会秘书处干事。好奇心强，长期参与科普活动；正在学习并探索把 AI 与营养学科普和实际营养工作相结合，希望帮助更多人。她设计本项目，把循证营养传播与原创的可爱中国梦核视觉系统结合起来。

- GitHub：[@9s5bz2jvd2-lang](https://github.com/9s5bz2jvd2-lang)
- 联系方式：[jykmsg@163.com](mailto:jykmsg@163.com)

## 示例

![人类提供的真实示例：温暖粉彩色、带浮空岛和教育场景的可爱中国梦核营养插画。](docs/images/authentic-demo-0718_1.png)

> **人类提供的参考图：**保留原始字节（SHA-256：`4d7f583ad897190720038f0f00775aae876593166d0fe2978aa0623be06feaf2`）。

### 中英文叠字实效图（离线 fixture）

![同一张人类提供的离线底图上，左侧为 zh-CN、右侧为英文程序叠字，两张图都明确标注 FIXTURE。](docs/images/bilingual-overlay-fixture-proof.jpg)

同一张底图，分别实际运行中文和英文 compositor；可见的 `FIXTURE` 标签用来区分离线叠字实效图和 provider 成图。

## 精确的六阶段产品链

1. **输入主题：**接收科普主题、受众、语言、版式和可选的调用方内容。
2. **提取教学重点：**GPT-5.6 提取一至三个面向受众的教学重点；可注入的有类型规划器会先验证结果。
3. **生成结构化视觉规格：**GPT-5.6 将教学重点变成经过验证的结构化视觉方案，包括信息、隐喻、浮岛世界、装饰母题和画面方向。
4. **梦核风格编译：**既有风格/世界编译器消费经过验证的方案，生成可爱中国梦核浮空岛绘图指令、安全区和负面提示词。
5. **生成插画：**选定的图像 provider 生成不嵌入长文字的真实画面；真实 provider 运行写出 `illustration_raw.png`。
6. **准确叠字与导出：**Pillow 在中文运行选择 `text_zh_cn`，在英文运行选择 `text_en`，加入标题、副标题和 callout，并导出 `illustration_final.png`、检查包和来源清单。

渲染器不判断或改写用户的科普内容；内容准确性由上游作者负责。

## 安装

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

默认离线路径不需要 API key。

## 离线开发

默认离线路径使用 `FakeTextPlanner` 与 `MockProvider`，所有预览都标记 **LAYOUT MOCK — NOT FINAL ARTWORK**。

```bash
PYTHONPATH=src python -m dreamnutri.cli generate \
  --topic "Dietary Fiber and Gut Health" \
  --audience "general adults" \
  --language zh-CN \
  --provider mock \
  --output outputs/fiber-poster
```

测试可通过 `generate_package(..., text_planner=FakeTextPlanner())` 注入 fake。它会记录两个明确阶段并验证两个 Pydantic 合约。生产规划器不可用时会如实报告，不会悄悄伪造 GPT 输出。

## 生产 provider

文字规划器使用既有 `httpx` 和 OpenAI-compatible endpoint；请显式配置：

```bash
export OPENAI_API_KEY="..."
export OPENAI_TEXT_MODEL="gpt-5.6"
export OPENAI_TEXT_ENDPOINT="https://api.openai.com/v1/chat/completions"
```

图像 adapter 独立配置：

```bash
export OPENAI_IMAGE_MODEL="your-approved-image-model"
export OPENAI_IMAGE_ENDPOINT="https://api.openai.com/v1/images/generations"

PYTHONPATH=src python -m dreamnutri.cli generate \
  --topic "膳食纤维与肠道健康" \
  --audience "普通成年人" \
  --language zh-CN \
  --provider openai \
  --output outputs/fiber-poster-real
```

不会保存或打印 key。provider 失败会被记录且不写最终插画；`FixtureImageProvider` 只用于测试。

## 可检查输出

每次运行写出请求、归一化内容、两阶段规划来源、`visual_spec.json`、图像/负面提示词、中英 caption 与 alt text、质量报告、mock 预览和 `generation_manifest.json`。真实 provider 或 fixture provider 测试成功时，另外写出 `illustration_raw.png` 和 `illustration_final.png`。


## 使用边界

本 Skill 渲染调用方提供的科普内容，不验证医学主张，也不替代人工审阅。发布前请检查最终画面与 provider 授权。

## 测试

```bash
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m compileall -q src tests
```

## 许可证和原创性

代码采用 MIT License，示例内容为项目原创。生成图片的权利遵循所选 provider 条款；项目不捆绑第三方字体、画作、角色或特许经营素材。
