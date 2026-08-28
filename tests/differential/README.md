# 正式板子差分测试

这里维护能直接验证的完整模板。纯思路、伪代码和依赖具体题意的框架不进入
`manifest.json`，也不为了凑覆盖率标记成“已验证”。

## 核心原则

1. 运行器从 `remake/large/*.tex` 提取包含指定唯一签名的正式代码块，不在测试目录
   手抄第二份模板实现。
2. `harnesses/` 只保存暴力解、随机生成器和调用包装；随机种子固定，失败可以复现。
3. 已发现的最小反例保存在 `regressions/`，修复后也永久保留。
4. `expected=pass` 表示必须通过；`expected=xfail` 表示问题已确认但尚未修复。
   `xfail` 意外通过会报告 `XPASS` 并返回失败，提醒维护者复核后升级状态。
   `xfail` 应配置 `expected_failure_contains`，避免把崩溃或新的失败原因当成旧问题。
   默认验证运行阶段；若板子本身不能编译，另设
   `expected_failure_stage=compile`，只把匹配既定诊断特征的编译失败算作 `XFAIL`。
5. 代码块选择器必须在指定 `.tex` 中恰好命中一次；签名漂移或重复时测试直接报错。

## 使用

```text
python tools/run_differential_tests.py --list
python tools/run_differential_tests.py
python tools/run_differential_tests.py --case strings.prefix_function
```

测试编译产物只写入被忽略的 `tmp/`，运行结束自动删除。

## 新增测试

1. 确认目标是完整、能定义输入输出或不变量的模板；框架不登记。
2. 在 `harnesses/` 新建驱动，并保留唯一的 `// @@@TEMPLATE@@@` 注入位置。
3. 在 `manifest.json` 填写正式源、代码块内唯一签名、驱动和预期状态。
4. 优先写小规模暴力解，再增加固定种子的随机对拍。
5. 发现错误时先把最小反例加入 `regressions/`，将状态设为 `xfail`；修复模板后
   确认出现 `XPASS`，再把状态改为 `pass`。
