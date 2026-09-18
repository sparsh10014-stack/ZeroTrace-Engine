import json
from pathlib import Path


# Ages used for testing.
# Some are valid for an 18+ verification,
# and some are intentionally invalid.
test_ages = [
    22,
    25,
    19,
    30,
    18,
    17,
    15,
    16,
    14,
    21
]


def generate_mock_users():
    """Generate fake users for testing the age verification system."""

    mock_users = []

    for number, age in enumerate(test_ages, start=1):

        if age >= 18:
            expected_status = "PASS"
        else:
            expected_status = "FAIL"

        user = {
            "mock_id": f"MOCK-{number:03d}",
            "age": age,
            "expected_status": expected_status
        }

        mock_users.append(user)

    return mock_users


def save_mock_users(mock_users):
    """Save mock users to a JSON file."""

    output_path = Path(__file__).resolve().parent / "mock_users.json"

    with open(output_path, "w") as file:
        json.dump(mock_users, file, indent=4)

    print(f"Mock users saved to: {output_path}")


if __name__ == "__main__":
    users = generate_mock_users()

    save_mock_users(users)

    print("\nGenerated mock users:")

    for user in users:
        print(
            f"{user['mock_id']} | "
            f"Age: {user['age']} | "
            f"Expected: {user['expected_status']}"
        )