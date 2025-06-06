# PLLM-C

PLLM-C 是一个多智能体语言编译器项目，支持将自定义的多智能体 DSL 编译为可执行的 Python 代码，并集成了类型检查、AST 可视化、REPL 等功能。

## 目录结构

```
pllm_c/
├── compile.py              # 命令行编译器入口
├── repl.py                 # 交互式 REPL
├── diagnostics.py          # 诊断与错误报告
├── ast_visual.py           # AST 可视化
├── config.py               # 配置文件（API KEY等）
├── generate/               # 代码生成相关
│   ├── code_gen.py
│   ├── built_in.py
│   └── topo_manager.py
├── pllm_parser/            # 词法/语法分析与AST定义
│   ├── pllm_lexer.py
│   ├── pllm_parser.py
│   └── pllm_ast.py
├── type_system/            # 类型系统与类型检查
│   ├── type_checker.py
│   ├── type_env.py
│   └── built_in_sig.json
├── docs/                   # 语法文档等
│   ├── grammar.txt
│   └── type_system.txt
├── tests/                  # 测试用例
│   ├── complex_expr.pllm
│   ├── complex_type.pllm
│   └── ...
├── examples/               # 示例
│   ├── example.pllm
│   └── output/
└── output/                 # 输出目录
    ├── ast.png
    └── ...
```

## 快速开始

### 依赖安装

主要依赖：`graphviz`, `openai`, `ply`。

### 编译 PLLM 源码

```bash
python compile.py examples/example.pllm --output_file output/output.py
```
- 解析、类型检查并生成 Python 代码到指定文件。
- 自动生成 AST 可视化图（`output/ast.png`）。

### 交互式 REPL

```bash
python repl.py
```
- 支持多行输入，空行执行，`exit`/`quit` 退出。

### 诊断工具

```bash
python diagnostics.py examples/example.pllm
```
- 输出语法和类型错误的诊断信息（JSON）。

## 语法简介

- 详见 [docs/grammar.txt](docs/grammar.txt)
- 支持 agent、connect、chat、函数定义、类型别名、流程控制等。

## 主要功能

- **自定义 DSL 解析**：支持多智能体编程范式。
- **类型检查**：静态类型推断与错误提示。
- **代码生成**：输出高质量 Python 代码，集成 OpenAI API。
- **AST 可视化**：一键生成语法树图像。
- **REPL**：交互式实验与调试。
- **测试用例**：丰富的测试覆盖。

## 贡献与开发

- 修改 `.gitignore` 以排除敏感信息和缓存。
- 代码风格建议遵循 PEP8。
- 欢迎提交 issue 和 PR！