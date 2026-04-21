
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
            margin-bottom: 1rem;
            color: var(--accent-color);
        }

        p {
            font-size: 1rem;
            color: #ccc;
            margin-bottom: 2rem;
        }

        .cf-turnstile {
            display: inline-block;
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

        .error { color: #ff4d4d; }
        .success { color: var(--accent-color); }
    </style>
</head>
<body>
    <div class="container">
        <h1>Verify You Are Human</h1>
        <p>Please complete the security check to access your requested content.</p>

        <div id="turnstile-container">
            <div class="cf-turnstile" data-sitekey="{{ SITE_KEY }}" data-callback="javascriptCallback"></div>
        </div>

        <div id="loader" class="spinner"></div>
        <div id="status-message"></div>
    </div>

    <script>
        function javascriptCallback(token) {
            const statusMsg = document.getElementById('status-message');
            const loader = document.getElementById('loader');
            const turnstileContainer = document.getElementById('turnstile-container');

            // Hide Turnstile and show loader
            turnstileContainer.style.display = 'none';
            loader.style.display = 'block';
            statusMsg.textContent = 'Verifying...';
            statusMsg.className = '';

            // Send token to backend
            fetch('/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    token: token,
                    payload: "{{ PAYLOAD }}"
                })
            })
            .then(response => response.json())
            .then(data => {
                loader.style.display = 'none';
                if (data.success) {
                    statusMsg.textContent = 'Success! Redirecting...';
                    statusMsg.className = 'success';
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 1000);
                } else {
                    statusMsg.textContent = data.message || 'Verification failed. Please refresh.';
                    statusMsg.className = 'error';
                    // Re-show turnstile on failure
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                loader.style.display = 'none';
                statusMsg.textContent = 'An error occurred. Please try again.';
                statusMsg.className = 'error';
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            });
        }
    </script>
</body>
</html>
"""
