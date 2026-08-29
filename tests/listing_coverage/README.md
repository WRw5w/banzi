# 正式代码块覆盖清单

`tools/audit_listing_coverage.py` 从正式入口 `banzi/板子_大版本.tex` 出发，按实际
引入顺序枚举全部 `lstlisting`，并把现有差分测试映射回唯一的正式代码块。

未被差分或契约测试覆盖的代码块必须在 `classification.json` 中显式登记。当前清单使用
`source + digest` 绑定代码块的完整正文；正文变化后旧分类会立即失效，必须重新
复核。也支持差分测试同款的 `source + contains` 唯一选择器。分类包括：

- `framework`：依赖题意或外部钩子的算法框架；
- `pseudocode`：不承诺可以直接编译的伪代码；
- `explanatory`：命令、配置、API 速查或说明性代码片段。

每项分类必须填写 `note`，说明该块具体缺少的输入、外部钩子、状态或题意语义；
`framework` 还必须填写 `structural_contract` 和逐块 `required_patterns`。门禁会拒绝
占位符、语法破损、未声明的空钩子、恒定返回算法空壳和结构漂移，并真实调用编译器
验证无效反例会失败。它只确认已登记框架仍保持声明的结构，不冒充编译或算法语义
测试。已经有关联差分/契约证据的代码块不能再重复分类。

验证状态只保存在本目录和生成报告中，不向正式 TeX/PDF 添加标记。生成或刷新清单：

```text
python tools/audit_listing_coverage.py --write
python tools/audit_listing_coverage.py
python tools/run_framework_checks.py
python -m unittest tests.test_listing_coverage tests.test_framework_checks
```

覆盖审计默认要求零 `PENDING`，因此新增代码块不会静默漏检。只有盘点过程确需查看
临时报告时才使用 `--allow-pending`，不得把带待分类项的报告作为完成状态提交。
