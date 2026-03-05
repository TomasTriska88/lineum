<script>
    import { content } from "$lib/content";
    import "../../app.css";
</script>

<div class="privacy-container">
    <h1>Privacy Policy</h1>
    <p class="last-updated">Last updated: {new Date().toLocaleDateString()}</p>

    <section>
        <h2>1. Introduction</h2>
        <p>
            Welcome to the Lineum Portal. We are committed to protecting your
            privacy and ensuring transparency about how we handle your data.
            This Privacy Policy explains what information we collect, how we use
            it, and your rights regarding that information.
        </p>
    </section>

    <section>
        <h2>2. Data Collection and Usage</h2>
        <p>
            We collect minimal data necessary to provide our services and ensure
            the security and stability of our platform.
        </p>
        <ul>
            <li>
                <strong>Session Cookies:</strong> We use a single essential
                cookie (<code>session_id</code>) to maintain your conversation
                state during your visit. This cookie is strictly necessary for
                the website to function.
            </li>
            <li>
                <strong>Usage Logging:</strong> We log anonymous usage statistics
                (token counts) associated with your session to monitor system load
                and managing our API budget. These logs do not contain personal identifiers.
            </li>
            <li>
                <strong>AI Processing:</strong> When you interact with our AI models,
                your input text is sent to Google's Gemini API for processing. Please
                do not share sensitive personal information in your chats.
            </li>
        </ul>
    </section>

    <section>
        <h2>3. Third-Party Services</h2>
        <p>
            We use <strong>Google Gemini API</strong> to provide AI chat
            functionality. By using this service, you acknowledge that your
            inputs are processed by Google in accordance with their
            <a
                href="https://policies.google.com/privacy"
                target="_blank"
                rel="noopener noreferrer">Privacy Policy</a
            >
            and
            <a
                href="https://policies.google.com/terms"
                target="_blank"
                rel="noopener noreferrer">Terms of Service</a
            >.
        </p>
    </section>

    <section>
        <h2>4. Your Rights</h2>
        <p>
            Under GDPR, you have the right to access, correct, or delete your
            personal data. Since we do not store personal accounts or persistent
            user profiles, most data is ephemeral. You can clear your session
            cookies at any time to reset your identifier.
        </p>
    </section>

    <section>
        <h2>5. Contact Us</h2>
        <p>
            If you have any questions about this Privacy Policy, please contact
            us at <a href="mailto:{content.contactEmail}"
                >{content.contactEmail}</a
            >.
        </p>
    </section>

    <div class="actions">
        <a href="/" class="button">Back to Home</a>
    </div>
</div>

<style>
    .privacy-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 4rem 2rem 8rem 2rem;
        color: #e0e0e0;
        font-family: "Inter", sans-serif;
    }

    h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #fff, #aaa);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .last-updated {
        font-size: 0.9rem;
        color: #888;
        margin-bottom: 3rem;
    }

    section {
        margin-bottom: 2.5rem;
    }

    h2 {
        font-size: 1.5rem;
        color: #fff;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0.5rem;
    }

    p,
    li {
        line-height: 1.6;
        color: #ccc;
        margin-bottom: 1rem;
    }

    ul {
        list-style-type: disc;
        padding-left: 1.5rem;
    }

    li {
        margin-bottom: 0.5rem;
    }

    a {
        color: var(--accent-color, #646cff);
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    .actions {
        margin-top: 4rem;
        text-align: center;
    }

    .button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.8rem 2rem;
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 4px;
        transition: background 0.2s;
        text-decoration: none;
        min-height: 44px;
    }

    .button:hover {
        background: rgba(255, 255, 255, 0.2);
        text-decoration: none;
    }
</style>
