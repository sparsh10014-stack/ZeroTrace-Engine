// ZeroTrace-Engine/backend/issuer_signer.js
const { buildEddsa, buildPoseidon, buildBabyjub } = require("circomlibjs");
const crypto = require("crypto");

let eddsa, poseidon, babyJub;

async function initCrypto() {
    eddsa = await buildEddsa();
    poseidon = await buildPoseidon();
    babyJub = await buildBabyjub();
}

// Government Private Key (stored on mock server)
const ISSUER_PRIVATE_KEY = crypto.createHash('sha256').update("Mock_DigiLocker_Secret_Key_2026").digest();

async function generateSignedCredential(idHash, dobYear, expiryTimestamp, isActive) {
    if (!eddsa) await initCrypto();

    // 1. Derive Public Key Coordinates [Ax, Ay]
    const pubKey = eddsa.prv2pub(ISSUER_PRIVATE_KEY);
    const pubKeyFormatted = [
        babyJub.F.toString(pubKey[0]),
        babyJub.F.toString(pubKey[1])
    ];

    // 2. Hash payload fields into a field element using Poseidon
    const payload = [
        BigInt(idHash),
        BigInt(dobYear),
        BigInt(expiryTimestamp),
        BigInt(isActive)
    ];
    const messageHash = poseidon(payload);

    // 3. Generate EdDSA Signature over Poseidon Hash
    const signature = eddsa.signPoseidon(ISSUER_PRIVATE_KEY, messageHash);

    // 4. Return complete signed credential JSON
    return {
        issuer_pubkey: pubKeyFormatted,
        credential_data: {
            id_hash: idHash.toString(),
            dob_year: Number(dobYear),
            expiry: Number(expiryTimestamp),
            is_active: Number(isActive)
        },
        signature: {
            R8: [
                babyJub.F.toString(signature.R8[0]),
                babyJub.F.toString(signature.R8[1])
            ],
            S: signature.S.toString()
        }
    };
}

module.exports = { generateSignedCredential };