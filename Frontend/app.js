// ============================================================
// ZeroTrace Engine - Frontend
// Current Flow:
// OCR → Issuer
//
// Step 5 (ZKP Proof + Verify) will be added later.
// ============================================================


// ============================================================
// BACKEND API
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
            "px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-semibold";

        btnVerifier.className =
            "px-4 py-2 bg-slate-800 rounded-lg text-sm font-semibold";

    } else {

        userScreen.classList.add("hidden");
        verifierScreen.classList.remove("hidden");

        btnUser.className =
            "px-4 py-2 bg-slate-800 rounded-lg text-sm font-semibold";

        btnVerifier.className =
            "px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-semibold";
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
        proof: "🔐 Proof",
        verify: "✅ Verify"
    };

    if (status === "processing") {

        element.className =
            "stage p-4 rounded-lg bg-blue-500/10 border border-blue-500 text-blue-400";

        element.innerText =
            `${labels[stage]} — Processing...`;

    } else if (status === "success") {

        element.className =
            "stage p-4 rounded-lg bg-emerald-500/10 border border-emerald-500 text-emerald-400";

        element.innerText =
            `${labels[stage]} — ✓ Completed`;

    } else if (status === "failed") {

        element.className =
            "stage p-4 rounded-lg bg-rose-500/10 border border-rose-500 text-rose-400";

        element.innerText =
            `${labels[stage]} — ✗ Failed`;

    } else {

        element.className =
            "stage p-4 rounded-lg bg-slate-900 border border-slate-700";

        element.innerText =
            `${labels[stage]} — Waiting`;
    }
}


// ============================================================
// LOADING / STATUS UI
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
            ${success ? "CREDENTIAL ISSUED" : "REJECTED"}
        </div>

        <div class="text-sm mt-2">
            ${message}
        </div>
    `;
}

// ============================================================
// OCR → 12-DIGIT ID EXTRACTION
// ============================================================

function extractIdHash(ocrText) {

    /*
     * Aadhaar number = 12 digits.
     *
     * OCR may read it like:
     *
     * 1234 5678 9012
     *
     * or:
     *
     * 123456789012
     *
     * We remove spaces and other non-digit characters.
     */

    const digitsOnly = ocrText.replace(/\D/g, "");

    // Find a 12-digit number
    const match = digitsOnly.match(/\d{12}/);

    if (!match) {
        return null;
    }

    return match[0];
}


// ============================================================
// MAIN VERIFICATION FLOW
// ============================================================

async function handleVerification(event) {

    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    const fileInput = document.getElementById("id-document");
    const submitBtn = document.getElementById("submit-btn");

    // Reset old result
    const badge = document.getElementById("result-badge");

    badge.classList.add("hidden");
    badge.style.display = "none";

    submitBtn.disabled = true;
    submitBtn.classList.add("opacity-50");


    try {

        // ====================================================
        // STEP 1 — CHECK FILE
        // ====================================================

        if (!fileInput.files || fileInput.files.length === 0) {

            throw new Error(
                "Please upload a government ID document."
            );
        }


        // ====================================================
        // STEP 2 — OCR
        // ====================================================

        updateStage("ocr", "processing");

        setStatus(
            "Scanning ID locally in your browser..."
        );

        // Use let so we can remove our reference after OCR.
        let file = fileInput.files[0];


        let ocrText;

        try {

            const result = await Tesseract.recognize(
                file,
                "eng"
            );

            ocrText = result.data.text;

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


        // ====================================================
        // IMPORTANT PRIVACY STEP
        // ====================================================
        //
        // Raw image is no longer needed after OCR.
        //
        // Remove our reference immediately.
        // Clear file input so the browser no longer keeps
        // the selected document in the form.
        //

        file = null;
        fileInput.value = "";


        // ====================================================
        // STEP 3 — EXTRACT ID
        // ====================================================

        const idHash = extractIdHash(ocrText);

        console.log(
            "OCR extracted ID hash:",
            idHash
        );


        if (!idHash) {

            updateStage("ocr", "failed");

            throw new Error(
                "OCR could not detect a valid ID number. Please upload a clearer document."
            );
        }


        updateStage("ocr", "success");


        // ====================================================
        // STEP 4 — SEND OCR RESULT TO ISSUER
        // ====================================================

        updateStage("issuer", "processing");

        setStatus(
            "Sending extracted ID to the credential issuer..."
        );


        let credentialResponse;

        try {

            credentialResponse = await fetch(
                `${API_BASE}/api/issue-credential`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        ocr_id_hash: idHash
                    })
                }
            );

        } catch (networkError) {

            updateStage("issuer", "failed");

            throw new Error(
                "Unable to connect to the credential issuer."
            );
        }


        const credentialData =
            await credentialResponse.json();


        // ====================================================
        // ISSUER RESPONSE HANDLING
        // ====================================================

        if (!credentialResponse.ok) {

            updateStage("issuer", "failed");


            // ID not found
            if (credentialResponse.status === 404) {

                throw new Error(
                    "ID not found in the government database."
                );
            }


            // ID revoked
            if (credentialResponse.status === 403) {

                throw new Error(
                    "This ID has been revoked and cannot be used."
                );
            }


            // Other issuer error
            throw new Error(
                credentialData.error ||
                "Credential could not be issued."
            );
        }


        // ====================================================
        // CREDENTIAL SUCCESS
        // ====================================================

        console.log(
            "Credential received:",
            credentialData
        );

        updateStage("issuer", "success");


        // ====================================================
        // PHASE 1 COMPLETE
        // ====================================================

        showResult(
            "Your identity was successfully matched and a signed credential was issued.",
            true
        );


        console.log(
            "OCR → ISSUER completed successfully."
        );


        // ====================================================
        // STEP 5 WILL COME HERE
        // ====================================================
        //
        // Later:
        //
        // Credential
        //      ↓
        // ZKP Proof
        //      ↓
        // Verifier
        //
        // We are intentionally NOT implementing that yet.
        //


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

        // Reset button
        submitBtn.disabled = false;
        submitBtn.classList.remove("opacity-50");

        hideStatus();
    }
}