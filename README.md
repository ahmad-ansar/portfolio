# Ahmad Ansar Portfolio

Static portfolio for Ahmad Ansar, a cybersecurity student at Wentworth Institute of Technology.

## Stack

- Plain HTML, CSS, and JavaScript
- No frontend framework
- No analytics or tracking scripts
- No backend password endpoint
- Cloudflare Pages security headers

## Local preview

From the repository root:

```bash
python -m http.server 8080
```

Open `http://localhost:8080`.

## Security and privacy choices

- The password strength demo runs only in the browser.
- The demo does not make network requests or log entered values.
- DOM updates use `textContent` instead of injecting user input as HTML.
- The generated sample uses the Web Crypto API with rejection sampling.
- A strict Content Security Policy blocks third-party scripts, network connections, frames, and form submissions.
- The public site omits a phone number, exact age, street address, and unrelated personal details.

The password estimator is educational. Its resistance estimate assumes a simplified offline attack model of 100 billion guesses per second and should not be treated as a guarantee.

## Deployment

Use the repository root as the Cloudflare Pages output directory. No build command is required.
