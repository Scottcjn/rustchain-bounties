<div align="right" dir="rtl">

# 🧱 RustChain: בלוקצ'יין הוכחת-עתיקות

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Consensus-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Network](https://img.shields.io/badge/Nodes-3%20Active-brightgreen)](https://rustchain.org/explorer)
[![As seen on BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**הבלוקצ'יין הראשון שמתגמל חומרה וינטג' על היותה ישנה, לא מהירה.**

*המחשב הנייד PowerPC G4 שלך מרוויח יותר ממחשב Threadripper מודרני. זו כל הנקודה.*

[אתר אינטרנט](https://rustchain.org) • [סייר חי](https://rustchain.org/explorer) • [החלף wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [התחלה מהירה wRTC](docs/wrtc.md) • [מדריך wRTC](docs/WRTC_ONBOARDING_TUTORIAL.md) • [הפניה בגרוקיפדיה](https://grokipedia.com/search?q=RustChain) • [נייר לבן](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [התחלה מהירה](#-התחלה-מהירה) • [איך זה עובד](#-איך-עובד-הוכחת-עתיקות)

</div>

---

## 🪙 wRTC על סולנה

אסימון RustChain (RTC) זמין כעת כ-**wRTC** על רשת סולנה דרך גשר BoTTube:

| משאב | קישור |
|----------|------|
| **החלף wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **תרשים מחירים** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **גשר RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **מדריך התחלה מהירה** | [wRTC התחלה מהירה (קנייה, גישור, בטיחות)](docs/wrtc.md) |
| **מדריך עלייה לאוויר** | [גשר wRTC + מדריך בטיחות החלפות](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **הפניה חיצונית** | [Grokipedia: RustChain](https://grokipedia.com/search?q=RustChain) |
| **Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 פרסומים אקדמיים

| מאמר | DOI | נושא |
|-------|-----|-------|
| **RustChain: CPU אחד, קול אחד** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | אלגוריתם קונצנזוס הוכחת-עתיקות, זיהוי חומרה |
| **Non-Bijunctive Permutation Collapse** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | AltiVec vec_perm לתשומת לב LLM (יתרון של 27-96x) |
| **PSE Hardware Entropy** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | אקראיות mftb של POWER8 לשונות התנהגותית |
| **Neuromorphic Prompt Translation** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623594.svg)](https://doi.org/10.5281/zenodo.18623594) | הנחיה רגשית לשיפור של 20% בדיפוזיית וידאו |
| **RAM Coffers** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18321905.svg)](https://doi.org/10.5281/zenodo.18321905) | ניהול משקלים מבוזר NUMA להסקת מסקנות LLM |

---

## 🎯 מה הופך את RustChain לשונה

| Proof-of-Work מסורתי | הוכחת-עתיקות |
|----------------|-------------------|
| מתגמל חומרה מהירה | מתגמל חומרה ישנה |
| חדש יותר = יותר טוב | ישן יותר = יותר טוב |
| בזבוז אנרגיה | משמר את היסטוריית המחשוב |
| מרוץ לתחתית | מתגמל שימור דיגיטלי |

**עיקרון מרכזי**: חומרה וינטג' אותנטית ששרדה עשרות שנים ראויה להכרה. RustChain הופך את הכרייה על פיה.

## ⚡ התחלה מהירה

### התקנה בשורת פקודה אחת (מומלץ)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

המתקין:
- ✅ מזהה את הפלטפורמה שלך אוטומטית (Linux/macOS, x86_64/ARM/PowerPC)
- ✅ יוצר סביבת Python וירטואלית מבודדת (ללא זיהום המערכת)
- ✅ מוריד את כורה הנכון עבור החומרה שלך
- ✅ מתקין הפעלה אוטומטית בעת האתחול (systemd/launchd)
- ✅ מספק הסרה קלה

### התקנה עם אפשרויות

**התקן עם ארנק ספציפי:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet my-miner-wallet
```

**הסרה:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### פלטפורמות נתמכות
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (אינטל, Apple Silicon, PowerPC)
- ✅ מערכות IBM POWER8

### לאחר ההתקנה

**בדוק את יתרת הארנק שלך:**
```bash
# הערה: שימוש בדגלים -sk בגלל שהצומת עשויה להשתמש בתעודת SSL חתומה עצמית
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_NAME"
```

**רשימת כורים פעילים:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**בדיקת תקינות הצומת:**
```bash
curl -sk https://50.28.86.131/health
```

**קבל את העידן הנוכחי:**
```bash
curl -sk https://50.28.86.131/epoch
```

**ניהול שירות הכורה:**

*Linux (systemd):*
```bash
systemctl --user status rustchain-miner    # בדיקת סטטוס
systemctl --user stop rustchain-miner      # עצירת כרייה
systemctl --user start rustchain-miner     # התחלת כרייה
journalctl --user -u rustchain-miner -f    # הצגת יומנים
```

*macOS (launchd):*
```bash
launchctl list | grep rustchain            # בדיקת סטטוס
launchctl stop com.rustchain.miner         # עצירת כרייה
launchctl start com.rustchain.miner        # התחלת כרייה
tail -f ~/.rustchain/miner.log             # הצגת יומנים
```

### התקנה ידנית
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet YOUR_WALLET_NAME
```

## 💰 מכפילי עתיקות

גיל החומרה שלך קובע את תגמול הכרייה:

| חומרה | עידן | מכפיל | דוגמא לרווחים |
|----------|-----|------------|------------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/עידן |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/עידן |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/עידן |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/עידן |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC/עידן |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/עידן |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/עידן |
| **x86_64 מודרני** | נוכחי | **1.0×** | 0.12 RTC/עידן |

*המכפילים פוחתים עם הזמן (15%/שנה) כדי למנוע יתרון קבוע.*

## 🔧 איך עובדת הוכחת-עתיקות

### 1. זיהוי חומרה (RIP-PoA)

כל כורה חייב להוכיח שהחומרה אמיתית, לא מודולה:

```
┌─────────────────────────────────────────────────────────────┐
│                  6 בדיקות חומרה                            │
├─────────────────────────────────────────────────────────────┤
│ 1. Clock-Skew & Oscillator Drift   ← דפוס הזדקנות סיליקון  │
│ 2. Cache Timing Fingerprint        ← טון זמן גישה L1/L2/L3  │
│ 3. SIMD Unit Identity              ← הטיית AltiVec/SSE/NEON│
│ 4. Thermal Drift Entropy           ← עקומות חום ייחודיות   │
│ 5. Instruction Path Jitter         ← מיפוי רעידות מיקרו-ארכיטקטורה |
│ 6. Anti-Emulation Checks           ← איתור מכונות וירטואליות/אמולטורים |
└─────────────────────────────────────────────────────────────┘
```

**למה זה חשוב**: אמולטור SheepShaver שמתחזה ל-Mac G4 ייכשל בבדיקות אלה. לסיליקון וינטג' אמיתי יש דפוסי הזדקנות ייחודיים שאי אפשר לזייף.

### 2. מעבד אחד = קול אחד (RIP-200)

בניגוד ל-PoW שבו כוח חישוב = קולות, RustChain משתמש ב**קונצנזוס מסתובב**:

- לכל חומרה ייחודית יש בדיוק קול אחד לכל עידן
- התגמולים מתחלקים שווה בשווה בין כל המצביעים, ואז מוכפלים במדד העתיקות
- אין יתרון להרצת מספר תהליכים או מעבדים מהירים יותר

### 3. תגמולים מבוססי עידן

```
משך עידן: 10 דקות (600 שניות)
בריכת תגמולים בסיסית: 1.5 RTC לעידן
חלוקה: חלוקה שווה × מכפיל עתיקות
```

**דוגמא עם 5 כורים:**
```
Mac G4 (2.5×):    0.30 RTC  ████████████████████
Mac G5 (2.0×):    0.24 RTC  ████████████████
מחשב מודרני (1.0×): 0.12 RTC  ████████
מחשב מודרני (1.0×): 0.12 RTC  ████████
מחשב מודרני (1.0×): 0.12 RTC  ████████
                  ─────────
סה"כ:            0.90 RTC (+ 0.60 RTC חוזרים לבריכה)
```

## 🌐 ארכיטקטורת רשת

### צמתים פעילים (3)

| צומת | מיקום | תפקיד | סטטוס |
|------|----------|------|--------|
| **צומת 1** | 50.28.86.131 | ראשי + סייר | ✅ פעיל |
| **צומת 2** | 50.28.86.153 | עוגן Ergo | ✅ פעיל |
| **צומת 3** | 76.8.228.245 | חיצוני (קהילתי) | ✅ פעיל |

### עיגון לרשת Ergo

RustChain נעגן מעת לעת לבלוקצ'יין Ergo לצורך בלתי-הפיכות:

```
עידן RustChain → Hash מחייב → עסקה ב-Ergo (רישום R4)
```

זה מספק הוכחה קריפטוגרפית שמצב RustChain היה קיים בזמן ספציפי.

## 📊 נקודות קצה API

```bash
# בדיקת תקינות רשת
curl -sk https://50.28.86.131/health

# קבלת עידן נוכחי
curl -sk https://50.28.86.131/epoch

# רשימת כורים פעילים
curl -sk https://50.28.86.131/api/miners

# בדיקת יתרת ארנק
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET"

# סייר בלוקים (דפדפן)
open https://rustchain.org/explorer
```

## 🖥️ פלטפורמות נתמכות

| פלטפורמה | ארכיטקטורה | סטטוס | הערות |
|----------|--------------|--------|-------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ תמיכה מלאה | כורה תואם Python 2.5 |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ תמיכה מלאה | מומלץ למק וינטג' |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ תמיכה מלאה | ביצועים מיטביים |
| **Ubuntu Linux** | x86_64 | ✅ תמיכה מלאה | כורה סטנדרטי |
| **macOS Sonoma** | Apple Silicon | ✅ תמיכה מלאה | שבבי M1/M2/M3 |
| **Windows 10/11** | x86_64 | ✅ תמיכה מלאה | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 נסיוני | תגים בלבד |

## 🏅 מערכת תגי NFT

קבל תגים למטרות כרייה:

| תג | דרישה | נדירות |
|-------|-------------|--------|
| 🔥 **Bondi G3 Flamekeeper** | כרייה ב-PowerPC G3 | נדיר |
| ⚡ **QuickBasic Listener** | כרייה ממחשב DOS | אגדי |
| 🛠️ **DOS WiFi Alchemist** | המחשב DOS ברשת | מיתי |
| 🏛️ **Pantheon Pioneer** | 100 הכורים הראשונים | מוגבל |

## 🔒 מודל אבטחה

### זיהוי מכונות וירטואליות
מכונות וירטואליות מזוהות ומקבלות **מיליארדית** מהתגמול הרגיל:
```
Mac G4 אמיתי:    2.5× מכפיל  = 0.30 RTC/עידן
G4 מאולץ:        0.0000000025× = 0.0000000003 RTC/עידן
```

### קשירת חומרה
כל חתימת חומרה נקשרת לארנק אחד. מונע:
- מספר ארנקים על אותו חומרה
- זיוף חומרה
- מתקפות סיביל

</div>