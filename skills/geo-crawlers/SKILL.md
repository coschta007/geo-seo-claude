---
name: geo-crawlers
description: AI crawler access analysis. Checks robots.txt, meta tags, and HTTP headers to determine which AI crawlers can access the site. Provides a complete access map and recommendations for maximizing AI visibility while maintaining appropriate control.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - WebFetch
  - Write
---

# AI Crawler Access Analysis Skill

## Purpose

This skill analyzes a website's accessibility to AI crawlers -- the bots that AI companies use to discover, index, and train on web content. If AI search crawlers are blocked, the site's content cannot appear in AI-generated search answers regardless of its quality. Crawler access is the foundational technical requirement for GEO.

Operators increasingly split their crawlers by purpose: OpenAI uses GPTBot for model training and OAI-SearchBot for ChatGPT search; Anthropic uses ClaudeBot for training and Claude-SearchBot for search. Each robots.txt rule is independent, so a site can block training and still appear in AI search. Always judge a block by what the blocked crawler is actually used for.

## Key Insight

As of early 2026, many websites inadvertently block AI crawlers through overly aggressive robots.txt rules, inherited from legacy SEO configurations. An Originality.ai 2025 study found that over 35% of the top 1,000 websites block at least one major AI crawler, and 5-10% block all AI crawlers. Blocking AI crawlers is the single fastest way to become invisible in AI-generated search results.

---

## Complete AI Crawler Reference

### Tier 1: Critical for AI Search Visibility (RECOMMEND: ALLOW)

These crawlers fetch content for the AI search and answer products where users actively look for answers. Blocking them directly reduces your visibility in AI-generated responses.

#### OAI-SearchBot
- **Operator:** OpenAI
- **User-Agent:** `OAI-SearchBot`
- **Full User-Agent String:** `Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; OAI-SearchBot/1.0; +https://docs.openai.com/bots/overview)`
- **Purpose:** Surfaces websites in ChatGPT's search features. OpenAI documents its robots.txt settings as independent of each other: a site can allow OAI-SearchBot and disallow GPTBot. Whether content may be used for training is decided by the GPTBot rule alone.
- **Impact of Blocking:** Content will not be shown in ChatGPT search answers (OpenAI notes it can still appear as a plain navigational link). OpenAI says robots.txt changes take about 24 hours to take effect.
- **Recommendation:** **ALLOW** -- This is the crawler that decides ChatGPT search visibility (ChatGPT has 300M+ weekly active users as of 2025). There is no strategic reason to block it.

#### ChatGPT-User
- **Operator:** OpenAI
- **User-Agent:** `ChatGPT-User`
- **Full User-Agent String:** `Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ChatGPT-User/1.0; +https://openai.com/bot)`
- **Purpose:** Fetches pages when a ChatGPT user's request needs them, acting on behalf of the user. It does not crawl automatically and is not used to decide whether content appears in ChatGPT search (that is OAI-SearchBot).
- **Impact of Blocking:** OpenAI states that robots.txt rules may not apply to these user-initiated requests, so a block may not stop them. Where it does, ChatGPT cannot read your pages when users ask it to.
- **Recommendation:** **ALLOW** -- Blocking this bot only affects users who are actively trying to engage with your content through ChatGPT.

#### Claude-SearchBot
- **Operator:** Anthropic
- **User-Agent:** `Claude-SearchBot`
- **Purpose:** Crawls the web to improve the relevance and accuracy of Claude's search results. Not used for training (that is ClaudeBot).
- **Impact of Blocking:** Content is not indexed for Claude's search, which Anthropic says may reduce the site's visibility and accuracy in Claude search results.
- **Recommendation:** **ALLOW** -- This is the crawler that decides Claude search visibility.

#### Claude-User
- **Operator:** Anthropic
- **User-Agent:** `Claude-User`
- **Purpose:** Fetches pages when a Claude user asks a question that needs live web content.
- **Impact of Blocking:** Claude cannot retrieve your content in response to user queries, which Anthropic says may reduce visibility for user-directed web search.
- **Recommendation:** **ALLOW** -- Blocking this bot only affects users who are actively asking Claude about your content.

#### PerplexityBot
- **Operator:** Perplexity AI
- **User-Agent:** `PerplexityBot`
- **Full User-Agent String:** `Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)`
- **Purpose:** Powers Perplexity's AI search engine, which provides sourced answers with direct citations and links back to source pages.
- **Impact of Blocking:** Content will not appear in Perplexity search results. Perplexity is one of the best referral traffic sources among AI search products because it always displays source links.
- **Recommendation:** **ALLOW** -- Perplexity drives actual referral traffic and always attributes sources. High-value AI crawler for publishers and businesses.

---

### Tier 2: Important for Broader AI Ecosystem (RECOMMEND: ALLOW)

These crawlers serve large AI platforms or search ecosystems. Allowing them increases your content's reach.

Four of them only control model training: **GPTBot, ClaudeBot, Google-Extended and Applebot-Extended**. Blocking them does not remove a site from ChatGPT search, Claude search, Google Search (including AI Overviews) or Siri and Spotlight. It keeps future content out of model training, which can affect what models know about a brand when they answer without searching. Treat a training block as a deliberate licensing choice, not as a visibility defect, as long as the matching search crawler is allowed.

#### GPTBot
- **Operator:** OpenAI
- **User-Agent:** `GPTBot`
- **Full User-Agent String:** `Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)`
- **Purpose:** Crawls content that may be used to train OpenAI's generative AI foundation models. Not used for ChatGPT search (that is OAI-SearchBot).
- **Impact of Blocking:** Future content is excluded from OpenAI model training. ChatGPT search visibility is unaffected as long as OAI-SearchBot is allowed.
- **Recommendation:** **ALLOW** for maximum presence in model knowledge. Blocking is a legitimate training opt-out with no effect on ChatGPT search.

#### ClaudeBot
- **Operator:** Anthropic
- **User-Agent:** `ClaudeBot`
- **Full User-Agent String:** `ClaudeBot/1.0; +https://www.anthropic.com/claude-bot`
- **Purpose:** Collects web content that may contribute to training Anthropic's models. Claude's search uses Claude-SearchBot, and user-initiated fetches use Claude-User.
- **Impact of Blocking:** Future content is excluded from Anthropic model training. Claude search visibility is unaffected as long as Claude-SearchBot is allowed.
- **Recommendation:** **ALLOW** for maximum presence in model knowledge. Blocking is a legitimate training opt-out with no effect on Claude search.

#### Google-Extended
- **Operator:** Google
- **User-Agent:** `Google-Extended` (a robots.txt product token; Google crawls with its regular user agents)
- **Purpose:** Controls whether content Google crawls may be used to train Gemini models and to ground answers in Gemini apps and Vertex AI. **CRITICAL NOTE:** Google-Extended does NOT affect inclusion or ranking in Google Search, and that includes AI Overviews and AI Mode. Those are Search features, governed by Googlebot and the standard snippet controls (`nosnippet`, `max-snippet`, `noindex`).
- **Impact of Blocking:** Content may not be used for Gemini training or grounding in Gemini apps. Appearance in Google Search and AI Overviews is unaffected.
- **Recommendation:** **ALLOW** -- Keeps content available to Gemini. Blocking is a legitimate training opt-out with no Google Search impact.

#### GoogleOther
- **Operator:** Google
- **User-Agent:** `GoogleOther`
- **Purpose:** Used by Google for various non-search-ranking purposes including research, one-off crawls, and AI-related data collection.
- **Impact of Blocking:** Minimal impact on search rankings. May reduce presence in Google's AI research and experimental features.
- **Recommendation:** **ALLOW** -- Low risk, moderate potential benefit for AI feature inclusion.

#### Applebot-Extended
- **Operator:** Apple
- **User-Agent:** `Applebot-Extended`
- **Purpose:** Used by Apple to train and improve Apple Intelligence features, Siri, and Apple's AI products. Separate from standard Applebot (which powers Siri search and Spotlight Suggestions).
- **Impact of Blocking:** Content may not be used in Apple Intelligence features. Standard Siri and Spotlight functionality is unaffected (controlled by Applebot).
- **Recommendation:** **ALLOW** -- Apple Intelligence is integrated into all Apple devices (2B+ active devices). Presence in Apple's AI features has growing strategic value.

#### Amazonbot
- **Operator:** Amazon
- **User-Agent:** `Amazonbot`
- **Full User-Agent String:** `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/600.2.5 (KHTML, like Gecko) Version/8.0.2 Safari/600.2.5 (compatible; Amazonbot/0.1; +https://developer.amazon.com/support/amazonbot)`
- **Purpose:** Indexes content for Alexa answers and Amazon's AI features.
- **Impact of Blocking:** Content will not appear in Alexa voice responses or Amazon's AI-powered search features.
- **Recommendation:** **ALLOW** -- Relevant for voice search optimization. Lower priority than Tier 1 crawlers but no downside to allowing.

#### FacebookBot
- **Operator:** Meta
- **User-Agent:** `FacebookBot`
- **Purpose:** Used by Meta for AI features across Facebook, Instagram, WhatsApp, and Meta AI assistant.
- **Impact of Blocking:** Content may not be accessible to Meta AI. Link previews on Facebook/Instagram are handled by a different crawler and are unaffected.
- **Recommendation:** **ALLOW** -- Meta AI is embedded in apps with 3B+ combined users. Growing importance for AI visibility.

---

### Tier 3: Training-Only Crawlers (ALLOW or BLOCK Based on Strategy)

These crawlers are primarily used for AI model training rather than live search features. Blocking them does not affect AI search visibility.

#### CCBot
- **Operator:** Common Crawl (nonprofit)
- **User-Agent:** `CCBot`
- **Full User-Agent String:** `CCBot/2.0 (https://commoncrawl.org/faq/)`
- **Purpose:** Builds the Common Crawl dataset, which is used as training data by many AI companies (Google, Meta, Stability AI, and others).
- **Impact of Blocking:** Content will not appear in future Common Crawl datasets. Does NOT affect any live AI search product.
- **Recommendation:** **CONTEXT-DEPENDENT** -- Allow if you want maximum long-term AI training presence. Block if you want to control training data usage. No impact on search visibility.

#### anthropic-ai
- **Operator:** Anthropic
- **User-Agent:** `anthropic-ai`
- **Purpose:** Legacy Anthropic user agent. Anthropic's current crawler documentation lists ClaudeBot (training), Claude-SearchBot (search) and Claude-User (user requests).
- **Impact of Blocking:** No effect on Claude search (controlled by Claude-SearchBot) or user-initiated fetches (Claude-User). Keeping an existing rule is harmless.
- **Recommendation:** **CONTEXT-DEPENDENT** -- Mirror the site's ClaudeBot rule for consistency. No impact on live AI search.

#### Bytespider
- **Operator:** ByteDance
- **User-Agent:** `Bytespider`
- **Purpose:** Used by ByteDance for various AI products including TikTok's AI features and Doubao (their ChatGPT competitor in China).
- **Impact of Blocking:** Content will not be used for ByteDance AI products. Minimal impact for Western-market businesses.
- **Recommendation:** **BLOCK** for most Western businesses (aggressive crawling behavior reported, minimal search visibility benefit). **ALLOW** if targeting Chinese/Asian markets.

#### cohere-ai
- **Operator:** Cohere
- **User-Agent:** `cohere-ai`
- **Purpose:** Used by Cohere for model training. Cohere powers enterprise AI solutions and the Coral chat product.
- **Impact of Blocking:** Content will not be used for Cohere model training. Minimal direct consumer-facing impact.
- **Recommendation:** **CONTEXT-DEPENDENT** -- Low priority. Allow or block based on general training data stance.

---

## Recommendation Matrix Summary

| Crawler | Tier | Recommendation | Reason |
|---|---|---|---|
| OAI-SearchBot | 1 | **ALLOW** | ChatGPT search visibility (300M+ users) |
| ChatGPT-User | 1 | **ALLOW** | User-initiated fetches (robots.txt may not apply) |
| Claude-SearchBot | 1 | **ALLOW** | Claude search visibility |
| Claude-User | 1 | **ALLOW** | User-initiated fetches in Claude |
| PerplexityBot | 1 | **ALLOW** | Best referral traffic AI search |
| GPTBot | 2 | **ALLOW*** | OpenAI model training; no ChatGPT search impact |
| ClaudeBot | 2 | **ALLOW*** | Anthropic model training; no Claude search impact |
| Google-Extended | 2 | **ALLOW*** | Gemini training and grounding; no Google Search or AI Overviews impact |
| GoogleOther | 2 | **ALLOW** | Google AI research |
| Applebot-Extended | 2 | **ALLOW*** | Apple Intelligence (2B+ devices); no Siri/Spotlight impact |
| Amazonbot | 2 | **ALLOW** | Alexa and Amazon AI |
| FacebookBot | 2 | **ALLOW** | Meta AI (3B+ app users) |
| CCBot | 3 | Context | Training data only |
| anthropic-ai | 3 | Context | Legacy Anthropic token |
| Bytespider | 3 | **BLOCK** | Aggressive crawler, low benefit |
| cohere-ai | 3 | Context | Training data only |

\* Training control. Recommend ALLOW when the site wants maximum presence in model knowledge; a block is a legitimate opt-out that does not affect the matching search product.

### Maximum AI Visibility Configuration (robots.txt)

For sites wanting maximum AI search visibility:

```
# AI Crawlers - ALLOWED for AI search visibility
User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: GoogleOther
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: Amazonbot
Allow: /

User-agent: FacebookBot
Allow: /

# AI Crawlers - BLOCKED (aggressive/low value)
User-agent: Bytespider
Disallow: /

User-agent: CCBot
Disallow: /
```

### AI Search Without Training Configuration (robots.txt)

For sites that want to appear in AI search but keep content out of model training. OpenAI and Anthropic both document their search and training rules as independent, so this keeps ChatGPT and Claude search visibility:

```
# AI search and user-initiated fetches - ALLOWED
User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: PerplexityBot
Allow: /

# Model training - BLOCKED
User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: Applebot-Extended
Disallow: /

User-agent: CCBot
Disallow: /
```

---

## Analysis Procedure

### Step 1: Fetch and Parse robots.txt

1. Use WebFetch to retrieve `[domain]/robots.txt`.
2. Parse all User-agent directives and their associated Allow/Disallow rules.
3. For each AI crawler in the reference list above:
   - Check if there is a specific User-agent block for that crawler
   - Check if there is a wildcard (`User-agent: *`) block that would apply
   - Determine effective access: **Allowed**, **Blocked**, or **Not Mentioned** (inherits wildcard rules)
4. Note any `Crawl-delay` directives that may slow AI crawler access.
5. Check for `Sitemap` directives (AI crawlers use these for discovery).

### Step 2: Check Meta Robots Tags

1. For a sample of 5-10 key pages, fetch the HTML and check for:
   - `<meta name="robots" content="noindex">` -- blocks all bots
   - `<meta name="robots" content="nofollow">` -- prevents link following
   - `<meta name="robots" content="noai">` -- emerging tag to block AI use
   - `<meta name="robots" content="noimageai">` -- blocks AI image training
   - Bot-specific meta tags: `<meta name="GPTBot" content="noindex">`
2. Record any page-level overrides of the robots.txt directives.

### Step 3: Check HTTP Headers

1. For the same sample pages, check response headers for:
   - `X-Robots-Tag: noindex` -- HTTP header equivalent of meta noindex
   - `X-Robots-Tag: noai` -- HTTP header to block AI use
   - `X-Robots-Tag: noimageai` -- blocks AI image training
   - Bot-specific headers: `X-Robots-Tag: GPTBot: noindex`
2. Note that HTTP headers override meta tags and apply to non-HTML resources too.

### Step 4: Check for AI-Specific Files

1. Check for `/llms.txt` (emerging, optional convention). Google states that Google Search, including its AI features, does not use it, so record presence but never report its absence as an access problem.
2. Check for `/.well-known/ai-plugin.json` (OpenAI plugin manifest).
3. Check for `/ai.txt` (proposed standard, similar to ads.txt for AI).
4. Record presence/absence and quality of each file.

### Step 5: Assess JavaScript Rendering Requirements

1. Check if the site is a Single Page Application (SPA) or heavily JavaScript-rendered.
2. AI crawlers vary in their JavaScript rendering capabilities:
   - GPTBot: Limited JS rendering
   - ClaudeBot: Limited JS rendering
   - PerplexityBot: Limited JS rendering
   - Googlebot: Full JS rendering (but Google-Extended inherits this)
3. If critical content requires JS rendering, flag this as a potential issue.
4. Check for Server-Side Rendering (SSR) or Static Site Generation (SSG) as mitigations.

### Step 6: Parse Content Signals

Using the already-fetched robots.txt from Step 1, scan for `Content-Signal:` directives (IETF draft `draft-romm-aipref-contentsignals`).

1. Scan every line for a line starting with `Content-Signal:` (case-insensitive).
2. If found:
   - Parse all key=value pairs (split on `,` then on `=`).
   - Validate keys against the known set: `ai-train`, `search`, `ai-personalization`, `ai-retrieval`.
   - Validate values: only `yes` and `no` are valid.
   - Flag any unknown keys or invalid values as a warning — the spec is still an IETF draft.
   - Record the result as **Pass** and surface parsed values with plain-English meaning.
3. If absent: record as **Recommendation** — the site has not declared AI usage preferences.

No additional HTTP request is needed. robots.txt is already fetched in Step 1.

### Step 7: Detect Cloudflare Managed robots.txt

Using the already-fetched robots.txt from Step 1, check for a block starting with `# BEGIN Cloudflare Managed content` (case-insensitive).

1. If found, Cloudflare is prepending its managed robots.txt to the site's own file. That block disallows GPTBot, ClaudeBot, Google-Extended, Applebot-Extended, Amazonbot, Bytespider, CCBot and meta-externalagent. These are mostly training crawlers: the AI search crawlers OAI-SearchBot, Claude-SearchBot and PerplexityBot are not in the block, so ChatGPT, Claude and Perplexity search visibility is unaffected (Alexa is, through Amazonbot).
2. Record it as a **High** issue if the site owner's own rules allow these crawlers. The owner usually doesn't know it's on, because the block never appears in the robots.txt file on their server, only in the live response.
3. Recommend: in the Cloudflare dashboard, go to Security Settings, filter by "Bot traffic", and turn off "block training in robots.txt" if the site wants to be used by AI. If blocking training is intentional, note it as a deliberate choice, not an issue.

No additional HTTP request is needed. `fetch_page.py robots` returns this as `cloudflare_managed: true`.

---

## Output Format

Generate a file called `GEO-CRAWLER-ACCESS.md`:

```markdown
# AI Crawler Access Report: [Domain]

**Analysis Date:** [Date]
**Domain:** [Domain]
**robots.txt Status:** [Found/Not Found/Error]

---

## Crawler Access Summary

| Crawler | Operator | Tier | Status | Impact |
|---|---|---|---|---|
| OAI-SearchBot | OpenAI | 1 | [Allowed/Blocked/Not Mentioned] | [Impact description] |
| ChatGPT-User | OpenAI | 1 | [Status] | [Impact] |
| Claude-SearchBot | Anthropic | 1 | [Status] | [Impact] |
| Claude-User | Anthropic | 1 | [Status] | [Impact] |
| PerplexityBot | Perplexity | 1 | [Status] | [Impact] |
| GPTBot | OpenAI | 2 | [Status] | [Impact] |
| ClaudeBot | Anthropic | 2 | [Status] | [Impact] |
| Google-Extended | Google | 2 | [Status] | [Impact] |
| GoogleOther | Google | 2 | [Status] | [Impact] |
| Applebot-Extended | Apple | 2 | [Status] | [Impact] |
| Amazonbot | Amazon | 2 | [Status] | [Impact] |
| FacebookBot | Meta | 2 | [Status] | [Impact] |
| CCBot | Common Crawl | 3 | [Status] | [Impact] |
| anthropic-ai | Anthropic | 3 | [Status] | [Impact] |
| Bytespider | ByteDance | 3 | [Status] | [Impact] |
| cohere-ai | Cohere | 3 | [Status] | [Impact] |

## AI Visibility Score: [X]/100

**Tier 1 Access:** [X/5 crawlers allowed]
**Tier 2 Access:** [X/7 crawlers allowed]
**Tier 3 Access:** [X/4 crawlers allowed]

---

## Critical Issues

[List any Tier 1 crawlers that are blocked. A blocked training crawler (GPTBot, ClaudeBot, Google-Extended, Applebot-Extended) whose matching search crawler is allowed is a deliberate choice: list it under findings, not here.]

## Recommendations

### Immediate Actions
[Specific robots.txt changes needed]

### robots.txt Recommendation
```
[Complete recommended robots.txt content for AI crawlers]
```

### Additional Technical Findings
- **Meta Robots Tags:** [Findings]
- **X-Robots-Tag Headers:** [Findings]
- **JavaScript Rendering:** [Assessment]
- **llms.txt:** [Present/Absent]
- **Sitemap Accessibility:** [Assessment]

### Content Signals (IETF Draft)

**Status:** Present / Absent

<!-- If present: -->
| Signal Key | Value | Meaning |
|---|---|---|
| ai-train | no | Opted out of AI model training |
| search | yes | Permits use in AI-powered search results |

<!-- If absent: -->
**Recommendation:** Add a `Content-Signal:` directive to robots.txt to declare AI usage preferences explicitly. Example:

`Content-Signal: ai-train=no, search=yes, ai-retrieval=yes`

See https://contentsignals.org/ for the full specification.
```

---

## Scoring for Crawler Access

The AI Crawler Access Score is calculated as:

| Component | Weight | Scoring |
|---|---|---|
| Tier 1 Crawlers Allowed | 50% | 20 points per Tier 1 crawler allowed (5 crawlers = 100 points max, scaled to 50) |
| Tier 2 Crawlers Allowed | 25% | Share of the 7 Tier 2 crawlers allowed (7 crawlers = 100 points max, scaled to 25) |
| No Blanket AI Blocks | 15% | Full points if no `User-agent: *` Disallow: / and no noai meta tags |
| AI-Specific Files Present | 10% | 5 points for llms.txt, 5 points for sitemap accessible to AI crawlers |

Final score = sum of all weighted components, capped at 100.
