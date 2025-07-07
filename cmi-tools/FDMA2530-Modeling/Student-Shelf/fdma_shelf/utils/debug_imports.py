def debug_module_imports():
    """Debug utility to check module import status"""
    print("=== FDMA 2530 Module Import Debug ===")
    import traceback

    # Test root package
    try:
        import fdma_shelf
        print(f"✓ fdma_shelf imported successfully (v{fdma_shelf.__version__})")
    except Exception as e:
        print(f"✗ fdma_shelf import failed: {e}")
        traceback.print_exc()
        return

    # Test tools package
    try:
        import fdma_shelf.tools
        print("✓ fdma_shelf.tools imported successfully")
        tools = fdma_shelf.tools.get_available_tools()
        print(f"  Available tools: {tools}")
    except Exception as e:
        print(f"✗ fdma_shelf.tools import failed: {e}")
        traceback.print_exc()

    # Test checklist
    try:
        import fdma_shelf.tools.checklist as checklist
        print(f"✓ checklist imported successfully (v{checklist.__version__})")
    except Exception as e:
        print(f"✗ checklist import failed: {e}")
        traceback.print_exc()

    # Test updater
    try:
        import fdma_shelf.utils.updater as updater
        print("✓ updater imported successfully")
    except Exception as e:
        print(f"✗ updater import failed: {e}")
        traceback.print_exc()
