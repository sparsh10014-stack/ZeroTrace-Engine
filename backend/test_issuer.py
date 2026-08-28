from services.issuer_service import (
    create_credential,
    verify_credential
)


# =========================================================
# CREATE CREDENTIAL
# =========================================================

credential = create_credential(
    document_id="DEMO-ID-001",
    name="Test User",
    date_of_birth="2000-01-01"
)


print("\n========== GENERATED CREDENTIAL ==========")

print(credential)


# =========================================================
# VERIFY CREDENTIAL
# =========================================================

result = verify_credential(
    credential
)


print("\n========== VERIFICATION RESULT ==========")

print(result)