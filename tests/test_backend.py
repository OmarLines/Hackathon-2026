from app.backend import AwsBackend


def test_aws_backend_update_referral_status_updates_referrals_table():
    backend = AwsBackend.__new__(AwsBackend)
    captured: dict[str, object] = {}

    class FakeReferralsTable:
        def update_item(self, **kwargs):
            captured.update(kwargs)

    backend.referrals_table = FakeReferralsTable()
    backend.get_referral = lambda ref_number: {  # type: ignore[method-assign]
        "pk": "USER#user-123",
        "sk": f"REFERRAL#{ref_number}",
    }

    backend.update_referral_status("TEST1234", "accepted")

    assert captured["Key"] == {
        "pk": "USER#user-123",
        "sk": "REFERRAL#TEST1234",
    }
    assert captured["UpdateExpression"] == "SET #s = :s"
    assert captured["ExpressionAttributeNames"] == {"#s": "status"}
    assert captured["ExpressionAttributeValues"] == {":s": "accepted"}
