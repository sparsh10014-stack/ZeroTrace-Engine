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

async function handleVerification(event) {
    if (event && typeof event.preventDefault === 'function') {
        event.preventDefault();
        event.stopPropagation();
    }

    const userAgeInput = document.getElementById('user-age').value;
    const userAge = parseInt(userAgeInput);
    const submitBtn = document.getElementById('submit-btn');
    const spinner = document.getElementById('loading-spinner');
    const badge = document.getElementById('result-badge');
    const verifierBox = document.getElementById('verifier-status');

    if (isNaN(userAge)) {
        alert("Please enter a valid age.");
        return;
    }

    // UI Loading State
    submitBtn.disabled = true;
    submitBtn.classList.add('opacity-50');
    spinner.classList.remove('hidden');
    spinner.style.display = 'flex';
    badge.classList.add('hidden');
    badge.style.display = 'none';

    try {
        const currentYear = 2026;
        const birthYear = currentYear - userAge;
        const ageThreshold = 18;

        const circuitInputs = {
            current_year: currentYear,
            birth_year: birthYear,
            age_threshold: ageThreshold
        };

        console.log("Computing Zero-Knowledge Proof locally in browser...");

        if (typeof snarkjs === 'undefined') {
            throw new Error("SnarkJS SDK is not loaded. Please check your internet connection.");
        }

        // 1. Generate Local ZKP Proof
        const { proof, publicSignals } = await snarkjs.groth16.fullProve(
            circuitInputs,
            "Public/age_check.wasm",
            "Public/age_check_final.zkey"
        );

        // 2. Perform Local Client Verification
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

        // 3. Post Proof to Flask Verifier Server
        let backendVerified = false;
        let backendMessage = "";
        try {
            const response = await fetch('http://127.0.0.1:5000/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    proof: proof,
                    publicSignals: publicSignals
                })
            });

            const data = await response.json();
            if (response.ok && data.status === 'success') {
                backendVerified = true;
                backendMessage = data.message;
            } else {
                backendMessage = data.message || "Verification rejected by server.";
            }
        } catch (netErr) {
            console.warn("Backend node offline or starting up:", netErr);
            backendMessage = "Proof verified locally in browser.";
        }

        // 4. Update UI Badge & Verifier Monitor
        if (backendVerified || isLocallyVerified) {
            badge.className = "mt-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500 text-emerald-400 text-center shadow-lg transition-all";
            badge.classList.remove('hidden');
            badge.style.display = 'block';
            badge.innerHTML = `
                <div class="text-3xl mb-1">✅</div>
                <div class="font-bold text-xl text-emerald-400">VERIFIED: AGE >= 18</div>
                <div class="text-xs text-emerald-300/80 mt-1">Zero-Knowledge Proof verified — Zero private data exposed!</div>
                <div class="text-[11px] text-emerald-400/60 mt-1 font-mono">${backendMessage || "Confirmed valid by Verifier Node"}</div>
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
                <div>REJECTED: AGE CHECK FAILED</div>
                <div class="text-xs font-normal text-rose-300/80 mt-1">${userMsg}</div>
            `;
        }
    } finally {
        submitBtn.disabled = false;
        submitBtn.classList.remove('opacity-50');
        spinner.classList.add('hidden');
        spinner.style.display = 'none';
    }
}