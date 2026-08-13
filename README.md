# ZeroTrace Engine

ZeroTrace Engine is a Zero-Knowledge Proof (ZKP) verification backend.

The project uses **Circom**, **SnarkJS**, and **Flask** to verify Groth16 Zero-Knowledge Proofs.

The main purpose of the project is to allow a frontend/client to send a ZKP proof and its public signals to a backend verifier without revealing the underlying private information.

---

## 🚀 Current Architecture

```text
Frontend / Client
       |
       | POST /verify
       | proof + publicSignals
       ↓
   Flask Backend
       |
       ↓
 Temporary JSON Files
       |
       ↓
     SnarkJS
       |
       ↓
 Groth16 Verification
       |
       ↓
 Valid / Invalid Response