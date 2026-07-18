# 可爱中国梦核营养插画 Skill

> 将循证营养知识变成可爱的中国梦核浮空营养世界。

**科学优先。教学其次。梦幻视觉叙事第三。**

这是一个独立的开源 Python 项目：把经过验证的营养学主张转化为可检查的视觉包，包括事实、教学信息、浮空岛世界设计、模块化图片提示词、反向提示词、中英文文案、无障碍替代文本、质量报告和可选海报。

项目由中国注册营养师设计，将循证营养传播规则与原创的可爱中国梦核视觉系统结合起来。它用于营养科学传播，不提供诊断、治疗、处方或个体化医疗建议。

## 核心原则

系统严格分离四层：科学事实层、教学信息层、视觉世界层、文字叠加层。所有下游文件都从 `visual_spec.json` 派生。离线 MockProvider 只生成 `layout_mock_preview.png` 和 `text_overlay_mock_preview.png`，并带有 **LAYOUT MOCK — NOT FINAL ARTWORK** 标识；它们只能测试布局和文字叠加，不能代表目标艺术风格。

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

## 安全与限制

所有健康相关视觉必须来自输入或精选的 `NutritionClaim`。系统检查证据来源、因果表述、治疗承诺、数字、适用人群、局限和引用。视觉隐喻不能冒充真实生物解剖。当前 MVP 不包含文献全文检索、多智能体、数据库、网页应用或自动发布；真实图片仍需人工审核。

如果真实 provider 不可用，系统只输出提示词包和带标签的 mock 预览，不会创建 `illustration_final.png`。代码采用 MIT License；生成图片权利取决于具体图片服务商条款；项目不包含字体文件、版权角色或第三方艺术素材。
