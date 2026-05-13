# 舆情镜像公网部署说明

本项目是 Streamlit 应用，不能通过修改 `localhost` 直接变成公网网站。要让任何设备都能访问，需要部署到云端平台。

## 推荐方案：Streamlit Community Cloud

适合课程作业和作品集展示，优点是和 Streamlit 项目最匹配，部署步骤较少。

### 需要准备

1. 一个 GitHub 账号。
2. 一个公开或私有 GitHub 仓库。
3. 本项目文件夹中的这些文件必须上传：
   - `app.py`
   - `pages/`
   - `src/`
   - `config/`
   - `data/sample/`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `README.md`

### 部署步骤

1. 把 `E:\undergraduate\Web\PSM` 上传到 GitHub 仓库。不要上传上级目录里的 `.venv`、`tools` 或 `__pycache__`。
2. 打开 Streamlit Community Cloud。
3. 选择 `New app`。
4. 选择你的 GitHub 仓库。
5. Branch 选择 `main`。
6. Main file path 填写：

```text
app.py
```

7. 点击 Deploy。
8. 部署成功后，会得到类似下面的网址：

```text
https://your-project-name.streamlit.app
```

这个网址就是公网网站，其他人不在同一 Wi-Fi 也可以访问。

## 注意事项

- `localhost:8501` 只代表你自己的电脑。
- `0.0.0.0:8501` 只适合局域网访问，不是公网网站。
- GitHub Pages 不能直接运行 Streamlit，因为 Streamlit 需要 Python 后端。
- 如果后续加入大型模型，如 BERT、SBERT、BERTopic，云端启动会变慢，建议先保持基础版稳定。

## 备选方案

- Render：也可以部署 Streamlit，适合以后需要更自由的后端环境。
- Hugging Face Spaces：适合机器学习项目展示。
- 云服务器/VPS：最自由，但需要配置服务器、安全组、域名和进程守护，适合后期正式作品集网站。
