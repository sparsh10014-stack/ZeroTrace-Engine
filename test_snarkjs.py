# subprocess Python ka built-in module hai.
# Iska use karke hum Python se external commands/programs chala sakte hain.
import subprocess


# SnarkJS verification command ko Python se execute kar rahe hain.
result = subprocess.run(
    [
        # Windows par npx ko execute karne ke liye npx.cmd use kar rahe hain.
        "npx.cmd",

        # SnarkJS tool
        "snarkjs",

        # Hum Groth16 proving system use kar rahe hain.
        "groth16",

        # Proof ko verify karna hai.
        "verify",

        # Verification key
        "verification_key.json",

        # Public signals
        "public.json",

        # ZK proof
        "proof.json"
    ],

    # SnarkJS ka output Python ke paas capture hoga.
    capture_output=True,

    # Output ko readable string ke form me rakho.
    text=True
)


# SnarkJS ka normal output print karo.
print("========== STDOUT ==========")
print(result.stdout)


# Agar koi error hua to stderr me output milega.
print("========== STDERR ==========")
print(result.stderr)


# Command ka return code print karo.
print("========== RETURN CODE ==========")
print(result.returncode)