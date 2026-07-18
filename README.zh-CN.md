# 可爱中国梦核营养插画

这是一个严格限定为六个阶段的产品链：把任意科普主题变成一张可爱中国梦核浮空岛插画及其可检查的输出包。

![人类提供的真实示例：温暖粉彩色、带浮空岛和教育场景的可爱中国梦核营养插画。](docs/images/authentic-demo-0718_1.png)

> **真实示例说明：**上图是人类提供的真实 `0718_1.png` 示例（SHA-256：`4d7f583ad897190720038f0f00775aae876593166d0fe2978aa0623be06feaf2`）。本次修复保留其原始 PNG 字节；没有在此重新生成，也不能证明发生过实时 API 调用。

### 中英文叠字实效图（离线 fixture）

![同一张人类提供的离线底图上，左侧为 zh-CN、右侧为英文程序叠字，两张图都明确标注 FIXTURE。](docs/images/bilingual-overlay-fixture-proof.jpg)

这张实效图复用上述原始画面字节，分别实际运行中文和英文 compositor。已检查中文字符渲染、混合中英时英文单词不被拆开、溢出标志以及可见的 `FIXTURE` 来源标签。README 使用的是缩放审阅 JPG（SHA-256：`035c2ebdf8ec1dc57909d1d0b6a43b8ea1cc677d450f6bd40d6ba86cf96263ff`）；它**不**证明发生过实时 GPT 或图片 provider 调用，也不代表审美验收。

## 精确的六阶段产品链

1. **输入主题：**接收科普主题、受众、语言、版式和可选的调用方内容。
2. **提取教学重点：**GPT-5.6 提取一至三个面向受众的教学重点；可注入的有类型规划器会先验证结果。
3. **生成结构化视觉规格：**GPT-5.6 将教学重点变成经过验证的结构化视觉方案，包括信息、隐喻、浮岛世界、装饰母题和画面方向。
4. **梦核风格编译：**既有风格/世界编译器消费经过验证的方案，生成可爱中国梦核浮空岛绘图指令、安全区和负面提示词。
5. **生成插画：**选定的图像 provider 生成不嵌入长文字的真实画面；真实 provider 运行写出 `illustration_raw.png`。
6. **准确叠字与导出：**Pillow 在中文运行选择 `text_zh_cn`，在英文运行选择 `text_en`，加入标题、副标题和 callout，并导出 `illustration_final.png`、检查包和来源清单。

本项目只执行这条链，不是内容审查引擎。缺少引用、出现 `prevention`、`treatment`、`diagnosis` 或数字都不会阻止生成；内容责任属于上游作者。

## 安装

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

默认离线路径不需要 API key。

## 离线开发

默认 `mock` 请求使用明确命名的 `FakeTextPlanner` 做离线测试，并使用 `MockProvider` 生成布局预览。fake 不会被描述成 GPT-5.6；mock 预览始终标记 **LAYOUT MOCK — NOT FINAL ARTWORK**，不能证明真实艺术风格。

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

不会保存或打印 key。文字或图像 provider 不可用时，输出会记录错误且不会创建最终真实插画。离线 `FixtureImageProvider` 只用于确定性的真实 PNG 解码路径测试，不是实时 provider。

## 可检查输出

每次运行写出请求、归一化内容、两阶段规划来源、`visual_spec.json`、图像/负面提示词、中英 caption 与 alt text、质量报告、mock 预览和 `generation_manifest.json`。真实 provider 或 fixture provider 测试成功时，另外写出 `illustration_raw.png` 和 `illustration_final.png`。

真实示例仅保存在 `docs/images/authentic-demo-0718_1.png`，并保留原始 hash。README alt text 描述可见的浮空岛教育画面，不声称本次修复重新生成了它。

## 边界

世界是象征性的，不是真实解剖。渲染器不导入证据审查规则、不检索文献、不诊断、不治疗、不承诺预防，也不提供个体化医疗建议；它只编译经过验证的规划结果并导出插画包。真实画面仍需人工检查艺术风格、无障碍、含义和 provider 授权。

## 测试

```bash
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m compileall -q src tests
```

## 许可证和原创性

代码采用 MIT License。示例 JSON 和文字为项目原创；生成图片的权利取决于所选 provider 的条款。项目不包含版权角色、复制画作、第三方字体文件、模仿在世艺术家或特许经营素材。项目名称和视觉系统是项目标识，不代表已注册商标。

## 作者

由中国注册营养师设计，把循证营养传播与原创的可爱中国梦核视觉系统结合起来。
