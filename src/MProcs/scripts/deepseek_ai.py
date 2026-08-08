import os
import json
import re
import urllib.parse
import keys as keys_module

try:
    import requests
    _requests_available = True
except ImportError:
    _requests_available = False

try:
    from bs4 import BeautifulSoup
    _bs4_available = True
except ImportError:
    _bs4_available = False

try:
    from ddgs import DDGS
    _ddgs_available = True
except ImportError:
    _ddgs_available = False

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

_messages = []
_session_buffer = []
_cmd_marker = 0

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information. Use this for real-time data, news, or anything requiring up-to-date knowledge.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of search results to return (default 5, max 10)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Fetch and read the content of a web page. Use this to browse websites, read articles, or get detailed information from a URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch"
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "Maximum characters to return (default 5000)",
                        "default": 5000
                    }
                },
                "required": ["url"]
            }
        }
    }
]

def write_output(text):
    global _cmd_marker
    _session_buffer.append(text)
    if len(_session_buffer) > 1000:
        _session_buffer[:500] = []
        _cmd_marker = max(0, _cmd_marker - 500)

def mark_cmd_boundary():
    global _cmd_marker
    _cmd_marker = len(_session_buffer)

def output_since_marker():
    if _cmd_marker >= len(_session_buffer):
        return ""
    return "\n".join(_session_buffer[_cmd_marker:])

def change_api_key():
    keys_module.set_key("deepseek_api_key", "")
    if "DEEPSEEK_API_KEY" in os.environ:
        del os.environ["DEEPSEEK_API_KEY"]
    print("API key cleared. You'll be prompted for a new one on next use.")

def get_api_key():
    api_key = keys_module.get_key("deepseek_api_key")
    if api_key:
        return api_key
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if api_key:
        return api_key
    api_key = input("Enter your Deepseek API key: ").strip()
    if api_key:
        keys_module.set_key("deepseek_api_key", api_key)
    return api_key

def read_session_lines(n=2):
    if len(_session_buffer) >= n:
        last = _session_buffer[-n:]
        return "\n".join(last)
    path = "MProcs-logs.txt"
    if not os.path.exists(path):
        return "\n".join(_session_buffer[-n:]) if _session_buffer else ""
    with open(path, "r") as fp:
        lines = fp.readlines()
    relevant = [l.strip() for l in lines if l.strip()]
    last = relevant[-n:] if len(relevant) >= n else relevant
    return "\n".join(last)

_BASE_PROMPT = (
    "You are a versatile AI assistant that responds meaningfully to any input. "
    "Handle questions, phrases, sentences, random letters, numbers, meta-tags, "
    "meta-seeds, meta-phrases, codes, symbols, and abstract patterns. "
    "Interpret creatively and respond with insight, analysis, or interpretation. "
    "Never refuse an input as meaningless — find meaning in everything."
)

_BROWSING_PROMPT = (
    "You are a versatile AI assistant that responds meaningfully to any input. "
    "Handle questions, phrases, sentences, random letters, numbers, meta-tags, "
    "meta-seeds, meta-phrases, codes, symbols, and abstract patterns. "
    "Interpret creatively and respond with insight, analysis, or interpretation. "
    "Never refuse an input as meaningless — find meaning in everything. "
    "When you need real-time or external information, use one of these tools: "
    "web_search(query) to search the web, web_fetch(url) to read a web page. "
    "To call a tool, end your response with exactly this format (no other text "
    "after it):\n"
    "<functioncall> {\"name\": \"tool_name\", \"arguments\": {\"arg1\": \"val1\"}} </functioncall>\n"
    "You can include a brief preamble before the tag, then the tag. "
    "The tool will be executed and its result provided to you."
)

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def web_search(query, max_results=5):
    if not _requests_available:
        return "Web search requires requests. Install with: pip install requests"
    max_results = min(max(max_results, 1), 10)
    if not _ddgs_available:
        return "Web search requires ddgs. Install with: pip install ddgs"

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            if results:
                formatted = []
                for i, r in enumerate(results, 1):
                    title = r.get("title", "")
                    body = r.get("body", "")
                    href = r.get("href", "")
                    formatted.append(f"{i}. {title}\n   URL: {href}\n   {body[:300]}")
                return "\n\n".join(formatted)
        except Exception:
            pass
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1},
            headers={"User-Agent": _UA},
            timeout=15,
        )
        data = resp.json()
        formatted = []
        abstract = data.get("AbstractText", "")
        if abstract:
            formatted.append(f"▸ {abstract[:500]}")
        for i, r in enumerate(data.get("Results", [])[:max_results], 1):
            formatted.append(f"{i}. {r.get('Text','')}\n   URL: {r.get('FirstURL','')}")
        for topic in data.get("RelatedTopics", []):
            if len(formatted) >= max_results:
                break
            if "Topics" in topic:
                for sub in topic["Topics"]:
                    if len(formatted) >= max_results:
                        break
                    if sub.get("Text"):
                        formatted.append(f"{len(formatted)+1}. {sub['Text'][:300]}")
            elif topic.get("Text"):
                formatted.append(f"{len(formatted)+1}. {topic['Text'][:300]}")
        if formatted:
            return "\n\n".join(formatted)
    except Exception:
        pass
    try:
        sug = requests.get(
            "https://duckduckgo.com/ac/",
            params={"q": query, "type": "list"},
            headers={"User-Agent": _UA},
            timeout=10,
        )
        items = [t for t in sug.json() if isinstance(t, str)]
        if items:
            return "\n".join(f"• {t}" for t in items[:max_results])
    except Exception:
        pass
    return f"No results found for '{query}'."

def web_fetch(url, max_chars=5000):
    if not _requests_available:
        return "Requests library is not available."
    if not _bs4_available:
        return "BeautifulSoup is not available. Install with: pip install beautifulsoup4"
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": _UA})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [l for l in text.split("\n") if l.strip()]
        text = "\n".join(lines)
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[Content truncated...]"
        return text if text.strip() else "Page appears to have no readable text content."
    except Exception as e:
        return f"Fetch error: {e}"

_AVAILABLE_TOOLS = {
    "web_search": web_search,
    "web_fetch": web_fetch,
}

_FCALL_XML_RE = re.compile(r'<functioncall>\s*(.*?)\s*</functioncall>', re.DOTALL)
_FCALL_BRACKET_RE = re.compile(
    r'\[Function\s*call:\s*(\w+)\s*\(([^)]*)\)\s*\]', re.IGNORECASE
)
_DSML = r'(?:\uFF5C\uFF5CDSML\uFF5C\uFF5C|(?:\|\|)DSML\|\|)?'
_FCALL_INVOKE_RE = re.compile(
    rf'<{_DSML}invoke\s+name\s*=\s*"(\w+)"[^>]*>(.*?)</{_DSML}invoke>', re.DOTALL
)
_FCALL_INVOKE_PARAM_RE = re.compile(
    rf'<{_DSML}parameter\s+name\s*=\s*"(\w+)"[^>]*>\s*(.*?)\s*</{_DSML}parameter>', re.DOTALL
)

def _parse_function_calls(text):
    calls = []
    for m in _FCALL_XML_RE.finditer(text):
        raw = m.group(1).strip()
        try:
            data = json.loads(raw)
            name = data.get("name", "")
            args = data.get("arguments", {})
            calls.append((name, args))
        except json.JSONDecodeError:
            pass

    for m in _FCALL_BRACKET_RE.finditer(text):
        name = m.group(1)
        raw_args = m.group(2)
        args = {}
        if raw_args.strip():
            for pair in raw_args.split(","):
                pair = pair.strip()
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"\'')
                    args[k] = v
        calls.append((name, args))

    for m in _FCALL_INVOKE_RE.finditer(text):
        name = m.group(1)
        inner = m.group(2)
        args = {}
        for pm in _FCALL_INVOKE_PARAM_RE.finditer(inner):
            k = pm.group(1)
            v = pm.group(2).strip().strip('"\'')
            if v.lower() in ("true", "false"):
                args[k] = v.lower() == "true"
            elif v.isdigit():
                args[k] = int(v)
            else:
                args[k] = v
        if name in _AVAILABLE_TOOLS:
            calls.append((name, args))

    return calls

def _execute_tool_calls(tool_calls_source):
    for tc in tool_calls_source:
        func_name = tc["function"]["name"]
        try:
            args = json.loads(tc["function"]["arguments"])
        except json.JSONDecodeError:
            args = {}

        tool_func = _AVAILABLE_TOOLS.get(func_name)
        if tool_func:
            result = tool_func(**args)
        else:
            result = f"Unknown tool: {func_name}"

        _messages.append({
            "role": "tool",
            "tool_call_id": tc["id"],
            "content": str(result),
        })

def chat_once(prompt, log_func=None, enable_browsing=True):
    global _messages
    if not _requests_available:
        return "Deepseek AI requires 'requests' library. Install with: pip install requests"
    api_key = get_api_key()
    if not api_key:
        return "No API key configured."

    write_output(f"DS q: {prompt}")
    if not _messages:
        prompt_text = _BROWSING_PROMPT if enable_browsing else _BASE_PROMPT
        _messages.append({"role": "system", "content": prompt_text})
    _messages.append({"role": "user", "content": prompt})

    _tool_call_id = 0

    max_turns = 10
    _dup_count = 0
    _prev_tool_calls = set()
    for turn in range(max_turns):
        payload = {
            "model": "deepseek-v4-flash",
            "messages": _messages,
            "stream": False,
        }
        if enable_browsing and turn < max_turns - 1:
            payload["tools"] = TOOLS
            payload["tool_choice"] = "auto"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=120)
            response.raise_for_status()
            data = response.json()
            choice = data["choices"][0]
            msg = choice["message"]
            reply = msg.get("content", "") or ""

            tool_calls = msg.get("tool_calls")
            fcall_calls = _parse_function_calls(reply) if (not tool_calls and enable_browsing) else []

            if not tool_calls and not fcall_calls:
                _messages.append({"role": "assistant", "content": reply})
                write_output(f"DS a: {reply}")
                if log_func:
                    log_func(prompt, reply)
                return reply

            if tool_calls:
                current_names = frozenset(tc["function"]["name"] for tc in tool_calls)
                if current_names == _prev_tool_calls:
                    _dup_count += 1
                    if _dup_count >= 2:
                        break
                else:
                    _dup_count = 0
                _prev_tool_calls = current_names
                assistant_msg = {"role": "assistant", "content": reply}
                assistant_msg["tool_calls"] = tool_calls
                _messages.append(assistant_msg)
                _execute_tool_calls(tool_calls)
            elif fcall_calls:
                tag_matches = list(_FCALL_XML_RE.finditer(reply))
                if not tag_matches:
                    tag_matches = list(_FCALL_BRACKET_RE.finditer(reply))
                if not tag_matches:
                    tag_matches = list(_FCALL_INVOKE_RE.finditer(reply))
                preamble = reply[:tag_matches[0].start()].strip() if tag_matches else reply
                if preamble:
                    _messages.append({"role": "assistant", "content": preamble})
                for name, args in fcall_calls:
                    _tool_call_id += 1
                    tc_source = [{
                        "id": f"call_{_tool_call_id}",
                        "function": {"name": name, "arguments": json.dumps(args)},
                    }]
                    _execute_tool_calls(tc_source)

        except requests.exceptions.RequestException as e:
            return f"Error: {e}"

    for msg in _messages:
        if msg["role"] == "system":
            msg["content"] = _BASE_PROMPT
            break
    for _ in range(3):
        final_payload = {
            "model": "deepseek-v4-flash",
            "messages": _messages,
            "stream": False,
        }
        try:
            r = requests.post(DEEPSEEK_API_URL, json=final_payload, headers=headers, timeout=120)
            r.raise_for_status()
            reply = r.json()["choices"][0]["message"].get("content", "") or ""
        except Exception:
            reply = ""
        if not reply.strip():
            continue
        stripped = reply.strip()
        if len(stripped) < 80 and stripped.startswith("<"):
            continue
        fcall_calls = _parse_function_calls(reply) if enable_browsing else []
        if not fcall_calls:
            _messages.append({"role": "assistant", "content": reply})
            write_output(f"DS a: {reply}")
            return reply
        tag_matches = list(_FCALL_XML_RE.finditer(reply))
        if not tag_matches:
            tag_matches = list(_FCALL_BRACKET_RE.finditer(reply))
        if not tag_matches:
            tag_matches = list(_FCALL_INVOKE_RE.finditer(reply))
        preamble = reply[:tag_matches[0].start()].strip() if tag_matches else ""
        preamble = re.sub(r'</?[\w\uff5c|]+[^>]*>', '', preamble).strip()
        if preamble:
            _messages.append({"role": "assistant", "content": preamble})
        for idx, (name, args) in enumerate(fcall_calls):
            tc_source = [{
                "id": f"call_fallback_{idx}",
                "function": {"name": name, "arguments": json.dumps(args)},
            }]
            _execute_tool_calls(tc_source)
    _xml_strip = re.compile(r'</?[\w\uff5c|]+[^>]*>', re.DOTALL)
    _messages.append({"role": "user", "content": "Please answer concisely without using XML tags or tool calls."})
    try:
        r = requests.post(DEEPSEEK_API_URL, json={"model": "deepseek-v4-flash", "messages": _messages, "stream": False}, headers=headers, timeout=120)
        r.raise_for_status()
        reply = r.json()["choices"][0]["message"].get("content", "") or ""
        if reply.strip() and not reply.strip().startswith("<"):
            _messages.append({"role": "assistant", "content": reply})
            write_output(f"DS a: {reply}")
            return reply
    except Exception:
        pass
    for msg in reversed(_messages):
        if msg["role"] == "assistant" and isinstance(msg.get("content"), str) and msg["content"].strip():
            reply = msg["content"]
            clean = _xml_strip.sub('', reply).strip()
            if clean:
                reply = clean
            write_output(f"DS a: {reply}")
            return reply
    return "Maximum tool call turns reached."

def reset():
    global _messages
    _messages = []

def interactive(initial_prompt=None, usr_prompt="", log_func=None, enable_browsing=True):
    if not get_api_key():
        print("No Deepseek API key found.")
        return
    reset()
    browsing = enable_browsing
    if browsing:
        print("Browsing tools: ENABLED (web search + page fetch)")
    if initial_prompt:
        reply = chat_once(initial_prompt, log_func=log_func, enable_browsing=browsing)
        print(f"DS: {reply}")
    while True:
        try:
            p = input(f"DS{usr_prompt} > ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if p.lower() in ("exit", "quit", "/exit", "/quit"):
            break
        if p.lower() in ("reset", "/reset"):
            reset()
            print("Conversation reset.")
            continue
        if p.lower() in ("/browse", "/browsing"):
            browsing = not browsing
            print(f"Browsing tools: {'ENABLED' if browsing else 'DISABLED'}")
            continue
        reply = chat_once(p, log_func=log_func, enable_browsing=browsing)
        print(f"DS: {reply}")
