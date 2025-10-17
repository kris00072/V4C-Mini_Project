import project_manager as pm


def test_validate_status_and_role():
    assert pm.validate_status("Planning") is True
    assert pm.validate_status("Invalid") is False
    assert pm.validate_role("Dev") is True
    assert pm.validate_role("") is False


def test_validate_date_rules():
    assert pm.validate_date("2024-01-01") is True
    assert pm.validate_date("01/01/2024") is False


