<execution>
  <constraint>
    ## 技术环境约束
    - **Python版本**：必须使用Python 3.8+以支持Textual的异步特性
    - **Textual版本**：优先使用Textual 0.50+的最新稳定版本
    - **终端兼容性**：必须在主流终端（Terminal.app, iTerm2, Windows Terminal, GNOME Terminal）中正常工作
    - **Docker环境**：应用需要在容器化环境中稳定运行
    - **SSH连接**：通过SSH远程访问时保持完整功能
  </constraint>

  <rule>
    ## 强制性开发规则
    - **组件化强制**：所有UI元素必须基于Textual的Widget系统构建
    - **异步处理**：网络请求和文件IO必须使用异步操作避免界面阻塞
    - **错误处理**：所有用户操作必须有明确的错误处理和反馈机制
    - **键盘导航**：所有功能必须可通过键盘操作完成，鼠标支持为可选
    - **状态管理**：使用Textual的Reactive系统管理组件状态变化
    - **CSS样式**：必须使用Textual的CSS系统而非内联样式定义
  </rule>

  <guideline>
    ## 开发指导原则
    - **用户体验优先**：每个设计决策都要从用户操作便利性角度考虑
    - **性能意识**：时刻关注渲染性能和内存使用情况
    - **可测试性**：编写可单元测试的组件和业务逻辑
    - **可维护性**：保持代码清晰的结构和充分的文档
    - **渐进增强**：基础功能稳定后再添加高级特性
    - **平台一致性**：确保在不同操作系统下的体验一致
  </guideline>

  <process>
    ## Textual开发完整流程
    
    ### 阶段1：项目初始化 (15分钟)
    
    ```mermaid
    flowchart TD
        A[项目需求分析] --> B[创建项目结构]
        B --> C[配置开发环境]
        C --> D[设计UI原型]
        D --> E[定义组件架构]
        
        B -.-> B1[创建src/app目录结构]
        C -.-> C1[配置Pixi依赖管理]
        D -.-> D1[绘制界面草图和交互流程]
        E -.-> E1[规划组件层次和通信方式]
    ```
    
    **项目结构模板**：
    ```
    textual-app/
    ├── pyproject.toml          # Pixi项目配置
    ├── src/
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── main.py         # 应用入口
    │   │   ├── screens/        # 界面管理
    │   │   ├── widgets/        # 自定义组件
    │   │   └── styles/         # CSS样式文件
    │   └── utils/              # 工具函数
    ├── tests/                  # 测试文件
    └── assets/                 # 静态资源
    ```
    
    ### 阶段2：核心组件开发 (30-45分钟)
    
    ```mermaid
    graph TD
        A[App类设计] --> B[Screen布局]
        B --> C[Widget组件]
        C --> D[事件处理]
        D --> E[样式定义]
        
        A1[生命周期管理] --> A
        B1[响应式布局] --> B
        C1[可复用组件] --> C
        D1[键盘鼠标事件] --> D
        E1[CSS样式系统] --> E
    ```
    
    **核心开发检查清单**：
    - [ ] App类继承自textual.app.App
    - [ ] 定义SCREENS和BINDINGS类属性
    - [ ] 实现compose()方法构建界面层次
    - [ ] 设置CSS_PATH指向样式文件
    - [ ] 实现关键事件处理方法
    - [ ] 添加适当的类注解和文档
    
    ### 阶段3：交互逻辑实现 (20-30分钟)
    
    ```mermaid
    flowchart LR
        A[用户输入] --> B{事件类型判断}
        B -->|键盘| C[键盘事件处理]
        B -->|鼠标| D[鼠标事件处理]
        B -->|系统| E[系统事件处理]
        C --> F[更新应用状态]
        D --> F
        E --> F
        F --> G[触发界面重渲染]
    ```
    
    **事件处理最佳实践**：
    ```python
    # 键盘快捷键绑定
    BINDINGS = [
        ("q", "quit", "退出应用"),
        ("ctrl+s", "save", "保存数据"),
        ("f1", "help", "显示帮助")
    ]
    
    # 自定义消息处理
    async def on_custom_message(self, message: CustomMessage) -> None:
        """处理自定义组件消息"""
        await self.handle_business_logic(message.data)
    ```
    
    ### 阶段4：样式和体验优化 (15-20分钟)
    
    ```mermaid
    mindmap
      root((样式优化))
        布局优化
          Grid布局
          Flexbox布局
          响应式设计
        视觉层次
          颜色主题
          字体样式
          间距设计
        交互反馈
          hover效果
          focus指示
          loading状态
        性能优化
          懒加载
          虚拟化
          缓存策略
    ```
    
    **CSS样式规范**：
    ```css
    /* 主题色彩定义 */
    :root {
        --primary: #0066cc;
        --secondary: #6c757d;
        --success: #28a745;
        --warning: #ffc107;
        --error: #dc3545;
    }
    
    /* 组件样式 */
    .main-container {
        layout: grid;
        grid-size: 2 3;
        margin: 1;
        padding: 1;
    }
    ```
    
    ### 阶段5：测试和调试 (10-15分钟)
    
    ```mermaid
    graph TD
        A[单元测试] --> B[集成测试]
        B --> C[用户体验测试]
        C --> D[性能测试]
        D --> E[跨平台测试]
        
        A1[组件功能] --> A
        B1[界面交互] --> B
        C1[操作流程] --> C
        D1[响应速度] --> D
        E1[兼容性] --> E
    ```
    
    **调试工具使用**：
    ```python
    # 开启开发者模式
    app = MyApp()
    app.run(debug=True, dev=True)
    
    # 使用Textual开发者工具
    from textual import log
    log("调试信息", level="INFO")
    ```
  </process>

  <criteria>
    ## 开发质量标准
    
    ### 功能完整性
    - ✅ 所有核心功能可通过键盘操作完成
    - ✅ 错误情况有清晰的用户反馈
    - ✅ 应用启动和退出流程正常
    - ✅ 数据持久化功能正常工作
    
    ### 用户体验质量
    - ✅ 界面响应时间 < 100ms
    - ✅ 操作流程符合用户直觉
    - ✅ 视觉层次清晰明确
    - ✅ 帮助信息易于访问
    
    ### 代码质量标准
    - ✅ 组件职责单一明确
    - ✅ 代码覆盖率 > 80%
    - ✅ 类型注解完整准确
    - ✅ 文档字符串齐全
    
    ### 兼容性要求
    - ✅ 支持主流终端应用
    - ✅ 在Docker环境正常运行
    - ✅ 通过SSH连接正常使用
    - ✅ 跨操作系统兼容
  </criteria>
</execution>