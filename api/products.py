"""
ShopMind Product Catalog
50 sample retail products across categories — used to build the FAISS vector store.
In production: replace with your database connector or Shopify/commerce API.
"""

PRODUCT_CATALOG = [
    # ── Headphones ──────────────────────────────────────────────────────────
    {
        "sku": "HP-001", "name": "Sony WH-1000XM5", "brand": "Sony",
        "category": "headphones", "price": 279.99, "rating": 4.8, "in_stock": True,
        "description": "Industry-leading noise canceling headphones with 30-hour battery, "
                       "multipoint connection for two devices, soft earcups, lightweight design. "
                       "Best for travel, commuting, and deep work. Foldable. USB-C charging. "
                       "Crystal clear call quality with beamforming mics."
    },
    {
        "sku": "HP-002", "name": "Bose QuietComfort 45", "brand": "Bose",
        "category": "headphones", "price": 199.00, "rating": 4.6, "in_stock": True,
        "description": "Premium wireless noise-canceling headphones with 24-hour battery. "
                       "TriPort acoustic architecture for balanced sound. Comfortable over-ear "
                       "design with memory foam. Ideal for office and travel use."
    },
    {
        "sku": "HP-003", "name": "Apple AirPods Max", "brand": "Apple",
        "category": "headphones", "price": 449.00, "rating": 4.5, "in_stock": True,
        "description": "Premium over-ear headphones with Apple H1 chip, adaptive EQ, "
                       "active noise cancellation, transparency mode. 20-hour battery. "
                       "Spatial audio with dynamic head tracking. Best for Apple ecosystem users."
    },
    {
        "sku": "HP-004", "name": "Jabra Evolve2 85", "brand": "Jabra",
        "category": "headphones", "price": 349.00, "rating": 4.7, "in_stock": True,
        "description": "Professional wireless headset with world-class ANC, 37-hour battery, "
                       "10-mic call technology. Built for enterprise and hybrid workers. "
                       "UC/MS certified. Ergonomic design for all-day wear."
    },
    {
        "sku": "HP-005", "name": "Anker Soundcore Q45", "brand": "Anker",
        "category": "headphones", "price": 59.99, "rating": 4.3, "in_stock": True,
        "description": "Budget wireless headphones with 40-hour battery, hybrid active noise "
                       "canceling, multi-mode ANC, foldable design. Best value pick for "
                       "students and casual listeners under $60."
    },
    {
        "sku": "HP-006", "name": "Sennheiser Momentum 4", "brand": "Sennheiser",
        "category": "headphones", "price": 279.95, "rating": 4.7, "in_stock": False,
        "description": "Audiophile-grade wireless headphones with 60-hour battery, adaptive ANC, "
                       "customizable sound via Smart Control app. Premium build with vegan leather. "
                       "Best-in-class sound signature for music lovers."
    },
    # ── Earbuds ─────────────────────────────────────────────────────────────
    {
        "sku": "EB-001", "name": "Apple AirPods Pro (2nd Gen)", "brand": "Apple",
        "category": "earbuds", "price": 189.00, "rating": 4.8, "in_stock": True,
        "description": "True wireless earbuds with H2 chip, Adaptive Transparency, Personalized "
                       "Spatial Audio, up to 30hr with case. IP68 sweat-resistant. Best for "
                       "iPhone users wanting premium ANC earbuds for workouts and commuting."
    },
    {
        "sku": "EB-002", "name": "Samsung Galaxy Buds2 Pro", "brand": "Samsung",
        "category": "earbuds", "price": 149.99, "rating": 4.5, "in_stock": True,
        "description": "Premium earbuds with 2.5D Sound, 360 Audio, intelligent ANC. "
                       "29-hour total playback. IPX7 water resistance. Ergonomic design. "
                       "Seamless integration with Galaxy devices."
    },
    {
        "sku": "EB-003", "name": "Sony WF-1000XM5", "brand": "Sony",
        "category": "earbuds", "price": 229.99, "rating": 4.7, "in_stock": True,
        "description": "Industry-best ANC in a compact earbud. 8hr battery + 24hr case. "
                       "Auto-switching between devices. QN2e chip for precise noise sensing. "
                       "Multipoint Bluetooth. Best overall premium earbuds for sound quality."
    },
    {
        "sku": "EB-004", "name": "Jabra Elite 4 Active", "brand": "Jabra",
        "category": "earbuds", "price": 79.99, "rating": 4.4, "in_stock": True,
        "description": "Sport earbuds with IP57 active-grade protection, 28hr battery total, "
                       "ANC, adjustable HearThrough, Spotify Tap. Best mid-range workout earbuds."
    },
    # ── Laptops ─────────────────────────────────────────────────────────────
    {
        "sku": "LT-001", "name": "MacBook Pro 14 (M3 Pro)", "brand": "Apple",
        "category": "laptops", "price": 1999.00, "rating": 4.9, "in_stock": True,
        "description": "Professional laptop with M3 Pro chip, Liquid Retina XDR display, "
                       "22-hour battery life, 18GB unified memory, 1TB SSD. Best for creators, "
                       "developers, and ML engineers. MagSafe 3 charging. MacOS."
    },
    {
        "sku": "LT-002", "name": "Dell XPS 15 (9530)", "brand": "Dell",
        "category": "laptops", "price": 1799.99, "rating": 4.6, "in_stock": True,
        "description": "Premium Windows laptop with Intel i7-13700H, RTX 4060, 15.6-inch OLED "
                       "touch display, 32GB RAM, 1TB NVMe SSD. Best Windows laptop for creative "
                       "professionals and developers who need GPU acceleration."
    },
    {
        "sku": "LT-003", "name": "Lenovo ThinkPad X1 Carbon", "brand": "Lenovo",
        "category": "laptops", "price": 1499.00, "rating": 4.7, "in_stock": True,
        "description": "Ultra-light business laptop at 2.48 lbs, Intel i7, 16GB RAM, 512GB SSD, "
                       "14-inch IPS display. MIL-SPEC durability. 15-hour battery. Best business "
                       "travel laptop. ThinkShield security. Windows 11 Pro."
    },
    {
        "sku": "LT-004", "name": "ASUS ROG Zephyrus G14", "brand": "ASUS",
        "category": "laptops", "price": 1449.99, "rating": 4.6, "in_stock": True,
        "description": "Gaming laptop with AMD Ryzen 9, RTX 4060, 14-inch 165Hz display, "
                       "32GB RAM, 1TB SSD. AniMe Matrix LED lid. Compact form factor for "
                       "gaming and content creation on the go."
    },
    {
        "sku": "LT-005", "name": "Acer Chromebook Plus 515", "brand": "Acer",
        "category": "laptops", "price": 399.99, "rating": 4.2, "in_stock": True,
        "description": "Best budget Chromebook with Intel Core i3, 8GB RAM, 128GB SSD, "
                       "15.6-inch Full HD display, 10-hour battery. ChromeOS with Google AI "
                       "features. Ideal for students and light productivity."
    },
    # ── Monitors ────────────────────────────────────────────────────────────
    {
        "sku": "MN-001", "name": "LG 27GP950-B UltraGear", "brand": "LG",
        "category": "monitors", "price": 599.99, "rating": 4.7, "in_stock": True,
        "description": "27-inch 4K Nano IPS gaming monitor, 144Hz (160Hz OC), 1ms response, "
                       "HDMI 2.1, NVIDIA G-Sync compatible, AMD FreeSync Premium Pro. "
                       "Best 4K gaming monitor with high refresh rate."
    },
    {
        "sku": "MN-002", "name": "Dell UltraSharp U2723QE", "brand": "Dell",
        "category": "monitors", "price": 649.99, "rating": 4.8, "in_stock": True,
        "description": "27-inch 4K USB-C hub monitor with IPS Black technology, 2000:1 contrast, "
                       "100% sRGB, 98% DCI-P3. Built-in KVM switch, 90W USB-C PD. Best "
                       "professional monitor for color-accurate work."
    },
    {
        "sku": "MN-003", "name": "Samsung Odyssey OLED G9", "brand": "Samsung",
        "category": "monitors", "price": 1099.99, "rating": 4.6, "in_stock": False,
        "description": "49-inch ultrawide curved OLED gaming monitor, 240Hz, 0.03ms GTG, "
                       "Dual QHD resolution. Infinite contrast OLED. Best ultrawide for "
                       "immersive gaming and multi-tasking."
    },
    # ── Keyboards ───────────────────────────────────────────────────────────
    {
        "sku": "KB-001", "name": "Keychron Q1 Pro", "brand": "Keychron",
        "category": "keyboards", "price": 199.99, "rating": 4.8, "in_stock": True,
        "description": "Premium wireless mechanical keyboard, 75% layout, QMK/Via compatible, "
                       "aluminum frame, pre-lubed Gateron Pro switches, gasket mount. Best "
                       "wireless mechanical keyboard for typing enthusiasts."
    },
    {
        "sku": "KB-002", "name": "Logitech MX Keys S", "brand": "Logitech",
        "category": "keyboards", "price": 109.99, "rating": 4.6, "in_stock": True,
        "description": "Wireless productivity keyboard with backlit spherical keys, multi-device "
                       "Bluetooth, smart illumination, 10-day battery. Low-profile switches. "
                       "Best for office use and multi-device switching."
    },
    {
        "sku": "KB-003", "name": "Das Keyboard 6 Professional", "brand": "Das Keyboard",
        "category": "keyboards", "price": 169.00, "rating": 4.5, "in_stock": True,
        "description": "Full-size wired mechanical keyboard with Cherry MX Blue switches, "
                       "anodized aluminum top panel, 2-port USB-C hub. Best for programmers "
                       "who want tactile feedback and a premium build."
    },
    # ── Mice ────────────────────────────────────────────────────────────────
    {
        "sku": "MS-001", "name": "Logitech MX Master 3S", "brand": "Logitech",
        "category": "mice", "price": 99.99, "rating": 4.8, "in_stock": True,
        "description": "Flagship ergonomic wireless mouse with 8K DPI optical sensor, "
                       "MagSpeed scroll wheel, 70-day battery, Bluetooth+USB receiver. "
                       "Best productivity mouse for right-handed users."
    },
    {
        "sku": "MS-002", "name": "Razer DeathAdder V3 Pro", "brand": "Razer",
        "category": "mice", "price": 149.99, "rating": 4.7, "in_stock": True,
        "description": "Professional wireless gaming mouse, 30K DPI Focus Pro sensor, "
                       "ultra-light 64g, 90-hour battery, HyperSpeed wireless. Best esports "
                       "wireless mouse. Ergonomic right-hand design."
    },
    {
        "sku": "MS-003", "name": "Apple Magic Mouse", "brand": "Apple",
        "category": "mice", "price": 79.00, "rating": 4.1, "in_stock": True,
        "description": "Wireless rechargeable mouse with Multi-Touch surface for gestures, "
                       "seamless scrolling, swipe between apps. Best for Mac users who want "
                       "native gesture integration. Lightning charging."
    },
    # ── Smartwatches ─────────────────────────────────────────────────────────
    {
        "sku": "SW-001", "name": "Apple Watch Series 9", "brand": "Apple",
        "category": "smartwatches", "price": 399.00, "rating": 4.8, "in_stock": True,
        "description": "Latest Apple Watch with S9 chip, Double Tap gesture, Precision Finding "
                       "for iPhone, always-on display, 18-hour battery. ECG, blood oxygen, "
                       "crash detection. Best for iPhone users tracking fitness and health."
    },
    {
        "sku": "SW-002", "name": "Samsung Galaxy Watch 6 Classic", "brand": "Samsung",
        "category": "smartwatches", "price": 379.99, "rating": 4.6, "in_stock": True,
        "description": "Premium smartwatch with rotating bezel, advanced sleep coaching, "
                       "body composition analysis, Wear OS 4, 40-hour battery. Best for "
                       "Android users who want comprehensive health tracking."
    },
    {
        "sku": "SW-003", "name": "Garmin Fenix 7X Solar", "brand": "Garmin",
        "category": "smartwatches", "price": 749.99, "rating": 4.8, "in_stock": True,
        "description": "Premium multisport GPS watch with solar charging, 28-day battery, "
                       "topographic maps, advanced training metrics, expedition-grade durability. "
                       "Best for serious athletes, hikers, and ultra-endurance athletes."
    },
    {
        "sku": "SW-004", "name": "Fitbit Versa 4", "brand": "Fitbit",
        "category": "smartwatches", "price": 149.95, "rating": 4.3, "in_stock": True,
        "description": "Fitness smartwatch with built-in GPS, 6-day battery, stress management "
                       "score, Active Zone Minutes, 40+ exercise modes. Google Wallet, Alexa. "
                       "Best budget smartwatch for fitness beginners."
    },
    # ── Tablets ─────────────────────────────────────────────────────────────
    {
        "sku": "TB-001", "name": "iPad Pro 12.9 (M2)", "brand": "Apple",
        "category": "tablets", "price": 1099.00, "rating": 4.8, "in_stock": True,
        "description": "Professional tablet with M2 chip, Liquid Retina XDR ProMotion display, "
                       "Apple Pencil 2 support, Thunderbolt port, 12MP front camera with "
                       "Center Stage. Best tablet for artists, note-takers, and creative pros."
    },
    {
        "sku": "TB-002", "name": "Samsung Galaxy Tab S9+", "brand": "Samsung",
        "category": "tablets", "price": 899.99, "rating": 4.6, "in_stock": True,
        "description": "Android tablet with Snapdragon 8 Gen 2, 12.4-inch Dynamic AMOLED, "
                       "IP68 water resistance, S Pen included, DeX mode for desktop experience. "
                       "Best Android tablet for productivity."
    },
    # ── Cameras ─────────────────────────────────────────────────────────────
    {
        "sku": "CM-001", "name": "Sony Alpha A7 IV", "brand": "Sony",
        "category": "cameras", "price": 2498.00, "rating": 4.9, "in_stock": True,
        "description": "Full-frame mirrorless camera with 33MP BSI-CMOS sensor, 10fps burst, "
                       "4K60 video, 5-axis IBIS, 759-point AF system, dual card slots. Best "
                       "all-around full-frame camera for enthusiasts and professionals."
    },
    {
        "sku": "CM-002", "name": "Fujifilm X100VI", "brand": "Fujifilm",
        "category": "cameras", "price": 1599.00, "rating": 4.8, "in_stock": False,
        "description": "Compact fixed-lens camera with 40MP X-Trans sensor, 6.2K video, "
                       "in-body stabilization, classic film simulations, built-in ND filter. "
                       "Best street photography camera for enthusiasts."
    },
    # ── Audio ────────────────────────────────────────────────────────────────
    {
        "sku": "AU-001", "name": "Sonos Era 300", "brand": "Sonos",
        "category": "audio", "price": 449.00, "rating": 4.7, "in_stock": True,
        "description": "Spatial audio speaker with six drivers, Dolby Atmos, WiFi+Bluetooth, "
                       "Trueplay tuning, voice mic array. Best standalone speaker for immersive "
                       "music listening in home environments."
    },
    {
        "sku": "AU-002", "name": "JBL Charge 5", "brand": "JBL",
        "category": "audio", "price": 149.95, "rating": 4.7, "in_stock": True,
        "description": "Portable waterproof Bluetooth speaker with 20-hour playtime, built-in "
                       "powerbank, IP67 rating, JBL PartyBoost for connecting multiple speakers. "
                       "Best rugged portable speaker for outdoor use."
    },
    {
        "sku": "AU-003", "name": "Bang & Olufsen Beosound A5", "brand": "Bang & Olufsen",
        "category": "audio", "price": 799.00, "rating": 4.6, "in_stock": True,
        "description": "Premium portable speaker with aluminum + oak design, 37-hour battery, "
                       "360-degree sound, IP65 protection, WiFi+Bluetooth, Spotify Connect. "
                       "Best premium portable speaker for audiophiles."
    },
    # ── Smart Home ───────────────────────────────────────────────────────────
    {
        "sku": "SH-001", "name": "Amazon Echo Show 10", "brand": "Amazon",
        "category": "smart home", "price": 199.99, "rating": 4.4, "in_stock": True,
        "description": "Smart display with 10.1-inch HD screen, built-in Alexa, automatic "
                       "motion tracking camera for video calls, premium stereo sound, Zigbee hub. "
                       "Best for Alexa smart home control center."
    },
    {
        "sku": "SH-002", "name": "Google Nest Hub Max", "brand": "Google",
        "category": "smart home", "price": 179.99, "rating": 4.4, "in_stock": True,
        "description": "10-inch smart home display with Google Assistant, built-in camera with "
                       "Face Match, Nest camera hub, 30W stereo speakers. Best for Google Home "
                       "ecosystem users."
    },
    {
        "sku": "SH-003", "name": "Philips Hue Starter Kit", "brand": "Philips",
        "category": "smart home", "price": 179.99, "rating": 4.6, "in_stock": True,
        "description": "Smart lighting starter kit with 4 A19 bulbs (white and color ambiance), "
                       "Hue Bridge, 16 million colors, voice and app control, Works with Alexa/"
                       "Google/HomeKit. Best smart lighting ecosystem."
    },
    # ── Fitness ──────────────────────────────────────────────────────────────
    {
        "sku": "FT-001", "name": "Whoop 4.0", "brand": "Whoop",
        "category": "fitness", "price": 0.00, "rating": 4.5, "in_stock": True,
        "description": "Screenless wearable fitness tracker with 24/7 strain and recovery "
                       "coaching, 5-day battery, 100% continuous HR monitoring, blood oxygen, "
                       "skin temperature. Subscription-based. Best for serious athletes "
                       "optimizing performance."
    },
    {
        "sku": "FT-002", "name": "Theragun Prime", "brand": "Theragun",
        "category": "fitness", "price": 299.00, "rating": 4.7, "in_stock": True,
        "description": "Professional percussive therapy device with 5 attachments, 120-minute "
                       "battery, Bluetooth app integration, QuietForce Technology (60dB). "
                       "Best recovery tool for athletes and gym-goers."
    },
    # ── Backpacks / Bags ─────────────────────────────────────────────────────
    {
        "sku": "BG-001", "name": "Peak Design Everyday Backpack 20L", "brand": "Peak Design",
        "category": "bags", "price": 299.95, "rating": 4.8, "in_stock": True,
        "description": "Versatile camera and everyday backpack with MagLatch closure, internal "
                       "FlexFold dividers, side access panel, weatherproofed nylon, laptop sleeve. "
                       "Best premium backpack for photographers and daily carry."
    },
    {
        "sku": "BG-002", "name": "Cotopaxi Allpa 35L", "brand": "Cotopaxi",
        "category": "bags", "price": 249.00, "rating": 4.7, "in_stock": True,
        "description": "Travel backpack designed as a carry-on, clamshell opening, internal "
                       "organization, laptop sleeve, hip belt, TSA-friendly. Made from recycled "
                       "nylon. Best travel backpack for one-bag travel."
    },
    # ── Phones ───────────────────────────────────────────────────────────────
    {
        "sku": "PH-001", "name": "iPhone 15 Pro", "brand": "Apple",
        "category": "phones", "price": 999.00, "rating": 4.8, "in_stock": True,
        "description": "Pro smartphone with A17 Pro chip, titanium frame, Action Button, "
                       "48MP main camera with 5x optical zoom, USB-C Thunderbolt, ProMotion display. "
                       "Best iPhone for power users."
    },
    {
        "sku": "PH-002", "name": "Samsung Galaxy S24 Ultra", "brand": "Samsung",
        "category": "phones", "price": 1299.99, "rating": 4.7, "in_stock": True,
        "description": "Android flagship with Snapdragon 8 Gen 3, built-in S Pen, 200MP quad "
                       "camera, 100x Space Zoom, titanium frame, 5000mAh battery, AI-powered "
                       "features. Best Android phone for power users and creators."
    },
    {
        "sku": "PH-003", "name": "Google Pixel 8 Pro", "brand": "Google",
        "category": "phones", "price": 999.00, "rating": 4.6, "in_stock": True,
        "description": "Google's flagship with Tensor G3 chip, 50MP wide + 48MP ultrawide + "
                       "48MP telephoto, 7 years of OS updates, Call Screen, Magic Eraser, "
                       "Best Take, temperature sensor. Best for AI features and clean Android."
    },
    # ── Chargers & Power ─────────────────────────────────────────────────────
    {
        "sku": "CH-001", "name": "Anker 737 Power Bank", "brand": "Anker",
        "category": "power", "price": 89.99, "rating": 4.7, "in_stock": True,
        "description": "24,000mAh portable charger with 140W output, smart digital display, "
                       "charges MacBook Pro from 0-50% in 32 minutes. 3 ports simultaneous. "
                       "Best high-wattage power bank for laptops and multiple devices."
    },
    {
        "sku": "CH-002", "name": "Belkin BoostCharge Pro 3-in-1", "brand": "Belkin",
        "category": "power", "price": 99.99, "rating": 4.5, "in_stock": True,
        "description": "3-in-1 wireless charging pad for iPhone 15 MagSafe, Apple Watch, "
                       "and AirPods simultaneously. 15W fast wireless charging. Best for "
                       "Apple ecosystem users who want a clean charging station."
    },
]
