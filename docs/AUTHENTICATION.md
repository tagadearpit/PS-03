# Authentication

PayGuard AI now includes email/password account screens at `/login` and `/signup`, a password recovery screen at `/reset-password`, and an icon-only logout action in the signed-in navigation. The hero **Get started** CTA and the navigation **Sign in** action open the login route. New users can create an account and are redirected to the protected Verification Studio. The Scan History and Verification Studio routes also redirect unauthenticated visitors to login.

The current frontend implementation is a lightweight demo session. It stores the account profile and active-session flag in browser `localStorage`; it does not transmit or persist passwords and is not a production identity system. The reset form provides a safe success message without sending email in this demo. Before launch, replace the local `AuthPage` handlers with a real identity provider or backend authentication service, add password hashing, email verification, password reset email delivery, session expiry, CSRF protection, and server-side route authorization.

The generated login and signup visuals are stored in `client/src/assets/payguard-login.jpg` and `client/src/assets/payguard-signup.jpg`. The architecture page now uses `client/src/assets/payguard-architecture-v2.jpg`, a clearer left-to-right intake, risk-engine, and outcome composition.
