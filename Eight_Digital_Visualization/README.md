目录：

/your-project-directory
├── /backend
│   ├── **app.py           # Flask 后端代码**
│   ├── requirements.txt # 后端依赖列表
├── /frontend
│   ├── /src
│   │   ├── **App.js       # React 前端代码**
│   │   ├── **App.css      # 前端样式**
│   │   └── index.js     # React 入口文件
│   ├── package.json     # 前端依赖列表
│   └── .env             # 前端环境配置
└── README.md            # 项目说明文件

加粗为要使用的主要代码。环境不一样配置的文件也不一样，可以按照两个目录创建文件目录，再把主要代码放进去。配置流程：

1. pycharm创建flask项目
2. 创建文件目录backend，frontend

3. backend相关：

安装flask和flask_cors

```

```



4. frontend相关：

打开 PyCharm 的终端，切换到 `frontend` 目录：

```
cd frontend
```

运行以下命令初始化 React 项目：

```
npx create-react-app .
```

注意：运行这个命令需要安装 Node.js。

安装 Axios 进行后端通信：

```bash
npm install axios
```



# 运行后端

直接运行app.py

#  运行前端

命令行里面先

```
cd frontend
```

再运行：

```
npm start
```

