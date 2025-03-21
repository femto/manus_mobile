# 发布指南

本文档说明如何将mobile_use包发布到PyPI。

## 准备工作

1. 确保你已经注册了PyPI账号：https://pypi.org/account/register/
2. 如果想先在测试环境发布，也要注册TestPyPI：https://test.pypi.org/account/register/
3. 安装必要的工具：
   ```bash
   pip install --upgrade setuptools wheel twine build
   ```

## 版本更新

1. 在发布新版本前，更新`mobile_use/__init__.py`文件中的`__version__`变量
2. 更新`setup.py`中的`version`字段，确保两者一致
3. 更新`README.md`中的相关内容，确保文档和代码同步

## 发布步骤

### 使用发布脚本

我们提供了一个简单的发布脚本`publish.sh`，你可以直接运行：

```bash
./publish.sh
```

该脚本会自动执行下面的所有步骤。

### 手动发布

如果你想手动控制发布过程，请按以下步骤操作：

1. 清理旧的构建文件：
   ```bash
   rm -rf build/ dist/ *.egg-info/
   ```

2. 构建发布包：
   ```bash
   python -m build
   ```
   这会在`dist/`目录下创建源代码包(`.tar.gz`)和轮子包(`.whl`)

3. 检查构建结果：
   ```bash
   ls -l dist/
   ```

4. 上传到TestPyPI（可选）：
   ```bash
   python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
   ```
   会提示输入你的TestPyPI用户名和密码

5. 测试从TestPyPI安装（可选）：
   ```bash
   pip install --index-url https://test.pypi.org/simple/ mobile_use
   ```

6. 上传到正式PyPI：
   ```bash
   python -m twine upload dist/*
   ```
   会提示输入你的PyPI用户名和密码

7. 测试从正式PyPI安装：
   ```bash
   pip install --upgrade mobile_use
   ```

## 配置.pypirc文件（可选）

为避免每次都输入用户名和密码，可以在用户主目录下创建`.pypirc`文件：

```
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = your_username
password = your_password

[testpypi]
repository = https://test.pypi.org/legacy/
username = your_username
password = your_password
```

记得保护这个文件的安全性：`chmod 600 ~/.pypirc`

## 疑难解答

- 如果上传时出现错误，请确保你的包名在PyPI上是唯一的
- 版本号必须严格递增，不能重复使用已发布的版本号
- 如果包含非ASCII字符，确保所有文件都使用UTF-8编码
- 如果上传失败，请查看错误信息并修复问题，然后重试

## 发布后的工作

1. 在GitHub仓库中创建一个新的release，标记版本号
2. 更新文档网站（如果有）
3. 通知用户新版本发布及其功能变化 