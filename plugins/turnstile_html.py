
TURNSTILE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verification Required - OTAKULUX</title>
    <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
    <style>
        :root {
            --bg-color: #0f0f12;
            --text-color: #ffffff;
            --accent-color: #00ffcc;
            --container-bg: #1a1a24;
            --danger-color: #ff4d4d;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            overflow: hidden;
        }

        .container {
            background-color: var(--container-bg);
            padding: 2.5rem;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            text-align: center;
            width: 90%;
            max-width: 400px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        h1 {
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
            color: var(--accent-color);
        }

        .timer-box {
            font-size: 2.5rem;
            font-weight: bold;
            margin: 1.5rem 0;
            color: var(--accent-color);
            background: rgba(0, 255, 204, 0.1);
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid rgba(0, 255, 204, 0.3);
        }

        p {
            font-size: 1rem;
            color: #ccc;
            margin-bottom: 1.5rem;
        }

        .cf-turnstile {
            display: none;
            margin-bottom: 1.5rem;
        }

        #status-message {
            margin-top: 1rem;
            font-weight: 500;
        }

        .spinner {
            display: none;
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-left-color: var(--accent-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 1rem auto;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .error { color: var(--danger-color); }
        .success { color: var(--accent-color); }

        #submit-btn {
            display: none;
            background-color: var(--accent-color);
            color: #000;
            border: none;
            padding: 0.8rem 2rem;
            font-size: 1rem;
            font-weight: bold;
            border-radius: 5px;
            cursor: pointer;
            transition: transform 0.2s, opacity 0.2s;
            width: 100%;
        }

        #submit-btn:hover {
            transform: scale(1.02);
        }

        #submit-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Security Check</h1>
        <p id="instruction">Please wait for the timer to complete...</p>

        <div id="timer-display" class="timer-box">100</div>

        <div id="turnstile-container">
            <div class="cf-turnstile" data-sitekey="{{ SITE_KEY }}" data-callback="onTurnstileSuccess"></div>
        </div>

        <button id="submit-btn" disabled onclick="submitForm()">Verify & Proceed</button>

        <div id="loader" class="spinner"></div>
        <div id="status-message"></div>
    </div>

    <script>
        let timeLeft = 100;
        let turnstileToken = null;
        const timerDisplay = document.getElementById('timer-display');
        const submitBtn = document.getElementById('submit-btn');
        const instruction = document.getElementById('instruction');
        const turnstileWidget = document.querySelector('.cf-turnstile');

        const countdown = setInterval(() => {
            timeLeft--;
            timerDisplay.textContent = timeLeft;
            if (timeLeft <= 0) {
                clearInterval(countdown);
                timerDisplay.style.display = 'none';
                instruction.textContent = 'Please complete the verification below.';
                turnstileWidget.style.display = 'inline-block';
            }
        }, 1000);

        function onTurnstileSuccess(token) {
            turnstileToken = token;
            submitBtn.style.display = 'block';
            submitBtn.disabled = false;
        }

        function submitForm() {
            const statusMsg = document.getElementById('status-message');
            const loader = document.getElementById('loader');
            const turnstileContainer = document.getElementById('turnstile-container');

            submitBtn.style.display = 'none';
            turnstileContainer.style.display = 'none';
            loader.style.display = 'block';
            statusMsg.textContent = 'Verifying security...';
            statusMsg.className = '';

            fetch('/verify_token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    token: turnstileToken,
                    payload: "{{ PAYLOAD }}",
                    session_id: "{{ SESSION_ID }}"
                })
            })
            .then(response => response.json())
            .then(data => {
                loader.style.display = 'none';
                if (data.success) {
                    statusMsg.textContent = 'Verification successful! Redirecting...';
                    statusMsg.className = 'success';
                    setTimeout(() => { window.location.href = data.redirect; }, 1000);
                } else {
                    statusMsg.textContent = data.message || 'Verification failed.';
                    statusMsg.className = 'error';
                    if (data.banned) {
                        setTimeout(() => { window.location.href = '/banned'; }, 2000);
                    } else {
                        setTimeout(() => { window.location.reload(); }, 2000);
                    }
                }
            })
            .catch(error => {
                loader.style.display = 'none';
                statusMsg.textContent = 'Network error. Please try again.';
                statusMsg.className = 'error';
            });
        }
    </script>
</body>
</html>
"""

BANNED_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Access Blocked - OTAKULUX</title>
    <style>
        body {
            background-color: #0f0f12;
            color: #fff;
            font-family: sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .box {
            background: #1a1a24;
            padding: 3rem;
            border-radius: 15px;
            text-align: center;
            border: 1px solid #ff4d4d;
            max-width: 400px;
        }
        h1 { color: #ff4d4d; margin-top: 0; }
        .time { font-size: 1.5rem; font-weight: bold; color: #00ffcc; margin: 1rem 0; }
        p { color: #ccc; line-height: 1.5; }
    </style>
</head>
<body>
    <div class="box">
        <h1>ACCESS BLOCKED</h1>
        <p>You have been temporarily blocked due to repeated bypass attempts.</p>
        <p>Block expires in:</p>
        <div class="time">{{ TIME_LEFT }}</div>
        <p>Please try again after the block period has ended. Automated systems are monitored.</p>
    </div>
</body>
</html>
"""

BOT_DETECTED_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bot Detected - OTAKULUX</title>
    <style>
        body { background-color: #0f0f12; color: #fff; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { background: #1a1a24; padding: 3rem; border-radius: 15px; text-align: center; border: 1px solid #ff9900; }
        h1 { color: #ff9900; }
    </style>
</head>
<body>
    <div class="box">
        <h1>BOT DETECTED</h1>
        <p>Our security system has detected suspicious activity.</p>
        <p>Please return to the bot and try again using a real browser.</p>
    </div>
</body>
</html>
"""
