# 可爱中国梦核营养插画 Skill

> 将输入的营养与健康科普内容变成可爱的中国梦核浮空世界。

**给它科普内容，它负责把可爱视觉世界做好。**

这是一个独立的开源 Python 项目：把调用者提供的营养或健康科普内容转化为可检查的视觉包，包括事实、教学信息、浮空岛世界设计、模块化图片提示词、反向提示词、中英文文案、无障碍替代文本、质量报告和可选海报。

项目由中国注册营养师设计，是一套原创的可爱中国梦核科普视觉系统。它负责呈现调用者提供的内容，不判断临床正确性，也不提供个体化医疗建议。

## 核心原则

系统分离四层：输入内容层、教学信息层、视觉世界层、文字叠加层。所有下游文件都从 `visual_spec.json` 派生。离线 MockProvider 只生成 `layout_mock_preview.png` 和 `text_overlay_mock_preview.png`，并带有 **LAYOUT MOCK — NOT FINAL ARTWORK** 标识；它们只能测试布局和文字叠加，不能代表目标艺术风格。

## 离线运行

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
dreamnutri generate --topic "Dietary Fiber and Gut Health" --audience "general adults" --language en --use-case social_poster --aspect-ratio 4:5 --provider mock --output outputs/fiber-poster
```

也可以直接使用示例请求：

```bash
dreamnutri generate --request examples/dietary-fiber-gut-health/request.json --provider mock
```

## 视觉系统

真实图片生成成功后，每张图都应像漂浮在柔和天空里的微型营养世界：主浮空岛、食物卫星岛、云朵路径、微型花园、友好的微生物居民、小蘑菇向导、星星、花朵，以及含蓄的祥云曲线或园林桥梁。整体可爱、温暖、明亮、舒适，不使用恐怖梦核、阴暗梦核、诡异解剖或企业医疗模板。MockProvider 永远不能通过艺术风格检查。

## 内容边界

这个项目是插画渲染器，不是医学内容审稿引擎。没有引用也可以正常出图；输入中出现“预防、治疗、诊断”等词时，不会被关键词扫描粗暴拦截。事实、编辑和临床审核由上游内容提供者负责。视觉层仍避免身体羞辱、恐吓式表达、把隐喻冒充真实解剖，以及版权或不安全图像。当前 MVP 不包含文献检索、多智能体、数据库、网页应用或自动发布；真实图片仍需人工视觉审核。

如果真实 provider 不可用，系统只输出提示词包和带标签的 mock 预览，不会创建 `illustration_final.png`。代码采用 MIT License；生成图片权利取决于具体图片服务商条款；项目不包含字体文件、版权角色或第三方艺术素材。
