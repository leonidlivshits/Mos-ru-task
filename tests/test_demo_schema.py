from app.schemas.demo import DemoFoundItem


def test_demo_found_item_schema_hides_internal_fields() -> None:
    properties = DemoFoundItem.model_json_schema()["properties"]

    assert "description" not in properties
    assert "private_features" not in properties
