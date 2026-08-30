// ============================================================
// ZeroTrace Engine - Frontend
// Full Flow:
//
// OCR
//   ↓
// Government DB / Mock Issuer
//   ↓
// Signed Credential
//   ↓
// Local Credential Signature Verification
//   ↓
// ZKP Generation
//   ↓
// Local ZKP Verification
//   ↓
// Flask Verifier
// ============================================================


// ============================================================
// BACKEND
// ============================================================

const API_BASE = "http://127.0.0.1:5000";


// ============================================================
// TAB SWITCHING
// ============================================================

function switchTab(tab) {

    const userScreen = document.getElementById("screen-user");
    const verifierScreen = document.getElementById("screen-verifier");

    const btnUser = document.getElementById("btn-user");
    const btnVerifier = document.getElementById("btn-verifier");

    if (tab === "user") {

        userScreen.classList.remove("hidden");
        verifierScreen.classList.add("hidden");

        btnUser.className =
            "px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-semibold transition";

        btnVerifier.className =
            "px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm font-semibold transition";

    } else {

        userScreen.classList.add("hidden");
        verifierScreen.classList.remove("hidden");

        btnUser.className =
            "px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm font-semibold transition";

        btnVerifier.className =
            "px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-semibold transition";
    }
}


// ============================================================
// PIPELINE DASHBOARD
// ============================================================

function updateStage(stage, status) {

    const element = document.getElementById(`stage-${stage}`);

    if (!element) return;

    const labels = {
        ocr: "🔍 OCR",
        issuer: "🪪 Issuer",
        credential: "🔏 Credential",
        proof: "🔐 Proof",
        verify: "✅ Verify"
    };

    if (status === "processing") {

        element.className =
            "stage p-4 rounded-lg bg-blue-500/10 border border-blue-500 text-blue-400 transition";

        element.innerText =
            `${labels[stage]} — Processing...`;

    } else if (status === "success") {

        element.className =
            "stage p-4 rounded-lg bg-emerald-500/10 border border-emerald-500 text-emerald-400 transition";

        element.innerText =
            `${labels[stage]} — ✓ Completed`;

    } else if (status === "failed") {

        element.className =
            "stage p-4 rounded-lg bg-rose-500/10 border border-rose-500 text-rose-400 transition";

        element.innerText =
            `${labels[stage]} — ✗ Failed`;

    } else {

        element.className =
            "stage p-4 rounded-lg bg-slate-900 border border-slate-700 transition";

        element.innerText =
            `${labels[stage]} — Waiting`;
    }
}


// ============================================================
// STATUS UI
// ============================================================

function setStatus(message) {

    const spinner = document.getElementById("loading-spinner");
    const spinnerText = document.getElementById("spinner-text");

    spinner.classList.remove("hidden");
    spinner.style.display = "block";

    spinnerText.innerText = message;
}


function hideStatus() {

    const spinner = document.getElementById("loading-spinner");

    spinner.classList.add("hidden");
    spinner.style.display = "none";
}


// ============================================================
// RESULT UI
// ============================================================

function showResult(message, success = false) {

    const badge = document.getElementById("result-badge");

    badge.className = success
        ? "mt-6 p-5 rounded-xl bg-emerald-500/10 border border-emerald-500 text-emerald-400 text-center shadow-lg"
        : "mt-6 p-5 rounded-xl bg-rose-500/10 border border-rose-500 text-rose-400 text-center shadow-lg";

    badge.classList.remove("hidden");
    badge.style.display = "block";

    badge.innerHTML = `
        <div class="text-3xl mb-2">
            ${success ? "✅" : "❌"}
        </div>

        <div class="font-bold text-xl">
            ${success ? "VERIFIED: AGE ≥ 18" : "REJECTED"}
        </div>

        <div class="text-sm mt-2">
            ${message}
        </div>
    `;
}


// ============================================================
// OCR → CITIZEN ID EXTRACTION
// ============================================================

function extractCitizenId(ocrText) {

    if (!ocrText) {
        return null;
    }

    // ========================================================
    // NORMALIZE OCR TEXT
    // ========================================================

    let normalized = ocrText
        .toUpperCase()
        .replace(/\r?\n/g, " ")
        .replace(/\s+/g, " ")
        .trim();


    // ========================================================
    // HANDLE COMMON OCR MISTAKES
    // ========================================================
    //
    // Tesseract may read:
    //
    // CITIZEN012  → correct
    // CITIZEN 012 → correct
    // CITIZEN-012 → correct
    // CITIZENO12  → O instead of 0
    // CITIZEN O12  → O instead of 0
    //
    // We correct O → 0 only when it appears immediately
    // after the word CITIZEN.
    // ========================================================

    normalized = normalized.replace(
        /CITIZEN\s*[-_]?\s*O(?=\d)/g,
        "CITIZEN0"
    );


    // ========================================================
    // MOCK CITIZEN ID
    // ========================================================
    //
    // Expected format:
    //
    // CITIZEN001
    // CITIZEN002
    // ...
    // CITIZEN020
    //
    // Supports:
    // CITIZEN012
    // CITIZEN 012
    // CITIZEN-012
    // CITIZEN_012
    // ========================================================

    const citizenMatch = normalized.match(
        /\bCITIZEN\s*[-_]?\s*(\d{3,})\b/
    );

    if (citizenMatch) {

        const number = citizenMatch[1];

        return `CITIZEN${number}`;
    }


    // ========================================================
    // SUPPORT 12-DIGIT GOVERNMENT ID FORMAT
    // ========================================================
    //
    // Example:
    //
    // 1234 5678 9012
    // 123456789012
    // ========================================================

    const aadhaarMatch = normalized.match(
        /\b\d{4}\s*\d{4}\s*\d{4}\b/
    );

    if (aadhaarMatch) {

        return aadhaarMatch[0].replace(/\D/g, "");
    }


    // ========================================================
    // FALLBACK — SEARCH ANY 12 DIGIT NUMBER
    // ========================================================

    const digitsOnly = normalized.replace(/\D/g, "");

    const twelveDigitMatch = digitsOnly.match(/\d{12}/);

    if (twelveDigitMatch) {

        return twelveDigitMatch[0];
    }


    // ========================================================
    // ID NOT FOUND
    // ========================================================

    return null;
}


// ============================================================
// VERIFY SIGNED CREDENTIAL LOCALLY
// ============================================================

async function verifyDigiLockerCredential(credential) {

    if (typeof circomlibjs === "undefined") {

        throw new Error(
            "Cryptography library is not loaded."
        );
    }


    if (!credential || !credential.credential_data) {

        throw new Error(
            "Invalid credential received from issuer."
        );
    }


    const data = credential.credential_data;


    // --------------------------------------------------------
    // REVOCATION
    // --------------------------------------------------------

    if (
        data.is_active !== 1 &&
        data.is_active !== true
    ) {

        throw new Error(
            "CREDENTIAL REVOKED: This ID has been invalidated by the issuer."
        );
    }


    // --------------------------------------------------------
    // EXPIRY
    // --------------------------------------------------------

    if (data.expiry) {

        const currentUnixTime =
            Math.floor(Date.now() / 1000);

        if (
            Number(data.expiry) < currentUnixTime
        ) {

            throw new Error(
                "CREDENTIAL EXPIRED: Issued credential has expired."
            );
        }
    }


    // --------------------------------------------------------
    // REQUIRED CRYPTOGRAPHIC DATA
    // --------------------------------------------------------

    if (
        !credential.issuer_pubkey ||
        !credential.signature
    ) {

        throw new Error(
            "Credential cryptographic data is missing."
        );
    }


    try {

        const eddsa =
            await circomlibjs.buildEddsa();

        const poseidon =
            await circomlibjs.buildPoseidon();

        const babyJub =
            await circomlibjs.buildBabyjub();


        // ----------------------------------------------------
        // RECREATE SIGNED MESSAGE HASH
        // ----------------------------------------------------

        const payload = [

            BigInt(data.id_hash),

            BigInt(data.dob_year),

            BigInt(data.expiry),

            BigInt(data.is_active)
        ];


        const messageHash =
            poseidon(payload);


        // ----------------------------------------------------
        // PUBLIC KEY
        // ----------------------------------------------------

        const pubKey = [

            babyJub.F.e(
                credential.issuer_pubkey[0]
            ),

            babyJub.F.e(
                credential.issuer_pubkey[1]
            )
        ];


        // ----------------------------------------------------
        // SIGNATURE
        // ----------------------------------------------------

        const signature = {

            R8: [

                babyJub.F.e(
                    credential.signature.R8[0]
                ),

                babyJub.F.e(
                    credential.signature.R8[1]
                )
            ],

            S: BigInt(
                credential.signature.S
            )
        };


        // ----------------------------------------------------
        // VERIFY SIGNATURE
        // ----------------------------------------------------

        const isValid =
            eddsa.verifyPoseidon(
                messageHash,
                signature,
                pubKey
            );


        if (!isValid) {

            throw new Error(
                "FORGERY DETECTED: Invalid issuer signature."
            );
        }


        return Number(data.dob_year);

    } catch (error) {

        if (
            error.message &&
            (
                error.message.includes("FORGERY") ||
                error.message.includes("CREDENTIAL")
            )
        ) {
            throw error;
        }

        console.error(
            "Credential verification error:",
            error
        );

        throw new Error(
            "Unable to cryptographically verify the issued credential."
        );
    }
}


// ============================================================
// MAIN VERIFICATION FLOW
// ============================================================

async function handleVerification(event) {

    if (event) {

        event.preventDefault();
        event.stopPropagation();
    }


    const fileInput =
        document.getElementById("id-document");

    const submitBtn =
        document.getElementById("submit-btn");

    const badge =
        document.getElementById("result-badge");

    const verifierStatus =
        document.getElementById("verifier-status");


    badge.classList.add("hidden");
    badge.style.display = "none";


    if (verifierStatus) {

        verifierStatus.classList.add("hidden");
        verifierStatus.style.display = "none";
    }


    submitBtn.disabled = true;
    submitBtn.classList.add("opacity-50");


    // Reset dashboard

    updateStage("ocr", "waiting");
    updateStage("issuer", "waiting");
    updateStage("credential", "waiting");
    updateStage("proof", "waiting");
    updateStage("verify", "waiting");


    try {

        // ====================================================
        // STEP 1 — FILE CHECK
        // ====================================================

        if (
            !fileInput.files ||
            fileInput.files.length === 0
        ) {

            throw new Error(
                "Please upload a government ID document."
            );
        }


        // ====================================================
        // STEP 2 — LOCAL OCR
        // ====================================================

        updateStage("ocr", "processing");

        setStatus(
            "Scanning ID locally in your browser..."
        );


        let file =
            fileInput.files[0];


        let ocrText;


        try {

            const result =
                await Tesseract.recognize(
                    file,
                    "eng"
                );

            ocrText =
                result.data.text;


            console.log(
                "OCR extracted text:",
                ocrText
            );

        } catch (ocrError) {

            console.error(
                "OCR error:",
                ocrError
            );

            updateStage("ocr", "failed");

            throw new Error(
                "OCR failed. Please upload a clearer document."
            );
        }


        // Delete browser reference

        file = null;
        fileInput.value = "";


        // ====================================================
        // STEP 3 — EXTRACT CITIZEN ID
        // ====================================================

        const citizenId =
            extractCitizenId(ocrText);


        console.log(
            "Extracted Citizen ID:",
            citizenId
        );


        if (!citizenId) {

            updateStage("ocr", "failed");

            throw new Error(
                "OCR could not detect a valid citizen ID."
            );
        }


        updateStage("ocr", "success");


        // ====================================================
        // STEP 4 — ISSUE SIGNED CREDENTIAL
        // ====================================================

        updateStage("issuer", "processing");

        setStatus(
            "Checking government database and issuing credential..."
        );


        let credentialResponse;


        try {

            credentialResponse =
                await fetch(
                    `${API_BASE}/api/issue-credential`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            ocr_id_hash:
                                citizenId
                        })
                    }
                );

        } catch (networkError) {

            updateStage("issuer", "failed");

            throw new Error(
                "Unable to connect to the credential issuer."
            );
        }


        let credentialData = {};


        try {

            credentialData =
                await credentialResponse.json();

        } catch (jsonError) {

            throw new Error(
                "Issuer returned an invalid response."
            );
        }


        if (!credentialResponse.ok) {

            updateStage("issuer", "failed");


            if (
                credentialResponse.status === 404
            ) {

                throw new Error(
                    "ID not found in the government database."
                );
            }


            if (
                credentialResponse.status === 403
            ) {

                throw new Error(
                    "This ID has been revoked and cannot be used."
                );
            }


            throw new Error(
                credentialData.message ||
                credentialData.error ||
                "Credential could not be issued."
            );
        }


        updateStage("issuer", "success");


        console.log(
            "Signed credential received:",
            credentialData
        );


        // ====================================================
        // STEP 5 — VERIFY ISSUER SIGNATURE
        // ====================================================

        updateStage("credential", "processing");

        setStatus(
            "Verifying issuer signature locally..."
        );


        const trustedBirthYear =
            await verifyDigiLockerCredential(
                credentialData
            );


        updateStage("credential", "success");


        console.log(
            "Trusted birth year:",
            trustedBirthYear
        );


        // ====================================================
        // STEP 6 — GENERATE ZKP
        // ====================================================

        updateStage("proof", "processing");

        setStatus(
            "Generating Zero-Knowledge Proof locally..."
        );


        if (
            typeof snarkjs === "undefined"
        ) {

            throw new Error(
                "SnarkJS is not loaded. Check your internet connection."
            );
        }


        const currentYear =
            new Date().getFullYear();


        const ageThreshold = 18;


        const circuitInputs = {

            current_year:
                currentYear,

            birth_year:
                trustedBirthYear,

            age_threshold:
                ageThreshold
        };


        console.log(
            "Generating ZKP with trusted credential data..."
        );


        const {

            proof,

            publicSignals

        } = await snarkjs.groth16.fullProve(

            circuitInputs,

            "Public/age_check.wasm",

            "Public/age_check_final.zkey"
        );


        console.log(
            "ZKP generated:",
            proof
        );

        console.log(
            "Public signals:",
            publicSignals
        );


        updateStage(
            "proof",
            "success"
        );


        // ====================================================
        // STEP 7 — LOCAL ZKP VERIFICATION
        // ====================================================

        setStatus(
            "Verifying Zero-Knowledge Proof..."
        );


        let localVerified = false;


        try {

            const vKeyResponse =
                await fetch(
                    "Public/verification_key.json"
                );


            if (!vKeyResponse.ok) {

                throw new Error(
                    "Verification key unavailable."
                );
            }


            const verificationKey =
                await vKeyResponse.json();


            localVerified =
                await snarkjs.groth16.verify(

                    verificationKey,

                    publicSignals,

                    proof
                );


        } catch (localError) {

            console.error(
                "Local ZKP verification error:",
                localError
            );

            localVerified = false;
        }


        if (!localVerified) {

            updateStage(
                "verify",
                "failed"
            );

            throw new Error(
                "Zero-Knowledge Proof could not be verified."
            );
        }


        // ====================================================
        // STEP 8 — SEND PROOF TO FLASK
        // ====================================================

        updateStage(
            "verify",
            "processing"
        );


        setStatus(
            "Sending proof to verifier..."
        );


        let backendVerified =
            false;

        let backendMessage =
            "";


        try {

            const response =
                await fetch(
                    `${API_BASE}/verify`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({

                            proof:
                                proof,

                            publicSignals:
                                publicSignals
                        })
                    }
                );


            const verifierData =
                await response.json();


            if (
                response.ok &&
                (
                    verifierData.valid === true ||
                    verifierData.status === "success"
                )
            ) {

                backendVerified = true;

                backendMessage =
                    verifierData.message ||
                    "Proof verified successfully by Verifier Node.";

            } else {

                backendMessage =
                    verifierData.message ||
                    "Verifier rejected the proof.";
            }


        } catch (backendError) {

            console.warn(
                "Backend verifier unavailable:",
                backendError
            );

            backendMessage =
                "Proof verified locally in browser. Verifier server unavailable.";
        }


        // ====================================================
        // STEP 9 — FINAL RESULT
        // ====================================================

        if (
            localVerified &&
            (
                backendVerified ||
                backendMessage.includes("unavailable")
            )
        ) {

            updateStage(
                "verify",
                "success"
            );


            showResult(

                "Age requirement satisfied. Your birth year and personal identity remain private.",

                true
            );


            if (verifierStatus) {

                verifierStatus.className =
                    "mt-6 p-5 rounded-xl bg-emerald-500/10 border border-emerald-500 text-emerald-400 text-center";


                verifierStatus.classList.remove(
                    "hidden"
                );


                verifierStatus.style.display =
                    "block";


                verifierStatus.innerHTML = `

                    <div class="text-3xl mb-2">
                        🛡️
                    </div>

                    <div class="font-bold text-lg">
                        VERIFIED: AGE ≥ 18
                    </div>

                    <div class="text-sm mt-2">
                        Zero-Knowledge Proof is valid.
                    </div>

                    <div class="text-xs mt-2 text-emerald-300">
                        Exact birth year and personal identity were not exposed.
                    </div>

                `;
            }


            console.log(
                "ZEROTrace verification completed successfully."
            );


        } else {

            updateStage(
                "verify",
                "failed"
            );


            throw new Error(
                backendMessage ||
                "Verification failed."
            );
        }


    } catch (error) {

        console.error(
            "Verification error:",
            error
        );


        showResult(

            error.message ||
            "Verification failed."

        );


    } finally {

        submitBtn.disabled = false;

        submitBtn.classList.remove(
            "opacity-50"
        );

        hideStatus();
    }
}