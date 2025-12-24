"""
LangChain 1.0.0+ 兼容性测试脚本
运行此脚本来验证项目是否完全兼容 LangChain 1.0.0+
"""
import sys

def test_imports():
    """测试所有必要的导入"""
    results = []
    
    # 测试 1: langchain_core.tools
    try:
        from langchain_core.tools import BaseTool, tool
        results.append(("✅", "langchain_core.tools", "导入成功"))
    except ImportError as e:
        results.append(("❌", "langchain_core.tools", f"导入失败: {e}"))
    
    # 测试 2: langchain_core.prompts
    try:
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        results.append(("✅", "langchain_core.prompts", "导入成功"))
    except ImportError as e:
        results.append(("❌", "langchain_core.prompts", f"导入失败: {e}"))
    
    # 测试 3: langchain_openai
    try:
        from langchain_openai import ChatOpenAI
        results.append(("✅", "langchain_openai", "导入成功"))
    except ImportError as e:
        results.append(("❌", "langchain_openai", f"导入失败: {e}"))
    
    # 测试 4: langchain.agents (标准导入)
    try:
        from langchain.agents import create_openai_tools_agent, AgentExecutor
        results.append(("✅", "langchain.agents (标准)", "导入成功"))
    except ImportError:
        # 测试 5: langchain_agents (独立包)
        try:
            from langchain_agents import create_openai_tools_agent, AgentExecutor
            results.append(("✅", "langchain_agents (独立包)", "导入成功"))
        except ImportError:
            # 测试 6: langchain.agents.create_agent (新 API)
            try:
                from langchain.agents import AgentExecutor, create_agent
                results.append(("⚠️", "langchain.agents (新API)", "使用 create_agent"))
            except ImportError as e:
                results.append(("❌", "langchain.agents", f"所有导入方式都失败: {e}"))
    
    return results

def test_versions():
    """测试版本号"""
    results = []
    
    try:
        import langchain
        version = langchain.__version__
        major_version = int(version.split('.')[0])
        if major_version >= 1:
            results.append(("✅", f"langchain {version}", "版本 >= 1.0.0"))
        else:
            results.append(("❌", f"langchain {version}", "版本 < 1.0.0，需要升级"))
    except Exception as e:
        results.append(("❌", "langchain", f"无法获取版本: {e}"))
    
    try:
        import langchain_core
        version = langchain_core.__version__
        major_version = int(version.split('.')[0])
        if major_version >= 1:
            results.append(("✅", f"langchain_core {version}", "版本 >= 1.0.0"))
        else:
            results.append(("❌", f"langchain_core {version}", "版本 < 1.0.0，需要升级"))
    except Exception as e:
        results.append(("❌", "langchain_core", f"无法获取版本: {e}"))
    
    return results

def test_project_imports():
    """测试项目模块导入"""
    results = []
    
    try:
        from tools import get_all_tools
        tools = get_all_tools()
        results.append(("✅", "tools.get_all_tools", f"成功，共 {len(tools)} 个工具"))
    except Exception as e:
        results.append(("❌", "tools.get_all_tools", f"导入失败: {e}"))
    
    try:
        from agent import VoiceChatAgent
        results.append(("✅", "agent.VoiceChatAgent", "导入成功"))
    except Exception as e:
        results.append(("❌", "agent.VoiceChatAgent", f"导入失败: {e}"))
    
    return results

def main():
    """主测试函数"""
    print("=" * 60)
    print("LangChain 1.0.0+ 兼容性测试")
    print("=" * 60)
    print()
    
    # 测试版本
    print("📦 版本检查:")
    print("-" * 60)
    version_results = test_versions()
    for status, module, message in version_results:
        print(f"{status} {module}: {message}")
    print()
    
    # 测试导入
    print("📥 导入测试:")
    print("-" * 60)
    import_results = test_imports()
    for status, module, message in import_results:
        print(f"{status} {module}: {message}")
    print()
    
    # 测试项目模块
    print("🔧 项目模块测试:")
    print("-" * 60)
    project_results = test_project_imports()
    for status, module, message in project_results:
        print(f"{status} {module}: {message}")
    print()
    
    # 总结
    print("=" * 60)
    all_passed = all(
        status == "✅" or status == "⚠️" 
        for status, _, _ in version_results + import_results + project_results
    )
    
    if all_passed:
        print("✅ 兼容性测试通过！项目已适配 LangChain 1.0.0+")
    else:
        print("❌ 兼容性测试失败，请检查上述错误并修复")
        sys.exit(1)

if __name__ == "__main__":
    main()

