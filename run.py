if __name__ == "__main__":
    from csufactory.dialoge import prompt_user_for_params,run_component_function

    selected_component_name, params = prompt_user_for_params()
    if selected_component_name:
        # 使用用户输入的参数运行组件函数
        component = run_component_function(selected_component_name, params)
        # 显示生成的组件
        component.show()