# 正式代码块覆盖清单

`tools/audit_listing_coverage.py` 从正式入口 `banzi/板子_大版本.tex` 出发，按实际
引入顺序枚举全部 `lstlisting`，并把现有差分测试映射回唯一的正式代码块。

首次盘点时，未被差分测试覆盖的代码块统一显示为 `PENDING`。后续人工复核时，在
`classification.json` 中使用与差分测试相同的 `source + contains` 唯一选择器，将其
归入：

- `framework`：依赖题意或外部钩子的算法框架；
- `pseudocode`：不承诺可以直接编译的伪代码；
- `explanatory`：命令、配置、API 速查或说明性代码片段。

每项分类必须填写 `note`，说明分类依据。已经有关联差分证据的代码块不能再重复
分类。生成或刷新清单：

```text
python tools/audit_listing_coverage.py --write
python tools/audit_listing_coverage.py
```

全部人工归类完成后，可用严格模式阻止新代码块静默落入待处理状态：

```text
python tools/audit_listing_coverage.py --require-classified
```
