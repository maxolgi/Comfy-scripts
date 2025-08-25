# 🔑 Manual SSH Key Transfer (Private + Public) — No `scp`

Copy your SSH keys from an old host to a new one using only `cat` and `vi`.

---

## 1️⃣ On the Old Host — View & Copy Keys

```bash
cat ~/.ssh/id_ed25519
```
> **Private key** — copy everything exactly. Keep secret.

```bash
cat ~/.ssh/id_ed25519.pub
```
> **Public key** — copy this too. Safe to share, but still protect.

---

## 2️⃣ On the New Host — Create Key Files

**Private key:**
```bash
mkdir -p ~/.ssh
vi ~/.ssh/id_ed25519
```
Paste the private key text, save, exit.

**Public key:**
```bash
vi ~/.ssh/id_ed25519.pub
```
Paste the public key text, save, exit.

---

## 3️⃣ Set Correct Permissions

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

---

## 4️⃣ Test with GitHub

```bash
ssh -T git@github.com
```
Expected:
```
Hi <username>! You've successfully authenticated, but GitHub does not provide shell access.
```

---

⚠ **Security Tip:**  
Never paste your private key into untrusted systems, public repos, or shared screens. Treat it like a password.
