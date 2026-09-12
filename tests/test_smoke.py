from app.agent.tools import SupportTools
from app.data_loader import discover_assets
from app.config import settings


def test_tools_start_empty():
    tools = SupportTools()
    result = tools.search_documents('where is my parcel')
    assert result.ok
    assert result.data == []


def test_asset_discovery_is_safe_without_data():
    result = discover_assets(settings.data_dir, settings.knowledge_dir)
    assert 'workbooks' in result
    assert 'pdfs' in result
