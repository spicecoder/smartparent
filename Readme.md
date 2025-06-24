# SmartGuard - AI-Powered Parental Network Monitor

> *Intelligent family digital wellness through contextual network monitoring*
## Follow Progress Here - https://docs.google.com/document/d/1IwiegovGq8HE8o94GQXhwb0HJ7YpOz4ULNJYlr5LSug/edit?usp=drive-slack&ts=685a7333
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Raspberry Pi](https://img.shields.io/badge/Platform-Raspberry%20Pi%204-red.svg)](https://raspberrypi.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)]()

## 🎯 Project Overview

SmartGuard is an intelligent network monitoring system designed to help parents understand and guide their teenagers' internet usage through AI-powered content analysis. Unlike traditional parental controls that simply block content, SmartGuard provides contextual understanding - distinguishing between a teenager researching "drugs" for a school health project versus visiting actual drug-related websites.

### The Problem We're Solving

- **Context-blind filtering**: Traditional parental controls can't distinguish educational content from inappropriate material
- **False positives overload**: Parents get overwhelmed with alerts about harmless content  
- **Easy circumvention**: Tech-savvy teenagers easily bypass simple keyword-based filters
- **Lack of family insight**: No visibility into healthy vs. concerning digital behavior patterns
- **All-or-nothing approach**: Current solutions are either too restrictive or too permissive

## Project Limitation
What the Pi Actually Sees
DNS Queries Only:

facebook.com
reddit.com/r/teenagers
youtube.com
example-drug-site.com

What It Doesn't See:

Actual page content
Search terms ("how to make drugs" vs "drugs for health project")
Videos watched
Messages sent
Images viewed
HTTPS traffic content (which is 95%+ of modern web traffic)

The Smart Analysis Limitation
The LLM classification in your project can only work with:

Domain names (youtube.com, reddit.com)
Subdomains (m.facebook.com, old.reddit.com)
Basic URL patterns if available in DNS requests

It cannot distinguish between:

Educational YouTube video about drug awareness vs. inappropriate content
Reddit homework help vs. harmful communities
Google search for "drugs" (school project) vs. actual drug-seeking behavior

Why This Architecture Was Chosen
 

Privacy Compliance: Deep packet inspection raises serious privacy/legal concerns
Technical Simplicity: DNS monitoring is much easier to implement
Encryption Reality: Most traffic is HTTPS-encrypted anyway
Legal Requirements: Intercepting actual content could violate wiretapping laws

Real-World Implications for Your this Project
Your SmartParent tool will be effective for:

✅ Identifying visits to known problematic domains
✅ Tracking time spent on different categories of sites
✅ Detecting unusual browsing patterns (new domains, late-night activity)
✅ Blocking access to specific categories

But it will miss:

❌ Context within legitimate sites (harmful content on YouTube/Reddit)
❌ Encrypted messaging apps content
❌ Search query intent
❌ Social media interactions

