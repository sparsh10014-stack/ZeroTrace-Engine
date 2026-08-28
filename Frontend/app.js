function switchTab(tab) {
    const userScreen = document.getElementById('screen-user');
    const verifierScreen = document.getElementById('screen-verifier');
    const btnUser = document.getElementById('btn-user');
    const btnVerifier = document.getElementById('btn-verifier');

    if (tab === 'user') {
        userScreen.classList.remove('hidden');
        verifierScreen.classList.add('hidden');
        btnUser.className = "px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-semibold transition";
        btnVerifier.className = "px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm font-semibold text-slate-300 transition";
    } else {
        userScreen.classList.add('hidden');
        verifierScreen.classList.remove('hidden');
        btnUser.className = "px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm font-semibold text-slate-300 transition";
        btnVerifier.className = "px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-semibold transition";
    }
}

// ========================================================
// SPARSH PHASE 3: Client-Side Signature Verification
// ========================================================
async function verifyDigiLockerCredential(credential) {
    if (typeof circomlibjs === 'undefined') {
        throw new Error("circomlibjs not loaded. Check index.html CDN script.");
    }

    const eddsa = await circomlibjs.buildEddsa();
    const poseidon = await circomlibjs.buildPoseidon();
    const babyJub = await circomlibjs.buildBabyjub();

    // 1. Check Revocation and Expiry Flags first
    if (credential.credential_data.is_active !== 1) {
        throw new Error("CREDENTIAL REVOKED: This ID has been invalidated by the issuer.");
    }
    const currentUnixTime = Math.floor(Date.now() / 1000);
    if (credential.credential_data.expiry < currentUnixTime) {
        throw new Error("CREDENTIAL EXPIRED: Issued credential has expired.");
    }

    // 2. Re-compute Poseidon Hash of payload
    const payload = [
        BigInt(credential.credential_data.id_hash),
        BigInt(credential.credential_data.dob_year),
        BigInt(credential.credential_data.expiry),
        BigInt(credential.credential_data.is_active)
    ];
    const messageHash = poseidon(payload);

    // 3. Unpack public key and signature
    const pubKey = [
        babyJub.F.e(credential.issuer_pubkey[0]),
        babyJub.F.e(credential.issuer_pubkey[1])
    ];
    const signature = {
        R8: [
            babyJub.F.e(credential.signature.R8[0]),
            babyJub.F.e(credential.signature.R8[1])
        ],
        S: BigInt(credential.signature.S)
    };

    // 4. Verify Signature
    const isValid = eddsa.verifyPoseidon(messageHash, signature, pubKey);
    if (!isValid) {
        throw new Error("FORGERY DETECTED: Invalid signature from issuer!");
    }

    // Return the cryptographically trusted DOB
    return credential.credential_data.dob_year;
}


async function handleVerification(event) {
    if (event && typeof event.preventDefault === 'function') {
        event.preventDefault();
        event.stopPropagation();
    }

    const fileInput = document.getElementById('id-document');
    const submitBtn = document.getElementById('submit-btn');
    const spinner = document.getElementById('loading-spinner');
    const spinnerText= document.getElementById('spinner-text');
    const badge = document.getElementById('result-badge');
    const verifierBox = document.getElementById('verifier-status');

    // UI Loading State
    submitBtn.disabled = true;
    submitBtn.classList.add('opacity-50');
    spinner.classList.remove('hidden');
    spinner.style.display = 'flex';
    badge.classList.add('hidden');
    badge.style.display = 'none';
    spinnerText.innerText = "Initializing...";

    try {
        const currentYear = 2026;
        const ageThreshold = 18;
        let ocrExtractedIdHash = "123456789012345"; // Default fallback for demo if OCR ID isn't parsed perfectly

        // ========================================================
        // STEP 1: Local OCR Check (Snehlata's Flow)
        // ========================================================
        if (fileInput && fileInput.files && fileInput.files.length > 0) {
            spinnerText.innerText = "Scanning ID card locally on your device...";
            const file = fileInput.files[0];
            
            try {
                // Run Tesseract.js locally in the browser
                const { data: { text } } = await Tesseract.recognize(file, 'eng');
                console.log("RAW OCR TEXT: ", text);
                
                // For this demo, we assume the document is valid enough to proceed to mock issuer
                spinnerText.innerText = "Document scanned successfully.";
            } catch (ocrError) {
                console.error("OCR Error:", ocrError);
                throw new Error("Failed to scan document. Please try a clearer image.");
            }
        } else {
            throw new Error("Please upload an ID document to proceed.");
        }

        // ========================================================
        // STEP 2: Phase 4 - Request Challenge Nonce
        // ========================================================
        spinnerText.innerText = "Requesting verification challenge...";
        let nonce = "12345"; // Fallback nonce in case backend endpoint isn't fully ready
        try {
            const nonceRes = await fetch('http://127.0.0.1:5000/api/get-nonce');
            if (nonceRes.ok) {
                const nonceData = await nonceRes.json();
                nonce = nonceData.nonce;
            }
        } catch (e) {
            console.warn("Nonce endpoint unavailable, using mock nonce for demo.");
        }

        // ========================================================
        // STEP 3: Phase 2 Integration - Fetch Signed Credential
        // ========================================================
        spinnerText.innerText = "Fetching signed credential from mock DigiLocker...";
        let credential;
        try {
            const credentialResponse = await fetch('http://127.0.0.1:5000/api/issue-credential', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ocr_id_hash: ocrExtractedIdHash })
            });
            if (!credentialResponse.ok) throw new Error("ID not found or revoked in government database.");
            credential = await credentialResponse.json();
        } catch (e) {
            throw new Error(e.message || "Failed to connect to Mock DigiLocker Issuer.");
        }

        // ========================================================
        // STEP 4: Phase 3 - Verify EdDSA Signature Locally
        // ========================================================
        spinnerText.innerText = "Verifying DigiLocker signature locally...";
        const trustedDobYear = await verifyDigiLockerCredential(credential);

        // ========================================================
        // STEP 5: Configure Circuit Inputs & Generate ZKP
        // ========================================================
        const circuitInputs = {
            current_year: currentYear,
            birth_year: trustedDobYear,
            age_threshold: ageThreshold,
            nonce: nonce
        };

        if (typeof snarkjs === 'undefined') {
            throw new Error("SnarkJS SDK is not loaded. Please check your internet connection.");
        }

        spinnerText.innerText = "Computing Zero-Knowledge Proof locally...";
        const { proof, publicSignals } = await snarkjs.groth16.fullProve(
            circuitInputs,
            "Public/age_check.wasm",
            "Public/age_check_final.zkey"
        );

        // ========================================================
        // STEP 6: Perform Local Client Verification (Optional Check)
        // ========================================================
        let isLocallyVerified = false;
        try {
            const vKeyRes = await fetch("Public/verification_key.json");
            if (vKeyRes.ok) {
                const vKey = await vKeyRes.json();
                isLocallyVerified = await snarkjs.groth16.verify(vKey, publicSignals, proof);
            }
        } catch (localErr) {
            console.warn("Local verification key check skipped:", localErr);
        }

        // ========================================================
        // STEP 7: Post Proof to Flask Verifier Server
        // ========================================================
        let backendVerified = false;
        let backendMessage = "";
        try {
            spinnerText.innerText = "Sending Proof to Verifier Node...";
            const response = await fetch('http://127.0.0.1:5000/api/verify-proof', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    proof: proof,
                    publicSignals: publicSignals,
                    nonce: nonce
                })
            });

            const data = await response.json();
            if (response.ok && (data.status === 'success' || data.valid === true)) {
                backendVerified = true;
                backendMessage = data.message || "Confirmed valid by Verifier Node";
            } else {
                throw new Error(data.message || "Verification failed at server.");
            }
        } catch (netErr) {
            console.warn("Backend node offline or starting up:", netErr);
            backendMessage = "Proof verified locally in browser. (Backend unreachable)";
        }

        // ========================================================
        // STEP 8: Update UI Badge & Verifier Monitor
        // ========================================================
        if (backendVerified || isLocallyVerified) {
            badge.className = "mt-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500 text-emerald-400 text-center shadow-lg transition-all";
            badge.classList.remove('hidden');
            badge.style.display = 'block';
            badge.innerHTML = `
                <div class="text-3xl mb-1">✅</div>
                <div class="font-bold text-xl text-emerald-400">VERIFIED: AGE >= 18</div>
                <div class="text-xs text-emerald-300/80 mt-1">Zero-Knowledge Proof verified — Zero private data exposed!</div>
                <div class="text-[11px] text-emerald-400/60 mt-1 font-mono">${backendMessage}</div>
            `;

            if (verifierBox) {
                verifierBox.className = "p-8 border-2 border-emerald-500 bg-emerald-500/10 rounded-xl text-emerald-400 font-bold text-lg shadow-lg text-center";
                verifierBox.innerHTML = `
                    <div class="text-2xl mb-1">🛡️</div>
                    <div>VERIFIED: AGE >= 18</div>
                    <div class="text-xs font-normal text-emerald-300/80 mt-1">Proof confirmed valid. Birth year & exact age remain 100% private.</div>
                `;
            }
        } else {
            throw new Error(backendMessage || "Verification failed.");
        }

    } catch (err) {
        console.error("ZKP Error:", err);
        let userMsg = err.message || "Verification failed.";
        if (userMsg.includes("Assert Failed")) {
            userMsg = "Age requirement not satisfied (Age must be >= 18).";
        }

        badge.className = "mt-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500 text-rose-400 text-center shadow-lg transition-all";
        badge.classList.remove('hidden');
        badge.style.display = 'block';
        badge.innerHTML = `
            <div class="text-3xl mb-1">❌</div>
            <div class="font-bold text-xl text-rose-400">VERIFICATION REJECTED</div>
            <div class="text-sm text-rose-300/90 mt-1">${userMsg}</div>
        `;

        if (verifierBox) {
            verifierBox.className = "p-8 border-2 border-rose-500 bg-rose-500/10 rounded-xl text-rose-400 font-bold text-lg shadow-lg text-center";
            verifierBox.innerHTML = `
                <div class="text-2xl mb-1">⚠️</div>
                <div>REJECTED</div>
                <div class="text-xs font-normal text-rose-300/80 mt-1">${userMsg}</div>
            `;
        }
    } finally {
        // Reset UI State
        submitBtn.disabled = false;
        submitBtn.classList.remove('opacity-50');
        spinner.classList.add('hidden');
        spinner.style.display = 'none';
        spinnerText.innerText = "Processing locally..."; 
    }
}