from todo_mcp import mcp, mcp_tools
from todo_mcp.storage import FileStorage


def test_export_html(tmp_path):
    storage_file = tmp_path / "tasks.json"
    mcp_tools._storage = FileStorage(storage_file)

    # create two tasks via tools
    mcp.call_tool("create_task", {"task_id": "t1", "title": "First"})
    mcp.call_tool("create_task", {"task_id": "t2", "title": "Second"})

    outpath = tmp_path / "out.html"
    # tool should write file and return path
    res = mcp.call_tool("export_html", {"path": str(outpath)})
    assert str(outpath) == res.get("path")
    assert outpath.exists()
    content = outpath.read_text()
    assert "First" in content and "Second" in content
    assert "<script" in content
