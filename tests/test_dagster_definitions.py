from dagster_project.definitions import defs


def test_dagster_definitions_include_bronze_saas_asset() -> None:
    asset_keys = {asset.key.to_user_string() for asset in defs.assets or []}

    assert "bronze_saas_source_tables" in asset_keys
